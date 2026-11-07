"""Offline Chromium E2E using real API handlers and actual compiled React/widget scripts.

The page's transport is bridged to an in-process FastAPI TestClient because
outbound networking may be disabled. No simulated API responses. The result
is a browser-level functional test, NOT public production network verification.
"""
import os,re,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['ENABLE_OUTBOX_WORKER']='false'
os.environ['ENABLE_AVITO_POLLING']='false'
os.environ['DATABASE_URL']='sqlite:////tmp/omnichat-v04-browser-verify.db'
from app.main import app

OUT=Path(os.environ.get('OMNICHAT_E2E_OUT','/mnt/data'))
OUT.mkdir(parents=True,exist_ok=True)
public=ROOT/'frontend'/'public'
HTML='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"/></head><body><div id="root"></div></body></html>'
JS='''(function(){
 const memo={};
 Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memo[k]||null,setItem:(k,v)=>memo[k]=v,removeItem:k=>delete memo[k]}});
 Object.defineProperty(window,'sessionStorage',{configurable:true,value:{getItem:k=>memo[k]||null,setItem:(k,v)=>memo[k]=v,removeItem:k=>delete memo[k]}});
 Object.defineProperty(document,'cookie',{configurable:true,get:()=> 'omnichat_csrf=CSRF_VALUE',set:()=>true});
 window.history.replaceState=()=>{};
 window.fetch=async function(url,opts={}){
   const r=await window.__apiBridge(String(url),{method:opts.method||'GET',headers:opts.headers||{},body:opts.body||null});
   return new Response(JSON.stringify(r.data),{status:r.status,headers:{'Content-Type':'application/json'}})
 };
}())'''

def bridge(client):
 def callback(source,url,opts=None):
  opts=opts or {}
  path=str(url).replace('http://127.0.0.1:8765','').replace('https://omnichat.example','')
  result=client.request(opts.get('method','GET'),path,content=opts.get('body'),headers=opts.get('headers') or {},follow_redirects=False)
  try:payload=result.json()
  except Exception:payload={'detail':result.text[:250]}
  return {'status':result.status_code,'data':payload}
 return callback

def setup_page(context,api,csrf,viewport=None,widget=False):
 page=context.new_page()
 if viewport:page.set_viewport_size(viewport)
 page.expose_binding('__apiBridge',bridge(api))
 page.set_content((public/'widget.html').read_text() if widget else HTML)
 page.evaluate(JS.replace('CSRF_VALUE',csrf))
 page.add_style_tag(path=str(public/('widget.css' if widget else 'styles.css')))
 if not widget:
  for file in ['vendor/react.production.min.js','vendor/react-dom.production.min.js','vendor/react-fragment-polyfill.js','app.js']:
   page.add_script_tag(path=str(public/file))
 return page

with TestClient(app) as api:
 assert api.post('/api/demo/start').status_code==200
 csrf=api.cookies.get('omnichat_csrf')
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  context=browser.new_context(viewport={'width':1600,'height':1000},device_scale_factor=1)
  errors=[]
  page=setup_page(context,api,csrf)
  page.on('pageerror',lambda err:errors.append('DESKTOP:'+str(err)))
  page.on('console',lambda msg:errors.append('DESKTOP:'+msg.text) if msg.type=='error' else None)
  page.locator('.inbox-list').wait_for()
  page.get_by_role('button',name='Центр управления').click()
  page.locator('.command-page .queue-item').first.wait_for(timeout=10000)
  assert page.locator('.command-page h1').inner_text().replace('\n',' ').startswith('Каждое обращение')
  page.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V04_РЕФЕРЕНС_ПАНЕЛЬ.png'),full_page=True)
  page.get_by_role('button',name='Светлая тема').click()
  assert page.evaluate("document.body.classList.contains('light')")
  page.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V04_СВЕТЛАЯ_ТЕМА.png'),full_page=False)
  page.get_by_role('button',name='Тёмная тема').click()
  assert not page.evaluate("document.body.classList.contains('light')")

  page.get_by_role('button',name='Сообщения').first.click()
  page.locator('.conversation-card').first.wait_for()
  row=page.locator('.conversation-card').first
  row.click()
  priority=page.get_by_label('Приоритет',exact=True)
  assert priority.count()==1
  priority.select_option('high')
  page.wait_for_timeout(200)
  assert priority.input_value()=='high'
  page.get_by_role('button',name='Сохранить фильтр').click()
  page.get_by_label('Название подборки').fill('Мои важные')
  page.get_by_role('button',name='Сохранить подборку').click()
  page.get_by_role('button',name='Мои важные').wait_for()
  page.get_by_label('Фильтр по приоритету').select_option('high')
  assert page.get_by_label('Фильтр по приоритету').input_value()=='high'
  page.get_by_role('button',name='Мои важные').click()
  assert page.get_by_label('Фильтр по приоритету').input_value()==''
  page.locator('.conversation-card').first.click()
  page.locator('.message-bubble').first.wait_for(timeout=10000)
  page.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V04_РЕФЕРЕНС_СООБЩЕНИЯ.png'),full_page=False)

  # Another real first-party channel, all Russian in visitor interface.
  page.get_by_role('button',name='Чат для сайтов').first.click()
  page.locator('.site-form').wait_for()
  labels=page.locator('.site-form label')
  labels.nth(0).locator('input').fill('Поддержка интернет-магазина')
  labels.nth(1).locator('textarea').fill('http://localhost:3000')
  page.get_by_role('button',name='Создать канал сайта').click()
  page.locator('.site-card').first.wait_for(timeout=10000)
  snippet=page.locator('.site-embed pre').first.inner_text()
  key=re.search(r'data-omnichat-key="([A-Za-z0-9_-]+)"',snippet).group(1)
  page.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V04_РЕФЕРЕНС_САЙТЫ.png'),full_page=True)

  visitor=setup_page(context,api,csrf,{'width':390,'height':690},widget=True)
  visitor.on('pageerror',lambda err:errors.append('WIDGET:'+str(err)))
  script=(public/'widget-client.js').read_text().replace("var key = decodeURIComponent(location.pathname.split('/').filter(Boolean).pop() || '');",'var key = '+repr(key)+';')
  visitor.add_script_tag(content=script)
  visitor.locator('#company').wait_for()
  assert 'Начать переписку' in visitor.locator('#begin').inner_text()
  visitor.get_by_placeholder('Ваше имя').fill('Покупатель')
  visitor.locator('#begin').click()
  visitor.locator('#body').fill('Здравствуйте! Нужна помощь с заказом.')
  visitor.locator('#send').click()
  visitor.locator('.bubble.mine').first.wait_for(timeout=10000)
  page.get_by_role('button',name='Сообщения').first.click()
  page.locator('.conversation-card').filter(has_text='Покупатель').first.wait_for(timeout=10000)
  page.locator('.conversation-card').filter(has_text='Покупатель').first.click()
  page.get_by_label('Текст ответа').fill('Здравствуйте! Мы уже проверяем ваш заказ.')
  page.locator('.send-btn').click()
  visitor.locator('.bubble').filter(has_text='Мы уже проверяем').wait_for(timeout=14000)
  visitor.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V04_РЕФЕРЕНС_ВИДЖЕТ.png'),full_page=True)
  assert api.get('/api/public/widget/'+key+'/messages').status_code==401

  # Responsive dashboard, actual browser layout and two-way navigation.
  mobile=setup_page(context,api,csrf,{'width':390,'height':844})
  mobile.on('pageerror',lambda err:errors.append('MOBILE:'+str(err)))
  mobile.locator('.inbox-list').wait_for(timeout=10000)
  mobile.locator('.mobile-menu').click()
  mobile.get_by_role('button',name='Центр управления').click()
  mobile.locator('.command-page').wait_for()
  mobile.wait_for_timeout(250)
  # Take the above-fold mobile dashboard reference and a full-page version.
  mobile.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V04_РЕФЕРЕНС_МОБИЛЬНЫЙ.png'),full_page=True)
  horizontal=mobile.evaluate('document.documentElement.scrollWidth - window.innerWidth')
  assert horizontal<=2, f'Mobile has {horizontal}px unexpected horizontal overflow'
  mobile.locator('.queue-item').first.click()
  mobile.locator('.chat-pane').wait_for()
  try:
   mobile.get_by_label('Текст ответа').wait_for(timeout=12000)
  except Exception:
   print('MOBILE_DEBUG',mobile.locator('.chat-pane').inner_text()[:800], 'JSERRORS',errors)
   mobile.screenshot(path=str(OUT/'mobile_error_debug.png'),full_page=False)
   raise
  assert mobile.get_by_label('Текст ответа').count()==1
  mobile.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V04_РЕФЕРЕНС_МОБИЛЬНЫЙ_ЧАТ.png'),full_page=False)
  mobile.set_viewport_size({'width':320,'height':760})
  mobile.wait_for_timeout(120)
  mobile.screenshot(path=str(OUT/'OSMANX_OMNICHAT_V04_МОБИЛЬНЫЙ_320.png'),full_page=False)
  narrow_overflow=mobile.evaluate('document.documentElement.scrollWidth - window.innerWidth')
  assert narrow_overflow<=2, f'320px mobile overflow {narrow_overflow}px'
  assert not errors,errors
  print('V04 REAL-BACKEND CHROMIUM: desktop command, priority, saved views, visitor roundtrip, responsive mobile: PASS')
  print('JS errors:',errors)
  print('Mobile overflow:',horizontal)
  browser.close()
