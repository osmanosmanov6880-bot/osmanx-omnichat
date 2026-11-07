"""0.5 actual React + real FastAPI via in-process TestClient transport, not fake API responses."""
import os,sys,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp(prefix='omni-v05-browser-'))/'browser.db')
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
from app.main import app
OUT=Path(os.environ.get('OMNICHAT_E2E_OUT','/mnt/data'))
OUT.mkdir(parents=True,exist_ok=True)
public=ROOT/'frontend'/'public'
JS='''(function(){
 const memo={};
 Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memo[k]||null,setItem:(k,v)=>memo[k]=v,removeItem:k=>delete memo[k]}});
 Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf=CSRF_VALUE',set:()=>true});
 window.history.replaceState=()=>{};
 window.fetch=async function(url,opts={}){const r=await window.__apiBridge(String(url),{method:opts.method||'GET',headers:opts.headers||{},body:opts.body||null});return new Response(JSON.stringify(r.data),{status:r.status,headers:{'Content-Type':'application/json'}})};
}())'''

def make_page(context,client,csrf,viewport):
 page=context.new_page()
 page.set_viewport_size(viewport)
 def bridge(source,url,opts=None):
  opts=opts or {}
  response=client.request(opts.get('method','GET'),str(url),content=opts.get('body'),headers=opts.get('headers') or {},follow_redirects=False)
  try:data=response.json()
  except Exception:data={'detail':response.text[:150]}
  return {'status':response.status_code,'data':data}
 page.expose_binding('__apiBridge',bridge)
 page.set_content('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1" /></head><body><div id="root"></div></body></html>')
 page.evaluate(JS.replace('CSRF_VALUE',csrf))
 page.add_style_tag(path=str(public/'styles.css'))
 for f in ('vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js'):
  page.add_script_tag(path=str(public/f))
 return page

with TestClient(app) as api:
 assert api.post('/api/demo/start').status_code==200
 csrf=api.cookies.get('omnichat_csrf')
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  context=browser.new_context(device_scale_factor=1)
  errors=[]
  desktop=make_page(context,api,csrf,{'width':1512,'height':920})
  desktop.on('pageerror',lambda e:errors.append('DESKTOP:'+str(e)))
  desktop.locator('.inbox-list').wait_for(timeout=10000)
  assert desktop.locator('.conversation-card').count()==8
  assert desktop.locator('.inbox-quick-controls').is_visible()
  assert not desktop.locator('.saved-views').is_visible()
  desktop.locator('.conversation-card').first.click()
  desktop.locator('.message-bubble').first.wait_for()
  assert not desktop.locator('.details-pane').is_visible()
  desktop.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V05_FOCUS_INBOX.png'),full_page=False)
  desktop.get_by_role('button',name='Клиент',exact=True).click()
  assert desktop.locator('.details-pane').is_visible()
  desktop.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V05_CUSTOMER_DRAWER.png'),full_page=False)
  desktop.get_by_role('button',name='Закрыть информацию о клиенте').click()
  assert not desktop.locator('.details-pane').is_visible()
  desktop.get_by_label('Показать канал').select_option('telegram')
  desktop.locator('.conversation-card').first.wait_for()
  assert desktop.locator('.conversation-card').count()==1
  desktop.locator('.conversation-card').first.click()
  desktop.get_by_label('Текст ответа').fill('Здравствуйте! Ответ из единого OSMANX OMNICHAT (демо)')
  desktop.locator('.send-btn').click()
  desktop.get_by_text('Здравствуйте! Ответ из единого OSMANX OMNICHAT (демо)',exact=True).wait_for(timeout=10000)
  desktop.get_by_role('button',name='Ещё разделы').click()
  desktop.get_by_role('button',name='Интеграции').click()
  desktop.locator('.integration-card').first.wait_for()
  assert desktop.locator('.integration-card').count()==6
  desktop.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V05_CHANNELS.png'),full_page=False)
  mobile=make_page(context,api,csrf,{'width':390,'height':844})
  mobile.on('pageerror',lambda e:errors.append('MOBILE:'+str(e)))
  mobile.locator('.conversation-card').first.wait_for()
  mobile.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V05_MOBILE_LIST.png'),full_page=False)
  mobile.locator('.conversation-card').first.click()
  mobile.get_by_label('Текст ответа').wait_for()
  mobile.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V05_MOBILE_CHAT.png'),full_page=False)
  assert mobile.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=2
  mobile.locator('.customer-toggle').click()
  assert mobile.locator('.details-pane').is_visible()
  mobile.get_by_role('button',name='Закрыть информацию о клиенте').click()
  assert not mobile.locator('.details-pane').is_visible()
  mobile.set_viewport_size({'width':320,'height':720})
  mobile.wait_for_timeout(140)
  assert mobile.evaluate('document.documentElement.scrollWidth-window.innerWidth')<=2
  assert not errors,errors
  print('V0.5 focus Inbox and 6-channel demo E2E: PASS. Chromium desktop and mobile, 320px overflow: 0, no page JS errors.')
  browser.close()
