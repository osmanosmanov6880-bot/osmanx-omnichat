"""Actual React UI + local FastAPI, official Meta response mocked.

UI interactions include consent attestation, text variables and queue insertion.
This is not a live provider acceptance test.
"""
from pathlib import Path
import os
import sys
import tempfile
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='wa-template-browser-'))/'ui.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from cryptography.fernet import Fernet
os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
from fastapi.testclient import TestClient
from app.main import app
from app import db
from app.db import ChannelConnection,Message,OutgoingJob,now
from app.services import ingest_inbound
from app.integrations.adapters import seal
from app.integrations import adapters

async def fake_graph(method,url,*,headers=None,params=None,data=None,json_data=None):
    if method=='GET' and '/message_templates' in url:
        return {'data':[{'name':'appointment_reminder','language':'ru','status':'APPROVED',
            'components':[{'type':'BODY','text':'Здравствуйте, {{1}}! Встреча: {{2}}.'}]}]}
    raise AssertionError('Only official catalog GET expected in this UI test')
adapters.call=fake_graph

with TestClient(app) as api:
    register=api.post('/api/auth/register',json={'company':'Тестовая студия','name':'Владелец',
        'email':'wa-ui@example.org','password':'StrongTestPassword2026!'})
    assert register.status_code==201,register.text
    me=api.get('/api/auth/me').json()
    csrf=api.cookies.get('omnichat_csrf')
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=me['organization']['id'],provider='whatsapp',
            name='Номер тестовой студии',external_account_id='12340001234',mode='live',status='connected',
            encrypted_credentials=seal({'phone_number_id':'12340001234','waba_id':'987654321','access_token':'TEST_TOKEN'}))
        session.add(ch);session.flush()
        ingest_inbound(session,channel=ch,external_chat_id='79990001122',
            external_message_id='incoming-1',sender_id='79990001122',
            sender_name='Тестовый клиент',text='Хочу записаться',timestamp=now()-72*3600)
        session.commit()

    def bridge(data):
        path=data['url']
        if not path.startswith('/api/'):
            raise AssertionError('Unexpected request '+path)
        response=api.request(data.get('method','GET'),path,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=data.get('body').encode() if data.get('body') else None)
        return {'status':response.status_code,'body':response.text}

    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        output=Path(os.environ.get('OMNICHAT_WA_PREVIEW_DIR',str(ROOT/'docs')))
        output.mkdir(parents=True,exist_ok=True)
        for width,height,name in [(1512,980,'desktop'),(390,844,'mobile'),(320,720,'phone320')]:
            page=browser.new_page(viewport={'width':width,'height':height})
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.expose_function('bridgeOmni',bridge)
            page.set_content('<!doctype html><html lang="ru"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
            page.evaluate('''csrf=>{
                const storage={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=v}});
                Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
                window.history.replaceState=()=>{};
                window.fetch=async(url,opts={})=>{
                    const r=await window.bridgeOmni({url:String(url),method:opts.method||'GET',body:opts.body||null});
                    return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})
                }
            }''',csrf)
            page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
            for script in ('vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js'):
                page.add_script_tag(path=str(ROOT/'frontend/public'/script))
            page.locator('.conversation-card').first.wait_for(timeout=12000)
            page.locator('.conversation-card').first.click()
            page.get_by_role('button',name='Одобренный шаблон WhatsApp').wait_for(timeout=12000)
            page.get_by_role('button',name='Одобренный шаблон WhatsApp').click()
            page.get_by_role('dialog').wait_for(timeout=6000)
            if page.get_by_label('Источник и дата согласия').count():
                page.get_by_label('Источник и дата согласия').fill('Форма записи от 1 ноября; клиент подтвердил согласие')
                page.get_by_text('Подтверждаю, что клиент дал согласие').click()
                page.get_by_role('button',name='Зафиксировать согласие').click()
            page.get_by_text('Согласие зафиксировано сотрудником').wait_for(timeout=8000)
            page.get_by_label('Параметр 1').fill('Алина')
            page.get_by_label('Параметр 2').fill('12 ноября, 14:00')
            assert 'Алина' in page.locator('.wa-preview').inner_text()
            shot=output/f'preview-wa-template-{name}.png'
            page.screenshot(path=str(shot),full_page=False)
            if name=='desktop':
                page.get_by_role('button',name='Поставить шаблон в очередь').click()
                page.get_by_role('dialog').wait_for(state='hidden',timeout=10000)
                with db.SessionLocal() as session:
                    assert session.query(Message).filter_by(kind='whatsapp_template').count()==1
                    assert session.query(OutgoingJob).filter_by(status='queued').count()==1
            assert not errors,errors
            assert page.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=0
            print('UI_OK',name,shot)
            page.close()
        browser.close()
