"""R34 end-to-end Chromium: fenced account status and signed batch replay.

Loads the real legacy React bundle into Chromium and connects fetch to a
FastAPI TestClient; all social events are synthetic, no real provider involved.
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
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r34-browser-'))/'qa.sqlite')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
from app.main import app
from app import db
from app.db import ChannelConnection, InboundJob
from app.inbound_jobs import stage, _claim

OUTPUT=Path(os.getenv('OMNICHAT_R34_PREVIEW_DIR',str(ROOT/'docs')))
OUTPUT.mkdir(parents=True,exist_ok=True)
with TestClient(app) as api:
    registered=api.post('/api/auth/register',json={
      'company':'OSMANX · контроль R34','name':'Владелец',
      'email':'r34-owner@local.example','password':'R34StrongTestPassword!2026'})
    assert registered.status_code==201,registered.text
    org=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as s:
        ch=ChannelConnection(organization_id=org,name='Telegram · инциденты R34',
          provider='telegram',mode='live',status='connected',external_account_id='r34-local-test')
        s.add(ch);s.commit();channel_id=ch.id
    def seed_failed(i):
        with db.SessionLocal() as s:
            channel=s.get(ChannelConnection,channel_id)
            jid=stage(s,channel=channel,external_chat_id='visitor-'+str(i),
              external_message_id='event-'+str(i),sender_id='visitor-'+str(i),
              text='Synthetic non-personal preview test')
            job=s.get(InboundJob,jid)
            job.status='failed';job.attempts=5;job.last_error='SyntheticFailure'
            s.commit()
            return jid
    # Leave an independently claimed job in progress to verify the diagnostic
    # indicator without disclosing any worker identifier to the browser.
    with db.SessionLocal() as s:
        channel=s.get(ChannelConnection,channel_id)
        busy=stage(s,channel=channel,external_chat_id='active-qa',
          external_message_id='active-qa',sender_id='active-qa',text='synthetic')
        s.commit()
    busy_token=_claim(db.SessionLocal,busy)
    assert busy_token

    def bridge(payload):
        path=str(payload['url'])
        assert path.startswith('/api/')
        response=api.request(payload.get('method','GET'),path,headers={
          'X-CSRF-Token':csrf,'Content-Type':'application/json'},
          content=payload['body'].encode() if payload.get('body') else None)
        return {'status':response.status_code,'body':response.text}

    with sync_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():options['executable_path']='/usr/bin/chromium'
        browser=pw.chromium.launch(**options)
        try:
            for i,(width,height,label) in enumerate(((1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320'))):
                job_id=seed_failed(i)
                page=browser.new_page(viewport={'width':width,'height':height})
                js_errors=[]
                page.on('pageerror',lambda error:js_errors.append(str(error)))
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
                page.get_by_role('button',name='Входящие').first.wait_for(timeout=30000)
                if width<700:page.locator('.quiet-mobile-menu').click()
                page.locator('.sidebar .quiet-more').click()
                page.locator('.sidebar-extra .nav-item',has_text='Контроль доставки').first.click()
                page.get_by_text('Диагностика входящих по аккаунтам',exact=True).wait_for(timeout=20000)
                page.get_by_text('Обработка аккаунта выполняется',exact=False).wait_for(timeout=15000)
                select=page.get_by_label('Аккаунт для пакетного восстановления')
                select.select_option(channel_id)
                page.get_by_role('button',name='Проверить до 20 ошибок').click()
                page.get_by_text('Подготовлено к восстановлению',exact=True).wait_for(timeout=20000)
                count=page.locator('.ops-batch-preview strong').inner_text()
                assert '1 событий' in count,(label,count)
                if label=='desktop':
                    page.screenshot(path=str(OUTPUT/'preview-r34-reviewed-inbound-approval.png'),full_page=False)
                page.get_by_label('Причина пакетного восстановления').fill(
                  'Проверены настройки шифрования и канал; это безопасный тестовый повтор')
                page.get_by_role('button',name='Подтвердить восстановление 1 событий').click()
                page.get_by_text('Подготовлено к восстановлению',exact=True).wait_for(state='hidden',timeout=20000)
                with db.SessionLocal() as s:
                    assert s.get(InboundJob,job_id).status=='queued'
                assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
                assert not js_errors,js_errors
                page.get_by_text('Диагностика входящих по аккаунтам',exact=True).scroll_into_view_if_needed()
                screenshot=OUTPUT/f'preview-r34-reviewed-inbound-{label}.png'
                page.screenshot(path=str(screenshot),full_page=False)
                print('R34_BROWSER_PASS',label,screenshot.name,flush=True)
                page.close()
        finally:
            browser.close()
print('R34_REVIEWED_RECOVERY_CHROMIUM=PASS')
