"""V1.0 interactive UI smoke test with real FastAPI and mocked provider HTTP.

No live provider calls are made, and the preview is not evidence of delivery.
"""
import os
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ['DATABASE_URL'] = 'sqlite:///' + str(Path(tempfile.mkdtemp(prefix='omni-v10-')) / 'ui.db')
os.environ['ENABLE_OUTBOX_WORKER'] = 'false'
os.environ['ENABLE_AVITO_POLLING'] = 'false'
os.environ['COOKIE_SECURE'] = 'false'
os.environ['PUBLIC_BASE_URL'] = 'https://omnichat.example'
os.environ['INTEGRATION_ENCRYPTION_KEY'] = __import__('cryptography.fernet', fromlist=['Fernet']).Fernet.generate_key().decode()

import app.integrations.adapters as adapter_mod
import app.integrations.subscription_check as subscription_mod
from fastapi.testclient import TestClient
from app.main import app

async def provider_http(method, url, **kwargs):
    if url.endswith('/getMe'):
        return {'ok': True, 'result': {'id': 182736, 'username': 'private_demo_bot', 'is_bot': True}}
    if url.endswith('/getWebhookInfo'):
        return {'ok': True, 'result': {'url': 'https://omnichat.example/api/webhooks/telegram/' + CHANNEL_ID,
                                         'pending_update_count': 0}}
    raise AssertionError('Unexpected provider HTTP method: ' + method + ' ' + url)

adapter_mod.call = provider_http
subscription_mod.call = provider_http

with TestClient(app) as api:
    r = api.post('/api/auth/register', json={'company':'Workspace demo', 'name':'Owner',
        'email':'v10-preview-owner@example.com', 'password':'StrongUniquePassword!2026'})
    assert r.status_code == 201, r.text
    csrf = api.cookies.get('omnichat_csrf')
    r = api.post('/api/integrations/bots', headers={'X-CSRF-Token':csrf},
        json={'provider':'telegram','access_token':'182736:fake-test-bot-token'})
    assert r.status_code == 201, r.text
    CHANNEL_ID = r.json()['id']

    def bridge(payload):
        path = payload['url']
        assert path.startswith('/api/'), path
        response = api.request(payload.get('method', 'GET'), path,
            headers={'X-CSRF-Token':csrf,'Content-Type':'application/json'},
            content=(payload.get('body') or '').encode() if payload.get('body') else None)
        return {'status':response.status_code, 'body':response.text}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width, height, label in [(1512, 950, 'desktop'), (390, 844, 'mobile'), (320, 700, 'phone320')]:
            page = browser.new_page(viewport={'width':width, 'height':height},device_scale_factor=1)
            errors = []
            page.on('pageerror',lambda err:errors.append(str(err)))
            page.expose_function('bridgeOmni', bridge)
            page.set_content('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
            page.evaluate('''(csrf)=>{
                const memory={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memory[k]||null,setItem:(k,v)=>memory[k]=v}});
                Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf='+csrf,set:()=>true});
                window.history.replaceState=()=>{};
                window.fetch=async(url,opts={})=>{const r=await window.bridgeOmni({url:String(url),method:opts.method||'GET',body:opts.body||null});return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})};
            }''',csrf)
            page.add_style_tag(path=str(ROOT/'frontend/public/styles.css'))
            for script in ['vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js']:
                page.add_script_tag(path=str(ROOT/'frontend/public'/script))
            page.locator('.nav-item').first.wait_for(timeout=15000)
            if width < 700:
                page.locator('.quiet-mobile-menu').first.click()
                page.locator('.sidebar.open').wait_for(timeout=5000)
            page.locator('.quiet-nav .nav-item').nth(3).click()
            page.locator('.integration-card').first.wait_for(timeout=10000)
            if width > 700:
                page.locator('.onboarding-actions button').first.click()
                page.locator('.onboarding-diagnostics').wait_for(timeout=9000)
                assert page.locator('.channel-step.is-complete').count() == 2
                assert page.locator('.channel-step.is-pending').count() == 2
                assert page.locator('.onboarding-diagnostics').get_by_text('API',exact=False).count() > 0
            page.wait_for_timeout(350)
            overflow = page.evaluate('document.documentElement.scrollWidth-window.innerWidth')
            assert overflow <= 0, f'horizontal overflow on {width}px: {overflow}'
            assert not errors, errors
            path = ROOT / 'docs' / f'preview-v10-connector-{label}.png'
            page.screenshot(path=str(path),full_page=False)
            print('UI_OK',label,'saved',path)
            page.close()
        browser.close()
