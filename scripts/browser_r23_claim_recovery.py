"""R23 UI: pre-send recovery and durable checkpoint, with R22 controls.

Screenshots at 1512, 390, 320 px. No provider API calls are made. UI actions
perform real SQL writes, with CSRF and tenant auth, in an isolated SQLite DB.
"""
from pathlib import Path
import os
import sys
import tempfile
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-r22-browser-'))/'qa.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from fastapi.testclient import TestClient
from app.main import app
from app import db
from app.db import ChannelConnection, Contact, Conversation, Message, OutgoingJob, AuditLog, now

with TestClient(app) as api:
    reg=api.post('/api/auth/register',json={
        'company':'Магазин OSMANX', 'name':'Руководитель',
        'email':'r22-browser@example.org','password':'R22SecurePassword2026!'})
    assert reg.status_code==201,reg.text
    org_id=api.get('/api/auth/me').json()['organization']['id']
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=org_id,provider='telegram',name='Telegram магазина',
                                  mode='live',status='connected')
        contact=Contact(organization_id=org_id,name='Покупатель')
        session.add_all([channel,contact]);session.flush()
        conv=Conversation(organization_id=org_id,channel_id=channel.id,
                          contact_id=contact.id,external_chat_id='r22-buyer')
        session.add(conv);session.flush()
        ids=[]
        for i in range(2):
            status='queued' if i==0 else 'failed'
            msg=Message(organization_id=org_id,conversation_id=conv.id,direction='out',
                        client_nonce='r22-nonce-'+str(i),external_id='client-r22-nonce-'+str(i),
                        body='Проверочный ответ '+str(i),delivery_status=status)
            session.add(msg);session.flush()
            job=OutgoingJob(organization_id=org_id,message_id=msg.id,channel_id=channel.id,
                            status=status,last_error='API 403: проверка прав' if i else None)
            session.add(job);session.flush()
            ids.append((job.id,msg.id))
        # A preparation in progress has no external-send marker; UI must say so.
        extra_message=Message(organization_id=org_id,conversation_id=conv.id,
                              direction='out',body='Подготовка ответа оператором',
                              delivery_status='queued')
        session.add(extra_message);session.flush()
        extra_job=OutgoingJob(organization_id=org_id,message_id=extra_message.id,
                              channel_id=channel.id,status='processing',
                              claim_token='r23-local-browser-fixture',claimed_at=now(),
                              send_started_at=None,attempts=1)
        session.add(extra_job)
        # Representative previously recorded recovery event; the underlying
        # safe recovery transaction itself is covered by SQL unit tests.
        session.add(AuditLog(organization_id=org_id,user_id=None,
                             action='outbox.recovered_before_send',entity_id=extra_job.id,
                             detail='Проверенная подготовка восстановлена до HTTP-отправки'))
        session.commit()

    def bridge(payload):
        path=payload['url']
        if not path.startswith('/api/'):
            raise AssertionError('Unexpected request '+path)
        response=api.request(payload.get('method','GET'),path,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=payload.get('body').encode() if payload.get('body') else None)
        return {'status':response.status_code,'body':response.text}

    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        output=Path(os.getenv('OMNICHAT_R23_PREVIEW_DIR',str(ROOT/'docs')))
        output.mkdir(parents=True,exist_ok=True)
        for width,height,name in [(1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')]:
            with db.SessionLocal() as session:
                for idx,(jid,mid) in enumerate(ids):
                    job=session.get(OutgoingJob,jid)
                    job.status='queued' if idx==0 else 'failed'
                    job.last_error=None if idx==0 else 'API 403: проверка прав'
                    job.attempts=0
                    msg=session.get(Message,mid)
                    msg.delivery_status=job.status
                session.commit()
            page=browser.new_page(viewport={'width':width,'height':height})
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.expose_function('bridgeOmni',bridge)
            page.set_content('<!doctype html><html lang="ru"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
            page.evaluate('''csrf=>{
                const storage={};
                Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=v}});
                Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
                window.history.replaceState=()=>{};
                window.fetch=async(url,opts={})=>{
                    const r=await window.bridgeOmni({url:String(url),method:opts.method||'GET',body:opts.body||null});
                    return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})
                }
            }''',csrf)
            page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
            for script in ('vendor/react.production.min.js','vendor/react-dom.production.min.js',
                           'vendor/react-fragment-polyfill.js','app.js'):
                page.add_script_tag(path=str(ROOT/'frontend/public'/script))
            page.locator('.quiet-more').wait_for(timeout=15000)
            if width<700:
                page.locator('.quiet-mobile-menu').click()
                page.locator('.sidebar.open').wait_for(timeout=6000)
            page.locator('.quiet-more').click()
            page.get_by_role('button',name='Контроль доставки').click()
            page.locator('.ops-next-step').wait_for(timeout=9000)
            assert page.get_by_role('button',name='Отменить до отправки').count()==1
            assert page.get_by_role('button',name='Повторить после проверки').count()==1
            page.get_by_text('Подготовка до отправки',exact=True).first.wait_for(timeout=9000)
            assert page.get_by_text('Восстановлено безопасно: 1').count()==1
            # Capture the page, not a sidebar caught mid-close animation.
            page.wait_for_timeout(450)
            assert not page.locator('.sidebar').evaluate('(n)=>n.classList.contains("open")')
            snap=output/f'preview-r23-recovery-{name}.png'
            page.screenshot(path=str(snap),full_page=False)
            # A second screenshot shows the actual new actions, not just the
            # existing delivery overview at the top of a long mobile page.
            page.get_by_role('button',name='Повторить после проверки').scroll_into_view_if_needed()
            page.wait_for_timeout(180)
            actions=output/f'preview-r23-actions-{name}.png'
            page.screenshot(path=str(actions),full_page=False)
            page.once('dialog',lambda dialog:dialog.accept())
            page.get_by_role('button',name='Отменить до отправки').click()
            page.get_by_text('Отменено до отправки').first.wait_for(timeout=9000)
            with db.SessionLocal() as session:
                assert session.get(OutgoingJob,ids[0][0]).status=='cancelled'
                assert session.get(Message,ids[0][1]).delivery_status=='cancelled'
            page.get_by_role('button',name='Повторить после проверки').click()
            dlg=page.get_by_role('dialog')
            dlg.wait_for(timeout=9000)
            btn=dlg.get_by_role('button',name='Поставить повтор в очередь')
            assert btn.is_disabled()
            dlg.get_by_label('Подтверждение отсутствия доставки').fill('Проверил в Telegram: сообщения нет, отказ API 403')
            dlg.get_by_text('Я проверил отсутствие доставки').click()
            assert btn.is_enabled()
            btn.click()
            page.get_by_text('Повтор поставлен в очередь').first.wait_for(timeout=9000)
            with db.SessionLocal() as session:
                assert session.get(OutgoingJob,ids[1][0]).status=='queued'
                assert session.get(Message,ids[1][1]).delivery_status=='queued'
            assert not errors, errors
            overflow=page.evaluate('document.documentElement.scrollWidth-window.innerWidth')
            assert overflow<=0,f'Unexpected horizontal scroll {width}: {overflow}'
            print('R23_OUTBOX_UI_PASS',name,snap,actions)
            page.close()
        browser.close()
