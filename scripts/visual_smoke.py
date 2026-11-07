"""Offline Chromium smoke test of the actual compiled React UI (API responses fixture-backed)."""
import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ.setdefault('DATABASE_URL','sqlite:////tmp/omnichat-visual-smoke-qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as api:
    response=api.post('/api/demo/start')
    assert response.status_code==200,response.text
    routes={'/api/auth/me':api.get('/api/auth/me').json(),
            '/api/conversations':api.get('/api/conversations').json(),
            '/api/team':api.get('/api/team').json(),
            '/api/quick-replies':api.get('/api/quick-replies').json(),
            '/api/alerts':api.get('/api/alerts').json(),
            '/api/contacts':api.get('/api/contacts').json(),
            '/api/integrations':api.get('/api/integrations').json(),
            '/api/analytics':api.get('/api/analytics').json(),
            '/api/plans':api.get('/api/plans').json(),
            '/api/rules':api.get('/api/rules').json()}
    for c in routes['/api/conversations']:
        routes['/api/conversations/'+c['id']]=api.get('/api/conversations/'+c['id']).json()

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height,name in [(1512,920,'desktop'),(390,844,'mobile')]:
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        errors=[]
        page.on('console',lambda msg: errors.append(msg.text) if msg.type=='error' else None)
        page.on('pageerror',lambda err: errors.append(str(err)))
        page.set_content('<!doctype html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
        page.evaluate('''(fixture) => {
           const memory={};
           Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:(k)=>memory[k]||null,setItem:(k,v)=>{memory[k]=v},removeItem:(k)=>{delete memory[k]}}});
           Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf=smoke-csrf',set:()=>true});
           Object.defineProperty(window,'fetch',{configurable:true,value: async (u,opts={})=>{
              const route=String(u).split('?')[0];
              if(route in fixture) return new Response(JSON.stringify(fixture[route]),{status:200,headers:{'Content-Type':'application/json'}});
              if(opts.method && opts.method!=='GET') return new Response(JSON.stringify({ok:true}),{status:200,headers:{'Content-Type':'application/json'}});
              return new Response(JSON.stringify({detail:'not found: '+route}),{status:404,headers:{'Content-Type':'application/json'}});
           }});
        }''',routes)
        page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
        page.add_script_tag(path=str(ROOT/'frontend/public/vendor/react.production.min.js'))
        page.add_script_tag(path=str(ROOT/'frontend/public/vendor/react-dom.production.min.js'))
        page.add_script_tag(path=str(ROOT/'frontend/public/vendor/react-fragment-polyfill.js'))
        page.add_script_tag(path=str(ROOT/'frontend/public/app.js'))
        page.locator('.inbox-list').wait_for(timeout=10000)
        assert page.locator('.inbox-list').count()==1
        assert page.locator('.conversation-card').count()>0, page.locator('body').inner_text()[:2000]
        first=page.locator('.conversation-card').first
        first.click(timeout=7000)
        assert page.locator('textarea[aria-label="Текст ответа"]').count()==1
        page.screenshot(path=str(ROOT.parent/f'OSMANX_OMNICHAT_{name}.png'),full_page=False)
        print(name,'rendered', 'visible labels:',page.locator('body').inner_text()[:145].replace('\n',' '),'JS errors',errors)
        assert not errors,errors
        page.close()
    browser.close()
