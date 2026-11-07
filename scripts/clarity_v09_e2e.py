"""Browser tests against real FastAPI handlers via in-process HTTP bridge.
No social network tokens, simulated successful social API calls, or public deploy.
"""
import os,sys,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omni-v09-'))/'browser.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['COOKIE_SECURE']='false'
from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as api:
    rr=api.post('/api/auth/register',json={'company':'Ателье Север','name':'Хозяин',
        'email':'owner-clarity@example.com','password':'NewStrongPassword!2026'})
    assert rr.status_code==201,rr.text
    lost_ack={'remaining':0}
    def open_app(browser,width,height,csrf):
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        errs=[]
        page.on('pageerror',lambda e:errs.append(str(e)))
        page.expose_function('omniApiBridge',lambda payload: handle(payload,csrf))
        page.set_content('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
        page.evaluate('''(csrf)=>{
            const store={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>store[k]||null,setItem:(k,v)=>store[k]=v}});
            Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
            window.history.replaceState=()=>{};
            window.fetch=async(url,opts={})=>{const r=await window.omniApiBridge({url:String(url),method:opts.method||'GET',body:opts.body||null});if(r.drop)throw new TypeError('Failed to fetch');return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})};
        }''',csrf)
        page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
        for part in ['vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js']:
            page.add_script_tag(path=str(ROOT/'frontend/public'/part))
        return page,errs
    def handle(payload,csrf):
        path=payload['url'];assert path.startswith('/api/'),path
        result=api.request(payload.get('method','GET'),path,headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},content=(payload.get('body') or '').encode() if payload.get('body') else None)
        if '/reply' in path and result.status_code==201 and lost_ack['remaining']>0:
            lost_ack['remaining']-=1
            return {'drop':True,'status':result.status_code,'body':result.text}
        return {'status':result.status_code,'body':result.text}

    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width,height,label in [(1512,940,'desktop'),(390,844,'mobile'),(320,700,'phone320')]:
            page,errs=open_app(browser,width,height,api.cookies.get('omnichat_csrf'))
            page.locator('.inbox-list').wait_for(timeout=12000)
            if width>720:
                page.locator('.quickstart-nav').wait_for(timeout=10000)
                page.get_by_role('button',name='Быстрый старт',exact=False).click()
            else:
                page.get_by_role('button',name='Открыть меню').click()
                page.locator('.sidebar.open').wait_for(timeout=3000)
                page.locator('.quickstart-nav').click()
            page.locator('.quickstart-step').first.wait_for(timeout=10000)
            assert page.locator('.quickstart-step').count()==3
            assert page.locator('.sidebar.open').count()==0
            page.wait_for_timeout(330) # mobile menu closes with a 220ms animation
            assert page.get_by_text('0 из 3 шагов').count()==1
            assert page.locator('.quickstart-step.done').count()==0
            assert page.evaluate('document.documentElement.scrollWidth - window.innerWidth')<=0
            screenshot=ROOT/'docs'/('preview-v09-start-'+label+'.png')
            page.screenshot(path=str(screenshot),full_page=False)
            if width==1512:
                page.locator('.quickstart-step').first.get_by_role('button',name='Выбрать соцсеть').click()
                page.get_by_role('heading',name='Подключение каналов').wait_for(timeout=7000)
                page.locator('.channel-chooser').wait_for(timeout=7000)
                assert page.locator('.integration-card').count()==1
                page.get_by_role('button',name='Instagram',exact=False).last.click()
                assert page.locator('.integration-card').count()==1
                assert page.locator('.integration-card h3').inner_text()=='Instagram'
                page.screenshot(path=str(ROOT/'docs/preview-v09-choose-channel.png'),full_page=False)
                page.get_by_role('button',name='Все каналы').click()
                assert page.locator('.integration-card').count()==7
            assert not errs,errs
            print(label,'start + UI OK',screenshot)
            page.close()
        # A new isolated demo organization for draft and same-nonce reply testing.
        demo=api.post('/api/demo/start',headers={'X-CSRF-Token':api.cookies.get('omnichat_csrf')})
        assert demo.status_code==200,demo.text
        page,errs=open_app(browser,1512,940,api.cookies.get('omnichat_csrf'))
        page.locator('.conversation-card').nth(1).wait_for(timeout=10000)
        first=page.locator('.conversation-card').nth(0)
        name=first.locator('.conv-top strong').inner_text()
        first.click()
        page.locator('.chat-topbar').wait_for(timeout=7000)
        page.locator('textarea[aria-label="Текст ответа"]').fill('Черновик для первого клиента')
        page.locator('.conversation-card').nth(1).click()
        assert page.locator('textarea[aria-label="Текст ответа"]').input_value()==''
        page.locator('.conversation-card',has_text=name).click()
        assert page.locator('textarea[aria-label="Текст ответа"]').input_value()=='Черновик для первого клиента'
        page.locator('.conversation-card',has_text=name).get_by_text('Черновик:',exact=False).wait_for(timeout=5000)
        page.locator('button[aria-label="Отправить ответ"]').click()
        page.locator('.message-text',has_text='Черновик для первого клиента').wait_for(timeout=5000)
        page.wait_for_function('document.querySelector("textarea[aria-label=\\"Текст ответа\\"]").value === ""',timeout=5000)
        # Emulate a real failure mode: the API records the message, but the HTTP
        # acknowledgement is lost. Retrying must reuse the original nonce.
        conv_id=api.get('/api/conversations').json()[0]['id']
        before=len(api.get('/api/conversations/'+conv_id).json()['messages'])
        lost_ack['remaining']=1
        page.locator('textarea[aria-label="Текст ответа"]').fill('Проверка ответа после обрыва сети')
        page.locator('button[aria-label="Отправить ответ"]').click()
        page.get_by_text('Не удалось связаться с OSMANX',exact=False).wait_for(timeout=5000)
        assert page.locator('textarea[aria-label="Текст ответа"]').input_value()=='Проверка ответа после обрыва сети'
        assert len(api.get('/api/conversations/'+conv_id).json()['messages'])==before+1
        page.locator('button[aria-label="Отправить ответ"]').click()
        page.locator('.message-text',has_text='Проверка ответа после обрыва сети').wait_for(timeout=5000)
        page.wait_for_function('document.querySelector("textarea[aria-label=\\"Текст ответа\\"]").value === ""',timeout=5000)
        assert len(api.get('/api/conversations/'+conv_id).json()['messages'])==before+1
        assert not errs,errs
        page.screenshot(path=str(ROOT/'docs/preview-v09-inbox.png'),full_page=False)
        print('Draft preservation, reliable retry / lost HTTP acknowledgment and idempotent send OK')
        browser.close()
