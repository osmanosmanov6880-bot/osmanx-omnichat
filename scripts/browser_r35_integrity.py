"""R35 real Chromium + FastAPI: inspect / repair expired inbound tenant claims.

The bridge feeds actual FastAPI responses into the compiled React interface.
No external social network or live customer data is used.
"""
import os
import sys
import tempfile
from pathlib import Path
from sqlalchemy import update
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r35-browser-'))/'test.sqlite')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
from app.main import app
from app import db
from app.db import ChannelConnection, InboundJob, now
from app.inbound_jobs import stage, _claim

OUTPUT=Path(os.getenv('OMNICHAT_R35_PREVIEW_DIR',str(ROOT/'docs')))
OUTPUT.mkdir(parents=True,exist_ok=True)
with TestClient(app) as api:
    registered=api.post('/api/auth/register',json={
        'company':'OSMANX · R35 проверка очереди','name':'Владелец',
        'email':'r35-local@local.example','password':'R35StrongTestPassword!2026'})
    assert registered.status_code==201,registered.text
    org=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as s:
        ch=ChannelConnection(organization_id=org,name='Telegram · поддержка R35',
             provider='telegram',mode='live',status='connected')
        s.add(ch);s.commit();channel_id=ch.id

    def seed_expired(number):
        with db.SessionLocal() as s:
            ch=s.get(ChannelConnection,channel_id)
            jid=stage(s,channel=ch,external_chat_id='qa-'+str(number),
                      external_message_id='qa-msg-'+str(number),
                      sender_id='qa-user-'+str(number),text='Synthetic QA only')
            s.commit()
        token=_claim(db.SessionLocal,jid)
        assert token
        with db.SessionLocal() as s:
            s.execute(update(InboundJob).where(InboundJob.id==jid).values(
                claim_expires_at=now()-20))
            s.execute(update(ChannelConnection).where(ChannelConnection.id==channel_id).values(
                inbound_processing_until=now()-20))
            s.commit()
        return jid

    def bridge(payload):
        url=str(payload['url'])
        assert url.startswith('/api/')
        response=api.request(payload.get('method','GET'),url,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload['body'].encode() if payload.get('body') else None)
        return {'status':response.status_code,'body':response.text}

    with sync_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():
            options['executable_path']='/usr/bin/chromium'
        browser=pw.chromium.launch(**options)
        try:
            for width,height,label in ((1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')):
                job=seed_expired(label)
                page=browser.new_page(viewport={'width':width,'height':height})
                errors=[]
                page.on('pageerror',lambda exc:errors.append(str(exc)))
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
                page.get_by_text('Безопасность и восстановление SQL-очереди',exact=True).wait_for(timeout=20000)
                card=page.locator('.ops-r35-integrity')
                assert 'Просроченные захваты: 1' in card.inner_text(),(label,card.inner_text())
                card.scroll_into_view_if_needed()
                if label=='desktop':
                    page.screenshot(path=str(OUTPUT/'preview-r35-integrity-before.png'),full_page=False)
                card.get_by_role('button',name='Проверить и восстановить').click()
                page.get_by_label('Причина служебного восстановления').fill(
                    'Проверено состояние сервера: это просроченный тестовый захват')
                page.get_by_label('Подтверждаю восстановление только просроченных заданий.').check()
                page.get_by_role('button',name='Выполнить безопасное восстановление').click()
                page.get_by_text('Восстановление просроченных захватов',exact=True).wait_for(state='hidden',timeout=20000)
                with db.SessionLocal() as s:
                    assert s.get(InboundJob,job).status=='retrying'
                    assert s.get(ChannelConnection,channel_id).inbound_processing_token is None
                page.wait_for_function("document.querySelector('.ops-r35-integrity')?.textContent?.includes('Просроченные захваты: 0')",timeout=20000)
                card=page.locator('.ops-r35-integrity')
                assert 'Просроченные захваты: 0' in card.inner_text(),(label,card.inner_text())
                assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
                assert not errors,errors
                card.scroll_into_view_if_needed()
                image=OUTPUT/f'preview-r35-integrity-{label}.png'
                page.screenshot(path=str(image),full_page=False)
                print('R35_BROWSER_PASS',label,image.name,flush=True)
                page.close()
        finally:
            browser.close()
print('R35_CHROMIUM_INTEGRITY=PASS')
