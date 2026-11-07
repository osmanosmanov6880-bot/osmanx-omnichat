"""V1.4 Chromium smoke test of the real React delivery console + FastAPI.

Provider requests are never issued. The inbox and operational data are persisted
by the real backend via in-process TestClient while only transport is bridged.
"""
from pathlib import Path
import os
import sys
import tempfile
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omnichat-v14-browser-'))/'ui.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from fastapi.testclient import TestClient
from app.main import app
from app import db
from app.db import ChannelConnection,Contact,Conversation,Message,OutgoingJob

with TestClient(app) as api:
    register=api.post('/api/auth/register',json={'company':'Тест OSMANX','name':'Владелец',
        'email':'ops-v14@example.org','password':'LongTestPassword2026!'})
    assert register.status_code==201,register.text
    me=api.get('/api/auth/me').json()
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=me['organization']['id'],provider='telegram',name='Бот поддержки',
                            mode='live',status='connected',external_account_id='bot-v14-test')
        contact=Contact(organization_id=me['organization']['id'],name='Тестовый клиент')
        session.add_all([ch,contact]);session.flush()
        conv=Conversation(organization_id=me['organization']['id'],channel_id=ch.id,
                          contact_id=contact.id,external_chat_id='chat-v14-test')
        session.add(conv);session.flush()
        for i in range(115):
            msg=Message(organization_id=me['organization']['id'],conversation_id=conv.id,
                        body='Тестовый ответ '+str(i),direction='out',delivery_status='accepted')
            session.add(msg);session.flush()
            session.add(OutgoingJob(organization_id=me['organization']['id'],channel_id=ch.id,
                message_id=msg.id,status='uncertain' if i==0 else 'done',
                last_error='Сеть оборвалась: результат нужно сверить' if i==0 else None))
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
        output=Path(os.environ.get('OMNICHAT_V14_PREVIEW_DIR',str(ROOT/'docs')))
        output.mkdir(parents=True,exist_ok=True)
        for width,height,name in [(1512,950,'desktop'),(390,844,'mobile'),(320,700,'phone320')]:
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
            if width<700:
                page.locator('.quiet-mobile-menu').click()
                page.locator('.sidebar.open').wait_for(timeout=5000)
            page.locator('.quiet-more').click()
            page.get_by_role('button',name='Контроль доставки').click()
            page.locator('.ops-next-step').wait_for(timeout=10000)
            text=page.locator('.ops-next-step').inner_text()
            assert 'неизвестным результатом' in text,text
            row=page.locator('.table-scroll tbody tr').first.inner_text()
            assert 'Требует проверки' in row,row
            assert 'uncertain' not in row
            assert 'Фоновый обработчик не отвечает' in page.locator('.worker-signal').inner_text()
            assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=0, 'Horizontal scroll'
            assert not errors,errors
            shot=output/f'preview-v14-worker-{name}.png'
            page.screenshot(path=str(shot),full_page=False)
            print('V14_UI_OK',name,shot)
            page.close()
        browser.close()
