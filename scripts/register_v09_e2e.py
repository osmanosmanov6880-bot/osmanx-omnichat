"""Real registration flow in the browser, ending in quickstart (no fabricated API state)."""
import os,sys,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omni-register-v09-'))/'site.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['COOKIE_SECURE']='false'
from fastapi.testclient import TestClient
from app.main import app
with TestClient(app) as api, sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1200,'height':830})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def bridge(payload):
        r=api.request(payload['method'],payload['url'],headers={'X-CSRF-Token':api.cookies.get('omnichat_csrf',''),'Content-Type':'application/json'},content=(payload.get('body') or '').encode() if payload.get('body') else None)
        return {'status':r.status_code,'body':r.text,'csrf':api.cookies.get('omnichat_csrf','')}
    page.expose_function('apiBridge',bridge)
    page.set_content('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
    page.evaluate('''()=>{
      const store={};window.history.replaceState=()=>{};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>store[k]||null,setItem:(k,v)=>store[k]=v}});
      let csrf='';Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
      window.fetch=async(url,opts={})=>{const result=await window.apiBridge({url:String(url),method:opts.method||'GET',body:opts.body||null});csrf=result.csrf;return new Response(result.body,{status:result.status,headers:{'Content-Type':'application/json'}})};
    }''')
    page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
    for name in ['vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js']:
        page.add_script_tag(path=str(ROOT/'frontend/public'/name))
    page.get_by_role('button',name='Регистрация').wait_for(timeout=10000)
    page.get_by_role('button',name='Регистрация').click()
    page.get_by_placeholder('Название компании').fill('Студия Проверка')
    page.get_by_placeholder('Как вас зовут?').fill('Владелец')
    page.get_by_placeholder('company@example.com').fill('ui-registered@example.com')
    page.get_by_placeholder('Не менее 12 символов для регистрации').fill('VeryStrongPassword!2026')
    page.get_by_role('button',name='Создать компанию',exact=True).click()
    page.get_by_role('heading',name='Настроим OSMANX за три шага').wait_for(timeout=10000)
    assert page.locator('.quickstart-step').count()==3
    assert api.get('/api/quickstart').json()['completed']==0
    assert not errors,errors
    page.screenshot(path=str(ROOT/'docs/preview-v09-after-register.png'))
    print('UI registration -> authenticated server -> 3-step quickstart OK')
    browser.close()
