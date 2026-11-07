"""R33 actual Chromium: per-account health and irreversible encrypted event disposal.

Uses the real R33 FastAPI TestClient through a browser fetch bridge; no external
social account or real recipient is involved.
"""
import os
import sys
import tempfile
from pathlib import Path

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r33-browser-'))/'qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
os.environ['INBOUND_MAX_PENDING_PER_CHANNEL']='8'
os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
from app.main import app
from app import db
from app.db import ChannelConnection, InboundJob
from app.inbound_jobs import stage

OUTPUT=Path(os.getenv('OMNICHAT_R33_PREVIEW_DIR',str(ROOT/'docs')))
OUTPUT.mkdir(parents=True,exist_ok=True)

with TestClient(app) as api:
    response=api.post('/api/auth/register',json={
        'company':'OSMANX · контроль очередей', 'name':'Владелец',
        'email':'r33-owner@local.example','password':'R33LocalTestPassword!2026'})
    assert response.status_code==201,response.text
    org=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=org,provider='telegram',
              name='Telegram · восстановление',status='connected',mode='live',
              external_account_id='r33-tg-qa')
        session.add(ch);session.commit(); channel_id=ch.id

    def seed(index):
        with db.SessionLocal() as session:
            channel=session.get(ChannelConnection,channel_id)
            job=stage(session,channel=channel,external_chat_id='guest-'+str(index),
              external_message_id='r33-event-'+str(index),sender_id='guest-'+str(index),
              sender_name='Тестовый посетитель',text='R33_UI_FAKE_CLIENT_TEXT')
            item=session.get(InboundJob,job)
            item.status='failed';item.attempts=5;item.last_error='SyntheticError'
            session.commit()
        return job

    def bridge(payload):
        url=str(payload['url'])
        assert url.startswith('/api/')
        r=api.request(payload.get('method','GET'),url,headers={
            'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload['body'].encode() if payload.get('body') else None)
        return {'status':r.status_code,'body':r.text}

    with sync_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():options['executable_path']='/usr/bin/chromium'
        browser=pw.chromium.launch(**options)
        try:
            for index,(width,height,label) in enumerate(((1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320'))):
                jid=seed(index)
                page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
                errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.expose_function('bridgeOmni',bridge)
                page.set_content('<!doctype html><html lang="ru"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
                page.evaluate('''csrf=>{
                   const local={};window.history.replaceState=()=>{};
                   Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>local[k]||null,setItem:(k,v)=>local[k]=v}});
                   Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
                   window.fetch=async(url,opts={})=>{
                    const r=await window.bridgeOmni({url:String(url),method:opts.method||'GET',body:opts.body||null});
                    return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}});
                   };
                }''',csrf)
                page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
                for asset in ('vendor/react.production.min.js','vendor/react-dom.production.min.js',
                              'vendor/react-fragment-polyfill.js','app.js'):
                    page.add_script_tag(path=str(ROOT/'frontend/public'/asset))
                page.get_by_role('button',name='Входящие').first.wait_for(timeout=25000)
                if width<700:page.locator('.quiet-mobile-menu').click()
                page.locator('.sidebar .quiet-more').click()
                page.locator('.sidebar-extra .nav-item',has_text='Контроль доставки').first.click()
                page.get_by_text('Диагностика входящих по аккаунтам',exact=True).wait_for(timeout=15000)
                assert page.get_by_text('Telegram · восстановление').count()>=1
                page.get_by_role('button',name='Ошибки',exact=True).click()
                page.locator('.ops-inbound-table tbody tr').first.wait_for(timeout=15000)
                page.get_by_role('button',name='Закрыть и удалить').first.click()
                page.get_by_role('heading',name='Необратимое закрытие входящего').wait_for(timeout=10000)
                page.get_by_label('Категория закрытия входящего').select_option('invalid_event')
                page.get_by_label('Причина необратимого закрытия').fill(
                    'Проверена история синтетического теста, безопасный импорт невозможен')
                page.get_by_label('Подтверждаю, что событие будет удалено без возможности восстановления.').check()
                page.get_by_role('button',name='Необратимо закрыть и удалить').click()
                page.get_by_role('heading',name='Необратимое закрытие входящего').wait_for(state='hidden',timeout=20000)
                with db.SessionLocal() as session:
                    row=session.get(InboundJob,jid)
                    assert row.status=='dismissed' and row.encrypted_event is None,row.status
                page.get_by_role('button',name='Закрыты',exact=True).click()
                page.locator('.ops-inbound-table tbody tr').first.wait_for(timeout=15000)
                assert page.get_by_text('Закрыто с удалением').count()>=1
                assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
                assert not errors,errors
                page.get_by_text('Диагностика входящих по аккаунтам',exact=True).scroll_into_view_if_needed()
                dest=OUTPUT/f'preview-r33-inbound-fairness-{label}.png'
                page.screenshot(path=str(dest),full_page=False)
                print('R33_CHROMIUM_PASS',label,dest.name)
                page.close()
        finally:browser.close()
print('R33_INBOUND_FAIRNESS_E2E=PASS')
