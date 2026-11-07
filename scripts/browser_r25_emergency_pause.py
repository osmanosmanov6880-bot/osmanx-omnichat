"""R25 real Chromium/FastAPI: admin pauses new outbound sends without disconnecting.

Three viewports; no provider calls and no public deployment. Browser buttons
exercise real authenticated endpoints, CSRF and SQL state changes.
"""
import os
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r25-ui-'))/'ui.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from app.main import app
from app import db
from app.db import ChannelConnection
from app.services import ingest_inbound

with TestClient(app) as api:
    registration=api.post('/api/auth/register',json={
        'company':'Магазин OSMANX R25','name':'Администратор',
        'email':'r25-pause-ui@example.org','password':'R25SecurePassword2026!'})
    assert registration.status_code==201,registration.text
    org=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=org,provider='telegram',
            name='Telegram службы поддержки',mode='live',status='connected',
            external_account_id='r25-browser-bot')
        session.add(ch);session.flush()
        ingest_inbound(session,channel=ch,external_chat_id='r25-qa-visitor',
            external_message_id='r25-inbound-qa',sender_id='r25-qa-visitor',
            sender_name='Покупатель R25',text='Здравствуйте, подскажите наличие товара')
        session.commit()
        channel_id=ch.id

    def bridge(payload):
        url=payload['url']
        assert url.startswith('/api/'),url
        response=api.request(payload.get('method','GET'),url,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload['body'].encode() if payload.get('body') else None)
        return {'status':response.status_code,'body':response.text}

    out=Path(os.getenv('OMNICHAT_R25_PREVIEW_DIR',str(ROOT/'docs')))
    out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():
            options['executable_path']='/usr/bin/chromium'
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
                  const res=await window.bridgeOmni({url:String(url),method:opts.method||'GET',body:opts.body||null});
                  return new Response(res.body,{status:res.status,headers:{'Content-Type':'application/json'}});
                }
            }''',csrf)
            page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
            for file in ('vendor/react.production.min.js','vendor/react-dom.production.min.js',
                         'vendor/react-fragment-polyfill.js','app.js'):
                page.add_script_tag(path=str(ROOT/'frontend/public'/file))
            page.get_by_role('button',name='Интеграции').first.wait_for(timeout=15000)
            if width<700:
                page.locator('.quiet-mobile-menu').click()
            page.get_by_role('button',name='Интеграции').first.click()
            page.get_by_text('Telegram службы поддержки').wait_for(timeout=12000)
            btn=page.get_by_role('button',name='Приостановить исходящие').first
            btn.wait_for(timeout=8000)
            page.once('dialog',lambda dialog:dialog.accept())
            btn.click()
            page.get_by_text('Новые исходящие приостановлены.',exact=True).wait_for(timeout=10000)
            assert api.get('/api/operations/overview').json()['outbound_paused_channels']==1
            assert page.get_by_text('Telegram службы поддержки').count()>=1
            assert not errors,errors
            assert page.evaluate('document.documentElement.scrollWidth - window.innerWidth')<=1
            page.get_by_text('Новые исходящие приостановлены.',exact=True).scroll_into_view_if_needed()
            snap=out/f'preview-r25-outbound-pause-{label}.png'
            page.screenshot(path=str(snap),full_page=False)
            resume=page.get_by_role('button',name='Возобновить исходящие').first
            page.once('dialog',lambda dialog:dialog.accept())
            resume.click()
            page.get_by_role('button',name='Приостановить исходящие').first.wait_for(timeout=10000)
            assert api.get('/api/operations/overview').json()['outbound_paused_channels']==0
            # A normal operator composing in Inbox must see an explicit warning,
            # not silently believe that a queued reply already left this server.
            reopened=api.post('/api/integrations/'+channel_id+'/outbound-pause',
                headers={'X-CSRF-Token':csrf},
                json={'reason':'operator_request','acknowledge_inflight':True})
            assert reopened.status_code==200,reopened.text
            if width<700:
                # Integration/settings pages have a top-strip hamburger, not
                # the Inbox-only .quiet-mobile-menu used on initial entry.
                page.locator('.top-strip .mobile-menu').click(timeout=6000)
                page.locator('.sidebar.open .nav-item',has_text='Входящие').first.click(timeout=6000)
            else:
                page.locator('.sidebar .nav-item',has_text='Входящие').first.click(timeout=6000)
            page.locator('.conversation-card').first.wait_for(timeout=10000)
            page.locator('.conversation-card').first.click()
            warning=page.get_by_text('Отправка через этот аккаунт приостановлена.',exact=True)
            warning.wait_for(timeout=10000)
            if page.locator('.toast button').count():
                page.locator('.toast button').click()
            assert page.evaluate('document.documentElement.scrollWidth - window.innerWidth')<=1
            inboxshot=out/f'preview-r25-inbox-pause-{label}.png'
            warning.scroll_into_view_if_needed()
            page.screenshot(path=str(inboxshot),full_page=False)
            reset=api.post('/api/integrations/'+channel_id+'/outbound-resume',
                headers={'X-CSRF-Token':csrf})
            assert reset.status_code==200,reset.text
            assert not errors,errors
            print('R25_OUTBOUND_PAUSE_UI_PASS',label,snap,inboxshot)
            page.close()
        browser.close()
