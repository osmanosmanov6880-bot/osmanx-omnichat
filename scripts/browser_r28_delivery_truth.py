"""R28 Chromium UI + real FastAPI analytics and fake external provider acceptance.

Requires locally installed Chromium and playwright. Browser paints the compiled
React application and queries actual SQL. No live social API is accessed.
"""
import asyncio
import os
import sys
import tempfile
import time
from threading import Thread
from pathlib import Path
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r28-ui-'))/'qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from app import db
from app.main import app
from app.db import Organization,ChannelConnection,Conversation
from app.services import ingest_inbound,process_outbox
import app.services as services

class LocalFakeProvider:
    async def send_message(self,*args):return 'r28-verified-local-only'
services.adapter_for=lambda _: LocalFakeProvider()
services.unseal=lambda _: {'access_token':'local-only'}

OUT=Path(os.getenv('OMNICHAT_R28_PREVIEW_DIR',str(ROOT/'docs')))
OUT.mkdir(parents=True,exist_ok=True)
with TestClient(app) as api:
    registered=api.post('/api/auth/register',json={
        'company':'Тестовая компания OSMANX','name':'Владелец',
        'email':'r28-qa@example.org','password':'R28SafePassword2026!'})
    assert registered.status_code==201,registered.text
    org=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        session.get(Organization,org).plan='business'
        session.get(Organization,org).sla_minutes=1
        channel=ChannelConnection(organization_id=org,provider='telegram',name='Telegram · тест',
            mode='live',status='connected',external_account_id='r28-browser',encrypted_credentials='mock')
        session.add(channel);session.flush()
        ingest_inbound(session,channel=channel,external_chat_id='browser-client',
            external_message_id='r28-browser-in',sender_id='browser-client',
            sender_name='Тестовый клиент',text='Сколько стоит доставка?',timestamp=time.time()-250)
        session.commit()
        conv=session.query(Conversation).filter_by(channel_id=channel.id).one()
        conv_id,version=conv.id,conv.version
    created=api.post('/api/conversations/'+conv_id+'/reply',
        headers={'X-CSRF-Token':csrf},json={'body':'Доставка стоит 300 рублей',
        'expected_version':version,'client_nonce':'r28-browser-response'})
    assert created.status_code==201,created.text
    assert api.get('/api/analytics').json()['outgoing_pending']==1
    assert api.get('/api/alerts').json()['unanswered_over_sla']==1

    def bridge(payload):
        assert str(payload['url']).startswith('/api/'),payload
        response=api.request(payload.get('method','GET'),payload['url'],
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload['body'].encode() if payload.get('body') else None)
        return {'status':response.status_code,'body':response.text}

    with sync_playwright() as pw:
        opts={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():opts['executable_path']='/usr/bin/chromium'
        browser=pw.chromium.launch(**opts)
        def show(width,height,label,pending):
            page=browser.new_page(viewport={'width':width,'height':height})
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
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
            page.locator('.sidebar-extra .nav-item',has_text='Аналитика').first.click()
            page.get_by_role('heading',name='Аналитика коммуникаций').wait_for(timeout=10000)
            if width<700:
                # Let the 200ms mobile navigation transition finish: a midway
                # screenshot can show the departing drawer over the content.
                page.wait_for_function("() => document.querySelector('.sidebar').getBoundingClientRect().right <= 0",timeout=3000)
            page.get_by_text(f'Исходящих в очереди или обработке: {pending}.',exact=False).wait_for(timeout=10000)
            assert page.get_by_text('Черновик и очередь не считаются ответом').is_visible()
            assert page.get_by_text('От первого обращения до подтверждения API / веб-чата, с R28').is_visible()
            if pending:
                assert page.get_by_text('Ожидают подтверждённого ответа').locator('..').locator('strong').inner_text()=='1'
            else:
                assert page.get_by_text('Ожидают подтверждённого ответа').locator('..').locator('strong').inner_text()=='0'
            assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
            assert not errors,errors
            path=OUT/f'preview-r28-delivery-truth-{label}.png'
            page.screenshot(path=str(path),full_page=True)
            print('R28_CHROMIUM',label,'PASSED',path)
            page.close()
        for width,height,label in ((1512,950,'desktop-queued'),(390,844,'mobile-queued'),(320,700,'phone320-queued')):
            show(width,height,label,1)
        results=[]
        task=Thread(target=lambda:results.append(asyncio.run(process_outbox(db.SessionLocal))),daemon=True)
        task.start();task.join(12)
        assert not task.is_alive() and results==[1],results
        assert api.get('/api/analytics').json()['outgoing_pending']==0
        assert api.get('/api/analytics').json()['no_response']==0
        show(1512,950,'desktop-confirmed',0)
        browser.close()
print('R28_DELIVERY_AWARE_BROWSER_PASS')
