"""Chromium UI and first-party visitor messaging, backed by the real FastAPI app.

Chromium network navigation may be prohibited in restricted/offline CI, so this
uses its actual React and widget scripts with an in-process HTTP transport.
No mocked API responses. This does not replace a public-deployment E2E test.
"""
import os
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['DATABASE_URL']='sqlite:////tmp/omnichat-world-browser-e2e.db'
from app.main import app

OUT=Path(os.environ.get('OMNICHAT_E2E_OUT','/mnt/data'))
OUT.mkdir(parents=True,exist_ok=True)
HTML='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"/></head><body><div id="root"></div></body></html>'

def bridge(client):
    def handler(source,url,init=None):
        init=init or {}
        path=str(url).replace('http://127.0.0.1:8765','').replace('https://omnichat.example','')
        response=client.request(init.get('method','GET'),path,content=init.get('body'),headers=init.get('headers') or {},follow_redirects=False)
        try:payload=response.json()
        except Exception:payload={'detail':response.text[:120]}
        return {'status':response.status_code,'data':payload}
    return handler

FETCH_JS='''(function () {
 const mem={};
 Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:(k)=>mem[k]||null,setItem:(k,v)=>mem[k]=v,removeItem:(k)=>delete mem[k]}});
 Object.defineProperty(window,'sessionStorage',{configurable:true,value:{getItem:(k)=>mem[k]||null,setItem:(k,v)=>mem[k]=v,removeItem:(k)=>delete mem[k]}});
 Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf=CSRF_VALUE',set:()=>true});
 window.history.replaceState=()=>{};
 window.fetch=async function (url,opts={}) {
   const response=await window.__apiBridge(String(url),{method:opts.method||'GET',headers:opts.headers||{},body:opts.body||null});
   return new Response(JSON.stringify(response.data),{status:response.status,headers:{'Content-Type':'application/json'}});
 };
}())'''

with TestClient(app) as backend:
    demo=backend.post('/api/demo/start')
    assert demo.status_code==200,demo.text
    csrf=backend.cookies.get('omnichat_csrf')
    with sync_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():
            options['executable_path']='/usr/bin/chromium'
        browser=pw.chromium.launch(**options)
        context=browser.new_context(viewport={'width':1512,'height':950},device_scale_factor=1)
        errors=[]
        page=context.new_page()
        page.on('pageerror',lambda err:errors.append('APP: '+str(err)))
        page.on('console',lambda msg:errors.append('APP: '+msg.text) if msg.type=='error' else None)
        page.expose_binding('__apiBridge',bridge(backend))
        page.set_content(HTML)
        page.evaluate(FETCH_JS.replace('CSRF_VALUE',csrf))
        public=ROOT/'frontend'/'public'
        page.add_style_tag(path=str(public/'styles.css'))
        for filename in ['vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js']:
            page.add_script_tag(path=str(public/filename))
        page.locator('.inbox-list').wait_for(timeout=10000)
        page.locator('.nav-item').filter(has_text='Web Chat').click()
        page.locator('.site-form').wait_for(timeout=12000)
        labels=page.locator('.site-form label')
        labels.nth(0).locator('input').fill('OSMANX Store Live Support')
        labels.nth(1).locator('textarea').fill('http://localhost:3000')
        page.get_by_role('button',name='Create website channel').click()
        page.locator('.site-card').wait_for(timeout=12000)
        snippet=page.locator('.site-embed pre').first.inner_text()
        key=re.search(r'data-omnichat-key="([A-Za-z0-9_-]+)"',snippet).group(1)
        page.screenshot(path=str(OUT/'OSMANX_OMNICHAT_WORLD_websites.png'),full_page=True)

        # Real visitor widget JS, real API and distinct visitor session.
        widget=context.new_page()
        widget.set_viewport_size({'width':390,'height':660})
        widget.on('pageerror',lambda err:errors.append('WIDGET: '+str(err)))
        widget.on('console',lambda msg:errors.append('WIDGET: '+msg.text) if msg.type=='error' else None)
        widget.expose_binding('__apiBridge',bridge(backend))
        widget.set_content((public/'widget.html').read_text())
        widget.evaluate(FETCH_JS.replace('CSRF_VALUE',csrf))
        widget.add_style_tag(path=str(public/'widget.css'))
        script=(public/'widget-client.js').read_text()
        script=script.replace("var key = decodeURIComponent(location.pathname.split('/').filter(Boolean).pop() || '');",'var key = '+repr(key)+';')
        widget.add_script_tag(content=script)
        widget.locator('#company').wait_for(timeout=8000)
        widget.locator('#begin').click()
        widget.locator('#body').fill('I want to speak to a real operator')
        widget.locator('#send').click()
        widget.locator('.bubble.mine').first.wait_for(timeout=12000)

        page.locator('.nav-item').filter(has_text='Сообщения').first.click()
        page.locator('.conversation-card').filter(has_text='Website').first.wait_for(timeout=12000)
        page.locator('.conversation-card').filter(has_text='Website').first.click()
        page.locator('textarea[aria-label="\u0422\u0435\u043a\u0441\u0442 \u043e\u0442\u0432\u0435\u0442\u0430"]').fill('Your order support is here, welcome!')
        page.locator('button.send-btn').click()
        page.locator('.message-text').filter(has_text='Your order support').wait_for(timeout=12000)
        page.screenshot(path=str(OUT/'OSMANX_OMNICHAT_WORLD_inbox.png'),full_page=False)
        widget.locator('.bubble').filter(has_text='Your order support').wait_for(timeout=14000)
        widget.screenshot(path=str(OUT/'OSMANX_OMNICHAT_WORLD_widget.png'),full_page=True)

        # The same public key without private visitor session cannot see messages.
        visitor_other=backend.get('/api/public/widget/'+key+'/messages')
        assert visitor_other.status_code==401

        mobile=context.new_page()
        mobile.set_viewport_size({'width':390,'height':844})
        mobile.on('pageerror',lambda err:errors.append('MOBILE: '+str(err)))
        mobile.expose_binding('__apiBridge',bridge(backend))
        mobile.set_content(HTML)
        mobile.evaluate(FETCH_JS.replace('CSRF_VALUE',csrf))
        mobile.add_style_tag(path=str(public/'styles.css'))
        for filename in ['vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js']:
            mobile.add_script_tag(path=str(public/filename))
        mobile.locator('.inbox-list').wait_for(timeout=10000)
        mobile.locator('.mobile-menu').click()
        mobile.locator('.nav-item').filter(has_text='Web Chat').click()
        mobile.locator('.site-card').wait_for(timeout=10000)
        mobile.wait_for_timeout(400)
        mobile.screenshot(path=str(OUT/'OSMANX_OMNICHAT_WORLD_mobile.png'),full_page=True)
        print('CHROMIUM_APP_AND_WIDGET_ROUNDTRIP=PASS')
        print('CHROMIUM_MOBILE_WEBSITE_PAGE=PASS')
        print('UNAUTHENTICATED_VISITOR_READ=401')
        print('JAVASCRIPT_ERRORS=',errors)
        assert not errors,errors
        context.close()
        browser.close()
