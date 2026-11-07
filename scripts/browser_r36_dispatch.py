"""R36 on R35: browser E2E against real FastAPI in-process, no provider calls."""
from pathlib import Path
import os, sys, tempfile, shutil
from cryptography.fernet import Fernet
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r36-real-browser-'))/'test.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
from fastapi.testclient import TestClient
from app.main import app
from app import db
from app.db import ChannelConnection,Contact,Conversation,Message,OutgoingJob

OUTPUT=Path(os.environ.get('OMNICHAT_R36_PREVIEW_DIR',str(ROOT/'docs')))
OUTPUT.mkdir(parents=True,exist_ok=True)
with TestClient(app) as api:
    r=api.post('/api/auth/register',json={'company':'OSMANX · R36 проверка',
        'name':'Владелец','email':'r36@local.example','password':'LongTestPassword2026!'})
    assert r.status_code==201,r.text
    me=api.get('/api/auth/me').json(); csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        org=me['organization']['id']
        ch=ChannelConnection(organization_id=org,provider='telegram',name='Бот поддержки',
            mode='live',status='connected',external_account_id='r36-synthetic-test')
        contact=Contact(organization_id=org,name='Synthetic private name')
        session.add_all([ch,contact]);session.flush()
        conv=Conversation(organization_id=org,channel_id=ch.id,contact_id=contact.id,
            external_chat_id='synthetic_r36_chat')
        session.add(conv);session.flush()
        msg=Message(organization_id=org,conversation_id=conv.id,
            body='PRIVATE SYNTHETIC R36 CONTENT',direction='out',delivery_status='uncertain')
        session.add(msg);session.flush()
        job=OutgoingJob(organization_id=org,channel_id=ch.id,message_id=msg.id,
            status='uncertain',last_error='Проверить вручную')
        session.add(job);session.commit()

    def bridge(payload):
        path=str(payload['url']); assert path.startswith('/api/'),path
        response=api.request(payload.get('method','GET'),path,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload['body'].encode() if payload.get('body') else None)
        return {'status':response.status_code,'body':response.text}

    with sync_playwright() as pw:
        opts={'headless':True,'args':['--no-sandbox']}
        if shutil.which('chromium'):opts['executable_path']=shutil.which('chromium')
        browser=pw.chromium.launch(**opts)
        try:
            for w,h,label in ((1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')):
                page=browser.new_page(viewport={'width':w,'height':h},accept_downloads=True)
                errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                page.on('dialog',lambda d:d.accept())
                page.expose_function('bridgeOmniR36',bridge)
                page.set_content('<!doctype html><html lang="ru"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
                page.evaluate('''csrf=>{
                    const storage={};window.history.replaceState=()=>{};
                    Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=v}});
                    Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
                    window.fetch=async(url,opts={})=>{
                        const r=await window.bridgeOmniR36({url:String(url),method:opts.method||'GET',body:opts.body||null});
                        return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}});
                    }
                }''',csrf)
                page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
                for asset in ('vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js'):
                    page.add_script_tag(path=str(ROOT/'frontend/public'/asset))
                page.get_by_role('button',name='Входящие').first.wait_for(timeout=30000)
                if w<700:page.locator('.quiet-mobile-menu').click()
                page.locator('.sidebar .quiet-more').click()
                page.locator('.sidebar-extra .nav-item',has_text='Контроль доставки').first.click()
                safety=page.locator('.ops-r36-safety');safety.wait_for(timeout=20000)
                assert 'Временная пауза отправок' in safety.inner_text()
                assert 'Нужна проверка отправок: 1' in safety.inner_text()
                safety.get_by_role('button',name='Включить паузу').click()
                page.wait_for_function("document.querySelector('.ops-r36-pauses')?.textContent?.includes('Вся компания')",timeout=20000)
                assert api.get('/api/operations/dispatch-pauses').json()['pauses']
                page.locator('.ops-r36-pauses').get_by_role('button',name='Снять').first.click()
                page.wait_for_function("document.querySelector('.ops-r36-pauses')===null",timeout=20000)
                assert api.get('/api/operations/dispatch-pauses').json()['pauses']==[]
                page.locator('.ops-job-actions').get_by_role('button',name='История').first.click()
                page.locator('.ops-r36-history').wait_for(timeout=15000)
                assert 'Событий пока нет' in page.locator('.ops-r36-history').inner_text()
                with page.expect_download(timeout=20000) as dl:
                    page.locator('.ops-r36-safety').get_by_role('button',name='Скачать обезличенный отчёт').click()
                assert dl.value.suggested_filename=='osmanx-omnichat-r36-support.json'
                assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
                assert not errors,errors
                safety.scroll_into_view_if_needed()
                path=OUTPUT/f'preview-r36-r35-{label}.png';page.screenshot(path=str(path),full_page=False)
                print('R36_BROWSER_PASS',label,path.name,flush=True)
                page.close()
        finally:browser.close()
print('R36_R35_CHROMIUM=PASS')
