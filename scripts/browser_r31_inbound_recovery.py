"""R31 verified local Chromium UI: encrypted inbound failures and manual redrive.

Actual shipped React UI + FastAPI TestClient + SQLite. No real social API calls.
"""
import os
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r31-browser-'))/'qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
from app.main import app
from app import db
from app.db import ChannelConnection, InboundJob
from app.inbound_jobs import stage, process_batch

OUTPUT=Path(os.getenv('OMNICHAT_R31_PREVIEW_DIR', str(ROOT/'docs')))
OUTPUT.mkdir(parents=True,exist_ok=True)

with TestClient(app) as api:
    created=api.post('/api/auth/register',json={
        'company':'OSMANX · приём событий', 'name':'Владелец',
        'email':'r31-e2e@local.example', 'password':'R31TestOnlyPassword!2026'})
    assert created.status_code==201, created.text
    org_id=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=org_id,provider='telegram',
            name='Telegram · тестовый канал',status='connected',mode='live')
        session.add(channel);session.flush()
        for index in range(3):
            job_id=stage(session,channel=channel,external_chat_id=f'user-{index}',
                external_message_id=f'event-r31-{index}',sender_id=f'user-{index}',
                sender_name='Клиент',text=f'Приватный текст номер {index}')
            job=session.get(InboundJob,job_id)
            job.status='failed';job.attempts=5;job.last_error='RuntimeError'
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
            for iteration,(width,height,label) in enumerate(((1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320'))):
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
                page.get_by_role('button',name='Входящие').first.wait_for(timeout=15000)
                if width<700:
                    page.locator('.quiet-mobile-menu').click()
                page.locator('.sidebar .quiet-more').click()
                page.locator('.sidebar-extra .nav-item',has_text='Контроль доставки').first.click()
                page.get_by_text('Приём обращений',exact=True).wait_for(timeout=15000)
                assert page.get_by_text('Повторные события',exact=True).is_visible()
                page.get_by_role('button',name='Повторить после проверки').first.click()
                page.get_by_role('heading',name='Восстановление входящего события').wait_for()
                page.get_by_label('Причина повтора входящего').fill('Проверил настройки, устранил сбой, повтор разрешён')
                page.get_by_role('button',name='Вернуть входящее в очередь').click()
                page.get_by_role('heading',name='Восстановление входящего события').wait_for(state='hidden',timeout=10000)
                assert api.get('/api/operations/inbound').status_code==200
                assert process_batch(db.SessionLocal)==1
                page.get_by_role('button',name='Обновить состояние').click()
                page.wait_for_function('expected=>document.querySelector(".ops-inbound-metrics strong")?.textContent?.trim()===String(expected)',arg=iteration+1,timeout=10000)
                assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
                assert not errors,errors
                page.get_by_text('Приём обращений',exact=True).scroll_into_view_if_needed()
                screenshot=OUTPUT/f'preview-r31-inbound-recovery-{label}.png'
                page.screenshot(path=str(screenshot),full_page=False)
                print('R31_BROWSER_PASS',label,screenshot.name)
                page.close()
        finally:browser.close()
    with db.SessionLocal() as session:
        assert session.query(InboundJob).filter_by(organization_id=org_id,status='done').count()==3
print('R31_INBOUND_JOBS_E2E=PASS')
