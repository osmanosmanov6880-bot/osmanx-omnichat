/* Isolated visitor token; no external analytics, trackers or third-party cookies. */
(function () {
 'use strict';
 var key = decodeURIComponent(location.pathname.split('/').filter(Boolean).pop() || '');
 var tokenKey='omnichat-widget-token:'+key;
 var visitorToken='';
 var el = function (id) { return document.getElementById(id); };
 var msgContainer=el('messages');
 var pollTimer=null;
 var locale='ru';
 var ui={sub:'Мы готовы помочь',online:'На связи',intro:'Напишите нам, и команда ответит прямо здесь.',name:'Ваше имя (необязательно)',start:'Начать переписку',input:'Напишите сообщение...',safe:'Защищённая переписка',failed:'Нет связи. Попробуйте снова.',demo:'ДЕМОРЕЖИМ — только тестовые сообщения'};
 function updateText(){el('subtitle').textContent=ui.sub;document.querySelector('.online').lastChild.textContent=' '+ui.online;document.querySelector('.welcome p').textContent=ui.intro;document.querySelector('label[for=name]').textContent=ui.name;el('begin').firstChild.textContent=ui.start+' ';el('body').placeholder=ui.input;el('status').textContent=ui.safe;el('demo').textContent=ui.demo;}
 function status(value,error){el('status').textContent=value;el('status').classList.toggle('error',!!error);}
 async function api(path,opts){
  opts=opts||{};
  var headers={'Content-Type':'application/json'};
  if(visitorToken)headers['X-Widget-Session']=visitorToken;
  var res=await fetch('/api/public/widget/'+encodeURIComponent(key)+path,Object.assign({headers:headers,credentials:'omit',cache:'no-store'},opts));
  if(!res.ok)throw new Error('Не удалось отправить запрос: '+res.status);
  return res.json();
 }
 function showConversation(){el('welcome').hidden=true;el('messages').hidden=false;el('compose').hidden=false;}
 function time(ts){return new Date(ts*1000).toLocaleTimeString(locale,{hour:'2-digit',minute:'2-digit'});}
 var renderedIds='';
 var pendingSend=null;
 async function refresh(){
  if(!visitorToken)return;
  try{
   var result=await api('/messages');
   var signature=result.messages.map(function(m){return m.id;}).join('|');
   if(signature!==renderedIds){
    msgContainer.replaceChildren();
    result.messages.forEach(function(m){
     var bubble=document.createElement('div');bubble.className='bubble'+(m.direction==='in'?' mine':'');
     var p=document.createElement('p');p.textContent=m.body;
     var stamp=document.createElement('div');stamp.className='stamp';stamp.textContent=time(m.created_at)+(m.is_demo?' [ТЕСТ]':'');
     bubble.appendChild(p);bubble.appendChild(stamp);msgContainer.appendChild(bubble);
    });
    renderedIds=signature;
    el('chat').scrollTop=el('chat').scrollHeight;
   }
   var delivered=result.messages.filter(function(m){return m.direction==='out'&&m.delivery_status==='accepted';})
                                .map(function(m){return m.id;});
   if(delivered.length){try{await api('/receipts',{method:'POST',body:JSON.stringify({message_ids:delivered})});}
    catch(e){/* The next poll retries without claiming false delivery. */}}
   status(ui.safe,false);
  }catch(e){status(ui.failed,true);}
 }
 async function begin(){
  el('begin').disabled=true;
  try{
   var result=await api('/session',{method:'POST',body:JSON.stringify({name:el('name').value.trim()||'Посетитель сайта'})});
   visitorToken=result.visitor_token;
   sessionStorage.setItem(tokenKey,visitorToken);
   if(result.is_demo)el('demo').hidden=false;
   showConversation();await refresh();
   if(!pollTimer)pollTimer=setInterval(function(){if(!document.hidden)refresh();},3000);
  }catch(e){status(ui.failed,true);el('begin').disabled=false;}
 }
 async function send(){
  var body=el('body').value.trim();
  if(!body||!visitorToken)return;
  el('send').disabled=true;
  try{
   if(!pendingSend||pendingSend.body!==body){
    var array=new Uint8Array(16);crypto.getRandomValues(array);
    pendingSend={body:body,nonce:Array.prototype.map.call(array,function(v){return v.toString(16).padStart(2,'0');}).join('')};
   }
   await api('/messages',{method:'POST',body:JSON.stringify({body:body,client_nonce:pendingSend.nonce})});
   pendingSend=null;
   el('body').value='';await refresh();status(ui.safe,false);
  }catch(e){status('Не удалось подтвердить отправку. Повторите — дубля не будет.',true);}
  finally{el('send').disabled=false;el('body').focus();}
 }
 async function boot(){
  updateText();
  try{
   var info=await api('/bootstrap');
   document.title=info.company+' | Онлайн-поддержка';el('company').textContent=info.company;
   el('greeting').textContent=info.greeting;
   document.documentElement.style.setProperty('--accent',info.accent);
   if(info.is_demo)el('demo').hidden=false;
   visitorToken=sessionStorage.getItem(tokenKey)||'';
   if(visitorToken){try{await api('/messages');showConversation();await refresh();pollTimer=setInterval(function(){if(!document.hidden)refresh();},3000);}catch(e){visitorToken='';sessionStorage.removeItem(tokenKey);}}
  }catch(e){status(ui.failed,true);}
 }
 el('begin').addEventListener('click',begin);
 el('send').addEventListener('click',send);
 el('body').addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
 boot();
}());
