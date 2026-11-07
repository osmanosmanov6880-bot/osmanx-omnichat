"""Chromium E2E: latest-first Inbox, operator-driven older history, all widths.

Real React 16 browser bundle + real FastAPI TestClient. The HTTP transport is
bridged locally; no real customer or external social account is connected.
"""
from pathlib import Path
import os
import sys
import tempfile
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omni-r20-ui-'))/'ui.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from fastapi.testclient import TestClient
from app.main import app
from app import db
from app.db import Conversation, Message, now

with TestClient(app) as api:
    demo=api.post('/api/demo/start')
    assert demo.status_code==200,demo.text
    me=api.get('/api/auth/me').json()
    csrf=api.cookies.get('omnichat_csrf')
    chosen=api.get('/api/conversations').json()[0]
    with db.SessionLocal() as session:
        c=session.get(Conversation,chosen['id'])
        for i in range(330):
            session.add(Message(organization_id=me['organization']['id'],conversation_id=c.id,
                external_id='browser-history-'+str(i),direction='in',
                body=f'Архивное сообщение {i:04}',created_at=now()-50000+i,
                delivery_status='delivered',is_demo=True))
        c.last_message_at=now()+2
        session.commit()

    def bridge(payload):
        path=payload['url']
        assert path.startswith('/api/'),path
        resp=api.request(payload.get('method','GET'),path,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload.get('body').encode() if payload.get('body') else None)
        return {'status':resp.status_code,'body':resp.text}

    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        out=Path(os.environ.get('OMNICHAT_R20_PREVIEW_DIR',str(ROOT/'docs')))
        out.mkdir(parents=True,exist_ok=True)
        for width,height,name in [(1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')]:
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
            page.locator('.conversation-card').first.wait_for(timeout=16000)
            page.locator('.conversation-card').first.click()
            history=page.locator('.history-older-control button')
            history.wait_for(timeout=12000)
            assert page.locator('.message-line').count()==120,page.locator('.message-line').count()
            assert history.inner_text()=='Показать более ранние сообщения'
            shot=out/f'preview-r20-long-history-{name}.png'
            page.screenshot(path=str(shot),full_page=False)
            history.click()
            page.wait_for_function('document.querySelectorAll(".message-line").length >= 240',timeout=12000)
            assert page.locator('.message-line').count()==240
            history.click()
            page.wait_for_function('document.querySelectorAll(".message-line").length >= 330',timeout=12000)
            # Latest-first and the legacy demo messages still coexist.
            assert page.get_by_text('Архивное сообщение 0000').count()==1
            assert page.get_by_text('Архивное сообщение 0329').count()==1
            assert page.locator('.history-older-control button').count()==0
            assert page.locator('.message-line').count()>=330
            if name=='desktop':
                # The existing 7-second inbox refresh must preserve loaded
                # older pages rather than replacing them with the latest 120.
                page.wait_for_timeout(7600)
                assert page.get_by_text('Архивное сообщение 0000').count()==1
                assert page.locator('.history-older-control button').count()==0
            assert not errors,errors
            assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=0
            print('R20_HISTORY_UI_PASS',name,shot)
            page.close()
        browser.close()
