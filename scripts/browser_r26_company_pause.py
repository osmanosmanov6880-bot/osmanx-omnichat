"""R26 real Chromium + FastAPI: tenant-wide outbound incident pause, 3 sizes.

All network is local TestClient. No production credentials or provider calls.
"""
import os
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r26-ui-'))/'qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from app.main import app
from app import db
from app.db import ChannelConnection
from app.services import ingest_inbound

with TestClient(app) as api:
    registered=api.post('/api/auth/register',json={
        'company':'Служба поддержки OSMANX','name':'Владелец',
        'email':'r26-ui-incident@example.org','password':'R26SecurePassword2026!'})
    assert registered.status_code==201,registered.text
    org=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=org,provider='telegram',name='Telegram поддержки',
            mode='live',status='connected',external_account_id='r26-test-bot')
        session.add(ch);session.flush()
        ingest_inbound(session,channel=ch,external_chat_id='client-100',
            external_message_id='r26-visitor-inbound',sender_id='client-100',
            sender_name='Гость',text='Здравствуйте, можно узнать цену?')
        session.commit()
    def bridge(payload):
        url=payload['url']
        assert url.startswith('/api/'),url
        response=api.request(payload.get('method','GET'),url,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload['body'].encode() if payload.get('body') else None)
        return {'status':response.status_code,'body':response.text}

    out=Path(os.getenv('OMNICHAT_R26_PREVIEW_DIR',str(ROOT/'docs')))
    out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():options['executable_path']='/usr/bin/chromium'
        browser=pw.chromium.launch(**options)
        for width,height,label in ((1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')):
            page=browser.new_page(viewport={'width':width,'height':height})
            errors=[]
            page.on('pageerror',lambda exc:errors.append(str(exc)))
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
            for file in ('vendor/react.production.min.js','vendor/react-dom.production.min.js',
                         'vendor/react-fragment-polyfill.js','app.js'):
                page.add_script_tag(path=str(ROOT/'frontend/public'/file))
            page.get_by_role('button',name='Входящие').first.wait_for(timeout=15000)
            if width<700:page.locator('.quiet-mobile-menu').click()
            page.locator('.sidebar .quiet-more').click()
            page.locator('.sidebar-extra .nav-item',has_text='Контроль доставки').first.click()
            page.get_by_text('АВАРИЙНАЯ ЗАЩИТА КОМПАНИИ',exact=True).wait_for(timeout=10000)
            trigger=page.get_by_role('button',name='Остановить все исходящие')
            trigger.wait_for(timeout=8000)
            page.once('dialog',lambda d:d.accept())
            trigger.click()
            page.get_by_text('Все новые исходящие приостановлены',exact=True).wait_for(timeout=10000)
            report=api.get('/api/operations/overview').json()
            assert report['organization_outbound_paused_at'] is not None,report
            assert report['outbound_paused_channels']==0
            assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
            assert not errors,errors
            snap=out/f'preview-r26-global-pause-{label}.png'
            page.locator('.ops-global-guard').scroll_into_view_if_needed()
            page.screenshot(path=str(snap),full_page=False)
            button=page.get_by_role('button',name='Возобновить все исходящие')
            page.once('dialog',lambda d:d.accept())
            button.click()
            trigger.wait_for(timeout=10000)
            assert api.get('/api/operations/overview').json()['organization_outbound_paused_at'] is None
            # Re-enable incident via API, confirm ordinary operator sees inbox warning.
            response=api.post('/api/operations/outbound/pause',headers={'X-CSRF-Token':csrf},
                              json={'reason':'operator_request','acknowledge_inflight':True})
            assert response.status_code==200,response.text
            if width<700:
                page.locator('.top-strip .mobile-menu').click()
                page.locator('.sidebar.open .nav-item',has_text='Входящие').first.click()
            else:
                page.locator('.sidebar .nav-item',has_text='Входящие').first.click()
            page.locator('.conversation-card').first.wait_for(timeout=10000)
            page.locator('.conversation-card').first.click()
            warning=page.get_by_text('Компания приостановила все новые исходящие.',exact=True)
            warning.wait_for(timeout=10000)
            if page.locator('.toast button').count():page.locator('.toast button').click()
            warning.scroll_into_view_if_needed()
            inboxshot=out/f'preview-r26-global-pause-inbox-{label}.png'
            page.screenshot(path=str(inboxshot),full_page=False)
            assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=1
            assert not errors,errors
            stamp=api.get('/api/operations/overview').json()['organization_outbound_paused_at']
            resumed=api.post('/api/operations/outbound/resume',headers={'X-CSRF-Token':csrf},
                             json={'expected_paused_at':stamp,'acknowledge_inflight':True})
            assert resumed.status_code==200,resumed.text
            page.close()
            print('R26_GLOBAL_PAUSE_UI_PASS',label,snap.name,inboxshot.name)
        browser.close()
