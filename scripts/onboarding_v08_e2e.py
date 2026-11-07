"""True React UI + FastAPI TestClient with mocked external Telegram HTTP.

No claim of live provider delivery; this tests local onboarding UX and API
registration/diagnostics through real server handlers.
"""
import os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omni-v08-'))/'browser.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['PUBLIC_BASE_URL']='https://omnichat.example'
os.environ['COOKIE_SECURE']='false'
from cryptography.fernet import Fernet
os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright
from app.main import app
import app.integrations.adapters as adapters

async def fake(method,url,**kwargs):
    if url.endswith('/getMe'):
        return {'ok':True,'result':{'id':999010,'username':'osmanx_demo_onboarding_bot','is_bot':True}}
    raise RuntimeError('External provider call not allowed in UX test: '+method)
adapters.call=fake

with TestClient(app) as api:
    r=api.post('/api/auth/register',json={'company':'Автосалон Север','name':'Владелец',
        'email':'onboarding-owner@example.com','password':'StrongPassword!2026'})
    assert r.status_code==201,r.text
    csrf=api.cookies.get('omnichat_csrf')
    assert csrf
    register=api.post('/api/integrations/bots',json={'provider':'telegram','access_token':'999010:TEST-only-not-real-token'},headers={'X-CSRF-Token':csrf})
    assert register.status_code==201,register.text
    def bridge(payload):
        path=payload['url']
        method=payload.get('method','GET')
        assert str(path).startswith('/api/')
        res=api.request(method,path,headers={'Content-Type':'application/json','X-CSRF-Token':csrf},content=(payload.get('body') or '').encode() if payload.get('body') else None)
        return {'status':res.status_code,'body':res.text}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1512,'height':920},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.expose_function('omniApiBridge',bridge)
        page.set_content('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
        page.evaluate('''(csrf)=>{
          const mem={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>mem[k]||null,setItem:(k,v)=>mem[k]=v,removeItem:k=>delete mem[k]}});
          Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
          window.history.replaceState=()=>{};
          window.fetch=async(url,opts={})=>{const r=await window.omniApiBridge({url:String(url),method:opts.method||'GET',body:opts.body||null});return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})};
        }''',csrf)
        public=ROOT/'frontend/public'
        page.add_style_tag(path=str(public/'styles.css'))
        for f in ['vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js']:
            page.add_script_tag(path=str(public/f))
        page.locator('.inbox-list').wait_for(timeout=12000)
        menu=page.get_by_role('button',name='Интеграции',exact=True)
        if not menu.count():
            more=page.get_by_role('button',name='Ещё разделы')
            if more.count():more.click()
        page.get_by_role('button',name='Интеграции',exact=True).first.click()
        page.get_by_role('heading',name='Подключение каналов').wait_for(timeout=10000)
        assert page.locator('.integration-card').count()==7
        assert page.get_by_text('Этапы: 1 из 4').count()==1
        assert page.get_by_text('API-обмен проверен').count()==0
        page.get_by_role('button',name='Проверка по шагам').click()
        page.wait_for_function("document.querySelectorAll('.channel-step').length === 4",timeout=10000)
        assert page.locator('.channel-step').count()==4
        assert page.locator('.channel-step.is-complete').count()==1
        assert page.locator('.channel-step.is-pending').count()==3
        assert page.get_by_role('button',name='Проверить подписку').is_visible()
        page.locator('.onboarding-diagnostics').evaluate('(el)=>el.scrollIntoView({block:"start"})')
        screenshot=ROOT/'docs/preview-v08-onboarding.png'
        page.screenshot(path=str(screenshot),full_page=False)
        page.locator('.onboarding-diagnostics').screenshot(path=str(ROOT/'docs/preview-v08-steps.png'))
        overflow=page.evaluate('document.documentElement.scrollWidth-window.innerWidth')
        assert overflow<=0,overflow
        assert not errors,errors
        print('Desktop onboarding: 4 stages, tenant channel, no fake success, overflow',overflow,'->',screenshot)
        browser.close()
