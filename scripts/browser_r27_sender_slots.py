"""R27: real Chromium UI while a fake provider call holds the SQL sender slot.

The browser runs the actual React 16 artifact against FastAPI TestClient.
No external social API, token or network connection is required.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path
from threading import Thread, Event
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r27-browser-'))/'qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from app.main import app
from app import db
from app.db import ChannelConnection
from app.services import ingest_inbound,process_outbox
import app.services as services

started=Event();finish=Event();errors_worker=[];processed=[]
class HeldProvider:
    async def send_message(self,credentials,channel,conv,body):
        started.set()
        if not await asyncio.to_thread(finish.wait,20):
            raise RuntimeError('Browser E2E provider wait timeout')
        return 'r27-fake-provider-accepted'
services.unseal=lambda _: {'access_token':'fake-local-only'}
services.adapter_for=lambda _:HeldProvider()

with TestClient(app) as api:
    result=api.post('/api/auth/register',json={
        'company':'Тестовая компания OSMANX','name':'Владелец',
        'email':'r27-browser@example.org','password':'R27SafePassword2026!'})
    assert result.status_code==201,result.text
    org=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=org,provider='telegram',
            name='Telegram компании',mode='live',status='connected',
            external_account_id='r27-preview-only',encrypted_credentials='test')
        session.add(channel);session.flush()
        ingest_inbound(session,channel=channel,external_chat_id='guest',
            external_message_id='r27-inbound',sender_id='guest',
            sender_name='Покупатель',text='Здравствуйте!')
        session.commit()
        conv=next(c for c in api.get('/api/conversations').json())
        conv_id=conv['id'];version=conv['version']
    reply=api.post(f'/api/conversations/{conv_id}/reply',
        headers={'X-CSRF-Token':csrf},json={
            'body':'Здравствуйте, поможем с заказом!',
            'expected_version':version,'client_nonce':'r27-preview-reply'})
    assert reply.status_code==201,reply.text

    def background():
        try:processed.append(asyncio.run(process_outbox(db.SessionLocal)))
        except Exception as exc:errors_worker.append(str(exc))
    runner=Thread(target=background,daemon=True)
    runner.start()
    assert started.wait(10), 'Outbound provider was not reached'
    assert api.get('/api/operations/overview').json()['active_sender_accounts']==1

    def bridge(payload):
        assert payload['url'].startswith('/api/')
        response=api.request(payload.get('method','GET'),payload['url'],
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload['body'].encode() if payload.get('body') else None)
        return {'status':response.status_code,'body':response.text}

    output=Path(os.getenv('OMNICHAT_R27_PREVIEW_DIR',str(ROOT/'docs')))
    output.mkdir(parents=True,exist_ok=True)
    try:
        with sync_playwright() as pw:
            options={'headless':True,'args':['--no-sandbox']}
            if Path('/usr/bin/chromium').exists():options['executable_path']='/usr/bin/chromium'
            browser=pw.chromium.launch(**options)
            for width,height,label in ((1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')):
                page=browser.new_page(viewport={'width':width,'height':height})
                errors=[]
                page.on('pageerror',lambda exc:errors.append(str(exc)))
                page.expose_function('bridgeOmni',bridge)
                page.set_content('<!doctype html><html lang="ru"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
                page.evaluate('''csrf=>{
                    const memory={};
                    Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memory[k]||null,setItem:(k,v)=>memory[k]=v}});
                    Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
                    window.history.replaceState=()=>{};
                    window.fetch=async(url,opts={})=>{
                        const response=await window.bridgeOmni({url:String(url),method:opts.method||'GET',body:opts.body||null});
                        return new Response(response.body,{status:response.status,headers:{'Content-Type':'application/json'}});
                    };
                }''',csrf)
                page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
                for asset in ('vendor/react.production.min.js','vendor/react-dom.production.min.js',
                              'vendor/react-fragment-polyfill.js','app.js'):
                    page.add_script_tag(path=str(ROOT/'frontend/public'/asset))
                page.get_by_role('button',name='Входящие').first.wait_for(timeout=15000)
                if width<700:page.locator('.quiet-mobile-menu').click()
                page.locator('.sidebar .quiet-more').click()
                page.locator('.sidebar-extra .nav-item',has_text='Контроль доставки').first.click()
                page.get_by_text('Сейчас отправляют: 1 аккаунт',exact=True).wait_for(timeout=10000)
                assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
                assert not errors,errors
                shot=output/f'preview-r27-sender-serial-{label}.png'
                page.get_by_text('Сейчас отправляют: 1 аккаунт').scroll_into_view_if_needed()
                page.screenshot(path=str(shot),full_page=False)
                print('R27_SENDER_UI_PASS',label,shot.name)
                page.close()
            browser.close()
    finally:
        finish.set()
        runner.join(10)
    assert not runner.is_alive() and processed==[1] and not errors_worker,(processed,errors_worker)
    assert api.get('/api/operations/overview').json()['active_sender_accounts']==0
print('R27_SENDER_SLOT_RELEASE_VISIBLE=PASS')
