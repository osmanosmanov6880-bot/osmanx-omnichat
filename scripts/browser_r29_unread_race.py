"""R29 Chromium proof: an inbound arrives AFTER a chat is shown, BEFORE read-ack.

The same actual FastAPI/SQLite backend serves all UI API calls. One request is
intentionally interleaved to force HTTP 409. No live social accounts or mock
screenshots; images are captured from the compiled React application.
"""
import os
import sys
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r29-browser-'))/'qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from app import db
from app.db import ChannelConnection, Conversation
from app.main import app
from app.services import ingest_inbound

OUTPUT=Path(os.getenv('OMNICHAT_R29_PREVIEW_DIR',str(ROOT/'docs')))
OUTPUT.mkdir(parents=True,exist_ok=True)
with TestClient(app) as api:
    created=api.post('/api/auth/register',json={
        'company':'OSMANX · проверка входящих','name':'Руководитель',
        'email':'r29-browser@local.example','password':'R29LocalOnlyPassword!2026'})
    assert created.status_code==201,created.text
    org=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as s:
        channel=ChannelConnection(organization_id=org,name='Telegram · тестовый аккаунт',
            provider='telegram',mode='live',status='connected',external_account_id='r29-browser-account')
        s.add(channel);s.flush()
        ingest_inbound(s,channel=channel,external_chat_id='buyer-r29',
            external_message_id='r29-first',sender_id='buyer-r29',sender_name='Клиент',
            text='Здравствуйте! Нужна консультация.')
        s.commit()
        channel_id=channel.id
    conv=api.get('/api/conversations').json()[0]
    conv_id=conv['id']

    with sync_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():options['executable_path']='/usr/bin/chromium'
        browser=pw.chromium.launch(**options)
        try:
            for width,height,label in ((1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')):
                # Reset to one unread and fresh conversation version for every viewport.
                with db.SessionLocal() as s:
                    c=s.get(Conversation,conv_id)
                    c.unread_count=1
                    c.version+=1
                    s.commit()
                message_text={'desktop':'Уточните, пожалуйста, стоимость консультации.',
                              'mobile':'А когда можно записаться на консультацию?',
                              'phone320':'Вы работаете по выходным?'}[label]
                lost_race={'once':False,'errors':[]}
                def bridge(payload):
                    assert str(payload['url']).startswith('/api/'),payload
                    if payload['url'].endswith('/read') and payload.get('method')=='POST' and not lost_race['once']:
                        # The reader has already received the old conversation detail.
                        # A fresh signed-provider-like ingress commits NOW.
                        with db.SessionLocal() as s:
                            ingest_inbound(s,channel=s.get(ChannelConnection,channel_id),
                                external_chat_id='buyer-r29',external_message_id='r29-late-'+label,
                                sender_id='buyer-r29',sender_name='Клиент',
                                text=message_text)
                            s.commit()
                        lost_race['once']=True
                    response=api.request(payload.get('method','GET'),payload['url'],
                        headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
                        content=payload['body'].encode() if payload.get('body') else None)
                    if payload['url'].endswith('/read') and lost_race['once']:
                        lost_race['errors'].append(response.status_code)
                    return {'status':response.status_code,'body':response.text}
                page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
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
                page.locator('.conversation-card').first.wait_for(timeout=15000)
                if width<700:
                    page.locator('.conversation-card').first.click()
                page.get_by_text('Появилось новое сообщение — оно осталось непрочитанным.',exact=False).wait_for(timeout=6000)
                page.locator('.message-text').get_by_text(message_text,exact=True).wait_for(timeout=12000)
                assert lost_race['once'] and 409 in lost_race['errors'],lost_race
                with db.SessionLocal() as s:
                    state=s.get(Conversation,conv_id)
                    assert state.unread_count==2,state.unread_count
                assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
                assert not errors,errors
                screenshot=OUTPUT/f'preview-r29-incoming-race-{label}.png'
                page.screenshot(path=str(screenshot),full_page=True)
                print('R29_CHROMIUM',label,'HTTP_409_REFRESH_UNREAD_2=PASS',screenshot)
                page.close()
        finally:browser.close()
print('R29_BROWSER_INBOUND_RACE=PASS')
