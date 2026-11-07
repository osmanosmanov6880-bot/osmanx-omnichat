"""R32 Chromium end-to-end: incident pause, signed ingress, cursor and batch recovery."""
import hashlib
import hmac
import json
import os
import sys
import tempfile
from pathlib import Path

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r32-browser-'))/'qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
os.environ['META_APP_SECRET']='test-webhook-secret'
os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
from app.main import app
from app import db
from app.db import ChannelConnection, InboundJob, Message
from app.inbound_jobs import stage, process_batch

OUTPUT=Path(os.getenv('OMNICHAT_R32_PREVIEW_DIR', str(ROOT/'docs')))
OUTPUT.mkdir(parents=True,exist_ok=True)

with TestClient(app) as api:
    created=api.post('/api/auth/register',json={
        'company':'OSMANX · обработка входящих', 'name':'Владелец',
        'email':'r32-e2e@local.example', 'password':'R32LocalTestPassword!2026'})
    assert created.status_code==201,created.text
    org_id=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=org_id,provider='instagram',
            name='Instagram · очередь приёма',status='connected',mode='live',
            external_account_id='r32-ig-page')
        session.add(channel);session.flush()
        channel_id=channel.id
        for index in range(65):
            jid=stage(session,channel=channel,external_chat_id=f'guest-{index}',
                external_message_id=f'r32-failed-{index}',sender_id=f'guest-{index}',
                sender_name='Посетитель',text=f'Секретное содержимое заявки {index}')
            job=session.get(InboundJob,jid)
            job.status='failed';job.attempts=5;job.last_error='ConnectionError'
        session.commit()
    def bridge(payload):
        assert str(payload['url']).startswith('/api/')
        response=api.request(payload.get('method','GET'),payload['url'],
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload['body'].encode() if payload.get('body') else None)
        return {'status':response.status_code,'body':response.text}

    with sync_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():options['executable_path']='/usr/bin/chromium'
        browser=pw.chromium.launch(**options)
        try:
            for round_number,(width,height,label) in enumerate(((1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320'))):
                page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
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
                        return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}});
                    };
                }''',csrf)
                page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
                for asset in ('vendor/react.production.min.js','vendor/react-dom.production.min.js',
                              'vendor/react-fragment-polyfill.js','app.js'):
                    page.add_script_tag(path=str(ROOT/'frontend/public'/asset))
                page.get_by_role('button',name='Входящие').first.wait_for(timeout=20000)
                if width<700:page.locator('.quiet-mobile-menu').click()
                page.locator('.sidebar .quiet-more').click()
                page.locator('.sidebar-extra .nav-item',has_text='Контроль доставки').first.click()
                page.get_by_text('Приём обращений',exact=True).wait_for(timeout=15000)
                page.get_by_role('button',name='Ошибки',exact=True).click()
                pending_errors=65-20*round_number
                page.wait_for_function('expected=>document.querySelectorAll(".ops-inbound-table tbody tr").length===expected',arg=min(30,pending_errors),timeout=15000)
                if pending_errors>30:
                    page.get_by_role('button',name='Показать ещё 30 событий').click()
                    page.wait_for_function('expected=>document.querySelectorAll(".ops-inbound-table tbody tr").length===expected',arg=min(60,pending_errors),timeout=15000)
                page.get_by_role('button',name='Поставить входящие на паузу').click()
                page.get_by_role('heading',name='Управление входящими при инциденте').wait_for()
                page.get_by_label('Причина изменения обработки входящих').fill('Проверка аварийной очереди до приёма сообщений')
                page.get_by_role('button',name='Приостановить обработку').click()
                page.get_by_role('heading',name='Управление входящими при инциденте').wait_for(state='hidden')
                payload={'object':'instagram','entry':[{'id':'r32-ig-page','messaging':[
                    {'sender':{'id':f'e2e-guest-{round_number}'},'recipient':{'id':'r32-ig-page'},
                     'message':{'mid':f'e2e-event-{round_number}','text':'Новая тестовая заявка'}}]}]}
                raw=json.dumps(payload).encode()
                signature='sha256='+hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
                signed=api.post('/api/webhooks/instagram',content=raw,headers={'X-Hub-Signature-256':signature})
                assert signed.status_code==200,signed.text
                assert signed.json()['accepted']==0
                assert process_batch(db.SessionLocal)==0
                page.get_by_role('button',name='Возобновить обработку').click()
                page.get_by_label('Причина изменения обработки входящих').fill('Соединение проверено, обработку можно восстановить')
                page.get_by_role('button',name='Возобновить обработку',exact=True).last.click()
                page.get_by_role('heading',name='Управление входящими при инциденте').wait_for(state='hidden')
                assert process_batch(db.SessionLocal)==1
                page.get_by_label('Аккаунт для пакетного восстановления').select_option(channel_id)
                page.get_by_role('button',name='Повторить до 20 ошибок').click()
                page.get_by_label('Причина пакетного восстановления').fill('Подключение проверено, проблему устранено; восстановить пакет')
                page.get_by_role('button',name='Вернуть до 20 событий в очередь').click()
                page.get_by_role('heading',name='Пакетное восстановление входящих').wait_for(state='hidden')
                assert process_batch(db.SessionLocal,limit=50)==20
                assert not errors, errors
                assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
                page.get_by_text('Приём обращений',exact=True).scroll_into_view_if_needed()
                shot=OUTPUT/f'preview-r32-inbound-control-{label}.png'
                page.screenshot(path=str(shot),full_page=False)
                print('R32_BROWSER_PASS',label,shot.name)
                page.close()
        finally:browser.close()
    with db.SessionLocal() as session:
        assert session.query(InboundJob).filter_by(organization_id=org_id,status='done').count()==63
        assert session.query(InboundJob).filter_by(organization_id=org_id,status='failed').count()==5
        assert session.query(Message).filter_by(organization_id=org_id).count()==63
print('R32_INBOUND_CONTROL_E2E=PASS')
