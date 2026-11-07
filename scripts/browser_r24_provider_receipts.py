"""R24 Chromium smoke: signed WhatsApp receipts displayed in the real Inbox.

Uses FastAPI TestClient + React 16 legacy runtime in three viewport sizes.
No live external HTTP accounts, no production delivery claims.
"""
import hashlib
import hmac
import json
import os
import sys
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r24-browser-'))/'qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
os.environ['META_APP_SECRET']='r24-browser-secret'
from app.main import app
from app import db
from app.db import ChannelConnection, Contact, Conversation, Message, now


def signed_post(api,status):
    obj={'object':'whatsapp_business_account','entry':[{'changes':[{'value':{
        'metadata':{'phone_number_id':'r24-whatsapp-001'},
        'statuses':[{'id':'wamid.r24.browser-confirmed','status':status,
                     'recipient_id':'79001230001'}]}}]}]}
    raw=json.dumps(obj,ensure_ascii=False).encode('utf-8')
    signature=hmac.new(b'r24-browser-secret',raw,hashlib.sha256).hexdigest()
    return api.post('/api/webhooks/whatsapp',content=raw,headers={
        'X-Hub-Signature-256':'sha256='+signature})


with TestClient(app) as api:
    registration=api.post('/api/auth/register',json={
        'company':'Клиентский сервис OSMANX','name':'Оператор',
        'email':'r24-receipt-browser@example.org','password':'CorrectLongPassword!2026'})
    assert registration.status_code==201,registration.text
    org=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=org,provider='whatsapp',name='WhatsApp магазина',
            mode='live',status='connected',external_account_id='r24-whatsapp-001')
        contact=Contact(organization_id=org,name='Гость WhatsApp')
        session.add_all([ch,contact]);session.flush()
        conv=Conversation(organization_id=org,channel_id=ch.id,contact_id=contact.id,
            external_chat_id='79001230001',external_recipient_id='79001230001',
            last_message_at=now(),last_inbound_at=now())
        session.add(conv);session.flush()
        incoming=Message(organization_id=org,conversation_id=conv.id,
            direction='in',body='Здравствуйте! Когда привезёте мой заказ?',
            created_at=now()-30,delivery_status='delivered')
        outgoing=Message(organization_id=org,conversation_id=conv.id,
            direction='out',body='Здравствуйте! Ваш заказ уже передан курьеру.',
            external_id='wamid.r24.browser-confirmed',
            delivery_status='accepted',created_at=now()-15)
        session.add_all([incoming,outgoing]);session.commit()
        message_id=outgoing.id
    # Truly call the signed webhook twice, in increasing evidence quality.
    for status in ('delivered','read'):
        resp=signed_post(api,status)
        assert resp.status_code==200,resp.text
    with db.SessionLocal() as session:
        assert session.get(Message,message_id).delivery_status=='read'
    ops=api.get('/api/operations/overview')
    assert ops.status_code==200 and ops.json()['whatsapp_receipts_last_24h']==1

    def bridge(payload):
        path=payload['url']
        assert path.startswith('/api/'),path
        resp=api.request(payload.get('method','GET'),path,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload['body'].encode('utf-8') if payload.get('body') else None)
        return {'status':resp.status_code,'body':resp.text}

    output=Path(os.getenv('OMNICHAT_R24_PREVIEW_DIR',str(ROOT/'docs')))
    output.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():
            options['executable_path']='/usr/bin/chromium'
        browser=pw.chromium.launch(**options)
        for width,height,label in [(1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')]:
            page=browser.new_page(viewport={'width':width,'height':height})
            exceptions=[]
            page.on('pageerror',lambda exc: exceptions.append(str(exc)))
            page.expose_function('bridgeOmni',bridge)
            page.set_content('<!doctype html><html lang="ru"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
            page.evaluate('''csrf=>{
               const memory={};
               Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memory[k]||null,setItem:(k,v)=>memory[k]=v}});
               Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
               window.history.replaceState=()=>{};
               window.fetch=async(url,opts={})=>{
                 const r=await window.bridgeOmni({url:String(url),method:opts.method||'GET',body:opts.body||null});
                 return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}});
               };
            }''',csrf)
            page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
            for script in ('vendor/react.production.min.js','vendor/react-dom.production.min.js',
                           'vendor/react-fragment-polyfill.js','app.js'):
                page.add_script_tag(path=str(ROOT/'frontend/public'/script))
            page.get_by_text('Гость WhatsApp').first.wait_for(timeout=15000)
            if width<700:
                page.locator('.conversation-card').first.click()
            page.get_by_text('Прочитано',exact=True).first.wait_for(timeout=10000)
            assert page.get_by_text('Ваш заказ уже передан курьеру.',exact=False).count()>=1
            assert not exceptions,exceptions
            assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
            shot=output/f'preview-r24-whatsapp-receipts-{label}.png'
            page.screenshot(path=str(shot),full_page=False)
            # Operations must show a tenant-safe receipt count without tokens.
            if width>=700:
                page.locator('.quiet-more').click()
                page.get_by_role('button',name='Контроль доставки').first.click()
                page.get_by_text('Квитанций WhatsApp за 24 ч: 1').wait_for(timeout=10000)
                assert 'r24-browser-secret' not in page.locator('body').inner_text()
            print('R24_WHATSAPP_RECEIPTS_UI_PASS',label,shot)
            page.close()
        browser.close()
