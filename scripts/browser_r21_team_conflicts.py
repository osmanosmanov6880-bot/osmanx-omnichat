"""Real Chromium + FastAPI: stale team mutations must not overwrite a colleague.

Tests 1512, 390 and 320px. The server is the actual in-process API with
SQLite; no provider account or external API is contacted. This is a proof of
optimistic UI conflict handling, not PostgreSQL load validation.
"""
from pathlib import Path
import os
import sys
import tempfile
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r21-browser-'))/'ui.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as api:
    demo=api.post('/api/demo/start')
    assert demo.status_code==200,demo.text
    csrf=api.cookies.get('omnichat_csrf')
    chosen=api.get('/api/conversations').json()[0]
    cid=chosen['id']

    def bridge(payload):
        path=payload['url']
        assert path.startswith('/api/'),path
        res=api.request(payload.get('method','GET'),path,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload.get('body').encode() if payload.get('body') else None)
        return {'status':res.status_code,'body':res.text}

    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        output=Path(os.environ.get('OMNICHAT_R21_PREVIEW_DIR',str(ROOT/'docs')))
        output.mkdir(parents=True,exist_ok=True)
        for width,height,name in ((1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')):
            page=browser.new_page(viewport={'width':width,'height':height})
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.expose_function('bridgeOmni',bridge)
            page.set_content('<!doctype html><html lang="ru"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
            page.evaluate('''csrf=>{
              const memory={};
              Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memory[k]||null,setItem:(k,v)=>memory[k]=v}});
              Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
              window.history.replaceState=()=>{};
              window.fetch=async(url,opts={})=>{
                const r=await window.bridgeOmni({url:String(url),method:opts.method||'GET',body:opts.body||null});
                return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})
              };
            }''',csrf)
            page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
            for script in ('vendor/react.production.min.js','vendor/react-dom.production.min.js',
                           'vendor/react-fragment-polyfill.js','app.js'):
                page.add_script_tag(path=str(ROOT/'frontend/public'/script))
            page.locator('.conversation-card').first.wait_for(timeout=15000)
            page.locator('.conversation-card').first.click()
            page.get_by_role('button',name='Действия с диалогом').wait_for(timeout=8000)
            page.get_by_role('button',name='Действия с диалогом').click()
            select=page.get_by_label('Статус диалога')
            select.wait_for(timeout=8000)
            # Another employee changed the same record behind this browser's
            # back; selecting a stale value must be rejected and reloaded.
            latest=api.get('/api/conversations/'+cid).json()['conversation']
            assert latest['version']>=chosen['version']
            external=api.patch('/api/conversations/'+cid+'/status',
                json={'status':'in_progress','expected_version':latest['version']},
                headers={'X-CSRF-Token':csrf})
            assert external.status_code==200,external.text
            select.select_option('waiting')
            notice=page.locator('.toast')
            notice.get_by_text('Коллега изменил диалог',exact=False).wait_for(timeout=10000)
            assert api.get('/api/conversations/'+cid).json()['conversation']['status']=='in_progress'
            select.wait_for(timeout=8000)
            page.wait_for_function("document.querySelector('[aria-label=\"Статус диалога\"]').value==='in_progress'",timeout=8000)
            snap=output/f'preview-r21-team-conflict-{name}.png'
            page.screenshot(path=str(snap),full_page=False)
            assert not errors,errors
            assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=0
            # Successful subsequent update must use the refreshed version.
            select.select_option('waiting')
            page.wait_for_function("document.querySelector('[aria-label=\"Статус диалога\"]').value==='waiting'",timeout=10000)
            assert api.get('/api/conversations/'+cid).json()['conversation']['status']=='waiting'
            print('R21_COLLAB_UI_PASS',name,snap)
            page.close()
        browser.close()
