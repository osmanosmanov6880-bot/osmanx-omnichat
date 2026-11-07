"""Real React/Chromium smoke test for v1.1 session controls.

Uses the real FastAPI TestClient, but no external network or provider accounts.
"""
from pathlib import Path
import os
import sys
import tempfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-v11-browser-'))/'ui.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as api:
    login={'email':'v11-review@example.com','password':'StrongLongPassword-2026!'}
    assert api.post('/api/auth/register',json={'company':'OSMANX Тест',
        'name':'Ответственный','email':login['email'],'password':login['password']}).status_code==201
    assert api.post('/api/auth/login',json=login).status_code==200
    csrf=api.cookies.get('omnichat_csrf')

    def bridge(payload):
        path=payload['url']
        assert path.startswith('/api/'),path
        resp=api.request(payload.get('method','GET'),path,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=(payload.get('body') or '').encode() if payload.get('body') else None)
        return {'status':resp.status_code,'body':resp.text}

    def load_ui(browser,width,height):
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.on('console',lambda msg:errors.append('CONSOLE '+msg.text) if msg.type=='error' else None)
        page.expose_function('bridgeOmni',bridge)
        page.set_content('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
        page.evaluate('''(csrf)=>{
            const memory={};
            Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memory[k]||null,setItem:(k,v)=>memory[k]=v}});
            Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
            window.history.replaceState=()=>{};
            window.fetch=async(url,opts={})=>{const r=await window.bridgeOmni({url:String(url),method:opts.method||'GET',body:opts.body||null});return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})};
        }''',csrf)
        page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
        for script in ['vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js']:
            page.add_script_tag(path=str(ROOT/'frontend/public'/script))
        page.locator('.quiet-nav .nav-item').first.wait_for(timeout=15000)
        if width<700:
            page.locator('.quiet-mobile-menu').click()
            page.locator('.sidebar.open').wait_for(timeout=5000)
        page.locator('.quiet-nav .nav-item').filter(has_text='Настройки').click()
        page.locator('.security-session-panel').wait_for(timeout=10000)
        return page,errors

    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        output=Path(os.environ.get('OMNICHAT_E2E_OUT',str(ROOT/'docs')))
        output.mkdir(parents=True,exist_ok=True)
        for width,height,name in [(1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')]:
            page,errors=load_ui(browser,width,height)
            page.get_by_role('button',name='Проверить сеансы').click()
            page.locator('.session-status').wait_for(timeout=9000)
            assert 'Активных сеансов:' in page.locator('.session-status').inner_text()
            over=page.evaluate('document.documentElement.scrollWidth-window.innerWidth')
            assert over<=0,f'{width}px overflow: {over}'
            assert not errors,(width,errors)
            screenshot=output/f'preview-v11-security-{name}.png'
            page.screenshot(path=str(screenshot),full_page=False)
            print('UI_SETTINGS_OK',name,screenshot)
            if name=='desktop':
                assert '2' in page.locator('.session-status').inner_text()
                page.get_by_role('button',name='Завершить другие сеансы').click()
                page.get_by_text('Активных сеансов:',exact=False).wait_for(timeout=5000)
                page.wait_for_timeout(160)
                assert '1' in page.locator('.session-status').inner_text()
            page.close()
        # Verify the logged in browser can revoke itself and returns to login.
        page,errors=load_ui(browser,1512,950)
        page.on('dialog',lambda dlg:dlg.accept())
        page.get_by_role('button',name='Выйти на всех устройствах').click()
        page.get_by_role('button',name='Вход',exact=True).wait_for(timeout=9000)
        assert api.get('/api/auth/me').status_code==401
        assert not errors,errors
        print('UI_REVOKE_ALL_AND_SIGN_OUT_OK')
        page.close()
        browser.close()
