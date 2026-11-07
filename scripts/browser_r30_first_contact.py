#!/usr/bin/env python3
"""R30 Chromium proof: simultaneous first messages show one chat, no dupes.

A local FastAPI/SQLite process backs the actual shipped React UI. No external
social accounts are used, and the screenshots are not generated mockups.
"""
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r30-browser-'))/'qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from app import db
from app.db import ChannelConnection, Conversation, Message, Contact
from app.main import app
from app.services import ingest_inbound

OUTPUT=Path(os.getenv('OMNICHAT_R30_PREVIEW_DIR',str(ROOT/'docs')))
OUTPUT.mkdir(parents=True,exist_ok=True)

with TestClient(app) as api:
    created=api.post('/api/auth/register',json={
        'company':'OSMANX · первый клиент','name':'Руководитель',
        'email':'r30-browser@local.example','password':'R30LocalOnlyPassword!2026'})
    assert created.status_code==201,created.text
    org=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as s:
        ch=ChannelConnection(organization_id=org,provider='telegram',name='Telegram · магазин',
            mode='live',status='connected')
        s.add(ch);s.commit()
        channel_id=ch.id

    texts=['Здравствуйте! Интересует заказ.',
           'Подскажите, пожалуйста, условия доставки.']
    base_timestamp=time.time()-90
    barrier=Barrier(2)
    def inbound(index):
        with db.SessionLocal() as s:
            ch=s.get(ChannelConnection,channel_id)
            barrier.wait(timeout=15)
            msg=ingest_inbound(s,channel=ch,external_chat_id='visitor-r30',
                external_message_id=f'r30-concurrent-{index}',sender_id='visitor-r30',
                sender_name='Новый покупатель',text=texts[index],timestamp=base_timestamp+index*30)
            s.commit()
            return msg.id
    with ThreadPoolExecutor(max_workers=2) as pool:
        ids=list(pool.map(inbound,(0,1)))
    assert len(set(ids))==2
    with db.SessionLocal() as s:
        # A repeated webhook must not double the message or unread counter.
        ch=s.get(ChannelConnection,channel_id)
        repeated=ingest_inbound(s,channel=ch,external_chat_id='visitor-r30',
            external_message_id='r30-concurrent-0',sender_id='visitor-r30',
            sender_name='Новый покупатель',text=texts[0])
        assert repeated.id==ids[0]
        s.commit()
        assert s.query(Conversation).filter_by(organization_id=org).count()==1
        assert s.query(Contact).filter_by(organization_id=org).count()==1
        assert s.query(Message).filter_by(organization_id=org).count()==2
        assert s.query(Conversation).filter_by(organization_id=org).one().unread_count==2
    detail=api.get('/api/conversations').json()
    assert len(detail)==1,detail
    assert api.get('/api/conversations/'+detail[0]['id']).status_code==200

    with sync_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():
            options['executable_path']='/usr/bin/chromium'
        browser=pw.chromium.launch(**options)
        try:
            for width,height,label in ((1512,950,'desktop'),(390,844,'mobile'),
                                       (320,700,'phone320')):
                page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
                failures=[]
                page.on('pageerror',lambda error:failures.append(str(error)))
                def bridge(payload):
                    assert str(payload['url']).startswith('/api/'),payload
                    response=api.request(payload.get('method','GET'),payload['url'],
                        headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
                        content=payload['body'].encode() if payload.get('body') else None)
                    return {'status':response.status_code,'body':response.text}
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
                page.locator('.conversation-card').first.wait_for(timeout=15000)
                assert page.locator('.conversation-card').count()==1
                page.locator('.conversation-card').first.click()
                for message in texts:
                    page.locator('.message-text').get_by_text(message,exact=True).wait_for(timeout=10000)
                assert page.locator('.message-text').count()==2
                assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
                assert not failures,failures
                path=OUTPUT/f'preview-r30-first-contact-{label}.png'
                page.screenshot(path=str(path),full_page=True)
                print('R30_CHROMIUM',label,'ONE_CHAT_TWO_MESSAGES_NO_DUPLICATES=PASS',path)
                page.close()
        finally:
            browser.close()
print('R30_BROWSER_FIRST_CONTACT=PASS')
