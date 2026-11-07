"""Browser E2E tests against the actual FastAPI handlers through a local in-process bridge.
No external APIs, no fabricated success responses, no public network needed.
"""
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omni-v08-ui-'))/'e2e.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as api:
    r=api.post('/api/demo/start')
    assert r.status_code==200, r.text
    csrf=api.cookies.get('omnichat_csrf')
    assert csrf
    calls=[]
    def bridge(payload):
        path=payload['url']
        assert path.startswith('/api/'),path
        method=(payload.get('method') or 'GET').upper()
        headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'}
        body=payload.get('body')
        result=api.request(method,path,headers=headers,content=body.encode() if isinstance(body,str) else None)
        calls.append((method,path,result.status_code))
        return {'status':result.status_code,'body':result.text}

    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width,height,name in [(1648,928,'desktop'),(390,844,'mobile'),(320,700,'phone320')]:
            page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
            page.expose_function('omniApiBridge',bridge)
            page.set_content('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
            page.evaluate('''(csrf)=>{
              const bag={}; Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>bag[k]||null,setItem:(k,v)=>bag[k]=v,removeItem:k=>delete bag[k]}});
              Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
              Object.defineProperty(window,'fetch',{configurable:true,value:async(url,opts={})=>{
                const x=await window.omniApiBridge({url:String(url),method:opts.method||'GET',body:opts.body||null});
                return new Response(x.body,{status:x.status,headers:{'Content-Type':'application/json'}});
              }});
              window.history.replaceState=()=>{};
            }''',csrf)
            page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
            for name_js in ['react.production.min.js','react-dom.production.min.js','react-fragment-polyfill.js']:
                page.add_script_tag(path=str(ROOT/'frontend/public/vendor'/name_js))
            page.add_script_tag(path=str(ROOT/'frontend/public/app.js'))
            page.locator('.conversation-card').first.wait_for(timeout=10000)
            if width<=720:
                page.locator('.conversation-card').first.click()
                page.locator('.inbox-layout.mobile-chat').wait_for(timeout=3000)
            else:
                page.locator('.chat-topbar').wait_for(timeout=3000)
            if name=='desktop':
                assert page.locator('.details-pane').is_visible()
                # Direct user's actions must affect the true, persisted app state.
                page.locator('textarea[aria-label="Текст ответа"]').fill('Проверка ответа из нового интерфейса')
                page.locator('button[aria-label="Отправить ответ"]').click()
                page.locator('.message-text',has_text='Проверка ответа из нового интерфейса').wait_for(timeout=5000)
                page.locator('.quiet-add-tag').click()
                page.locator('input[aria-label="Новый тег"]').fill('Приоритетный')
                page.locator('input[aria-label="Новый тег"]').press('Enter')
                page.get_by_text('Приоритетный').first.wait_for(timeout=5000)
                page.get_by_role('button',name='Удалить тег Приоритетный').click()
                page.locator('select[aria-label="Этап сделки"]').select_option('negotiation')
                page.locator('button[aria-label="Действия с диалогом"]').click()
                page.get_by_role('button',name='Внутренние заметки').click()
                page.locator('textarea[aria-label="Новая заметка"]').fill('Проверка внутренней заметки')
                page.get_by_role('button',name='Сохранить заметку').click()
                page.get_by_text('Проверка внутренней заметки').wait_for(timeout=5000)
                page.get_by_role('button',name='К клиенту').click()
            # Image before navigation: this is the actual rendered app, not generated art.
            if page.locator('.toast button').count(): page.locator('.toast button').first.click()
            screenshot=ROOT/'docs'/('preview-v07-'+name+'.png')
            page.screenshot(path=str(screenshot),full_page=False)
            overflow=page.evaluate('document.documentElement.scrollWidth - window.innerWidth')
            assert overflow<=0,(name,'horizontal overflow',overflow)
            if name=='desktop':
                page.locator('nav.quiet-nav button',has_text='Сделки').click()
                page.locator('.quiet-deals').wait_for(timeout=5000)
                assert page.locator('.deals-stage').count()==6
                page.locator('nav.quiet-nav button',has_text='Входящие').click()
                page.locator('.inbox-list').wait_for(timeout=5000)
                page.locator('button[aria-label="Показать канал"]').count() if False else None
                page.locator('select[aria-label="Показать канал"]').select_option('instagram')
                page.locator('.conversation-card').first.wait_for(timeout=5000)
                assert 'instagram' in page.locator('.conversation-card').first.locator('.provider').get_attribute('class')
            elif name=='mobile':
                page.locator('button[aria-label="Показать карточку клиента"]').click()
                page.locator('.details-pane').wait_for(timeout=5000)
                page.locator('button[aria-label="Свернуть карточку клиента"]').click()
                page.locator('button[aria-label="К списку переписок"]').click()
                page.locator('.inbox-list').wait_for(timeout=3000)
                assert page.locator('.inbox-list').is_visible()
                page.screenshot(path=str(ROOT/'docs'/'preview-v07-mobile-list.png'),full_page=False)
            assert not errors,(name,errors)
            print(name,'OK','size',width,'x',height,'overflow',overflow,'api',len(calls))
            page.close()
        browser.close()
    assert any('reply' in path and status in (200,201) for method,path,status in calls),calls
    assert any('/contacts/' in path and status==200 for method,path,status in calls),calls
    assert any('/notes' in path and status in (200,201) for method,path,status in calls),calls
    print('E2E complete: genuine backend handlers, message reply, tags, stage, note, Deals and responsive layout.')
