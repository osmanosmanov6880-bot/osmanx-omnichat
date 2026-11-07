declare const React:any;
declare const ReactDOM:any;

const glyphs:any = {
 inbox:'M21 8v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8m0 0 5-5h8l5 5m-18 0h5l2 3h4l2-3h5',
 users:'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m14-18a4 4 0 0 1 0 8m6 10v-2a4 4 0 0 0-3-3.87M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
 chart:'M3 3v18h18M7 16v-5m5 5V7m5 9v-8',
 flow:'M12 3h7a2 2 0 0 1 2 2v7m-9-9V1m0 2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3M8 12h8M12 8v8',
 plug:'M12 22v-5m-4-7V2m8 8V2M7 10h10v3a5 5 0 0 1-10 0v-3Z',
 globe:'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm-10 10h20m-10-10c-6 5-6 15 0 20m0-20c6 5 6 15 0 20',
 activity:'M3 12h5l3-8 4 16 3-8h3',
 layout:'M3 3h18v18H3zM9 3v18m0-12h12',
 bookmark:'M5 3h14v19l-7-5-7 5V3Z',
 flag:'M4 22V4m0 1c6-4 10 4 16 0v11c-6 4-10-4-16 0',
 layers:'M12 2 2 7l10 5 10-5-10-5Zm-10 10 10 5 10-5M2 17l10 5 10-5',
 settings:'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm7.4-1a1.9 1.9 0 0 0 .4 2.1l-1.7 1.7a1.9 1.9 0 0 0-2.1-.4 1.9 1.9 0 0 0-1 1.8V21h-2.4v-1.8a1.9 1.9 0 0 0-1-1.8 1.9 1.9 0 0 0-2.1.4l-1.7-1.7a1.9 1.9 0 0 0 .4-2.1 1.9 1.9 0 0 0-1.8-1H4v-2.4h1.8a1.9 1.9 0 0 0 1.8-1 1.9 1.9 0 0 0-.4-2.1l1.7-1.7a1.9 1.9 0 0 0 2.1.4 1.9 1.9 0 0 0 1-1.8V3h2.4v1.8a1.9 1.9 0 0 0 1 1.8 1.9 1.9 0 0 0 2.1-.4l1.7 1.7a1.9 1.9 0 0 0-.4 2.1 1.9 1.9 0 0 0 1.8 1H21v2.4h-1.8a1.9 1.9 0 0 0-1.8 1Z',
 search:'M21 21l-4.35-4.35M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z',
 send:'m22 2-7 20-4-9-9-4 20-7ZM22 2 11 13',
 plus:'M12 5v14M5 12h14',
 bell:'M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4',
 pin:'m16 3 5 5m-6 4 4-4-4-4-7 7v3l-4 4m10-6-6-6M8 13l3 3',
 arrow:'M5 12h14m-7-7 7 7-7 7',
 back:'M19 12H5m7 7-7-7 7-7',
 logout:'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4m7 14 5-5-5-5m5 5H9',
 chevron:'m6 9 6 6 6-6',
 close:'M18 6 6 18M6 6l12 12',
 check:'M20 6 9 17l-5-5',
 note:'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Zm0 0v6h6M8 13h8m-8 4h8',
 moon:'M20 15.5A8 8 0 0 1 8.5 4 8 8 0 1 0 20 15.5Z',
 sun:'M12 2v2m0 16v2M2 12h2m16 0h2m-4.9-7.1 1.4-1.4M4.5 19.5l1.4-1.4M4.5 4.5l1.4 1.4m11.2 11.2 1.4 1.4M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z',
 filter:'M4 7h16M7 12h10m-7 5h4',
 briefcase:'M3 7h18v13H3V7Zm5 0V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18',
 clock:'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm0 5v5l3 2',
 shield:'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z',
 info:'M12 18v-6m0-4h.01M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Z',
 sparkles:'m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3ZM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z',
 menu:'M4 6h16M4 12h16M4 18h16',
 copy:'M8 4h11a2 2 0 0 1 2 2v12M5 8h10a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2Z'
};
function Icon({name,size=18}:any){return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={glyphs[name]||glyphs.info}/></svg>}
function fmt(ts:any){if(!ts)return '—';return new Date(ts*1000).toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'})}
function dateFmt(ts:any){if(!ts)return '—';return new Date(ts*1000).toLocaleDateString('ru-RU',{day:'numeric',month:'short'})}
function formatMoney(value:number,currency:string='RUB'){try{return new Intl.NumberFormat('ru-RU',{style:'currency',currency:currency||'RUB',maximumFractionDigits:0}).format(Number(value||0))}catch(e){return Number(value||0).toLocaleString('ru-RU')+' '+currency}}
function initials(name:any){return (name||'?').split(' ').slice(0,2).map((v:string)=>v[0]).join('').toUpperCase()}
function avatarColor(name:any){let h=0;for(let ch of name||'')h=((h<<5)-h)+ch.charCodeAt(0);return `hsl(${Math.abs(h)%360} 38% 28%)`}
function Avatar({name,size=42}:any){return <div className="avatar" style={{width:size,height:size,background:avatarColor(name),fontSize:size*.31}} aria-hidden="true">{initials(name)}</div>}
function outgoingLimit(type:string){return type==='instagram'?1000:type==='avito'?1000:4000}
function outgoingSize(type:string,text:string){return type==='instagram'?new TextEncoder().encode(text).length:text.length}
const DELIVERY_LABELS:any = {
 queued:'\u0412 \u043e\u0447\u0435\u0440\u0435\u0434\u0438',
 processing:'\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u044f\u0435\u0442\u0441\u044f',
 accepted:'\u041f\u0440\u0438\u043d\u044f\u0442\u043e API',
 sent:'\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e',
 delivered:'\u0414\u043e\u0441\u0442\u0430\u0432\u043b\u0435\u043d\u043e',
 read:'\u041f\u0440\u043e\u0447\u0438\u0442\u0430\u043d\u043e',
 uncertain:'\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c',
 failed:'\u041e\u0448\u0438\u0431\u043a\u0430',
 cancelled:'\u041e\u0442\u043c\u0435\u043d\u0435\u043d\u043e',
};
function inboundIssueLabel(error:string){return ({
 'encryption_key_unavailable':'Ключ шифрования недоступен: проверьте ключи перед восстановлением',
 'invalid_encrypted_event':'Событие повреждено: проверьте источник перед повтором',
 'worker_claim_expired':'Обработчик не завершил попытку: проверьте состояние сервера',
 'SyntheticFailure':'Тестовая ошибка обработки'
 } as any)[error]||'Ошибка обработки — требуется проверка'}
function deliveryLabel(status:string,provider:string=''){if(status==='accepted'&&provider==='website')return 'Ожидает подтверждения виджета';return DELIVERY_LABELS[status]||'\u041d\u0435 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u043e'}
function providerName(s:string){return ({avito:'Авито',instagram:'Instagram',whatsapp:'WhatsApp',telegram:'Telegram',vk:'ВКонтакте',max:'MAX',messenger:'Facebook Messenger',website:'Сайт'} as any)[s]||s}
function Provider({type,small=false}:any){
 const cls='provider '+type+(small?' small':'');
 let mark:any=null;
 if(type==='avito')mark=<span className="avito-mark"><i/><i/><i/><i/></span>;
 else if(type==='instagram')mark=<svg viewBox="0 0 30 30" aria-hidden="true"><rect x="5" y="5" width="20" height="20" rx="6" fill="none" stroke="white" strokeWidth="2.5"/><circle cx="15" cy="15" r="5.1" fill="none" stroke="white" strokeWidth="2.3"/><circle cx="21.3" cy="8.8" r="1.5" fill="white"/></svg>;
 else if(type==='whatsapp')mark=<svg viewBox="0 0 30 30" aria-hidden="true"><path d="M15 4a10.8 10.8 0 0 0-9 16.7L4 26l5.6-1.9A10.8 10.8 0 1 0 15 4Z" stroke="white" strokeWidth="2" fill="none"/><path d="M10.6 10.4c.6-1 1.3-1.1 1.8-.4l1.3 1.9-.8 1.2c1.1 2.1 2.4 3.2 4.5 4.1l1.2-.9 2.1 1.2c.6.4.6 1.2-.2 1.9-2.8 2.4-10.1-3.5-10.2-7.2 0-.7.1-1.2.3-1.8Z" fill="white"/></svg>;
 else if(type==='telegram')mark=<svg viewBox="0 0 30 30" aria-hidden="true"><path d="M4 14.2 25 6.5c1.2-.4 1.7.2 1.3 1.5l-3.8 17.1c-.3 1.2-1.1 1.4-2 0l-5.7-4.2-2.8 2.7-.1-5.2 10-9.1-12.2 7.8-5-1.5c-1.2-.4-1.3-.9-.7-1.4Z" fill="white"/></svg>;
 else if(type==='vk')mark=<span className="vk-mark">VK</span>;
 else if(type==='max')mark=<span className="max-mark">M</span>;
 else if(type==='messenger')mark=<span className="messenger-mark">↗</span>;
 else mark=<svg viewBox="0 0 30 30" aria-hidden="true"><path d="M6 6h18v14H14l-6 5v-5H6Z" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/><circle cx="11" cy="13" r="1.2"/><circle cx="15" cy="13" r="1.2"/><circle cx="19" cy="13" r="1.2"/></svg>;
 return <span className={cls} title={providerName(type)} aria-label={providerName(type)}>{mark}</span>;
}

const CHANNELS=['avito','instagram','whatsapp','telegram','vk','max','messenger','website'];
const PRIORITIES:any={urgent:'Срочно',high:'Высокий',normal:'Обычный',low:'Низкий'};
const STATUS:any={new:'Новый',in_progress:'В работе',waiting:'Ожидает',closed:'Закрыт'};
const STAGES:any={new:'Новый',interested:'Заинтересован',negotiation:'Переговоры',payment:'Оплата',success:'Успешно',lost:'Отказ'};
const NAV:any=[['command','layout','Центр управления'],['inbox','inbox','Входящие'],['contacts','users','Клиенты'],['analytics','chart','Аналитика'],['rules','flow','Автоматизация'],['integrations','plug','Интеграции'],['websites','globe','Чат для сайтов'],['operations','activity','Контроль доставки'],['team','users','Команда']];

function readableError(message:string){
 if(/Failed to fetch|NetworkError|fetch failed/i.test(message))return 'Не удалось связаться с OSMANX. Проверьте сеть и попробуйте снова — ваши сообщения не удалены.';
 if(/Another teammate is currently replying/i.test(message))return 'С этим клиентом сейчас работает коллега. Откройте другой диалог или повторите позже.';
 if(/Диалог уже изменился/i.test(message))return 'Пока вы писали, переписка обновилась. Текст ответа сохранён. Проверьте новые сообщения и отправьте снова.';
 if(/401|сессия истекла|не авторизован/i.test(message))return 'Сеанс завершён. Войдите снова, чтобы продолжить.';
 return message || 'Не удалось выполнить действие. Попробуйте ещё раз.';
}
function csrf(){const v=document.cookie.split('; ').find(x=>x.startsWith('omnichat_csrf='));return v?decodeURIComponent(v.split('=').slice(1).join('=')):''}
async function request(path:string,opts:any={}){
 const headers:any={'Content-Type':'application/json',...(opts.headers||{})};
 if(opts.method&&opts.method!=='GET')headers['X-CSRF-Token']=csrf();
 const response=await fetch('/api'+path,{credentials:'same-origin',...opts,headers});
 const data=await response.json().catch(()=>({detail:'Сервер вернул нечитаемый ответ'}));
 if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:`Ошибка ${response.status}`);
 return data;
}

class OmniApp extends React.Component {
 state:any={boot:true,me:null,view:new URLSearchParams(window.location.search).get('view')||'inbox',authMode:'demo',authCompany:'',authName:'',authEmail:'',authPassword:'',authError:'',loading:false,
 convs:[],selected:null,detail:null,search:'',channelFilter:'',statusFilter:'',priorityFilter:'',sortFilter:'recent',reply:'',note:'',tab:'info',activity:[],views:[],viewName:'',viewShared:false,command:null,team:[],sessions:null,contacts:[],analytics:null,rules:[],integrations:null,plans:null,
 toast:'',templates:[],alerts:null,archivedFilter:false,assignedFilter:'',privacy:null,templateName:'',templateBody:'',light:localStorage.getItem('omnichat_theme')==='light',mobilePane:'list',sidebarOpen:false,moreNav:false,advancedFilters:false,customerOpen:true,customerExtras:false,followupEditing:false,tagInput:'',tagEditing:false,showEmoji:false,showQuickReplies:false,chatActionsOpen:false,modal:'',connectToken:'',connectPhone:'',botProvider:'telegram',botGroupId:'',botConfirmation:'',botConnectedInfo:null,inviteEmail:'',inviteRole:'operator',inviteToken:'',
 integrationGuide:null,quickstart:null,focusedProvider:'',messengerPages:[],channelDiagnostics:null,channelDiagnosticsFor:'',connectWaba:'',newOrganization:'',rotateChannel:'',rotateToken:'',registerPhoneChannel:'',registrationPin:'',metaSession:null,
 ruleName:'',ruleCondition:'contains',ruleTerm:'',ruleAction:'tag',ruleActionValue:'VIP',demoInbound:'',contactDraft:null,sites:[],siteSelected:'',siteName:'',siteOrigins:'',siteGreeting:'Здравствуйте! Чем можем вам помочь?',siteAccent:'#90b7a7',localization:null,operations:null,operationsJobs:[],operationsInboundJobs:[],inboundHealth:null,inboundIntegrity:null,inboundRepairReason:'',inboundRepairConfirmed:false,inboundTriageStatus:'',inboundTriageCursor:null,
 inboundControlScope:'organization',inboundPauseAction:'pause',inboundPauseReason:'',
 inboundBatchChannel:'',inboundBatchReason:'',inboundBatchPreview:null,inboundRetryJob:null,inboundRetryReason:'',inboundDismissJob:null,inboundDismissReason:'',inboundDismissCode:'unrecoverable',inboundDismissConfirmed:false,reconcileJob:null,reconcileStatus:'accepted',reconcileEvidence:'',reconcileExternalId:'',outboxRetryJob:null,outboxRetryEvidence:'',outboxRetryVerified:false,
 dispatchPauses:null,deliveryTelemetry:null,opsPauseReason:'incident',opsPauseMinutes:'60',opsPauseChannel:'',selectedJobEvents:null,
 waTemplates:[],waConsent:false,waSelected:'',waParams:[],waConsentSource:'',waConsentCheckbox:false,waLoading:false,olderLoading:false};
 timer:any=null;searchTimer:any=null;toastTimer:any=null;ws:any=null;reconnectTimer:any=null;metaFlow:any=null;historyLoading:boolean=false;
 // Draft text lives in memory only. It is never written to browser storage or sent to the server before Send.
 drafts:any={};pendingSend:any={};sending:boolean=false;
 componentDidMount(){document.body.classList.toggle('light',this.state.light);window.addEventListener('message',this.metaMessage);this.boot();this.timer=setInterval(()=>this.tick(),7000);document.addEventListener('keydown',this.handleHotkey)}
 handleHotkey=(e:any)=>{
  if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){
   e.preventDefault();if(this.state.view!=='inbox')this.changeView('inbox');
   setTimeout(()=>document.querySelector<HTMLInputElement>('[aria-label="Поиск по перепискам"]')?.focus(),100);return;
  }
  if(e.key==='Escape'){this.setState({modal:'',sidebarOpen:false});return;}
  if((e.metaKey||e.ctrlKey)&&e.key==='1'){e.preventDefault();this.changeView('command');return;}
  if((e.metaKey||e.ctrlKey)&&e.key==='2'){e.preventDefault();this.changeView('inbox');return;}
  const target=e.target as HTMLElement;
  if(target&&['INPUT','TEXTAREA','SELECT'].includes(target.tagName))return;
  if(this.state.view==='inbox'&&!e.metaKey&&!e.ctrlKey&&['j','k'].includes(e.key)){
    const rows=this.state.convs;const current=rows.findIndex((c:any)=>c.id===this.state.selected);
    const index=e.key==='j'?Math.min(rows.length-1,current+1):Math.max(0,current-1);
    if(rows[index]){e.preventDefault();this.select(rows[index].id);}
  }
 }
 componentWillUnmount(){document.removeEventListener('keydown',this.handleHotkey);if(this.timer)clearInterval(this.timer);if(this.searchTimer)clearTimeout(this.searchTimer);if(this.toastTimer)clearTimeout(this.toastTimer);if(this.reconnectTimer)clearTimeout(this.reconnectTimer);if(this.ws)this.ws.close();window.removeEventListener('message',this.metaMessage)}
 notify=(text:string)=>{this.setState({toast:readableError(text)});if(this.toastTimer)clearTimeout(this.toastTimer);this.toastTimer=setTimeout(()=>this.setState({toast:''}),4500)};
 boot=async()=>{try{const me=await request('/auth/me');this.setState({me,boot:false},()=>this.connectRealtime());
  const requested=this.state.view;
  const view=['owner','admin'].includes(me.role)||requested!=='start'?requested:'inbox';
  if(view!==requested)this.setState({view});
  await this.loadView(view);await this.loadShared();
  if(['owner','admin'].includes(me.role)&&view!=='start'){
   try{this.setState({quickstart:await request('/quickstart')})}catch(e){}
  }
 }catch(e){this.setState({me:null,boot:false})}};
 connectRealtime=()=>{
  if(!this.state.me||!['http:','https:'].includes(window.location.protocol)||!('WebSocket' in window))return;
  try{
   if(this.ws){this.ws.close();this.ws=null}
   const proto=location.protocol==='https:'?'wss:':'ws:';
   const socket=new WebSocket(proto+'//'+location.host+'/api/ws');this.ws=socket;
   socket.onmessage=(e:any)=>{try{const event=JSON.parse(e.data);if(event.event==='inbox.changed'){this.loadConvs(true);if(this.state.selected)this.loadDetail(this.state.selected,true)}}catch(err){}};
   socket.onclose=()=>{if(this.ws===socket&&this.state.me){this.reconnectTimer=setTimeout(()=>this.connectRealtime(),6500)}};
  }catch(e){}
 };
 tick=async()=>{if(!this.state.me||document.hidden)return;if(this.state.view==='inbox'){await this.loadConvs(true);if(this.state.selected)await this.loadDetail(this.state.selected,true);await this.loadAlerts()}};
 loadShared=async()=>{try{const [team,templates,alerts,views]=await Promise.all([request('/team'),request('/quick-replies'),request('/alerts'),request('/views')]);this.setState({team,templates,alerts,views})}catch(e:any){this.notify(e.message)}};
 loadAlerts=async()=>{try{this.setState({alerts:await request('/alerts')})}catch(e){}};
 saveTemplate=()=>this.run(async()=>{await request('/quick-replies',{method:'POST',body:JSON.stringify({title:this.state.templateName,body:this.state.templateBody})});this.setState({templateName:'',templateBody:''});this.setState({templates:await request('/quick-replies')});this.notify('Шаблон сохранён')});
 deleteTemplate=(id:string)=>this.run(async()=>{await request('/quick-replies/'+id,{method:'DELETE'});this.setState({templates:await request('/quick-replies')})});
 changeAvailability=(id:string,available:boolean)=>this.run(async()=>{await request('/team/'+id+'/availability',{method:'PATCH',body:JSON.stringify({available})});this.setState({team:await request('/team')})});
 syncAvito=(id:string)=>this.run(async()=>{const result=await request('/integrations/'+id+'/sync',{method:'POST'});await this.loadView('integrations');await this.loadConvs();this.notify('Авито: получено '+result.new_inbound_messages+' новых сообщений')});
 savePrivacy=()=>this.run(async()=>{await request('/organization/privacy',{method:'PATCH',body:JSON.stringify({retention_days:Number(this.state.privacy.retention_days),sla_minutes:Number(this.state.privacy.sla_minutes)})});this.notify('Политика хранения и SLA обновлены')});
 saveLocalization=()=>this.run(async()=>{const data=await request('/organization/localization',{method:'PATCH',body:JSON.stringify({currency:this.state.localization.currency,timezone:this.state.localization.timezone})});this.setState({me:{...this.state.me,organization:{...this.state.me.organization,...data}}});this.notify('Региональные настройки сохранены')});
 pauseDispatch=()=>{
  const s=this.state;const channel_id=s.opsPauseChannel||null;
  const scope=channel_id?'выбранного аккаунта':'всей компании';
  if(!window.confirm('Временно остановить НОВЫЕ внешние отправки '+scope+'? Уже начатый запрос к площадке может завершиться.'))return;
  this.run(async()=>{
   await request('/operations/dispatch-pauses',{method:'POST',body:JSON.stringify({channel_id,reason_code:s.opsPauseReason,minutes:s.opsPauseMinutes==='unlimited'?null:Number(s.opsPauseMinutes)})});
   await this.loadView('operations');this.notify('Временная пауза установлена. Входящие продолжают работать.');
  });
 };
 resumeDispatch=(channel_id:string|null)=>{
  if(!window.confirm('Снять временную паузу '+(channel_id?'этого аккаунта':'всей компании')+'? Убедитесь, что причина инцидента устранена.'))return;
  this.run(async()=>{await request('/operations/dispatch-pauses/resume',{method:'POST',body:JSON.stringify({channel_id})});await this.loadView('operations');this.notify('Временная пауза снята');});
 };
 exportSafeSupport=()=>this.run(async()=>{
  const data=await request('/operations/support-bundle');
  const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  const uri=URL.createObjectURL(blob);const el=document.createElement('a');
  try{el.href=uri;el.download='osmanx-omnichat-r36-support.json';document.body.appendChild(el);el.click();el.remove();}
  finally{URL.revokeObjectURL(uri)}
  this.notify('Отчёт сохранён без переписок и персональных данных');
 });
 loadJobEvents=(job_id:string)=>this.run(async()=>{
  const result=await request('/operations/delivery-events?job_id='+encodeURIComponent(job_id));
  this.setState({selectedJobEvents:{job_id,events:result.events,truncated:result.truncated}});
 });
 exportWorkspace=()=>this.run(async()=>{const data=await request('/organization/export');const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download='osmanx-omnichat-export.json';document.body.appendChild(link);link.click();link.remove();URL.revokeObjectURL(url);this.notify('Экспорт создан из ваших данных')});
 toggleNotifications=()=>{if(!('Notification' in window)){this.notify('Браузер не поддерживает уведомления');return}Notification.requestPermission().then(v=>this.notify(v==='granted'?'Уведомления разрешены':'Разрешение на уведомления не предоставлено'))};
 run=async(action:any)=>{try{this.setState({loading:true});await action()}catch(e:any){this.notify(e.message||'Ошибка запроса')}finally{this.setState({loading:false})}};
 login=()=>this.run(async()=>{const s=this.state;const endpoint=s.authMode==='register'?'/auth/register':s.authMode==='login'?'/auth/login':'/demo/start';
   const body=s.authMode==='register'?{company:s.authCompany,name:s.authName,email:s.authEmail,password:s.authPassword}:{email:s.authEmail,password:s.authPassword};
   await request(endpoint,{method:'POST',body:JSON.stringify(body)});
   const landing=s.authMode==='register'?'start':'inbox';
   this.setState({view:landing,selected:null});
   history.replaceState({},'',landing==='start'?'/?view=start':'/');
   await this.boot();this.notify(s.authMode==='demo'?'Демопространство создано. Все данные тестовые.':'Добро пожаловать в OMNICHAT');});
 loadSessions=()=>this.run(async()=>{const sessions=await request('/auth/sessions');this.setState({sessions})});
 revokeOtherSessions=()=>this.run(async()=>{const r=await request('/auth/sessions/revoke-others',{method:'POST'});this.notify('Сеансы на других устройствах завершены: '+r.revoked);this.setState({sessions:await request('/auth/sessions')})});
 revokeAllSessions=()=>this.run(async()=>{if(!window.confirm('Завершить сеансы на всех устройствах, включая это?'))return;await request('/auth/sessions/revoke-all',{method:'POST'});this.drafts={};this.pendingSend={};if(this.ws){this.ws.close();this.ws=null}if(this.reconnectTimer)clearTimeout(this.reconnectTimer);this.setState({me:null,selected:null,detail:null,reply:'',authMode:'login',quickstart:null,sessions:null});this.notify('Все сеансы завершены. Для продолжения войдите снова.')});
 logout=()=>this.run(async()=>{await request('/auth/logout',{method:'POST'});this.drafts={};this.pendingSend={};this.setState({me:null,selected:null,detail:null,reply:'',authMode:'login',quickstart:null});if(this.ws){this.ws.close();this.ws=null}if(this.reconnectTimer)clearTimeout(this.reconnectTimer)});
 loadView=async(view:string)=>{
  if(view==='start'){this.setState({quickstart:await request('/quickstart')});return}
  if(view==='command'){this.setState({command:await request('/command-center')});return}
  if(view==='inbox'){await this.loadConvs();return}
  if(view==='contacts'||view==='deals')this.setState({contacts:await request('/contacts')});
  if(view==='analytics')this.setState({analytics:await request('/analytics')});
  if(view==='rules')this.setState({rules:await request('/rules')});
  if(view==='integrations'){
    const [integrations,integrationGuide]=await Promise.all([request('/integrations'),request('/integrations/guide')]);
    let messengerPages:any[]=[];
    if(['owner','admin'].includes(this.state.me?.role)){
      try{messengerPages=(await request('/integrations/messenger/pages')).pages||[]}catch(e){}
    }
    const owned=integrations.connections.find((c:any)=>c.mode==='live'&&c.status!=='disconnected');
    this.setState({integrations,integrationGuide,messengerPages,
      focusedProvider:this.state.focusedProvider||owned?.provider||'telegram'});
  }
  if(view==='websites')this.setState({sites:await request('/website-widgets')});
  if(view==='operations'){
   const params=new URLSearchParams({limit:'30'});
   if(this.state.inboundTriageStatus)params.set('status',this.state.inboundTriageStatus);
   const [operations,operationsJobs,triage,inboundHealth,inboundIntegrity,dispatchPauses,deliveryTelemetry]=await Promise.all([
     request('/operations/overview'),request('/operations/outbox'),
     request('/operations/inbound/triage?'+params.toString()),request('/operations/inbound/health'),request('/operations/inbound/integrity'),
     request('/operations/dispatch-pauses'),request('/operations/delivery-telemetry')]);
   this.setState({operations,operationsJobs,operationsInboundJobs:triage.items,inboundHealth,inboundIntegrity,dispatchPauses,deliveryTelemetry,
                  inboundTriageCursor:triage.next_cursor});
  }
  if(view==='team')this.setState({team:await request('/team')});
  if(view==='settings'){this.setState({plans:await request('/plans')});if(['owner','admin'].includes(this.state.me?.role||'')){const [privacy,localization]=await Promise.all([request('/organization/privacy'),request('/organization/localization')]);this.setState({privacy,localization})}}
 };
 changeView=(view:string)=>this.run(async()=>{this.setState({view,sidebarOpen:false});history.replaceState({},'',view==='inbox'?'/':'/?view='+view);await this.loadView(view)});
 loadConvs=async(silent=false)=>{try{const s=this.state;const params=new URLSearchParams();if(s.search)params.set('q',s.search);if(s.channelFilter)params.set('channel',s.channelFilter);if(s.statusFilter)params.set('status',s.statusFilter);if(s.archivedFilter)params.set('archived','true');if(s.assignedFilter)params.set('assigned',s.assignedFilter);if(s.priorityFilter)params.set('priority',s.priorityFilter);if(s.sortFilter)params.set('sort',s.sortFilter);
 const convs=await request('/conversations?'+params.toString());if(silent&&this.state.convs.length){const old=new Map(this.state.convs.map((x:any)=>[x.id,x.unread_count]));const changed=convs.find((c:any)=>(old.get(c.id)===undefined&&c.unread_count>0)||(c.unread_count>(old.get(c.id)||0)));if(changed&&!s.me.organization.is_demo){this.notify('Новое обращение: '+changed.contact_name);if('Notification' in window&&Notification.permission==='granted')new Notification('OSMANX OMNICHAT',{body:changed.contact_name+' · '+providerName(changed.channel)})}}this.setState({convs});if(!this.state.selected&&convs.length&&!silent)this.select(convs[0].id,window.innerWidth<=680)}catch(e:any){if(!silent)this.notify(e.message)}};
 loadDetail=async(id:string,silent=false)=>{try{
 const d=await request('/conversations/'+encodeURIComponent(id));
 if(this.state.selected!==id)return;
 const current=this.state.detail;
 const scroller=this.chatScroll;
 const wasAtBottom=!!scroller && scroller.scrollHeight-scroller.scrollTop-scroller.clientHeight<90;
 if(current?.conversation?.id===id){
  const byId=new Map((current.messages||[]).map((m:any)=>[m.id,m]));
  for(const m of d.messages)byId.set(m.id,m);
  d.messages=Array.from(byId.values()).sort((a:any,b:any)=>a.created_at-b.created_at||(a.id<b.id?-1:a.id>b.id?1:0));
  d.message_paging=current.message_paging||d.message_paging;
 }
 this.setState({detail:d,contactDraft:this.state.contactDraft&&this.state.contactDraft.id===d.contact.id?this.state.contactDraft:{...d.contact}},()=>{
  if(this.chatScroll&&(!current||wasAtBottom))this.chatScroll.scrollTop=this.chatScroll.scrollHeight;
 });
 return d; // Allows read receipt to use the exact visible snapshot version.
 }catch(e:any){if(!silent)this.notify(e.message);return null}};
 loadOlderMessages=async()=>{
  const d=this.state.detail, id=d?.conversation?.id;
  const cursor=d?.message_paging?.next_before;
  if(!id||!cursor||this.historyLoading)return;
  this.historyLoading=true;this.setState({olderLoading:true});
  const scroller=this.chatScroll;
  const priorHeight=scroller?.scrollHeight||0,priorTop=scroller?.scrollTop||0;
  try{
   const page=await request('/conversations/'+encodeURIComponent(id)+'/messages?'+new URLSearchParams({before:cursor,limit:'120'}));
   if(this.state.selected!==id||this.state.detail?.conversation?.id!==id)return;
   const latest=this.state.detail;
   const byId=new Map(page.messages.map((m:any)=>[m.id,m]));
   for(const m of latest.messages)byId.set(m.id,m);
   const messages=Array.from(byId.values()).sort((a:any,b:any)=>a.created_at-b.created_at||(a.id<b.id?-1:a.id>b.id?1:0));
   this.setState({detail:{...latest,messages,message_paging:page.message_paging}},()=>{
    if(this.chatScroll===scroller&&scroller){scroller.scrollTop=priorTop+scroller.scrollHeight-priorHeight;}
   });
  }catch(e:any){this.notify(readableError(e.message));}
  finally{this.historyLoading=false;this.setState({olderLoading:false});}
 };
 select=(id:string,autoMobile=false)=>{
   const previous=this.state.selected;
   if(previous&&this.state.reply.trim())this.drafts[previous]=this.state.reply;
   this.setState({selected:id,detail:null,olderLoading:false,tab:'info',activity:[],mobilePane:autoMobile?'list':'chat',customerOpen:window.innerWidth>=1260,customerExtras:false,followupEditing:false,tagEditing:false,showEmoji:false,showQuickReplies:false,chatActionsOpen:false,reply:this.drafts[id]||''},()=>this.run(async()=>{
    const loaded=await this.loadDetail(id);
    if(autoMobile||!loaded||this.state.selected!==id)return;
    let changedWhileReading=false;
    try{
      const seen=await request(`/conversations/${id}/read`,{method:'POST',body:JSON.stringify({expected_version:loaded.conversation.version})});
      if(this.state.selected===id){
       if(this.state.detail?.conversation?.version===loaded.conversation.version){
        const d=this.state.detail;
        this.setState({detail:{...d,conversation:{...d.conversation,version:seen.version,unread_count:0}}});
       }else await this.loadDetail(id,true);
      }
    }catch(e:any){
      // Concurrent inbound messages must remain unread; show the new state.
      changedWhileReading=true;
      if(this.state.selected===id){await this.loadDetail(id,true);this.notify('Появилось новое сообщение — оно осталось непрочитанным.');}
    }
    // The conflict already informed this operator. Suppress a second, generic
    // "new conversation" toast that would hide the more useful explanation.
    await this.loadConvs(!changedWhileReading);
   }));
  };
 loadActivity=async(id:string)=>{try{const activity=await request('/conversations/'+id+'/activity');if(this.state.selected===id)this.setState({activity})}catch(e:any){this.notify(e.message)}};
 setPriority=(priority:string)=>{const d=this.state.detail;if(!d)return;this.run(async()=>{
  const updated=await request('/conversations/'+d.conversation.id+'/priority',{method:'PATCH',body:JSON.stringify({priority,expected_version:d.conversation.version})});
  this.setState({detail:{...d,conversation:updated}});await this.loadConvs(true);await this.loadActivity(d.conversation.id);
  this.notify('Приоритет диалога изменён');
 })};
 createSavedView=()=>this.run(async()=>{
  const s=this.state;const filters:any={channel:s.channelFilter,status:s.statusFilter,priority:s.priorityFilter,assigned:s.assignedFilter,archived:s.archivedFilter,sort:s.sortFilter};
  const created=await request('/views',{method:'POST',body:JSON.stringify({name:s.viewName,shared:s.viewShared,filters})});
  this.setState({views:[created,...s.views],viewName:'',viewShared:false,modal:''});this.notify('Представление сохранено');
 });
 deleteSavedView=(id:string)=>this.run(async()=>{await request('/views/'+id,{method:'DELETE'});this.setState({views:this.state.views.filter((x:any)=>x.id!==id)});this.notify('Представление удалено')});
 applySavedView=(view:any)=>{
  const f=view.filters||{};
  this.setState({view:'inbox',channelFilter:f.channel||'',statusFilter:f.status||'',priorityFilter:f.priority||'',assignedFilter:f.assigned||'',archivedFilter:!!f.archived,sortFilter:f.sort||'recent',selected:null,detail:null,mobilePane:'list'},()=>this.loadConvs());
  history.replaceState({},'','/');
 };
 openQueueConversation=(id:string)=>{
  if(this.state.selected&&this.state.reply.trim())this.drafts[this.state.selected]=this.state.reply;
  this.setState({view:'inbox',search:'',channelFilter:'',statusFilter:'',priorityFilter:'',assignedFilter:'',archivedFilter:false,sortFilter:'recent',selected:id,detail:null,mobilePane:'chat',reply:this.drafts[id]||''},async()=>{await this.loadConvs(true);await this.loadDetail(id)});
  history.replaceState({},'','/');
 };
 changeSearch=(text:string)=>{this.setState({search:text});if(this.searchTimer)clearTimeout(this.searchTimer);this.searchTimer=setTimeout(()=>this.loadConvs(),250)};
 changeFilter=(key:string,value:any)=>{this.setState({[key]:value,selected:null,detail:null,mobilePane:'list'},()=>this.loadConvs())};
 changeReply=(value:string)=>{const id=this.state.selected;
  if(id){if(value)this.drafts[id]=value;else delete this.drafts[id]}
  this.setState({reply:value});
 };
 send=async()=>{
   const d=this.state.detail, s=this.state;
   if(!d||!s.reply.trim()||this.sending)return;
   const id=d.conversation.id, body=s.reply.trim();
   if(outgoingSize(d.conversation.channel,body)>outgoingLimit(d.conversation.channel)){
     this.notify('Сообщение слишком длинное для этой площадки. Укоротите текст.');return;
   }
   const pending=this.pendingSend[id];
   const nonce=pending&&pending.body===body?pending.nonce:
     (window.crypto?.randomUUID?window.crypto.randomUUID():'nonce-'+Date.now()+'-'+Math.random());
   this.pendingSend[id]={body,nonce};
   this.sending=true;this.setState({loading:true});
   try{
     const data=await request(`/conversations/${id}/reply`,{method:'POST',body:JSON.stringify({body,expected_version:d.conversation.version,client_nonce:nonce})});
     delete this.pendingSend[id];delete this.drafts[id];
     if(this.state.selected===id){
       const keepText=this.state.reply!==s.reply;
       this.setState({reply:keepText?this.state.reply:'',detail:{...d,conversation:data.conversation,
        messages:d.messages.some((m:any)=>m.id===data.message.id)?d.messages:[...d.messages,data.message]}});
       if(keepText)this.drafts[id]=this.state.reply;
       await this.loadDetail(id);
     }
     await this.loadConvs(true);
     this.notify(data.conversation.outbound_paused?'Ответ сохранён в очереди. Отправка приостановлена администратором.':data.message.delivery_status==='queued'?'Ответ передан в очередь. Статус доставки появится в переписке.':'Ответ сохранён в переписке.');
   }catch(e:any){
     this.notify(readableError(e.message||''));
     if(this.state.selected===id)await this.loadDetail(id,true); // refresh server version, keep draft and idempotency nonce
   }finally{this.sending=false;this.setState({loading:false})}
 };
 openWaTemplates=async()=>{
  const c=this.state.detail?.conversation;if(!c)return;
  this.setState({modal:'wa-template',waTemplates:[],waConsent:false,waSelected:'',waParams:[],waLoading:true});
  try{const result=await request(`/conversations/${c.id}/whatsapp-templates`);
   this.setState({waTemplates:result.templates,waConsent:result.consent_recorded,
    waSelected:result.templates[0]?result.templates[0].name+'|'+result.templates[0].language:'',
    waParams:Array(result.templates[0]?.param_count||0).fill(''),waLoading:false});
  }catch(e:any){this.notify(e.message);this.setState({waLoading:false})}
 };
 recordWaConsent=()=>this.run(async()=>{
  const c=this.state.detail?.conversation;if(!c)return;
  const response=await request(`/conversations/${c.id}/whatsapp-consent`,{method:'POST',
   body:JSON.stringify({source:this.state.waConsentSource,confirmed:this.state.waConsentCheckbox})});
  this.setState({waConsent:response.consent_recorded});
  this.notify('Факт согласия записан со слов сотрудника. Платформа не проверяла его автоматически.');
 });
 revokeWaConsent=()=>this.run(async()=>{
  const c=this.state.detail?.conversation;if(!c)return;
  await request(`/conversations/${c.id}/whatsapp-consent/revoke`,{method:'POST'});
  this.setState({waConsent:false});this.notify('Согласие отозвано: новые шаблоны нельзя отправлять');
 });
 sendWaTemplate=()=>this.run(async()=>{
  const s=this.state,c=s.detail?.conversation;if(!c)return;
  const selection=(s.waTemplates||[]).find((t:any)=>t.name+'|'+t.language===s.waSelected);
  if(!selection)return;
  const fingerprint=JSON.stringify([selection.name,selection.language,s.waParams]);
  const key='wa:'+c.id,pending=this.pendingSend[key];
  const nonce=pending?.body===fingerprint?pending.nonce:(window.crypto?.randomUUID?window.crypto.randomUUID():
     'template-'+Date.now()+'-'+Math.random());
  this.pendingSend[key]={body:fingerprint,nonce};
  const response=await request(`/conversations/${c.id}/whatsapp-template`,{method:'POST',
    body:JSON.stringify({name:selection.name,language:selection.language,
      parameters:s.waParams,expected_version:c.version,client_nonce:nonce})});
  delete this.pendingSend[key];
  this.setState({modal:''});await this.loadDetail(c.id);await this.loadConvs(true);
  this.notify(response.duplicate?'Этот шаблон уже находится в переписке':
    'Одобренный шаблон добавлен в очередь. Доставка ещё не подтверждена.');
 });
 updateConv=(kind:string,value:any)=>{const d=this.state.detail;if(!d)return;this.run(async()=>{const id=d.conversation.id;
 const path=kind==='status'?'/status':kind==='assign'?'/assign':'/pin';
 const body=kind==='status'?{status:value,expected_version:d.conversation.version}:
            kind==='assign'?{user_id:value,expected_version:d.conversation.version}:
            {expected_version:d.conversation.version};
 try{
  await request(`/conversations/${id}${path}`,{method:'PATCH',body:JSON.stringify(body)});
 }catch(e:any){
  if(/Диалог изменён|Диалог занят/.test(e.message||'')){
   await this.loadDetail(id);await this.loadConvs(true);
   throw new Error('Коллега изменил диалог. Данные обновлены — проверьте их и повторите действие.');
  }
  throw e;
 }
 await this.loadDetail(id);await this.loadConvs(true);
 })};
 addNote=()=>{const d=this.state.detail;if(!d||!this.state.note.trim())return;this.run(async()=>{await request(`/conversations/${d.conversation.id}/notes`,{method:'POST',body:JSON.stringify({body:this.state.note})});this.setState({note:''});await this.loadDetail(d.conversation.id)})};
 saveContact=(contact:any)=>this.run(async()=>{const patch:any={...contact};delete patch.id;await request('/contacts/'+contact.id,{method:'PATCH',body:JSON.stringify(patch)});this.notify('Карточка клиента сохранена');if(this.state.view==='contacts'||this.state.view==='deals')await this.loadView(this.state.view);if(this.state.selected)await this.loadDetail(this.state.selected)});
 addCustomerTag=()=>{const s=this.state;const draft=s.contactDraft;if(!draft)return;const tag=s.tagInput.trim();if(!tag)return;const tags=Array.from(new Set([...(draft.tags||[]),tag]));const next={...draft,tags};this.setState({tagInput:'',tagEditing:false,contactDraft:next});this.saveContact(next)};
 removeCustomerTag=(tag:string)=>{const draft=this.state.contactDraft;if(!draft)return;const next={...draft,tags:(draft.tags||[]).filter((v:string)=>v!==tag)};this.setState({contactDraft:next});this.saveContact(next)};
 appendEmoji=(emoji:string)=>{this.changeReply(this.state.reply+emoji);this.setState({showEmoji:false})};
 demoIncoming=()=>{const d=this.state.detail;if(!d||!this.state.demoInbound.trim())return;this.run(async()=>{await request('/demo/incoming',{method:'POST',body:JSON.stringify({conversation_id:d.conversation.id,body:this.state.demoInbound})});this.setState({demoInbound:''});await this.loadDetail(d.conversation.id);await this.loadConvs(true);this.notify('Тестовое входящее добавлено')})};
 toggleTheme=()=>{const next=!this.state.light;localStorage.setItem('omnichat_theme',next?'light':'dark');document.body.classList.toggle('light',next);this.setState({light:next})};
 oauth=(provider:string)=>this.run(async()=>{const {url}=await request('/integrations/oauth-start/'+provider,{method:'POST'});window.location.href=url});
 connectBot=()=>this.run(async()=>{
  const response=await request('/integrations/bots',{method:'POST',body:JSON.stringify({provider:this.state.botProvider,access_token:this.state.connectToken,group_id:this.state.botGroupId||null,confirmation_token:this.state.botConfirmation||null})});
  this.setState({modal:'',connectToken:'',botGroupId:'',botConfirmation:'',botConnectedInfo:response});
  await this.loadView('integrations');
  this.notify('Аккаунт проверен. Настройте защищённый webhook для приёма обращений.');
 });
 activateBot=(id:string)=>this.run(async()=>{
  const result=await request('/integrations/'+id+'/activate-webhook',{method:'POST'});
  await this.loadView('integrations');
  this.notify(result.message);
 });
 connectWhatsApp=()=>this.run(async()=>{
   const result=await request('/integrations/manual',{method:'POST',body:JSON.stringify({provider:'whatsapp',access_token:this.state.connectToken,phone_number_id:this.state.connectPhone,waba_id:this.state.connectWaba||null})});
   this.setState({modal:'',connectToken:'',connectPhone:'',connectWaba:''});await this.loadView('integrations');
   this.notify(result.status==='connected'?'Канал прошёл проверку': 'Номер подтверждён. Подключите подписку WABA и проверьте входящее сообщение.');
 });
 disconnect=(id:string)=>{if(!window.confirm('Отключить канал? Доступ к его сообщениям в OSMANX прекратится.'))return;this.run(async()=>{const r=await request('/integrations/'+id+'/disconnect',{method:'POST'});await this.loadView('integrations');this.notify(r?.message||'Подключение отключено')})};
 pauseCompanyOutbound=(pausedAt:number|null)=>{
   const paused=pausedAt!==null&&pausedAt!==undefined;
   const warning=paused
    ?'Возобновить новые исходящие сообщения ВСЕХ аккаунтов компании? Убедитесь, что инцидент устранён. Индивидуальные паузы сохранятся.'
    :'АВАРИЙНО ОСТАНОВИТЬ НОВЫЕ ИСХОДЯЩИЕ ВСЕХ АККАУНТОВ? Входящие продолжат поступать. Запросы, уже начатые на площадке, могут завершиться.';
   if(!window.confirm(warning))return;
   this.run(async()=>{
     const endpoint=paused?'/operations/outbound/resume':'/operations/outbound/pause';
     const body=paused?{expected_paused_at:pausedAt,acknowledge_inflight:true}
                      :{reason:'security_review',acknowledge_inflight:true};
     const result=await request(endpoint,{method:'POST',body:JSON.stringify(body)});
     await this.loadView('operations');
     if(this.state.selected)await this.loadDetail(this.state.selected,true);
     await this.loadConvs(true);
     this.notify(result.message);
   });
 };

 pauseOutbound=(id:string, paused:boolean)=>{
   const warning=paused?'Возобновить новые исходящие сообщения через этот аккаунт? Сначала проверьте причину остановки.':'Приостановить НОВЫЕ исходящие сообщения этого аккаунта? Входящие продолжат работать. Отправки, уже прошедшие контрольную точку, могут завершиться.';
   if(!window.confirm(warning))return;
   this.run(async()=>{
     const path='/integrations/'+id+(paused?'/outbound-resume':'/outbound-pause');
     const options:any={method:'POST'};
     if(!paused)options.body=JSON.stringify({reason:'security_review',acknowledge_inflight:true});
     const result=await request(path,options);
     await this.loadView('integrations');
     this.notify(result.message);
   });
 };

 diagnoseChannel=(id:string)=>this.run(async()=>{
   const data=await request('/integrations/'+id+'/diagnostics');
   this.setState({channelDiagnostics:data,channelDiagnosticsFor:id},()=>{
     const block=document.querySelector('.onboarding-diagnostics');
     if(block)block.scrollIntoView({behavior:'smooth',block:'start'});
   });
 });
 verifyProviderHook=(id:string)=>this.run(async()=>{
   const result=await request('/integrations/'+id+'/verify-provider-webhook',{method:'POST'});
   await this.loadView('integrations');
   const data=await request('/integrations/'+id+'/diagnostics');
   this.setState({channelDiagnostics:{...data,provider_error:result.provider_error||null,pending_updates:result.pending_updates},channelDiagnosticsFor:id},()=>{
     document.querySelector('.onboarding-diagnostics')?.scrollIntoView({behavior:'smooth',block:'start'});
   });
   this.notify(result.message);
 });
 probeChannel=(id:string)=>this.run(async()=>{
   const report=await request('/integrations/'+id+'/probe',{method:'POST'});
   await this.loadView('integrations');
   const diagnostic=await request('/integrations/'+id+'/diagnostics');
   this.setState({channelDiagnostics:diagnostic,channelDiagnosticsFor:id},()=>{
     document.querySelector('.onboarding-diagnostics')?.scrollIntoView({behavior:'smooth',block:'start'});
   });
   this.notify(report.next_step);
 });
 checkChannel=(id:string)=>this.run(async()=>{
   const result=await request('/integrations/'+id+'/check-access',{method:'POST'});
   await this.loadView('integrations');this.notify(result.message);
 });
 registerWhatsAppPhone=()=>this.run(async()=>{
   const result=await request('/integrations/'+this.state.registerPhoneChannel+'/register-phone',{
     method:'POST',body:JSON.stringify({pin:this.state.registrationPin})});
   this.setState({modal:'',registerPhoneChannel:'',registrationPin:''});await this.loadView('integrations');
   this.notify(result.message);
 });
 rotateChannelToken=()=>this.run(async()=>{
   await request('/integrations/'+this.state.rotateChannel+'/rotate-token',{method:'POST',body:JSON.stringify({access_token:this.state.rotateToken})});
   this.setState({modal:'',rotateChannel:'',rotateToken:''});await this.loadView('integrations');
   this.notify('Токен заменён. Проверьте webhook и входящее сообщение.');
 });
 vkCallback=(id:string)=>this.run(async()=>{
   const setup=await request('/integrations/'+id+'/vk-callback-setup');
   this.setState({channelDiagnostics:{...this.state.channelDiagnostics,...setup,secretVisible:true},channelDiagnosticsFor:id});
 });
 connectMessengerPage=(id:string)=>this.run(async()=>{
   const result=await request('/integrations/messenger/pages/'+id+'/connect',{method:'POST'});
   await this.loadView('integrations');
   this.notify(result.message);
 });
 createCompany=()=>this.run(async()=>{
   const org=await request('/organizations',{method:'POST',body:JSON.stringify({name:this.state.newOrganization.trim()})});
   await request('/auth/switch/'+org.id,{method:'POST'});
   window.location.assign('/?view=integrations');
 });
 switchCompany=(id:string)=>this.run(async()=>{
   await request('/auth/switch/'+id,{method:'POST'});
   window.location.assign('/?view=integrations');
 });
 metaMessage=(event:MessageEvent)=>{
   if(!this.metaFlow||!['https://www.facebook.com','https://web.facebook.com'].includes(event.origin))return;
   let packet:any=event.data;
   if(typeof packet==='string'){try{packet=JSON.parse(packet)}catch(e){return}}
   if(packet?.type!=='WA_EMBEDDED_SIGNUP')return;
   const data=packet.data||{};
   if(packet.event==='FINISH'&&data.waba_id&&data.phone_number_id){
      this.metaFlow.waba_id=String(data.waba_id);this.metaFlow.phone_number_id=String(data.phone_number_id);
      this.completeMetaIfReady();
   }
   if(packet.event==='CANCEL')this.notify('Регистрация WhatsApp отменена в Meta.');
 };
 completeMetaIfReady=()=>{
   const flow=this.metaFlow;
   if(!flow||flow.submitting||!flow.code||!flow.waba_id||!flow.phone_number_id)return;
   flow.submitting=true;
   this.run(async()=>{
     const result=await request('/integrations/whatsapp/embedded/complete',{method:'POST',body:JSON.stringify({state:flow.state,code:flow.code,waba_id:flow.waba_id,phone_number_id:flow.phone_number_id})});
     this.metaFlow=null;
     await this.loadView('integrations');
     this.notify(result.message);
   });
 };
 prepareMetaWhatsApp=()=>this.run(async()=>{
   // Preparation is asynchronous. The actual popup must open synchronously on
   // the NEXT user click, otherwise browsers may block it after an await.
   const flow=await request('/integrations/whatsapp/embedded/start',{method:'POST'});
   const w:any=window;
   if(!w.FB){await new Promise<void>((resolve,reject)=>{
      const script=document.createElement('script');script.src='https://connect.facebook.net/ru_RU/sdk.js';script.async=true;
      script.onload=()=>resolve();script.onerror=()=>reject(new Error('Meta SDK не загрузился. Проверьте доступность Facebook.'));
      document.head.appendChild(script);
   });}
   w.FB.init({appId:flow.app_id,autoLogAppEvents:false,xfbml:false,version:flow.graph_version});
   this.setState({metaSession:{...flow,prepared_at:Date.now()}});
   this.notify('Meta подготовлена. Нажмите «Продолжить в Meta», чтобы открыть официальный вход.');
 });
 launchMetaWhatsApp=()=>{
   const flow=this.state.metaSession;
   if(!flow||Date.now()-flow.prepared_at>12*60*1000){this.notify('Сеанс истёк. Подготовьте подключение ещё раз.');return}
   const w:any=window;
   if(!w.FB){this.notify('Meta SDK не загружен');return}
   this.metaFlow={...flow,code:'',waba_id:'',phone_number_id:'',submitting:false};
   // Direct gesture-driven FB.login is required by popup blockers.
   w.FB.login((response:any)=>{
     if(!this.metaFlow)return;
     const code=response?.authResponse?.code;
     if(!code){this.notify('Meta не предоставила код авторизации. Проверьте разрешения приложения.');return}
     this.metaFlow.code=String(code);this.completeMetaIfReady();
   },{config_id:flow.config_id,response_type:'code',override_default_response_type:true,
       extras:{setup:{},featureType:'whatsapp_embedded_signup',sessionInfoVersion:'3'}});
 };

 createRule=()=>this.run(async()=>{await request('/rules',{method:'POST',body:JSON.stringify({name:this.state.ruleName||'Новое правило',event:'message_received',condition_type:this.state.ruleCondition,condition_value:this.state.ruleTerm,action_type:this.state.ruleAction,action_value:this.state.ruleActionValue,enabled:true})});this.setState({modal:'',ruleName:'',ruleTerm:''});await this.loadView('rules');this.notify('Правило активно')});
 toggleRule=(id:string)=>this.run(async()=>{await request('/rules/'+id+'/toggle',{method:'PATCH'});await this.loadView('rules')});
 invite=()=>this.run(async()=>{const data=await request('/team/invite',{method:'POST',body:JSON.stringify({email:this.state.inviteEmail,role:this.state.inviteRole})});this.setState({inviteToken:data.invite_token});this.notify('Приглашение создано. Скопируйте токен и передайте сотруднику.')});
 clearSiteForm=()=>this.setState({siteSelected:'',siteName:'',siteOrigins:'',siteGreeting:'Здравствуйте! Чем можем вам помочь?',siteAccent:'#90b7a7'});
 startEditSite=(w:any)=>{this.setState({siteSelected:w.id,siteName:w.name,siteOrigins:w.allowed_origins.join('\n'),siteGreeting:w.greeting,siteAccent:w.accent});window.scrollTo({top:0,behavior:'smooth'})};
 saveSiteWidget=()=>this.run(async()=>{const s=this.state;const payload={name:s.siteName.trim(),allowed_origins:s.siteOrigins.split(/[\s,]+/).map((v:string)=>v.trim()).filter(Boolean),greeting:s.siteGreeting.trim(),accent:s.siteAccent};if(!payload.allowed_origins.length)throw new Error('Укажите хотя бы один разрешённый адрес сайта (HTTPS в production)');if(s.siteSelected)await request('/website-widgets/'+s.siteSelected,{method:'PATCH',body:JSON.stringify({...payload,enabled:s.sites.find((x:any)=>x.id===s.siteSelected)?.enabled??true})});else await request('/website-widgets',{method:'POST',body:JSON.stringify(payload)});this.clearSiteForm();await this.loadView('websites');this.notify('Канал сайта сохранён')});
 toggleSiteWidget=(w:any)=>this.run(async()=>{const payload={name:w.name,allowed_origins:w.allowed_origins,greeting:w.greeting,accent:w.accent,enabled:!w.enabled};await request('/website-widgets/'+w.id,{method:'PATCH',body:JSON.stringify(payload)});await this.loadView('websites');this.notify(w.enabled?'Виджет приостановлен':'Виджет включён')});
 rotateSiteWidget=(w:any)=>{if(!window.confirm('Сменить публичный ключ виджета? Старый код перестанет работать на сайте.'))return;this.run(async()=>{await request('/website-widgets/'+w.id+'/rotate-key',{method:'POST'});await this.loadView('websites');this.notify('Ключ изменён. Обновите код на сайте.')})};
 copySnippet=(code:string)=>{if(navigator.clipboard?.writeText)navigator.clipboard.writeText(code).then(()=>this.notify('Код виджета скопирован')).catch(()=>this.notify('Браузер запретил копирование. Выделите код вручную.'));else this.notify('Для копирования из браузера необходимо защищённое соединение HTTPS')};
 repairInboundExpired=()=>this.run(async()=>{
   const s=this.state;
   if(!s.inboundRepairConfirmed||s.inboundRepairReason.trim().length<12)return;
   const result=await request('/operations/inbound/repair-expired',{
     method:'POST',body:JSON.stringify({reason:s.inboundRepairReason.trim(),confirm_expired_only:true})});
   this.setState({modal:'',inboundRepairReason:'',inboundRepairConfirmed:false});
   await this.loadView('operations');
   this.notify('Проверка завершена. Безопасно исправлено: '+result.changes+'. Активные задачи сохранены.');
 });
 loadInboundTriage=(status:string='',more:boolean=false)=>this.run(async()=>{
   const params=new URLSearchParams({limit:'30'});
   if(status)params.set('status',status);
   if(more){if(!this.state.inboundTriageCursor)return;params.set('before',this.state.inboundTriageCursor);}
   const result=await request('/operations/inbound/triage?'+params.toString());
   this.setState({inboundTriageStatus:status,
     operationsInboundJobs:more?[...this.state.operationsInboundJobs,...result.items]:result.items,
     inboundTriageCursor:result.next_cursor});
 });
 applyInboundPause=()=>this.run(async()=>{
   const s=this.state,scope=s.inboundControlScope==='organization'?'organization':'channel';
   const body={scope,channel_id:scope==='channel'?s.inboundControlScope:null,
               reason:s.inboundPauseReason.trim()};
   if(body.reason.length<8)throw new Error('Укажите причину длиной от 8 символов');
   await request('/operations/inbound/'+s.inboundPauseAction,
     {method:'POST',body:JSON.stringify(body)});
   this.setState({modal:'',inboundPauseReason:''});
   await this.loadView('operations');
   this.notify(s.inboundPauseAction==='pause'
      ?'Входящие сохраняются, их обработка приостановлена.'
      :'Обработка входящих возобновлена.');
 });
 openInboundBatchPreview=()=>this.run(async()=>{
   if(!this.state.inboundBatchChannel)return;
   const preview=await request('/operations/inbound/retry-batch/preview',{
      method:'POST',body:JSON.stringify({channel_id:this.state.inboundBatchChannel,limit:20})});
   this.setState({modal:'inbound-batch',inboundBatchPreview:preview,inboundBatchReason:''});
 });
 refreshInboundBatchPreview=()=>this.run(async()=>{
   if(!this.state.inboundBatchChannel)return;
   const preview=await request('/operations/inbound/retry-batch/preview',{
     method:'POST',body:JSON.stringify({channel_id:this.state.inboundBatchChannel,limit:20})});
   this.setState({inboundBatchPreview:preview});
   this.notify('Предпросмотр обновлён. Проверьте количество событий перед подтверждением.');
 });
 retryInboundBatch=()=>this.run(async()=>{
   const s=this.state,preview=s.inboundBatchPreview;
   if(!preview||preview.count<1||s.inboundBatchReason.trim().length<8)return;
   const result=await request('/operations/inbound/retry-batch-confirm',{
     method:'POST',body:JSON.stringify({proof:preview.proof,
       reason:s.inboundBatchReason.trim()})});
   this.setState({modal:'',inboundBatchReason:'',inboundBatchPreview:null});
   await this.loadView('operations');
   this.notify('Проверено и возвращено в очередь: '+result.requeued+'. Результат появится в Inbox.');
 });
 dismissInbound=()=>this.run(async()=>{
   const s=this.state,job=s.inboundDismissJob;
   if(!job||!s.inboundDismissConfirmed||s.inboundDismissReason.trim().length<12)return;
   const result=await request('/operations/inbound/'+encodeURIComponent(job.id)+'/dismiss',{
     method:'POST',body:JSON.stringify({code:s.inboundDismissCode,
       reason:s.inboundDismissReason.trim(),confirm_permanent_loss:true})});
   this.setState({modal:'',inboundDismissJob:null,inboundDismissReason:'',inboundDismissConfirmed:false});
   await this.loadView('operations');
   this.notify(result.message||'Событие закрыто и шифротекст удалён.');
 });
 retryInbound=()=>this.run(async()=>{
   const job=this.state.inboundRetryJob;
   const reason=this.state.inboundRetryReason.trim();
   if(!job||reason.length<8)return;
   await request('/operations/inbound/'+encodeURIComponent(job.id)+'/retry',
      {method:'POST',body:JSON.stringify({reason})});
   this.setState({modal:'',inboundRetryJob:null,inboundRetryReason:''});
   await this.loadView('operations');
   this.notify('Входящее событие возвращено в очередь. После обработки обновите переписки.');
 });
 reconcileDelivery=()=>this.run(async()=>{const s=this.state;if(!s.reconcileJob||s.reconcileEvidence.trim().length<8)return;await request('/operations/outbox/'+s.reconcileJob.id+'/resolve',{method:'POST',body:JSON.stringify({status:s.reconcileStatus,evidence:s.reconcileEvidence.trim(),external_id:s.reconcileExternalId||null})});this.setState({modal:'',reconcileJob:null,reconcileEvidence:'',reconcileExternalId:''});await this.loadView('operations');this.notify('Результат проверки доставки записан в журнал действий')});
 cancelQueued=(j:any)=>{if(!window.confirm('Отменить ответ, который ещё не отправлен в соцсеть? Если отправка уже началась, OSMANX не позволит отменить её.'))return;
  this.run(async()=>{await request('/operations/outbox/'+j.id+'/cancel',{method:'POST'});await this.loadView('operations');if(this.state.selected)await this.loadDetail(this.state.selected,true);this.notify('Ответ отменён до начала отправки. Клиенту он не передан.')})};
 retryVerified=()=>this.run(async()=>{const s=this.state;if(!s.outboxRetryJob||!s.outboxRetryVerified||s.outboxRetryEvidence.trim().length<12)return;
  await request('/operations/outbox/'+s.outboxRetryJob.id+'/retry-verified',{method:'POST',body:JSON.stringify({verified_not_delivered:true,evidence:s.outboxRetryEvidence.trim()})});
  this.setState({modal:'',outboxRetryJob:null,outboxRetryEvidence:'',outboxRetryVerified:false});await this.loadView('operations');
  this.notify('Повтор поставлен в очередь. Это ещё не подтверждение доставки.')});
 claimReply=(release=false)=>{const c=this.state.detail?.conversation;if(!c)return;this.run(async()=>{await request('/conversations/'+c.id+'/'+(release?'release':'claim'),{method:'POST',body:release?undefined:JSON.stringify({seconds:120})});await this.loadDetail(c.id);await this.loadConvs(true);this.notify(release?'Диалог освобождён':'Диалог занят вами на 2 минуты')})};
 renderAuth(){const s=this.state;return <div className="quiet-auth-shell"><div className="quiet-auth-main">
  <div className="quiet-auth-brand"><span className="brand-symbol" aria-hidden="true"/><div><strong>OSMANX</strong><small>OMNICHAT</small></div></div>
  <div className="quiet-auth-title"><h1>Все сообщения.<br/><span>Одно место.</span></h1><p>Работайте с обращениями из подключённых социальных сетей в одном спокойном пространстве.</p></div>
  <div className="quiet-auth-card"><div className="quiet-auth-modes"><button className={s.authMode==='demo'?'selected':''} onClick={()=>this.setState({authMode:'demo'})}>Демоверсия</button><button className={s.authMode==='login'?'selected':''} onClick={()=>this.setState({authMode:'login'})}>Вход</button><button className={s.authMode==='register'?'selected':''} onClick={()=>this.setState({authMode:'register'})}>Регистрация</button></div>
  <h2>{s.authMode==='login'?'С возвращением':s.authMode==='register'?'Создать компанию':'Посмотрите, как всё устроено'}</h2>
  <p>{s.authMode==='demo'?'Откройте тестовые переписки, CRM и рабочий интерфейс. Реальные аккаунты не затрагиваются.':s.authMode==='register'?'Создайте отдельное рабочее пространство для своей компании.':'Войдите, чтобы продолжить работу с сообщениями.'}</p>
  {s.authMode!=='demo'?<form className="quiet-auth-form" onSubmit={(e:any)=>{e.preventDefault();this.login()}}>
    {s.authMode==='register'&&<><label>Компания<input value={s.authCompany} required minLength={2} onChange={(e:any)=>this.setState({authCompany:e.target.value})} placeholder="Название компании"/></label><label>Имя<input value={s.authName} required minLength={2} onChange={(e:any)=>this.setState({authName:e.target.value})} placeholder="Как вас зовут?"/></label></>}
    <label>Электронная почта<input type="email" required value={s.authEmail} onChange={(e:any)=>this.setState({authEmail:e.target.value})} placeholder="company@example.com"/></label><label>Пароль<input type="password" required minLength={s.authMode==='register'?12:1} value={s.authPassword} onChange={(e:any)=>this.setState({authPassword:e.target.value})} placeholder="Не менее 12 символов для регистрации"/></label>
    <button className="quiet-auth-primary" type="submit" disabled={s.loading}>{s.loading?'Проверяем...':s.authMode==='register'?'Создать компанию':'Войти'} <Icon name="arrow" size={18}/></button>
   </form>:<button className="quiet-auth-primary" disabled={s.loading} onClick={this.login}>{s.loading?'Создаём демопространство...':'Открыть демоверсию'} <Icon name="arrow" size={19}/></button>}
   <div className="quiet-auth-note"><Icon name="shield" size={14}/> В демоверсии нет отправки в реальные соцсети</div>
  </div><div className="quiet-auth-footer">OSMANX OMNICHAT · OBSIDIAN SILENCE</div>
 </div></div>}
 renderSidebar(){
  const s=this.state,me=s.me;
  const compact:any=[['inbox','inbox','Входящие'],['contacts','users','Клиенты'],['deals','briefcase','Сделки'],['integrations','layers','Интеграции'],['settings','settings','Настройки']];
  const other:any=[['command','layout','Центр управления'],['analytics','chart','Аналитика'],['rules','flow','Автоматизация'],['websites','globe','Чат для сайта'],['operations','activity','Контроль доставки'],['team','users','Команда']];
  return <aside className={'sidebar '+(s.sidebarOpen?'open':'')}>
   <div className="sidebar-top"><div className="brand"><span className="brand-symbol" aria-hidden="true"/><div><strong>OSMANX</strong><small>OMNICHAT</small></div></div><button className="icon-btn sidebar-close" aria-label="Закрыть меню" onClick={()=>this.setState({sidebarOpen:false})}><Icon name="close"/></button></div>
   <nav aria-label="Основная навигация" className="quiet-nav">
    {compact.filter(([id]:any)=>id!=='integrations'||['owner','admin','lead'].includes(me.role)).map(([id,ic,label]:any)=><button key={id} className={'nav-item '+(s.view===id?'active':'')} onClick={()=>this.changeView(id)}><Icon name={ic} size={22}/><span>{label}</span></button>)}
   </nav>
   {!me.organization.is_demo&&['owner','admin'].includes(me.role)&&s.quickstart&&!s.quickstart.all_done&&<button className={'nav-item quickstart-nav '+(s.view==='start'?'active':'')} onClick={()=>this.changeView('start')}><Icon name="check" size={19}/><span>Быстрый старт · {s.quickstart.completed}/{s.quickstart.total}</span></button>}
   <div className="sidebar-grow"/>
   <button className="nav-item quiet-more" aria-expanded={s.moreNav} onClick={()=>this.setState({moreNav:!s.moreNav})}><Icon name="menu" size={19}/><span>{s.moreNav?'Скрыть разделы':'Другие разделы'}</span><Icon name="chevron" size={15}/></button>
   {s.moreNav&&<nav aria-label="Дополнительные разделы" className="sidebar-extra">{other.filter(([id]:any)=>!['operations','rules','websites'].includes(id)||['owner','admin','lead'].includes(me.role)).map(([id,ic,label]:any)=><button key={id} className={'nav-item '+(s.view===id?'active':'')} onClick={()=>this.changeView(id)}><Icon name={ic} size={17}/><span>{label}</span></button>)}</nav>}
   <div className="sidebar-bottom">
    <div className="quiet-workspace"><span className="workspace-dot"/><div><strong>{me.organization.name}</strong><small>{me.organization.is_demo?'Демонстрация':'Рабочее пространство'}</small></div></div>
    <div className="quiet-account"><button onClick={this.toggleTheme} className="icon-btn" aria-label={s.light?'Включить тёмную тему':'Включить светлую тему'} title="Сменить тему"><Icon name={s.light?'moon':'sun'}/></button><button onClick={this.logout} className="icon-btn" aria-label="Выйти из аккаунта" title="Выйти"><Icon name="logout"/></button></div>
   </div>
  </aside>
 }

 renderStart(){const s=this.state, progress=s.quickstart;
  if(!progress)return <div className="page-content"><div className="empty-list">Проверяем настройки вашей компании...</div></div>;
  const tasks=progress.tasks||[];
  return <div className="page-content quickstart-page">
   <div className="quickstart-overline"><Icon name="sparkles" size={17}/> БЫСТРЫЙ СТАРТ · {progress.is_demo?'ДЕМО':'ВАША КОМПАНИЯ'}</div>
   <h1>{progress.all_done?'Первые шаги выполнены':'Настроим OSMANX за три шага'}</h1>
   <p className="quickstart-lead">Без технических терминов. Выберите свой канал общения, получите сообщение и ответьте прямо здесь.</p>
   {progress.is_demo&&<div className="quickstart-alert"><Icon name="info" size={17}/> В деморежиме все сообщения тестовые. Для работы с клиентами создайте обычную компанию.</div>}
   <div className="quickstart-status"><strong>{progress.completed} из {progress.total} шагов</strong><span>Система отмечает шаги по настоящим данным, а не по нажатию кнопки.</span></div>
   <div className="quickstart-track" role="progressbar" aria-label="Подготовка рабочего места" aria-valuemin={0} aria-valuemax={progress.total} aria-valuenow={progress.completed}><div style={{width:(progress.completed/progress.total*100)+'%'}}/></div>
   <div className="quickstart-steps">{tasks.map((task:any,i:number)=><section className={'quickstart-step '+(task.done?'done':'')} key={task.key}>
     <span className="quickstart-number">{task.done?<Icon name="check" size={19}/>:i+1}</span>
     <div className="quickstart-step-text"><h2>{task.title}</h2><p>{task.description}</p></div>
     <button className={'btn '+(task.done?'secondary':'primary')} onClick={()=>this.changeView(task.view)}>{task.key==='channel'?'Выбрать соцсеть':task.key==='incoming'?'Открыть сообщения':'Ответить клиенту'} <Icon name="arrow" size={15}/></button>
   </section>)}</div>
   <div className="quickstart-bottom"><button className="btn secondary" onClick={()=>this.changeView('websites')}><Icon name="globe" size={17}/> Вместо соцсети — чат для сайта</button><button className="btn ghost" onClick={()=>this.loadView('start')}><Icon name="activity" size={15}/> Проверить прогресс</button></div>
   <p className="quickstart-disclaimer"><Icon name="shield" size={16}/> {progress.note}</p>
  </div>
 }
 renderCommand(){const s=this.state;const a=s.command;
  if(!a)return <div className="page-content"><div className="empty-list">Загрузка центра управления...</div></div>;
  const queue=a.priority_queue||[];const maxLoad=Math.max(1,...(a.workload||[]).map((m:any)=>m.open));
  return <div className="page-content command-page">
   <div className="command-hero">
    <div className="command-hero-content"><div className="eyebrow"><span className="dot green"/> ОПЕРАТИВНЫЙ ОБЗОР / ОБНОВЛЯЕМЫЕ ДАННЫЕ</div>
     <h1>Каждое обращение<br/><span>под контролем.</span></h1>
     <p>Приоритеты, сроки ответа и работа команды — в одном пространстве. Очередь рассчитывается по прозрачным правилам, без ИИ.</p>
     <div className="command-hero-actions"><button className="btn command-primary" onClick={()=>this.changeView('inbox')}><Icon name="inbox" size={17}/> Открыть сообщения <Icon name="arrow" size={16}/></button><button className="btn command-secondary" onClick={()=>this.loadView('command')}><Icon name="activity" size={16}/> Обновить данные</button></div>
    </div>
    <div className="command-hero-art" aria-hidden="true"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="orbit orbit-three"/><div className="hero-monogram">OX<span> /</span></div><span className="orbit-marker a"/><span className="orbit-marker b"/><span className="orbit-marker c"/></div>
   </div>
   <div className="command-section-title"><div><div className="eyebrow small">ОПЕРАЦИОННЫЕ ПОКАЗАТЕЛИ</div><h2>Состояние обращений</h2></div><div className="command-updated"><span className="dot green"/> Данные на {fmt(a.refreshed_at)} · {a.is_demo?'тестовый режим':'рабочая область'}</div></div>
   <div className="command-metrics">
    <div className="command-metric"><div className="command-metric-top"><span>Активные диалоги</span><Icon name="inbox" size={19}/></div><strong>{a.total_open}</strong><small>В текущей области видимости</small><div className="command-metric-line"/></div>
    <div className="command-metric"><div className="command-metric-top"><span>Ожидают ответа</span><Icon name="clock" size={19}/></div><strong>{a.waiting}</strong><small>Последнее сообщение от клиента</small><div className="command-metric-line"/></div>
    <div className="command-metric warning"><div className="command-metric-top"><span>Просрочено по SLA</span><Icon name="flag" size={19}/></div><strong>{a.overdue}</strong><small>Порог — {a.sla_minutes} мин.</small><div className="command-metric-line"/></div>
    <div className="command-metric"><div className="command-metric-top"><span>Без ответственного</span><Icon name="users" size={19}/></div><strong>{a.unassigned}</strong><small>Нужен сотрудник для ответа</small><div className="command-metric-line"/></div>
   </div>
   <div className="command-bottom-grid">
    <section className="command-queue"><div className="command-card-head"><div><div className="eyebrow small">УМНАЯ ОЧЕРЕДЬ / БЕЗ ИИ</div><h2>В первую очередь</h2><p>По сроку ответа, приоритету и непрочитанным сообщениям</p></div><span className="queue-count">{queue.length} обращений</span></div>
     {queue.length?queue.slice(0,7).map((c:any,i:number)=><button className="queue-item" key={c.id} onClick={()=>this.openQueueConversation(c.id)}><span className="queue-rank">{String(i+1).padStart(2,'0')}</span><Avatar name={c.contact_name} size={40}/><span className="queue-person"><strong>{c.contact_name}</strong><small><Provider type={c.channel} small/> {providerName(c.channel)} · {c.reasons[0]||'Требует внимания'}</small></span><span className={'queue-priority '+c.priority}>{PRIORITIES[c.priority]}</span><span className="queue-score">{c.score}<small>баллов</small></span><Icon name="arrow" size={17}/></button>):<div className="command-empty"><Icon name="check" size={22}/> Нет обращений, требующих внимания</div>}
     <div className="command-card-foot"><Icon name="shield" size={14}/> Оценка основана на событиях и регламенте компании, а не на предположениях.</div>
    </section>
    <aside className="command-side">
     <div className="command-side-card"><div className="eyebrow small">КОМАНДА / НАГРУЗКА</div><h3>Распределение работы</h3>{a.workload.length?a.workload.map((m:any)=><div className="workload-row" key={m.id}><div className="workload-name"><span className={'workload-dot '+(m.active?'online':'')}/><strong>{m.name}</strong><small>{m.open} диал.</small></div><div className="workload-track"><div style={{width:(m.open/maxLoad*100)+'%'}}/></div></div>):<p className="no-workload">Доступна только ваша очередь</p>}</div>
     <div className="command-side-card command-how"><div className="eyebrow small">КАК РАБОТАЕТ ПРИОРИТЕТ</div><h3>Никакой чёрной магии.</h3><p>Система учитывает фактическое ожидание клиента, превышение SLA, непрочитанные обращения и установленный сотрудником приоритет.</p><button onClick={()=>this.changeView('rules')}>Настроить правила <Icon name="arrow" size={14}/></button></div>
    </aside>
   </div>
   <div className="command-footer">OSMANX OMNICHAT <span>·</span> КОММУНИКАЦИИ ПОД КОНТРОЛЕМ <span>·</span> ВЕРСИЯ 1.0</div>
  </div>
 }
 renderInbox(){
  const s=this.state,d=s.detail,conv=d?.conversation,demo=s.me.organization.is_demo;
  const contact=s.contactDraft||d?.contact;
  const disabledReply=!s.reply.trim()||s.loading||!!(conv?.reply_lock_owner_id&&conv?.reply_lock_owner_id!==s.me.user.id)||outgoingSize(conv?.channel||'website',s.reply)>outgoingLimit(conv?.channel||'website')||(conv?.channel==='whatsapp'&&conv?.channel_mode==='live'&&!conv?.whatsapp_window_open);
  const messages=d?.messages||[];
  const followupDate=contact?.next_followup_at?new Date(contact.next_followup_at*1000-new Date().getTimezoneOffset()*60000).toISOString().slice(0,16):'';
  return <div className={'inbox-layout quiet-layout '+(s.mobilePane==='chat'?'mobile-chat ':'')+(s.customerOpen?'show-customer ':'')+(s.advancedFilters?'show-advanced ':'')+(s.chatActionsOpen?'show-actions ':'')}>
   <section className="inbox-list" aria-label="Все переписки">
    <div className="inbox-list-head">
     <div className="heading-line"><button className="icon-btn quiet-mobile-menu" aria-label="Открыть меню" onClick={()=>this.setState({sidebarOpen:true})}><Icon name="menu" size={21}/></button><h1>Входящие</h1><button className="quiet-refresh" title="Обновить диалоги" aria-label="Обновить диалоги" onClick={()=>this.loadConvs()}><Icon name="arrow" size={18}/></button></div>
     <div className="search-wrap"><Icon name="search" size={21}/><input aria-label="Поиск по перепискам" value={s.search} onChange={(e:any)=>this.changeSearch(e.target.value)} placeholder="Поиск по перепискам..."/></div>
     <div className="quiet-quick-filters" aria-label="Быстрые фильтры переписок">
       {[['','Все'],['new','Новые'],['waiting','Ожидают']].map(([id,label])=><button key={id} className={s.statusFilter===id?'active':''} aria-pressed={s.statusFilter===id} onClick={()=>this.changeFilter('statusFilter',id)}>{label}</button>)}
     </div>
     <div className="quiet-channels"><select aria-label="Показать канал" value={s.channelFilter} onChange={(e:any)=>this.changeFilter('channelFilter',e.target.value)}><option value="">Все каналы</option>{CHANNELS.map(type=><option value={type} key={type}>{providerName(type)}</option>)}</select><button className={'quiet-filter-btn '+(s.advancedFilters?'active':'')} aria-label={s.advancedFilters?'Скрыть расширенные фильтры':'Открыть расширенные фильтры'} aria-expanded={s.advancedFilters} onClick={()=>this.setState({advancedFilters:!s.advancedFilters})}><Icon name="filter" size={17}/></button></div>
     {s.advancedFilters&&<div className="quiet-advanced-filters"><label>Статус <select value={s.statusFilter} aria-label="Фильтр статуса" onChange={(e:any)=>this.changeFilter('statusFilter',e.target.value)}><option value="">Все статусы</option>{Object.keys(STATUS).map(k=><option value={k} key={k}>{STATUS[k]}</option>)}</select></label><label>Приоритет<select value={s.priorityFilter} aria-label="Фильтр приоритета" onChange={(e:any)=>this.changeFilter('priorityFilter',e.target.value)}><option value="">Все приоритеты</option>{Object.keys(PRIORITIES).map(k=><option value={k} key={k}>{PRIORITIES[k]}</option>)}</select></label><label>Сортировка<select value={s.sortFilter} aria-label="Сортировка переписок" onChange={(e:any)=>this.changeFilter('sortFilter',e.target.value)}><option value="recent">Сначала новые</option><option value="priority">По важности</option><option value="oldest">Сначала старые</option></select></label><button className="quiet-filter-action" onClick={()=>this.changeFilter('archivedFilter',!s.archivedFilter)}>{s.archivedFilter?'Показать активные':'Показать архив'}</button><button className="quiet-filter-action" onClick={()=>this.setState({modal:'view',viewName:'',viewShared:false})}>Сохранить фильтры</button>{s.views.length>0&&<div className="quiet-saved-views">{s.views.map((v:any)=><button key={v.id} onClick={()=>this.applySavedView(v)}>{v.name}</button>)}</div>}</div>}
    </div>
    <div className="conversation-scroll">{s.convs.length===0?<div className="empty-list"><Icon name="inbox" size={30}/><h3>{s.me.organization.is_demo?'Нет диалогов по фильтру':'Здесь появятся сообщения'}</h3><p>{s.me.organization.is_demo?'Очистите фильтр, чтобы увидеть тестовые обращения.':'Когда клиент напишет в подключённый канал, обращение сразу появится здесь.'}</p>{!s.me.organization.is_demo&&['owner','admin'].includes(s.me.role)&&<button className="btn primary" onClick={()=>this.changeView('start')}>Настроить первый канал <Icon name="arrow" size={15}/></button>}{(s.channelFilter||s.statusFilter||s.search||s.priorityFilter)&&<button className="btn ghost" onClick={()=>this.setState({search:'',channelFilter:'',statusFilter:'',priorityFilter:''},()=>this.loadConvs())}>Сбросить поиск и фильтры</button>}</div>:s.convs.map((item:any)=><button key={item.id} className={'conversation-card '+(s.selected===item.id?'selected':'')} onClick={()=>this.select(item.id)}><div className="conv-avatar"><Provider type={item.channel}/></div><div className="conv-body"><div className="conv-top"><strong>{item.contact_name}</strong><time>{fmt(item.last_message_at)}</time></div><div className="conv-bottom"><p>{this.drafts[item.id]?'Черновик: '+this.drafts[item.id]:item.last_message||'Вложение'}</p>{item.unread_count>0&&<span className="unread-badge">{item.unread_count}</span>}</div></div></button>)}</div>
    {demo&&<div className="list-foot"><span className="online-dot"/>Демонстрационные переписки</div>}
   </section>
   <section className="chat-pane" aria-label="Активная переписка">
    {!conv?<div className="chat-empty"><div className="chat-empty-icon"><Icon name="inbox" size={28}/></div><h2>Выберите диалог</h2><p>Все сообщения ваших каналов собраны в одном окне.</p></div>:<>
     <div className="chat-topbar"><button className="icon-btn mobile-back" aria-label="К списку переписок" onClick={()=>this.setState({mobilePane:'list',customerOpen:false})}><Icon name="back" size={20}/></button><Avatar name={conv.contact_name} size={49}/><div className="chat-title"><strong>{conv.contact_name}</strong><small><Provider type={conv.channel} small/> {providerName(conv.channel)}{demo&&<span className="quiet-demo-inline"> · демо</span>}</small></div><button className="customer-toggle" aria-label={s.customerOpen?'Скрыть карточку клиента':'Показать карточку клиента'} aria-expanded={s.customerOpen} title="Карточка клиента" onClick={()=>this.setState({customerOpen:!s.customerOpen})}><Icon name="users" size={20}/></button><button className="chat-actions-toggle" aria-label="Действия с диалогом" aria-expanded={s.chatActionsOpen} onClick={()=>this.setState({chatActionsOpen:!s.chatActionsOpen})}>•••</button>
      {s.chatActionsOpen&&<div className="quiet-actions-menu"><strong>Управление диалогом</strong><label>Статус<select aria-label="Статус диалога" value={conv.status} onChange={(e:any)=>this.updateConv('status',e.target.value)}>{Object.keys(STATUS).map(k=><option value={k} key={k}>{STATUS[k]}</option>)}</select></label><label>Приоритет<select aria-label="Приоритет диалога" value={conv.priority||'normal'} onChange={(e:any)=>this.setPriority(e.target.value)}>{Object.keys(PRIORITIES).map(k=><option value={k} key={k}>{PRIORITIES[k]}</option>)}</select></label><button onClick={()=>this.claimReply(conv.reply_lock_owner_id===s.me.user.id)} disabled={s.loading||!!(conv.reply_lock_owner_id&&conv.reply_lock_owner_id!==s.me.user.id)}>{conv.reply_lock_owner_id===s.me.user.id?'Освободить диалог':conv.reply_lock_owner_id?'Диалог занят коллегой':'Занять диалог на 2 минуты'}</button><button onClick={()=>this.updateConv('pin',true)}>{conv.pinned?'Открепить':'Закрепить диалог'}</button><button onClick={()=>this.setState({showQuickReplies:true,chatActionsOpen:false})}>Шаблоны ответов</button><button onClick={()=>this.setState({customerOpen:true,tab:'notes',chatActionsOpen:false})}>Внутренние заметки</button><button onClick={()=>{this.setState({customerOpen:true,tab:'activity',chatActionsOpen:false});this.loadActivity(conv.id)}}>История действий</button></div>}
     </div>
     <div className="chat-content">
      {conv.reply_lock_owner_id&&<div className="lease-hint"><Icon name="shield" size={15}/>{conv.reply_lock_owner_id===s.me.user.id?'Вы отвечаете в этом диалоге':'Диалог занят другим сотрудником'}</div>}
      <div className="chat-messages" ref={(el:any)=>{this.chatScroll=el}}>
       {s.detail?.message_paging?.has_older&&<div className="history-older-control"><button type="button" onClick={this.loadOlderMessages} disabled={s.olderLoading}>{s.olderLoading?'Загружаем историю…':'Показать более ранние сообщения'}</button></div>}
       {messages.length>0&&<div className="chat-date-divider"><span>Переписка</span></div>}{messages.map((m:any)=><div key={m.id} className={'message-line '+(m.direction==='out'?'outbound':'inbound')}>
       {m.direction!=='out'&&<Avatar name={conv.contact_name} size={34}/>}
       <div className="message-stack"><div className="message-bubble">{m.is_demo&&<span className="message-demo-label">ДЕМО</span>}<div className="message-text">{m.body}</div>{m.kind==='whatsapp_template'&&<div className="wa-template-badge">Шаблон WhatsApp · Meta API</div>}{m.attachment&&m.kind!=='whatsapp_template'&&<div className="message-attachment">{(m.attachment.type==='image'||m.attachment.type==='sticker')?<img loading="lazy" alt="Вложение в переписке" src={m.attachment.provider==='whatsapp'?'/api/media/'+m.id:m.attachment.url||''}/>:<a href={m.attachment.provider==='whatsapp'?'/api/media/'+m.id:m.attachment.url||'#'} target="_blank" rel="noreferrer noopener"><Icon name="note" size={14}/> Открыть вложение</a>}</div>}</div><div className="message-meta">{fmt(m.created_at)} {m.direction==='out'&&<span className={'delivery-indicator delivery-'+(m.delivery_status||'unconfirmed')} title={deliveryLabel(m.delivery_status,conv.channel)}>{deliveryLabel(m.delivery_status,conv.channel)}</span>}</div></div>
      </div>)}</div>
      <div className="composer">
       {conv.outbound_paused&&<div className="outbound-stop-note" role="status"><Icon name="shield" size={16}/><span><strong>{conv.organization_outbound_paused?'Компания приостановила все новые исходящие.':'Отправка через этот аккаунт приостановлена.'}</strong> Ответ сохранится в очереди, но не уйдёт клиенту до решения администратора.</span></div>}
       {s.showQuickReplies&&<div className="composer-quick"><button className="quick-close" aria-label="Скрыть шаблоны" onClick={()=>this.setState({showQuickReplies:false})}><Icon name="close" size={14}/></button>{s.templates.length?s.templates.map((t:any)=><button key={t.id} onClick={()=>{this.changeReply(t.body);this.setState({showQuickReplies:false})}}>{t.title}</button>):<button onClick={()=>{this.changeReply('Здравствуйте! Чем можем вам помочь?');this.setState({showQuickReplies:false})}}>Приветствие</button>}</div>}
       <div className="composer-entry"><button className="quiet-attach" aria-label="Прикрепить файл" title="Отправка вложений появится после проверки API каждого канала" onClick={()=>this.notify('Исходящие вложения ещё не поддерживаются для всех каналов. Пока доступен текстовый ответ.')}><svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M20 12.5 11.5 21a6 6 0 0 1-8.5-8.5L13 2.5a4 4 0 0 1 5.7 5.7L8.2 18.7a2 2 0 0 1-2.8-2.8l9.2-9.2"/></svg></button><textarea aria-label="Текст ответа" rows={1} placeholder="Введите сообщение..." value={s.reply} onChange={(e:any)=>this.changeReply(e.target.value)} onKeyDown={(e:any)=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();this.send()}}}/><button className="quiet-emoji" aria-label="Вставить эмодзи" aria-expanded={s.showEmoji} onClick={()=>this.setState({showEmoji:!s.showEmoji})}>☺</button>{s.showEmoji&&<div className="quiet-emoji-menu">{['🙂','😊','👍','❤️','🙏','👋'].map((emoji:string)=><button key={emoji} onClick={()=>this.appendEmoji(emoji)}>{emoji}</button>)}</div>}<button className="send-btn" aria-label="Отправить ответ" title="Отправить ответ" disabled={disabledReply} onClick={this.send}><Icon name="send" size={23}/></button></div>
       {conv.channel==='whatsapp'&&conv.channel_mode==='live'&&<div className="wa-composer-actions">
        {conv.whatsapp_window_open===false&&<span>Окно обычных ответов закрыто. Отправить можно только одобренный шаблон.</span>}
        <button className="btn secondary" onClick={this.openWaTemplates} disabled={s.loading}>
         <Icon name="note" size={16}/> Одобренный шаблон WhatsApp
        </button>
       </div>}
       {outgoingSize(conv.channel,s.reply)>outgoingLimit(conv.channel)&&<div className="quiet-length-alert">Превышен лимит сообщения для {providerName(conv.channel)}</div>}
      </div>
     </div>
     {s.customerOpen&&<aside className="details-pane" aria-label="Карточка клиента">
      <div className="quiet-detail-head"><div><h2>{d.contact.name}</h2><div className="quiet-detail-channel"><Provider type={conv.channel} small/>{providerName(conv.channel)}</div></div><button className="quiet-detail-close" title="Свернуть карточку клиента" aria-label="Свернуть карточку клиента" onClick={()=>this.setState({customerOpen:false})}><Icon name="chevron" size={19}/></button></div>
      {s.tab==='info'?<div className="details-scroll">
       <div className="detail-section quiet-tags"><h3>Теги</h3><div className="quiet-tag-list">{(contact?.tags||[]).map((tag:string)=><span className="quiet-tag" key={tag}>{tag}<button aria-label={'Удалить тег '+tag} onClick={()=>this.removeCustomerTag(tag)}>×</button></span>)}</div>{s.tagEditing?<div className="quiet-tag-edit"><input autoFocus value={s.tagInput} aria-label="Новый тег" placeholder="Название тега" onChange={(e:any)=>this.setState({tagInput:e.target.value})} onKeyDown={(e:any)=>{if(e.key==='Enter')this.addCustomerTag();if(e.key==='Escape')this.setState({tagEditing:false,tagInput:''})}}/><button onClick={this.addCustomerTag} disabled={!s.tagInput.trim()}>Добавить</button></div>:<button className="quiet-add-tag" onClick={()=>this.setState({tagEditing:true})}><Icon name="plus" size={16}/> Добавить тег</button>}</div>
       <div className="detail-section"><h3>Стадия сделки</h3><select aria-label="Этап сделки" value={contact?.stage||d.contact.stage} onChange={(e:any)=>{const next={...contact,stage:e.target.value};this.setState({contactDraft:next});this.saveContact(next)}}>{Object.keys(STAGES).map(k=><option value={k} key={k}>{STAGES[k]}</option>)}</select></div>
       <div className="detail-section"><h3>Ответственный</h3><select aria-label="Ответственный" value={conv.assigned_user_id||''} onChange={(e:any)=>this.updateConv('assign',e.target.value||null)} disabled={!['owner','admin','lead'].includes(s.me.role)}><option value="">Не назначен</option>{s.team.map((m:any)=><option value={m.id} key={m.id}>{m.name}</option>)}</select></div>
       <div className="detail-section"><h3>Следующий контакт</h3>{(s.followupEditing||followupDate)?<input className="quiet-followup" type="datetime-local" aria-label="Дата следующего контакта" value={followupDate} onChange={(e:any)=>this.setState({contactDraft:{...contact,next_followup_at:e.target.value?Date.parse(e.target.value)/1000:null}})} onBlur={()=>{if(contact&&contact.next_followup_at!==d.contact.next_followup_at)this.saveContact(contact);this.setState({followupEditing:false})}}/>:<button className="quiet-followup-prompt" onClick={()=>this.setState({followupEditing:true})}><Icon name="clock" size={18}/> Выбрать дату и время</button>}</div>
       <button className="quiet-details-more" onClick={()=>this.setState({customerExtras:!s.customerExtras})} aria-expanded={s.customerExtras}>{s.customerExtras?'Скрыть дополнительные поля':'Дополнительные данные'}<Icon name="chevron" size={15}/></button>
       {s.customerExtras&&<div className="quiet-extra-fields"><label>Сумма сделки<input type="number" min="0" aria-label="Сумма сделки" value={contact?.deal_amount??''} placeholder="Не указана" onChange={(e:any)=>this.setState({contactDraft:{...contact,deal_amount:e.target.value?Number(e.target.value):null}})}/></label><label className="tiny-check"><input type="checkbox" checked={!!contact?.deal_confirmed} onChange={(e:any)=>this.setState({contactDraft:{...contact,deal_confirmed:e.target.checked}})}/> Сделка подтверждена</label><label>Телефон<input aria-label="Телефон" value={contact?.phone||''} placeholder="Не указан" onChange={(e:any)=>this.setState({contactDraft:{...contact,phone:e.target.value}})}/></label><button className="btn secondary wide" onClick={()=>this.saveContact(contact)}><Icon name="check" size={15}/> Сохранить изменения</button></div>}

       {s.customerExtras&&demo&&<div className="quiet-demo-incoming"><h3>Проверить входящее</h3><textarea rows={2} aria-label="Тестовое входящее" placeholder="Напишите сообщение от клиента..." value={s.demoInbound} onChange={(e:any)=>this.setState({demoInbound:e.target.value})}/><button className="btn secondary wide" onClick={this.demoIncoming} disabled={!s.demoInbound.trim()}>Добавить тестовое сообщение</button></div>}
      </div>:s.tab==='notes'?<div className="note-pane"><button className="quiet-back-detail" onClick={()=>this.setState({tab:'info'})}><Icon name="back" size={15}/> К клиенту</button><h3>Внутренние заметки</h3><p className="note-caption">Заметки видят только сотрудники.</p><div className="notes-list">{d.notes.length?d.notes.map((n:any)=><div key={n.id} className="note-card"><p>{n.body}</p><small>{n.author} · {dateFmt(n.created_at)}</small></div>):<p className="empty-note">Заметок пока нет</p>}</div><textarea rows={4} aria-label="Новая заметка" placeholder="Напишите заметку..." value={s.note} onChange={(e:any)=>this.setState({note:e.target.value})}/><button className="btn secondary wide" disabled={!s.note.trim()} onClick={this.addNote}>Сохранить заметку</button></div>:<div className="activity-pane"><button className="quiet-back-detail" onClick={()=>this.setState({tab:'info'})}><Icon name="back" size={15}/> К клиенту</button><h3>История действий</h3>{s.activity.length?s.activity.map((a:any)=><div className="activity-row" key={a.id}><div><strong>{a.title}</strong><small>{a.actor} · {dateFmt(a.created_at)} · {fmt(a.created_at)}</small></div></div>):<p className="empty-note">Записей пока нет</p>}</div>}
     </aside>}
    </>}
   </section>
  </div>
 }

 renderDeals(){const s=this.state;const stages:any=['new','interested','negotiation','payment','success','lost'];return <div className="page-content quiet-deals"><div className="section-head"><div><div className="eyebrow">CRM / ВОРОНКА</div><h1>Сделки</h1><p>Этапы подтверждаются сотрудниками, система не придумывает продажи.</p></div><button className="btn secondary" onClick={()=>this.loadView('deals')}><Icon name="arrow" size={16}/> Обновить</button></div><div className="deals-board">{stages.map((stage:string)=><section className="deals-stage" key={stage}><h3>{STAGES[stage]} <span>{s.contacts.filter((c:any)=>c.stage===stage).length}</span></h3>{s.contacts.filter((c:any)=>c.stage===stage).map((c:any)=><div className="deal-card" key={c.id}><div className="deal-person"><Avatar name={c.name} size={33}/><strong>{c.name}</strong></div><small>{c.deal_amount!=null?formatMoney(c.deal_amount,s.me.organization.currency):'Сумма не указана'}</small><select aria-label={'Этап сделки '+c.name} value={c.stage} onChange={(e:any)=>this.saveContact({...c,stage:e.target.value,deal_confirmed:c.deal_confirmed&&e.target.value==='success'})}>{stages.map((k:string)=><option value={k} key={k}>{STAGES[k]}</option>)}</select></div>)}{!s.contacts.some((c:any)=>c.stage===stage)&&<p className="deals-empty">Пока нет сделок</p>}</section>)}</div></div>}
 renderContacts(){const s=this.state;return <div className="page-content"><div className="section-head"><div><div className="eyebrow">КЛИЕНТЫ / ВЗАИМООТНОШЕНИЯ</div><h1>Клиенты</h1><p>Контакты, этапы сделок и история обращений в одной системе.</p></div><span className="heading-count">{s.contacts.length} контактов</span></div><div className="table-card"><div className="table-heading"><h3>Карточки клиентов</h3><span>Выручка учитывается только после подтверждения</span></div><div className="table-scroll"><table><thead><tr><th>КЛИЕНТ</th><th>ЭТАП</th><th>ТЕГИ</th><th>СУММА</th><th>РЕЗУЛЬТАТ</th></tr></thead><tbody>{s.contacts.map((c:any)=><tr key={c.id}><td><div className="table-name"><Avatar name={c.name} size={33}/><div><b>{c.name}</b><small>{c.phone||'Контакт не указан'}</small></div></div></td><td><select value={c.stage} onChange={(e:any)=>this.saveContact({...c,stage:e.target.value,deal_confirmed:false})}>{Object.keys(STAGES).map(k=><option key={k} value={k}>{STAGES[k]}</option>)}</select></td><td>{c.tags?.map((tag:string)=><span className="tag" key={tag}>{tag}</span>)}{!c.tags?.length&&<span className="muted">—</span>}</td><td className="number">{c.deal_amount!=null?formatMoney(c.deal_amount,s.me.organization.currency):'—'}</td><td>{c.deal_confirmed?<span className="pill green"><Icon name="check" size={13}/> Подтверждено</span>:<span className="pill neutral">Не подтверждено</span>}</td></tr>)}</tbody></table></div></div></div>}
 renderAnalytics(){const a=this.state.analytics;const demo=this.state.me.organization.is_demo;if(!a)return <div className="page-content"><div className="empty-list">Загружаем аналитику...</div></div>;const max=Math.max(1,...a.days.map((x:any)=>x.count));return <div className="page-content"><div className="section-head"><div><div className="eyebrow">МЕТРИКИ / ЭФФЕКТИВНОСТЬ</div><h1>Аналитика коммуникаций</h1><p>Реальные события, длительность ответа и нагрузка на каналы — без выдуманных продаж.</p></div><span className="pill neutral"><span className="dot green"></span>{demo?'Демоданные':'Данные системы'}</span></div>
 <div className="metric-grid"><div className="metric-card"><div className="metric-icon"><Icon name="inbox"/></div><small>Входящие сообщения</small><strong>{a.inbound}</strong><span>За всё время в рабочей области</span></div><div className="metric-card"><div className="metric-icon"><Icon name="clock"/></div><small>Принятие ответа</small><strong>{a.avg_first_reply_min==null?'—':a.avg_first_reply_min+' мин'}</strong><span>От первого обращения до подтверждения API / веб-чата, с R28</span></div><div className="metric-card"><div className="metric-icon"><Icon name="bell"/></div><small>Ожидают подтверждённого ответа</small><strong>{a.no_response}</strong><span>Черновик и очередь не считаются ответом</span></div><div className="metric-card"><div className="metric-icon"><Icon name="check"/></div><small>Нуждаются в проверке</small><strong>{a.outgoing_attention||0}</strong><span>Ошибка или неизвестный результат отправки</span></div></div><p className="metrics-delivery-note" role="status">Исходящих в очереди или обработке: <strong>{a.outgoing_pending||0}</strong>. Показатель времени включает только новые подтверждения с R28; доставку и прочтение отдельно подтверждает площадка.</p>
 <div className="analytics-grid"><div className="chart-card"><div className="card-title"><h3>Динамика обращений</h3><span>Последние 7 дней</span></div><div className="chart-bars">{a.days.map((d:any,i:number)=><div className="bar-column" key={i}><div className="bar-number">{d.count}</div><div className="bar-track"><div className="bar-fill" style={{height:Math.max(4,(d.count/max)*100)+'%'}}></div></div><span>{d.day}</span></div>)}</div></div><div className="chart-card"><div className="card-title"><h3>Источники обращений</h3><span>По количеству диалогов</span></div><div className="channel-chart">{CHANNELS.map(ch=>{const count=a.by_channel[ch]||0;return <div className="channel-row" key={ch}><div className="channel-name"><Provider type={ch}/><strong>{providerName(ch)}</strong><span>{count}</span></div><div className="progress-track"><div className={'progress-fill '+ch} style={{width:(a.conversations?count/a.conversations*100:0)+'%'}}></div></div></div>})}</div></div></div>
 <div className="revenue-row"><div><div className="revenue-head">Подтверждённая выручка</div><strong>{formatMoney(a.confirmed_revenue,a.currency)}</strong><small>Только сделки, отмеченные сотрудником как успешные и подтверждённые</small></div><div><div className="revenue-head">Потенциал сделок</div><strong>{formatMoney(a.potential_revenue,a.currency)}</strong><small>Оценка по суммам, введённым вручную — не фактическая выручка</small></div><div><div className="revenue-head">Конверсия в подтверждённую сделку</div><strong>{a.conversion_pct}%</strong><small>{a.confirmed_deals} подтверждённых сделок из {a.conversations} диалогов</small></div></div><div className="analytics-disclaimer"><Icon name="info" size={17}/> Показатели основаны только на сохранённых событиях. Без данных кассы или подтверждения менеджера платформа не определяет реальные продажи.</div></div>}
 renderRules(){const s=this.state;return <div className="page-content"><div className="section-head"><div><div className="eyebrow">СЦЕНАРИИ / БЕЗ ОБЯЗАТЕЛЬНОГО ИИ</div><h1>Автоматизация</h1><p>Прозрачные правила без искусственного интеллекта: событие → условие → действие.</p></div><button className="btn primary" onClick={()=>this.setState({modal:'rule'})}><Icon name="plus" size={17}/> Новое правило</button></div><div className="flow-visual"><div><div className="flow-step">01</div><Icon name="bell" size={20}/><strong>Событие</strong><small>Новое сообщение</small></div><span className="flow-connector"><Icon name="arrow"/></span><div><div className="flow-step">02</div><Icon name="filter" size={20}/><strong>Условие</strong><small>Ключевая фраза</small></div><span className="flow-connector"><Icon name="arrow"/></span><div><div className="flow-step">03</div><Icon name="sparkles" size={20}/><strong>Действие</strong><small>Добавить тег</small></div></div><div className="table-card"><div className="table-heading"><h3>Активные сценарии</h3><span>{s.rules.length} правил</span></div>{s.rules.length===0?<div className="empty-list"><p>Создайте первое правило для входящих сообщений</p></div>:s.rules.map((r:any)=><div className="rule-row" key={r.id}><div className="rule-icon"><Icon name="flow" size={20}/></div><div><strong>{r.name}</strong><p>{r.condition_type==='always'?'Для каждого сообщения':`Если содержит «${r.condition_value}»`} → {r.action_type==='tag'?`Добавить тег «${r.action_value}»`:r.action_type==='priority'?'Закрепить диалог':r.action_type==='assign_least_busy'?'Назначить свободного менеджера':`Изменить статус: ${r.action_value}`}</p></div><button className={'toggle '+(r.enabled?'on':'')} onClick={()=>this.toggleRule(r.id)} title={r.enabled?'Выключить правило':'Включить правило'} aria-label="Включить или выключить правило"><span/></button></div>)}</div><div className="analytics-disclaimer"><Icon name="info" size={16}/> Правила запускаются при новых входящих сообщениях; не меняют существующие переписки задним числом.</div></div>}
 renderWebsites(){
  const s=this.state,selected=s.sites.find((w:any)=>w.id===s.siteSelected);
  const canEdit=['owner','admin'].includes(s.me.role);
  const snippet=(w:any)=>'<script async src="'+(location.origin==='null'?'https://your-omnichat-domain.example':location.origin)+'/assets/embed.js" data-omnichat-key="'+w.key+'"></script>';
  return <div className="page-content website-page">
   <div className="section-head"><div><div className="eyebrow">СОБСТВЕННЫЙ КАНАЛ / БЕЗ ВНЕШНИХ API-КЛЮЧЕЙ</div><h1>Чат для вашего сайта</h1><p>Собственный чат для сайта. Все обращения посетителей попадают в единый центр сообщений.</p></div><div className="website-top-label"><span className="dot green"/> СОБСТВЕННЫЙ КАНАЛ</div></div>
   <div className="site-feature-grid"><div className="site-feature"><Icon name="shield" size={21}/><strong>Защита по архитектуре</strong><span>Независимые сессии посетителей и защищённый доступ</span></div><div className="site-feature"><Icon name="inbox" size={21}/><strong>Единая очередь обращений</strong><span>Сообщения настоящих посетителей сайта, а не имитация внешнего API</span></div><div className="site-feature"><Icon name="clock" size={21}/><strong>Мгновенный контакт</strong><span>Ответ оператора появляется прямо в виджете</span></div></div>
   {canEdit&&<div className="site-config"><div className="site-config-title"><div className="eyebrow">01 / НАСТРОЙКА КАНАЛА</div><h2>{selected?'Редактирование виджета':'Новый виджет сайта'}</h2><p>Для публичных сайтов разрешены только адреса HTTPS. Локальный HTTP — для разработки.</p></div><div className="site-form"><label>Название виджета<input placeholder="Поддержка клиентов" value={s.siteName} onChange={(e:any)=>this.setState({siteName:e.target.value})}/></label><label>Разрешённые адреса сайтов<textarea rows={2} placeholder={'https://store.example.com\nhttps://www.store.example.com'} value={s.siteOrigins} onChange={(e:any)=>this.setState({siteOrigins:e.target.value})}/></label><label>Приветствие посетителя<input value={s.siteGreeting} onChange={(e:any)=>this.setState({siteGreeting:e.target.value})}/></label><label>Акцентный цвет<input type="color" value={s.siteAccent} onChange={(e:any)=>this.setState({siteAccent:e.target.value})}/></label><div className="site-form-actions"><button className="btn primary" disabled={s.loading||!s.siteName.trim()||!s.siteOrigins.trim()} onClick={()=>this.saveSiteWidget()}><Icon name={selected?'check':'plus'} size={16}/>{selected?'Сохранить изменения':'Создать канал сайта'}</button>{selected&&<button className="btn secondary" onClick={()=>this.clearSiteForm()}>Отменить изменения</button>}</div></div></div>}
   <div className="site-channels-header"><div><div className="eyebrow">02 / УСТАНОВКА</div><h2>Подключённые сайты <span>{s.sites.length}</span></h2></div></div>
   {s.sites.length===0?<div className="site-empty"><div className="site-empty-icon"><Icon name="globe" size={32}/></div><h3>Сайты ещё не добавлены</h3><p>Создайте канал и добавьте код на сайт. Сообщения сразу появятся в разделе «Сообщения» с фильтром «Чат сайта».</p></div>:
   <div className="site-cards">{s.sites.map((w:any)=><article className="site-card" key={w.id}><div className="site-card-heading"><div className="site-card-identity"><div className="site-card-logo"><Icon name="globe" size={21}/></div><div><h3>{w.name}</h3><p>{w.allowed_origins.join(' / ')}</p></div></div><span className={'pill '+(w.enabled?'green':'neutral')}><span className="dot"/>{!w.enabled?'Приостановлен':w.is_demo?'Тестовый':'Активен'}</span></div><div className="site-card-content"><div className="site-embed"><div className="site-small-label">УСТАНОВКА ОДНОЙ СТРОКОЙ</div><pre>{snippet(w)}</pre><div className="site-card-actions"><button className="btn secondary" onClick={()=>this.copySnippet(snippet(w))}><Icon name="copy" size={16}/> Скопировать код</button><button className="btn secondary" onClick={()=>window.open('/widget/'+w.key,'_blank','noopener,noreferrer')}><Icon name="arrow" size={15}/> Открыть предпросмотр</button>{canEdit&&<button className="btn secondary" onClick={()=>this.startEditSite(w)}><Icon name="settings" size={15}/> Изменить</button>}{canEdit&&<button className="btn ghost" onClick={()=>this.toggleSiteWidget(w)}>{w.enabled?'Приостановить':'Включить'}</button>}{canEdit&&<button className="btn ghost" onClick={()=>this.rotateSiteWidget(w)}><Icon name="shield" size={14}/> Сменить ключ</button>}</div><div className="site-tip">Вставьте скрипт перед закрывающим тегом body. Если сайт использует строгую политику безопасности, разрешите загрузку скриптов вашего домена.</div></div><div className="site-visual"><div className="site-preview-title">ПРЕДПРОСМОТР ВИДЖЕТА</div><iframe loading="lazy" title={'Предпросмотр: '+w.name} src={'/widget/'+w.key} /></div></div></article>)}</div>}
   <div className="analytics-disclaimer"><Icon name="shield" size={16}/> Публичный ключ определяет виджет, но не раскрывает переписки. Посетители получают отдельные токены доступа, ограничение частоты запросов и изолированные записи в базе.</div>
  </div>
 }
 renderOperations(){const s=this.state,o=s.operations;if(!o)return <div className="page-content">Загружаем диагностику доставки...</div>;
 const queues=[['queued','В очереди'],['processing','Отправляется'],['uncertain','Нужна проверка'],['failed','Ошибка'],['done','Принято API']];
 const humanStatus:any={queued:'В очереди',processing:'Отправляется',uncertain:'Требует проверки',failed:'Ошибка',done:'Принято API',cancelled:'Отменено до отправки'};
 const inbound=o.inbound||{};
 const nextStep=o.organization_outbound_paused_at?'Все новые исходящие компании остановлены. Проверьте причины инцидента и разрешения аккаунтов перед возобновлением.':o.reconciliation_required>0
 ?'Есть ответы с неизвестным результатом. Сначала проверьте их в исходной соцсети: повторная отправка может создать дубль.'
 :o.outbox_delayed_over_5_min>0
 ?'Некоторые ответы ждут больше пяти минут. Проверьте подключение канала и состояние фонового обработчика.'
 :inbound.failed>0
 ?'Есть входящие события, которые не удалось обработать. Проверьте настройки канала и используйте повтор после устранения ошибки.'
 :o.outbox.failed>0
 ?'Есть сообщения с ошибкой. Откройте строку ниже и проверьте, почему площадка не приняла ответ.'
 :'Очередь не требует срочного вмешательства. Новые ответы будут обрабатываться автоматически.';
 return <div className="page-content operations-page"><div className="section-head"><div><div className="eyebrow">ОПЕРАЦИИ / КОНТРОЛЬ ДОСТАВКИ</div><h1>Контроль доставки</h1><p>Входящие события, исходящая очередь и состояние каналов. Подтверждения не подменяются предположениями.</p></div><button className="btn secondary" onClick={()=>this.loadView('operations')}><Icon name="arrow" size={16}/> Обновить состояние</button></div>
 <section className={'ops-global-guard '+(o.organization_outbound_paused_at?'is-paused':'')} aria-label="Аварийная защита компании" role="status">
  <div className="ops-global-guard-title"><Icon name="shield" size={23}/><div><div className="eyebrow">АВАРИЙНАЯ ЗАЩИТА КОМПАНИИ</div><strong>{o.organization_outbound_paused_at?'Все новые исходящие приостановлены':'Отправка компании разрешена'}</strong><p>{o.organization_outbound_paused_at
   ?'Входящие сообщения работают. Новые ответы через соцсети ждут в очереди. Начатые до паузы запросы могли завершиться.'
   :'При инциденте можно остановить отправки всех аккаунтов одним действием. Отдельные паузы каналов сохранятся.'}</p></div></div>
  {['owner','admin'].includes(s.me.role)&&!s.me.organization.is_demo&&<button className={'btn '+(o.organization_outbound_paused_at?'secondary':'ghost')} disabled={s.loading}
    onClick={()=>this.pauseCompanyOutbound(o.organization_outbound_paused_at||null)}>
   <Icon name={o.organization_outbound_paused_at?'check':'shield'} size={16}/>
   {o.organization_outbound_paused_at?'Возобновить все исходящие':'Остановить все исходящие'}
  </button>}
 </section>
 <section className="ops-section ops-r36-safety" aria-label="Временные ограничения отправки">
  <div className="ops-title"><div><div className="eyebrow">R36 / КОНТРОЛЬ РИСКОВ</div><h2>Временная пауза отправок</h2><p>Для аварий и технических работ. Новые захваты блокируются в базе; уже начатые запросы к площадке могут завершиться.</p></div>
   {['owner','admin'].includes(s.me.role)&&<button className="btn secondary" onClick={this.exportSafeSupport} disabled={s.loading}><Icon name="shield" size={16}/> Скачать обезличенный отчёт</button>}
  </div>
  <div className="ops-r36-indicators" role="status">
   <div><span>Активных ограничений</span><strong>{s.dispatchPauses?.pauses?.length||0}</strong></div>
   <div><span>Исходящих с неизвестным результатом</span><strong>{s.deliveryTelemetry?.outbox?.uncertain||0}</strong></div>
   <div><span>Очередь более пяти минут</span><strong>{s.deliveryTelemetry?.delayed_queued_over_5m||0}</strong></div>
  </div>
  {s.deliveryTelemetry?.alerts?.length>0&&<div className="ops-r36-alerts" role="status">{s.deliveryTelemetry.alerts.map((a:any)=><span className="pill amber" key={a.code}>{({uncertain:'Нужна проверка отправок',worker_offline:'Фоновый обработчик не отвечает',queue_delayed:'Задержка очереди',recent_failures:'Ошибки отправки',delivery_paused:'Отправка приостановлена'} as any)[a.code]||a.code}: {a.count}</span>)}</div>}
  {['owner','admin'].includes(s.me.role)&&<div className="ops-r36-controls">
   <label>Область<select aria-label="Область временной паузы" value={s.opsPauseChannel} onChange={(e:any)=>this.setState({opsPauseChannel:e.target.value})}>
    <option value="">Вся компания</option>{(o.channels||[]).filter((c:any)=>c.mode==='live').map((c:any)=><option key={c.id} value={c.id}>{providerName(c.provider)} · {c.name}</option>)}
   </select></label>
   <label>Причина<select aria-label="Причина временной паузы" value={s.opsPauseReason} onChange={(e:any)=>this.setState({opsPauseReason:e.target.value})}>
    <option value="incident">Инцидент</option><option value="provider_outage">Сбой площадки</option><option value="credential_rotation">Замена ключа</option><option value="maintenance">Обслуживание</option>
   </select></label>
   <label>Автоматическое снятие<select aria-label="Срок временной паузы" value={s.opsPauseMinutes} onChange={(e:any)=>this.setState({opsPauseMinutes:e.target.value})}>
    <option value="15">15 минут</option><option value="60">1 час</option><option value="240">4 часа</option><option value="1440">24 часа</option><option value="unlimited">Только вручную</option>
   </select></label>
   <button className="btn secondary" disabled={s.loading} onClick={this.pauseDispatch}><Icon name="shield" size={16}/> Включить паузу</button>
  </div>}
  {(s.dispatchPauses?.pauses||[]).length>0&&<div className="ops-r36-pauses">{s.dispatchPauses.pauses.map((entry:any,i:number)=><div key={(entry.channel_id||'all')+i}><span className="pill amber">Пауза</span><strong>{entry.channel_id?((o.channels||[]).find((v:any)=>v.id===entry.channel_id)?.name||'Аккаунт'):'Вся компания'}</strong><small>{({incident:'Инцидент',provider_outage:'Сбой площадки',credential_rotation:'Замена ключа',maintenance:'Обслуживание'} as any)[entry.reason_code]||'Обслуживание'} · {entry.expires_at?('до '+new Date(entry.expires_at*1000).toLocaleString('ru-RU')):'снятие вручную'}</small>{['owner','admin'].includes(s.me.role)&&<button className="btn ghost" onClick={()=>this.resumeDispatch(entry.channel_id)} disabled={s.loading}>Снять</button>}</div>)}</div>}
 </section>
 <section className="ops-next-step" aria-label="Следующее действие"><div><strong>Что сделать сейчас</strong><p>{nextStep}</p></div>{o.reconciliation_required>0&&<span className="pill amber">{o.reconciliation_required} {o.reconciliation_required===1?'требует':'требуют'} сверки</span>}</section>
 <div className="ops-metrics">{queues.map(([key,label]:any)=><div className={'ops-metric '+(key==='uncertain'&&o.outbox[key]?'warning':'')} key={key}><span>{label}</span><strong>{o.outbox[key]||0}</strong><small>{key==='uncertain'?'Требуется ручная проверка':key==='done'?'Принято сервисом / проверено':'Надёжная очередь отправки'}</small></div>)}</div>
 <div className={'worker-signal '+((o.worker?.code==='working'||o.worker?.code==='not_needed')?'healthy':'attention')} role="status" aria-live="polite">
   <Icon name={o.worker?.code==='working'?'check':'activity'} size={20}/>
   <div><strong>{o.worker?.summary||'Состояние обработчика неизвестно'}</strong>
     <p>{o.worker?.code==='working'?'Фоновая отправка работает. Принятие внешним API не равно доставке клиенту.':
         o.worker?.code==='not_needed'?'Новые сообщения с сайтов обрабатываются отдельно. Подключённые соцсети требуют работающего обработчика.':
         o.worker?.code==='checking'?'Сервер запущен, но завершённого цикла пока нет. Подождите немного и обновите страницу.':
         'Если внешние ответы стоят в очереди, проверьте запуск фонового обработчика на сервере.'}</p>
   </div>
   <button className="btn secondary" onClick={()=>this.loadView('operations')} disabled={s.loading}>Проверить снова</button>
 </div>
 <div className="ops-stats"><div><Icon name="globe" size={20}/><strong>{o.channel_total}</strong><span>Подключённые и тестовые каналы</span></div><div><Icon name="inbox" size={20}/><strong>{o.messages_total}</strong><span>Сохранённые сообщения</span></div><div><Icon name="clock" size={20}/><strong>{o.outbox_delayed_over_5_min}</strong><span>Ожидают более 5 минут</span></div></div>
 <section className="ops-section"><div className="ops-title"><div><div className="eyebrow">01 / СОСТОЯНИЕ ОТПРАВКИ</div><h2>Исходящая очередь</h2></div><div className="ops-title-tags"><span className="pill neutral">Отменено до отправки: {o.outbox.cancelled||0}</span>{o.active_sender_accounts>0&&<span className="pill green">Сейчас отправляют: {o.active_sender_accounts} {o.active_sender_accounts===1?'аккаунт':'аккаунтов'}</span>}{o.outbound_paused_channels>0&&<span className="pill amber">Аккаунтов с паузой отправки: {o.outbound_paused_channels}</span>}{o.safe_recoveries_last_7_days>0&&<span className="pill green">Восстановлено безопасно: {o.safe_recoveries_last_7_days}</span>}{o.whatsapp_receipts_last_24h>0&&<span className="pill neutral">Квитанций WhatsApp за 24 ч: {o.whatsapp_receipts_last_24h}</span>}<span className="pill neutral">Статусы основаны на событиях в базе</span></div></div>
 {s.operationsJobs.length===0?<div className="ops-empty">Исходящих заданий пока нет. Ответы в чат сайта доставляются напрямую и не попадают в очередь внешних API.</div>:
 <div className="table-scroll"><table><thead><tr><th>ИДЕНТИФИКАТОР</th><th>СТАТУС</th><th>ПОПЫТКИ</th><th>ОТВЕТ ПЛОЩАДКИ</th><th>ПРОВЕРКА</th></tr></thead><tbody>{s.operationsJobs.map((j:any)=><tr key={j.id}><td className="ops-mono">{j.message_id.slice(0,13)}...</td><td><span className={'pill '+(j.status==='uncertain'||j.status==='failed'?'amber':j.status==='done'?'green':'neutral')}>{j.processing_phase||humanStatus[j.status]||'Неизвестно'}</span></td><td>{j.attempts}</td><td className="ops-error">{j.last_error||'—'}</td><td><div className="ops-job-actions">
 {j.status==='uncertain'&&['owner','admin'].includes(s.me.role)&&<button className="btn secondary" onClick={()=>this.setState({modal:'reconcile',reconcileJob:j,reconcileStatus:'accepted',reconcileEvidence:'',reconcileExternalId:''})}>Проверить результат</button>}
 <button className="btn ghost" disabled={s.loading} onClick={()=>this.loadJobEvents(j.id)}>История</button>
 {j.can_cancel&&['owner','admin','lead'].includes(s.me.role)&&<button className="btn secondary" disabled={s.loading} onClick={()=>this.cancelQueued(j)}>Отменить до отправки</button>}
 {j.can_retry_verified&&['owner','admin'].includes(s.me.role)&&<button className="btn secondary" disabled={s.loading} onClick={()=>this.setState({modal:'retry-outbox',outboxRetryJob:j,outboxRetryEvidence:'',outboxRetryVerified:false})}>Повторить после проверки</button>}
 {!['uncertain','queued','failed'].includes(j.status)&&<span className="muted">—</span>}
 </div></td></tr>)}</tbody></table></div>}
 </section>
 {s.selectedJobEvents&&<section className="ops-section ops-r36-history" aria-label="История технических состояний">
  <div className="ops-title"><div><div className="eyebrow">R36 / ИСТОРИЯ</div><h2>Переходы исходящего задания</h2><p>Только технические статусы и время. Текст сообщения и данные клиента не сохраняются.</p></div><button className="btn ghost" onClick={()=>this.setState({selectedJobEvents:null})}>Скрыть</button></div>
  <div className="ops-r36-timeline">{s.selectedJobEvents.events.length===0?<span className="muted">Событий пока нет: журнал начинается с обновления R36.</span>:s.selectedJobEvents.events.map((item:any,i:number)=><div key={i}><span>{new Date(item.at*1000).toLocaleString('ru-RU')}</span><strong>{item.event_code}</strong><small>{item.from_status} → {item.to_status} · попытки: {item.attempts}</small></div>)}{s.selectedJobEvents.truncated&&<span className="muted">Показаны последние 100 событий</span>}</div>
 </section>}
 <section className="ops-section ops-inbound-section" aria-label="Надёжность входящих событий">
  <div className="ops-title"><div><div className="eyebrow">02 / ЗАЩИТА ВХОДЯЩИХ</div><h2>Приём обращений</h2><p className="ops-inbound-intro">Событие сначала сохраняется зашифрованным. При сбое обработка повторится. Текст клиента в журнале не отображается.</p></div>
    <div className="ops-title-tags">{(inbound.failed||0)>0&&<span className="pill amber">Требуют разбора: {inbound.failed}</span>}{(inbound.dismissed||0)>0&&<span className="pill neutral">Закрыты с удалением: {inbound.dismissed}</span>}{(inbound.queued||0)+(inbound.retrying||0)+(inbound.processing||0)>0&&<span className="pill neutral">В обработке: {(inbound.queued||0)+(inbound.retrying||0)+(inbound.processing||0)}</span>}</div>
  </div>
  <div className="ops-inbound-control" aria-label="Управление обработкой входящих">
    <div className="ops-control-copy"><strong>Управление при инциденте</strong>
      <span>Пауза останавливает обработку, но не приём проверенных webhook. События остаются зашифрованными в очереди.</span>
      {!!o.inbound_delayed_over_10_min&&<span className="ops-aging-alert">Ожидают более 10 минут: {o.inbound_delayed_over_10_min}</span>}
    </div>
    <div className="ops-control-actions">
     <label className="ops-control-select">Область
      <select aria-label="Область обработки входящих" value={s.inboundControlScope}
       onChange={(e:any)=>this.setState({inboundControlScope:e.target.value})}>
       <option value="organization">Вся компания</option>
       {(o.channels||[]).filter((c:any)=>c.mode==='live').map((c:any)=><option key={c.id} value={c.id}>{providerName(c.provider)} · {c.name}</option>)}
      </select>
     </label>
     {(()=>{
       const item=(o.channels||[]).find((c:any)=>c.id===s.inboundControlScope);
       const paused=s.inboundControlScope==='organization'?!!o.organization_inbound_paused_at:!!item?.inbound_paused_at;
       return <button className={'btn '+(paused?'secondary':'ghost')} disabled={s.loading||!['owner','admin'].includes(s.me.role)}
        onClick={()=>this.setState({modal:'inbound-pause',inboundPauseAction:paused?'resume':'pause',inboundPauseReason:''})}>
        {paused?'Возобновить обработку':'Поставить входящие на паузу'}
       </button>;
     })()}
    </div>
    {(!!o.organization_inbound_paused_at||o.inbound_paused_channels>0)&&<p className="ops-paused-notice" role="status">
      <Icon name="info" size={16}/> Входящая обработка приостановлена: {o.organization_inbound_paused_at?'вся компания':'отдельные каналы'}.
      Новые обращения сохраняются, но не появляются в переписках до возобновления. Технический срок хранения — 14 дней.
    </p>}
  </div>
  <div className="ops-inbound-metrics">
   <div><span>Обработано</span><strong>{inbound.done||0}</strong><small>Сохранено в переписках</small></div>
   <div><span>Ожидают / повторяются</span><strong>{(inbound.queued||0)+(inbound.retrying||0)+(inbound.processing||0)}</strong><small>После ошибки повтор автоматически</small></div>
   <div className={(inbound.failed||0)?'warn':''}><span>Требуют проверки</span><strong>{inbound.failed||0}</strong><small>После пяти неудачных попыток</small></div>
   <div><span>Аккаунты обрабатывают</span><strong>{o.inbound_active_accounts||0}</strong><small>{o.inbound_stalled_claims>0?'Зависшие захваты: '+o.inbound_stalled_claims:'Отправка входящих в Inbox'}</small></div>
  </div>
  {s.inboundIntegrity&&<div className="ops-r35-integrity" role="region" aria-label="Целостность входящей очереди">
    <div className="ops-r35-integrity-copy"><div className="eyebrow small">ПРОВЕРКА ЦЕЛОСТНОСТИ R35</div>
      <strong>Безопасность и восстановление SQL-очереди</strong>
      <p>Просроченные захваты: <b>{s.inboundIntegrity.expired_claims||0}</b> · Зависшие блокировки: <b>{s.inboundIntegrity.expired_channel_slots||0}</b> · Записи без содержимого: <b>{s.inboundIntegrity.missing_payload||0}</b></p>
      {s.inboundIntegrity.invalid_channel_bindings>0&&<p className="ops-r35-alert">Нарушены связи каналов: {s.inboundIntegrity.invalid_channel_bindings}. Требуется ручная проверка; автоматическое исправление запрещено.</p>}
      <small>Проверка не раскрывает тексты клиентов. Восстановление не затрагивает активные обработки.</small>
    </div>
    {['owner','admin'].includes(s.me.role)&&<button className="btn secondary" disabled={s.loading}
       onClick={()=>this.setState({modal:'inbound-repair',inboundRepairReason:'',inboundRepairConfirmed:false})}>
       <Icon name="shield" size={16}/> Проверить и восстановить</button>}
  </div>}
  <div className="ops-inbound-health" aria-label="Здоровье входящих по аккаунтам">
    <div className="ops-inbound-health-title"><strong>Диагностика входящих по аккаунтам</strong>
      <span>{s.inboundHealth?.critical_count||0} критических · {s.inboundHealth?.warning_count||0} требуют внимания · лимит {s.inboundHealth?.capacity_per_channel||5000} на канал</span></div>
    {(s.inboundHealth?.channels||[]).length===0?<p className="muted">Подключённых рабочих аккаунтов пока нет.</p>:
    <div className="ops-inbound-health-grid">{(s.inboundHealth?.channels||[]).slice(0,8).map((ch:any)=><div className={'ops-inbound-health-card '+ch.severity} key={ch.channel_id}>
      <div className="ops-inbound-health-header"><Provider type={ch.provider} small={true}/><strong>{ch.channel_name}</strong><span className={'pill '+(ch.severity==='critical'?'amber':'neutral')}>{ch.severity==='critical'?'Проверить':ch.severity==='warning'?'Задержка':'В норме'}</span></div>
      <div className="ops-inbound-health-stats"><span>Ожидают: <b>{ch.pending}</b></span><span>Ошибки: <b>{ch.failed}</b></span><span>Возраст: <b>{ch.oldest_pending_seconds==null?'—':Math.floor(ch.oldest_pending_seconds/60)+' мин'}</b></span></div>
      <div className="ops-inbound-lease-info" aria-live="polite">{ch.stalled_claims>0
        ?'Зависшие обработки: '+ch.stalled_claims+' · требуется проверка'
        :ch.actively_processing?'Обработка аккаунта выполняется · новые события ждут своей очереди':'Аккаунт свободен для обработки'}</div>
      <div className="ops-inbound-meter" aria-label={'Заполнение очереди '+ch.capacity_percent+'%'}><span style={{width:Math.min(100,ch.capacity_percent)+'%'}}/></div>
      <small>Заполнение: {ch.capacity_percent}% {ch.paused?'· Канал на паузе':''}</small>
    </div>)}</div>}
    {s.inboundHealth?.truncated&&<p className="muted">Показаны до 50 каналов с наибольшим риском. Счётчики учитывают все аккаунты компании.</p>}
  </div>
  <div className="ops-triage-head">
    <div className="ops-triage-filters" role="group" aria-label="Фильтр входящих событий">
      {([['','Все'],['failed','Ошибки'],['queued','В очереди'],['retrying','Повторяются'],['done','Обработаны'],['dismissed','Закрыты']] as any).map(([code,label]:any)=><button key={code} className={'btn '+(s.inboundTriageStatus===code?'primary':'ghost')} disabled={s.loading} onClick={()=>this.loadInboundTriage(code,false)}>{label}</button>)}
    </div>
    {['owner','admin'].includes(s.me.role)&&<div className="ops-batch-controls">
      <select aria-label="Аккаунт для пакетного восстановления" value={s.inboundBatchChannel}
       onChange={(e:any)=>this.setState({inboundBatchChannel:e.target.value})}>
        <option value="">Аккаунт с ошибками</option>
        {(o.channels||[]).filter((c:any)=>c.inbound_failed>0).map((c:any)=><option key={c.id} value={c.id}>{providerName(c.provider)} · {c.name} ({c.inbound_failed})</option>)}
      </select>
      <button className="btn secondary" disabled={!s.inboundBatchChannel||s.loading} onClick={this.openInboundBatchPreview}>Проверить до 20 ошибок</button>
    </div>}
  </div>
  {(s.operationsInboundJobs||[]).length===0?<div className="ops-empty">Событий для выбранного фильтра пока нет.</div>:
   <div className="table-scroll"><table className="ops-inbound-table"><thead><tr><th>ИСТОЧНИК</th><th>СТАТУС</th><th>ПОПЫТКИ</th><th>ПОЛУЧЕНО</th><th>ДЕЙСТВИЕ</th></tr></thead><tbody>{(s.operationsInboundJobs||[]).map((j:any)=><tr key={j.id}>
    <td><div className="ops-inbound-source"><Provider type={j.provider} small={true}/><span>{providerName(j.provider)}</span></div></td>
    <td><span className={'pill '+(j.status==='failed'?'amber':j.status==='done'?'green':'neutral')}>{({queued:'В очереди',retrying:'Ожидает повтора',processing:'Обрабатывается',failed:'Требует проверки',done:'Сохранено',expired:'Истёк срок хранения',dismissed:'Закрыто с удалением'} as any)[j.status]||j.status}</span></td>
    <td>{j.attempts}</td><td className="ops-time">{dateFmt(j.created_at)} · {fmt(j.created_at)}</td>
    <td><div className="ops-job-actions">
     {j.can_retry&&['owner','admin'].includes(s.me.role)&&<button className="btn secondary" disabled={s.loading} onClick={()=>this.setState({modal:'retry-inbound',inboundRetryJob:j,inboundRetryReason:''})}>Повторить</button>}
     {j.can_dismiss&&['owner','admin'].includes(s.me.role)&&<button className="btn ghost" disabled={s.loading} onClick={()=>this.setState({modal:'inbound-dismiss',inboundDismissJob:j,inboundDismissReason:'',inboundDismissCode:'unrecoverable',inboundDismissConfirmed:false})}>Закрыть и удалить</button>}
     {(!j.can_retry&&!j.can_dismiss||!['owner','admin'].includes(s.me.role))&&<span className="muted">{j.status==='done'?'Готово':j.status==='dismissed'?'Без восстановления':j.status==='expired'?'Содержимое удалено':'Автоматически'}</span>}
    </div></td>
   </tr>)}</tbody></table></div>}
  {s.inboundTriageCursor&&<button className="btn secondary ops-more-button" disabled={s.loading}
     onClick={()=>this.loadInboundTriage(s.inboundTriageStatus,true)}>Показать ещё 30 событий</button>}
  <p className="ops-inbound-footnote">Повторная обработка входящего не отправляет клиенту ответ. Текст события удаляется из очереди после сохранения в переписке.</p>
 </section>
 <section className="ops-section"><div className="ops-title"><div><div className="eyebrow">03 / ЗДОРОВЬЕ КАНАЛОВ</div><h2>Состояние подключений</h2></div></div><div className="ops-connections">{o.channels.map((c:any)=><div className="ops-channel" key={c.id}><Provider type={c.provider}/><div><strong>{c.name}</strong><small>{providerName(c.provider)} · {c.mode==='demo'?'Демоканал':c.status==='connected'?'Подключён':c.status==='disconnected'?'Отключён':c.status==='error'?'Ошибка':'Ожидает проверки'}</small>{c.outbound_paused_at&&<span>Новые исходящие на паузе. Входящие работают.</span>}{c.inbound_paused_at&&<span>Обработка входящих этого аккаунта приостановлена.</span>}{c.inbound_failed>0&&<span>Входящие на проверке: {c.inbound_failed}</span>}{c.last_error&&<span>{c.last_error}</span>}</div><time>{c.last_sync_at?dateFmt(c.last_sync_at):'Нет синхронизации'}</time></div>)}</div>{o.channels_truncated&&<p className="muted">Показаны последние 200 каналов. Общие счётчики учитывают все подключения компании.</p>}</section>
 <div className="analytics-disclaimer"><Icon name="shield" size={16}/> Очередь распределяет обработку между компаниями. Сбой до начала внешней отправки восстанавливается автоматически, а отправка с возможным результатом требует сверки. Принятие API не равно доставке клиенту.</div>
 </div>
 }
 renderIntegrations(){
  const s=this.state;const data=s.integrations;const guide=s.integrationGuide;
  if(!data)return <div className="page-content">Загружаем подключения...</div>;
  const demo=!!s.me.organization.is_demo;
  const owner=['owner','admin'].includes(s.me.role);
  const oauth=new URLSearchParams(location.search).get('oauth');
  const types=['avito','instagram','whatsapp','telegram','vk','max','messenger'];
  const liveConnections=data.connections.filter((c:any)=>c.mode==='live'&&c.status!=='disconnected');
  const counts={ready:liveConnections.filter((c:any)=>c.readiness?.ready_for_api_use).length,
    pending:liveConnections.filter((c:any)=>!c.readiness?.ready_for_api_use).length};
  return <div className="page-content onboarding-page">
    <div className="section-head"><div><div className="eyebrow">ВАШИ АККАУНТЫ / ЕДИНЫЙ INBOX</div><h1>Подключение каналов</h1>
      <p>Каждая компания подключает собственные официальные бизнес-аккаунты. Переписки организаций не смешиваются.</p></div></div>
    {demo&&<div className="demo-notice"><Icon name="info" size={20}/><div><strong>Сейчас вы в демонстрации</strong><p>Подключение настоящих аккаунтов доступно после регистрации рабочей компании.</p></div></div>}
    {oauth&&<div className="demo-notice"><Icon name="info" size={18}/>{oauth==='pages'?'Facebook подтвердил вход. Выберите страницу ниже.':oauth==='connected'?'Аккаунт подтверждён, выполните проверку доставки.':oauth==='denied'?'Вы не предоставили разрешения.':'Авторизация не завершена. Проверьте права приложения.'}</div>}
    {!demo&&<section className="onboarding-intro"><div><span className="onboarding-step">1</span><strong>Подключите аккаунт</strong><small>Авторизуйтесь через площадку или выдайте токен бота.</small></div>
     <div><span className="onboarding-step">2</span><strong>Проверьте входящее</strong><small>Подпишитесь на события и отправьте контрольное сообщение.</small></div>
     <div><span className="onboarding-step">3</span><strong>Ответьте из Inbox</strong><small>Ответ должен появиться в исходной социальной сети.</small></div></section>}
    {!demo&&guide&&(!guide.https_ready||!guide.encryption_ready)&&<details className="setup-preflight"><summary><Icon name="shield" size={18}/><span>Нужно подготовить сервер для настоящих сообщений</span><strong>{Number(!guide.https_ready)+Number(!guide.encryption_ready)} шага</strong><Icon name="chevron" size={16}/></summary><div className="setup-preflight-details"><p>Пока можно изучить интерфейс и подготовить свои аккаунты. Настоящие события поступят только после безопасной настройки сервера.</p>{!guide.https_ready&&<div><strong>Публичный защищённый адрес</strong><span>Владелец платформы должен указать адрес OSMANX с HTTPS в настройке PUBLIC_BASE_URL.</span></div>}{!guide.encryption_ready&&<div><strong>Защита ключей соцсетей</strong><span>Владелец платформы должен настроить INTEGRATION_ENCRYPTION_KEY на сервере.</span></div>}</div></details>}
    {liveConnections.length>0&&<div className="onboarding-summary"><span><b>{counts.ready}</b> подтверждена работа API</span><span><b>{counts.pending}</b> подключений ожидают проверки</span></div>}
    {s.channelDiagnostics&&<section className="onboarding-diagnostics" aria-live="polite" id="channel-checkup">
      <div className="onboarding-page-row"><div><h2>Проверка подключения</h2><p>{providerName(s.channelDiagnostics.provider||'vk')} · {s.channelDiagnostics.name||''}</p></div><button className="btn ghost" onClick={()=>this.setState({channelDiagnostics:null})}>Закрыть</button></div>
      <div className="channel-step-list">{(s.channelDiagnostics.stages||[]).map((stage:any,i:number)=><div key={stage.key} className={'channel-step '+(stage.done?'is-complete':'is-pending')}>
        <span className="channel-step-mark">{stage.done?<Icon name="check" size={16}/>:String(i+1)}</span>
        <div><strong>{stage.title}</strong><p>{stage.hint}</p></div>
        <span className="channel-step-status">{stage.done?'Подтверждено':'Ожидает'}</span>
      </div>)}</div>
      <p className="channel-next"><Icon name="info" size={16}/>{s.channelDiagnostics.next_step}</p>
      {s.channelDiagnostics.provider_check_available&&<div className="channel-live-check"><div><strong>Сверка с официальным API</strong><small>{s.channelDiagnostics.webhook_provider_verified?'Провайдер подтвердил адрес webhook':'Адрес webhook пока не сверялся с провайдером'}</small>{s.channelDiagnostics.provider_error&&<small>{s.channelDiagnostics.provider_error}</small>}</div><button className="btn secondary" onClick={()=>this.verifyProviderHook(s.channelDiagnostics.id)} disabled={s.loading}>Проверить подписку</button></div>}
      {s.channelDiagnostics.global_meta_webhook_url&&<div className="onboarding-copy"><code>{s.channelDiagnostics.global_meta_webhook_url}</code><button className="btn ghost" onClick={()=>navigator.clipboard?.writeText(s.channelDiagnostics.global_meta_webhook_url)}>Копировать URL Meta</button></div>}
      {s.channelDiagnostics.webhook_url&&<div className="onboarding-copy"><code>{s.channelDiagnostics.webhook_url}</code><button className="btn ghost" onClick={()=>navigator.clipboard?.writeText(s.channelDiagnostics.webhook_url)}>Копировать webhook</button></div>}
      {s.channelDiagnostics.secretVisible&&<p className="onboarding-secret">Конфиденциальный код VK: <code>{s.channelDiagnostics.confirmation_token}</code> · Секрет Callback: <code>{s.channelDiagnostics.secret}</code></p>}
      <p className="channel-disclaimer">Принято внешним API ≠ доставлено и прочитано клиентом. Для окончательной проверки ответ должен появиться в оригинальном приложении.</p>
    </section>}
    {owner&&s.messengerPages?.length>0&&<section className="onboarding-pages"><h2>Выберите страницу Facebook</h2><p>Показываются только страницы, для которых вы дали разрешение на сообщения Messenger.</p>
      {s.messengerPages.map((page:any)=><div className="onboarding-page-row" key={page.id}><div><strong>{page.name}</strong><small>ID страницы: {page.id}</small></div><button className="btn primary" onClick={()=>this.connectMessengerPage(page.id)} disabled={s.loading}>Подключить страницу</button></div>)}
    </section>}
    <div className="channel-chooser" role="group" aria-label="Выберите канал для настройки">
     <div className="channel-chooser-title"><strong>Выберите, что подключить</strong><span>Показываем один канал за раз, чтобы настройка была понятной.</span></div>
     <div className="channel-chooser-options">{types.map(type=><button key={type} type="button" className={s.focusedProvider===type?'selected':''} aria-pressed={s.focusedProvider===type} onClick={()=>this.setState({focusedProvider:type,channelDiagnostics:null,channelDiagnosticsFor:''})}><Provider type={type} small/>{providerName(type)}{data.connections.some((c:any)=>c.provider===type&&c.mode==='live'&&c.status!=='disconnected')&&<span className="channel-chooser-dot"/>}</button>)}
       <button type="button" className={s.focusedProvider==='all'?'selected':''} aria-pressed={s.focusedProvider==='all'} onClick={()=>this.setState({focusedProvider:'all'})}>Все каналы</button>
     </div>
    </div>
    <div className={'integration-grid '+(s.focusedProvider==='all'?'':'focused-integration')}>{types.filter(type=>s.focusedProvider==='all'||s.focusedProvider===type).map(type=>{
      const cs=data.connections.filter((c:any)=>c.provider===type);
      const active=cs.some((c:any)=>c.mode==='live'&&c.status==='connected');
      const readyForWork=cs.some((c:any)=>c.mode==='live'&&c.readiness?.ready_for_api_use);
      const pending=cs.some((c:any)=>c.mode==='live'&&c.status.startsWith('pending'));
      const instructions=guide?.providers?.[type];
      const descriptions:any={avito:'Сообщения покупателей по вашим объявлениям',instagram:'Direct профессионального Instagram',whatsapp:'Номер WhatsApp Business Platform',telegram:'Сообщения вашего Telegram-бота',vk:'Сообщения сообщества ВКонтакте',max:'Диалоги с ботом MAX',messenger:'Сообщения Facebook-страницы'};
      const ready=!!data.available[type];
      return <div className="integration-card" key={type}>
        <div className="integration-top"><Provider type={type}/><span className={'pill '+(active?'green':pending?'amber':'neutral')}><span className="dot"/>{readyForWork?'API-обмен проверен':active?'Входящие получены':pending?'Ожидает проверки':cs.some((c:any)=>c.mode==='demo')?'Демоканал':'Не подключён'}</span></div>
        <h3>{providerName(type)}</h3><p>{descriptions[type]}</p>
        {cs.filter((c:any)=>c.mode==='live'||demo).map((c:any)=><div className="onboarding-connected" key={c.id}>
          <strong>{c.name}</strong>
          <small>{c.mode==='demo'?'Только тестовые сообщения':c.last_error||c.readiness?.next_step||'Откройте проверку подключения'}</small>
          {c.mode==='live'&&c.outbound_paused_at&&<div className="outbound-stop-note" role="status"><Icon name="shield" size={16}/><span><strong>Новые исходящие приостановлены.</strong> Входящие работают; запросы, прошедшие контрольную точку, могут завершиться.</span></div>}
          {c.mode==='live'&&c.readiness&&<div className="channel-progress" role="group" aria-label="Прогресс настройки">
            <span>Этапы: {c.readiness.stages.filter((x:any)=>x.done).length} из 4</span>
            <div aria-hidden="true">{c.readiness.stages.map((x:any)=><i key={x.key} className={x.done?'complete':''}/>)}</div>
          </div>}
          {c.mode==='live'&&owner&&<div className="onboarding-actions">
           <button className="btn secondary" onClick={()=>this.probeChannel(c.id)}>{'\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435'}</button>
           <button className={'btn '+(c.outbound_paused_at?'secondary':'ghost')} aria-label={c.outbound_paused_at?'Возобновить исходящие':'Приостановить исходящие'} onClick={()=>this.pauseOutbound(c.id,!!c.outbound_paused_at)} disabled={s.loading}>{c.outbound_paused_at?'Возобновить исходящие':'Пауза исходящих'}</button>
           {['pending_webhook','needs_attention'].includes(c.status)&&c.provider!=='avito'&&<button className="btn ghost" onClick={()=>this.activateBot(c.id)}>Настроить события</button>}
           {['telegram','max'].includes(c.provider)&&<button className="btn ghost" onClick={()=>this.verifyProviderHook(c.id)}>Проверить webhook у сервиса</button>}
           {c.provider==='avito'&&<button className="btn ghost" onClick={()=>this.syncAvito(c.id)}>Синхронизировать</button>}
           <details className="channel-more"><summary>Дополнительно</summary><div><button className="btn ghost" onClick={()=>this.diagnoseChannel(c.id)}>Шаги проверки</button><button className="btn ghost" onClick={()=>this.checkChannel(c.id)}>Проверить права</button>
             {['telegram','vk','max','whatsapp'].includes(c.provider)&&<button className="btn ghost" onClick={()=>this.setState({modal:'rotate',rotateChannel:c.id,rotateToken:''})}>Сменить токен</button>}
             {c.provider==='whatsapp'&&<button className="btn ghost" onClick={()=>this.setState({modal:'register-phone',registerPhoneChannel:c.id,registrationPin:''})}>Зарегистрировать номер</button>}
             {c.provider==='vk'&&<button className="btn ghost" onClick={()=>this.vkCallback(c.id)}>Секрет Callback</button>}
             <button className="btn ghost" onClick={()=>this.disconnect(c.id)}>Отключить</button>
           </div></details>
          </div>}
        </div>)}
        {owner&&<div className="onboarding-connect-actions">
          <button className="btn secondary wide" disabled={demo||!ready||s.loading} onClick={()=>
            type==='whatsapp'?this.setState({modal:'whatsapp',connectToken:'',connectPhone:'',connectWaba:''}):
            ['telegram','vk','max'].includes(type)?this.setState({modal:'bot',botProvider:type,connectToken:'',botGroupId:'',botConfirmation:''}):this.oauth(type)}>
            {demo?'Только в рабочей компании':!ready?'Администратор должен настроить API':cs.some((c:any)=>c.mode==='live'&&c.status!=='disconnected')?'Добавить ещё аккаунт':'Подключить '+providerName(type)} <Icon name="arrow" size={14}/>
          </button>
          {type==='whatsapp'&&<button className="btn ghost wide" onClick={s.metaSession?this.launchMetaWhatsApp:this.prepareMetaWhatsApp} disabled={demo||!guide?.meta_embedded_signup_ready||s.loading}>{s.metaSession?'Продолжить в Meta':'Подготовить Meta' }</button>}
        </div>}
        {instructions&&<details className="onboarding-instructions"><summary>Что требуется для подключения?</summary><ol>{instructions.steps.map((step:string,i:number)=><li key={i}>{step}</li>)}</ol></details>}
      </div>;
    })}</div>
    <div className="onboarding-disclaimer"><Icon name="shield" size={17}/> В OSMANX нельзя читать переписки личных аккаунтов через бот. Подключения разрешены только владельцу организации через официальные API. Успешная проверка токена не является доказательством доставки сообщений.</div>
  </div>;
 }
 renderTeam(){const s=this.state;return <div className="page-content"><div className="section-head"><div><div className="eyebrow">КОМАНДА / ПРАВА ДОСТУПА</div><h1>Команда</h1><p>Назначение диалогов, роли и разграничение доступа сотрудников.</p></div><button className="btn primary" onClick={()=>this.setState({modal:'invite',inviteToken:''})}><Icon name="plus" size={16}/> Пригласить</button></div><div className="table-card"><div className="table-heading"><h3>Сотрудники</h3><span>{s.team.length} участников</span></div>{s.team.map((m:any)=><div className="member-row" key={m.id}><Avatar name={m.name} size={39}/><div><strong>{m.name}</strong><small>{m.email}</small></div><button className={'availability '+(m.available?'on':'off')} onClick={()=>this.changeAvailability(m.id,!m.available)} disabled={!['owner','admin','lead'].includes(s.me.role)&&m.id!==s.me.user.id}>{m.available?'На связи':'Недоступен'}</button><span className="pill neutral">{m.role==='owner'?'Владелец':m.role==='admin'?'Администратор':m.role==='lead'?'Руководитель':m.role==='manager'?'Менеджер':'Оператор'}</span></div>)}</div><div className="analytics-disclaimer"><Icon name="shield" size={17}/> Доступ менеджеров ограничен назначенными диалогами. Руководитель, администратор и владелец имеют расширенный обзор.</div></div>}
 renderSettings(){const me=this.state.me,p=this.state.plans,s=this.state;return <div className="page-content"><div className="section-head"><div><div className="eyebrow">РАБОЧАЯ ОБЛАСТЬ / ПАРАМЕТРЫ</div><h1>Настройки</h1><p>Организация, безопасность, доступные функции и подписка.</p></div></div><div className="settings-panel"><div className="detail-label">ОРГАНИЗАЦИЯ</div><h2>{me.organization.name}</h2><p>Текущий тариф: <strong>{me.organization.plan.toUpperCase()}</strong> · {me.organization.is_demo?'Демонстрационная организация':'Рабочая организация'}</p><button className="btn secondary" onClick={this.toggleTheme}><Icon name={this.state.light?'moon':'sun'}/> Переключить тему</button></div>{!me.organization.is_demo&&<><h3 className="settings-subtitle">Ваши компании</h3><div className="settings-panel"><p>Каждая компания видит только свои сообщения, сотрудников и подключённые аккаунты.</p>
   {me.organizations.map((org:any)=><div className="onboarding-page-row" key={org.id}><div><strong>{org.name}</strong><small>{org.role==='owner'?'Владелец':org.role==='admin'?'Администратор':'Сотрудник'}</small></div>
      <button className="btn secondary" disabled={s.loading||org.id===me.organization.id} onClick={()=>this.switchCompany(org.id)}>{org.id===me.organization.id?'Текущая':'Переключиться'}</button></div>)}
   <div className="onboarding-neworg"><label>Новая компания<input placeholder="Название компании" value={s.newOrganization} maxLength={120} onChange={(e:any)=>this.setState({newOrganization:e.target.value})}/></label><button className="btn primary" disabled={s.loading||s.newOrganization.trim().length<2} onClick={this.createCompany}>Создать отдельную компанию</button></div>
   </div></>}
 <h3 className="settings-subtitle">Безопасность входа</h3>
 <div className="settings-panel security-session-panel"><div className="session-info"><Icon name="shield" size={21}/><div><strong>Устройства и сеансы</strong><p>Можно завершить вход на других устройствах, если кто-то получил доступ к вашему аккаунту. Сеансы всех ваших компаний защищены одной учётной записью.</p></div></div>
 {s.sessions&&<div className="session-status" aria-live="polite">Активных сеансов: <strong>{s.sessions.count}</strong>. Текущий сеанс обозначен как активный.</div>}
 <div className="session-actions"><button className="btn secondary" onClick={this.loadSessions} disabled={s.loading}>Проверить сеансы</button><button className="btn secondary" onClick={this.revokeOtherSessions} disabled={s.loading}>Завершить другие сеансы</button><button className="btn secondary" onClick={this.revokeAllSessions} disabled={s.loading}>Выйти на всех устройствах</button></div></div>
 <h3 className="settings-subtitle">Тарифные возможности</h3><div className="plan-grid">{p?.plans.map((plan:any)=><div key={plan.id} className={'plan-card '+(plan.id===p.current?'selected':'')}><div className="plan-title">{plan.id.toUpperCase()}</div><h3>{plan.employees===99999?'Без лимита':plan.employees} <small>сотрудников</small></h3><p>{plan.channels===99999?'Без лимита':plan.channels} каналов</p><p>{plan.analytics?'Аналитика включена':'Базовый Inbox'}</p><p>{plan.automation?'Движок правил':'Без автоматизации'}</p><div className="plan-badge">{plan.id===p.current?'Текущий тариф':'Доступен по запросу'}</div></div>)}</div><div className="analytics-disclaimer">Подписки подготовлены на уровне ограничений, но платежи не принимаются: платёжный провайдер ещё не подключён.</div>
 <h3 className="settings-subtitle">Шаблоны быстрых ответов</h3><div className="settings-panel"><div className="template-list">{this.state.templates.map((t:any)=><div className="template-entry" key={t.id}><div><b>{t.title}</b><p>{t.body}</p></div>{['owner','admin','lead'].includes(me.role)&&<button className="icon-btn" title="Удалить шаблон" onClick={()=>this.deleteTemplate(t.id)}><Icon name="close" size={16}/></button>}</div>)}</div>{['owner','admin','lead'].includes(me.role)&&<div className="template-form"><input aria-label="Название нового шаблона" placeholder="Название шаблона" value={this.state.templateName} onChange={(e:any)=>this.setState({templateName:e.target.value})}/><textarea aria-label="Текст нового шаблона" placeholder="Текст быстрого ответа..." rows={2} value={this.state.templateBody} onChange={(e:any)=>this.setState({templateBody:e.target.value})}/><button className="btn secondary" onClick={this.saveTemplate} disabled={!this.state.templateName.trim()||!this.state.templateBody.trim()}>Сохранить шаблон</button></div>}</div>
 {this.state.localization&&<><h3 className="settings-subtitle">Регион и локализация</h3><div className="settings-panel privacy-panel"><label>Валюта сделок<select aria-label="Валюта сделок" value={this.state.localization.currency} onChange={(e:any)=>this.setState({localization:{...this.state.localization,currency:e.target.value}})}>{this.state.localization.currencies.map((c:string)=><option key={c} value={c}>{c}</option>)}</select></label><label>Часовой пояс IANA<input aria-label="Часовой пояс IANA" value={this.state.localization.timezone} placeholder="Europe/Moscow" onChange={(e:any)=>this.setState({localization:{...this.state.localization,timezone:e.target.value}})}/></label><button className="btn primary" onClick={this.saveLocalization}>Сохранить регион</button><p className="site-localization-note">Валюту нельзя менять, если уже есть сделки с суммами: это защищает расчёты. Даты аналитики рассчитываются в выбранном часовом поясе.</p></div></>}
 {this.state.privacy&&<><h3 className="settings-subtitle">Конфиденциальность и обслуживание</h3><div className="settings-panel privacy-panel"><label>Хранение сообщений <select value={this.state.privacy.retention_days} onChange={(e:any)=>this.setState({privacy:{...this.state.privacy,retention_days:Number(e.target.value)}})}>{[30,90,120,180,365,730,1095].map(n=><option key={n} value={n}>{n} дней</option>)}</select></label><label>Предупреждение, если нет ответа <select value={this.state.privacy.sla_minutes} onChange={(e:any)=>this.setState({privacy:{...this.state.privacy,sla_minutes:Number(e.target.value)}})}>{[1,3,5,7,10,15,30,60].map(n=><option key={n} value={n}>{n} минут</option>)}</select></label><button className="btn primary" onClick={this.savePrivacy}>Сохранить настройки</button><button className="btn secondary" onClick={this.exportWorkspace}><Icon name="note" size={15}/> Экспортировать данные компании</button></div></>}
</div>}
 renderModal(){const s=this.state;return <div className="modal-cover" onClick={()=>this.setState({modal:''})}><div className="modal" role="dialog" aria-modal="true" onClick={(e:any)=>e.stopPropagation()}><div className="modal-header"><div><div className="eyebrow">OSMANX / НАСТРОЙКА</div><h2>{s.modal==='view'?'Сохранить представление':s.modal==='rule'?'Новое правило':s.modal==='whatsapp'?'WhatsApp Cloud API':s.modal==='wa-template'?'Одобренный шаблон WhatsApp':s.modal==='rotate'?'Замена токена':s.modal==='register-phone'?'Регистрация номера WhatsApp':s.modal==='bot'?'Подключить '+providerName(s.botProvider):s.modal==='reconcile'?'Проверка отправки':s.modal==='retry-outbox'?'Повтор после отказа площадки':s.modal==='retry-inbound'?'Восстановление входящего события':s.modal==='inbound-batch'?'Пакетное восстановление входящих':s.modal==='inbound-dismiss'?'Необратимое закрытие входящего':s.modal==='inbound-pause'?'Управление входящими при инциденте':s.modal==='inbound-repair'?'Восстановление просроченных захватов':'Приглашение сотрудника'}</h2></div><button className="icon-btn" aria-label="Закрыть" onClick={()=>this.setState({modal:''})}><Icon name="close"/></button></div>
 {s.modal==='view'&&<div className="modal-form"><p className="modal-help">Сохраните текущие фильтры переписок, чтобы возвращаться к ним одним нажатием.</p><label>Название подборки<input aria-label="Название подборки" value={s.viewName} onChange={(e:any)=>this.setState({viewName:e.target.value})} placeholder="Например: Срочные обращения" maxLength={64}/></label>{['owner','admin','lead'].includes(s.me.role)&&<label className="view-share"><input type="checkbox" checked={s.viewShared} onChange={(e:any)=>this.setState({viewShared:e.target.checked})}/> Доступно всей команде</label>}<button className="btn primary wide" disabled={s.loading||s.viewName.trim().length<2} onClick={this.createSavedView}>Сохранить подборку</button></div>}
 {s.modal==='rule'&&<div className="modal-form"><label>Название правила<input value={s.ruleName} onChange={(e:any)=>this.setState({ruleName:e.target.value})} placeholder="Например: Срочные запросы"/></label><div className="modal-flow"><div className="flow-input"><small>СОБЫТИЕ</small><strong>Новое сообщение</strong></div><div className="flow-input"><small>УСЛОВИЕ</small><select value={s.ruleCondition} onChange={(e:any)=>this.setState({ruleCondition:e.target.value})}><option value="contains">Содержит слова</option><option value="always">Любое сообщение</option></select></div><div className="flow-input"><small>ДЕЙСТВИЕ</small><select value={s.ruleAction} onChange={(e:any)=>this.setState({ruleAction:e.target.value})}><option value="tag">Добавить тег</option><option value="priority">Закрепить</option><option value="status">Изменить статус</option><option value="assign_least_busy">Назначить свободного менеджера</option></select></div></div>{s.ruleCondition==='contains'&&<label>Ключевое слово или фраза<input value={s.ruleTerm} onChange={(e:any)=>this.setState({ruleTerm:e.target.value})} placeholder="срочно"/></label>}{!['priority','assign_least_busy'].includes(s.ruleAction)&&<label>{s.ruleAction==='tag'?'Название тега':'Код статуса'}<input value={s.ruleActionValue} onChange={(e:any)=>this.setState({ruleActionValue:e.target.value})} placeholder="VIP"/></label>}<button className="btn primary wide" onClick={this.createRule} disabled={s.loading}>Создать и включить правило</button></div>}
 {s.modal==='wa-template'&&<div className="modal-form wa-template-modal">
  <p className="modal-help">Шаблоны загружаются из официального каталога Meta и не отправляются без зафиксированного согласия клиента. Поддерживается только обычный текстовый шаблон без кнопок и вложений.</p>
  {s.waLoading?<p role="status">Проверяем шаблоны в Meta...</p>:<>
  {!s.waTemplates.length?<p className="wa-empty">Одобренных простых текстовых шаблонов не найдено. Проверьте WABA ID, доступ к каталогу и одобрение шаблона в WhatsApp Manager.</p>:<>
   <label>Одобренный шаблон<select aria-label="Одобренный шаблон WhatsApp" value={s.waSelected}
    onChange={(e:any)=>{const selection=s.waTemplates.find((t:any)=>t.name+'|'+t.language===e.target.value);
     this.setState({waSelected:e.target.value,waParams:Array(selection?.param_count||0).fill('')})}}>
    {s.waTemplates.map((t:any)=><option key={t.name+'|'+t.language} value={t.name+'|'+t.language}>{t.name} · {t.language}</option>)}
   </select></label>
   {(()=>{const chosen=s.waTemplates.find((t:any)=>t.name+'|'+t.language===s.waSelected);
    if(!chosen)return null;
    const preview=String(chosen.body||'').replace(/\{\{([1-9][0-9]*)\}\}/g,(_:string,n:string)=>s.waParams[Number(n)-1]||'…');
    return <><div className="wa-preview"><small>ПРЕДПРОСМОТР</small><p>{preview}</p></div>
      {Array.from({length:chosen.param_count},(_:any,i:number)=><label key={i}>Параметр {i+1}
       <input value={s.waParams[i]||''} maxLength={200} placeholder={'Значение '+(i+1)}
        onChange={(e:any)=>this.setState({waParams:s.waParams.map((value:string,j:number)=>j===i?e.target.value:value)})}/></label>)}
    </>})()}
  </>}
  {!s.waConsent?<div className="wa-consent"><strong>Не подтверждено согласие клиента</strong>
    <p>Согласие должно быть действительно получено вами. OSMANX только фиксирует подтверждение сотрудника.</p>
    {['owner','admin','lead'].includes(s.me.role)?<>
     <label>Источник и дата согласия<input value={s.waConsentSource} maxLength={240}
       placeholder="Например: форма записи 01.11.2026"
       onChange={(e:any)=>this.setState({waConsentSource:e.target.value})}/></label>
     <label className="wa-check"><input type="checkbox" checked={s.waConsentCheckbox}
       onChange={(e:any)=>this.setState({waConsentCheckbox:e.target.checked})}/>
       Подтверждаю, что клиент дал согласие на такие сообщения.</label>
     <button className="btn secondary" disabled={!s.waConsentCheckbox||s.waConsentSource.trim().length<8||s.loading}
       onClick={this.recordWaConsent}>Зафиксировать согласие</button>
    </>:<p>Попросите владельца, администратора или руководителя зафиксировать согласие клиента.</p>}
   </div>:<div className="wa-consent-valid"><Icon name="check" size={16}/> Согласие зафиксировано сотрудником. {['owner','admin','lead'].includes(s.me.role)&&<button className="btn ghost" onClick={this.revokeWaConsent}>Отозвать</button>}</div>}
  <button className="btn primary wide wa-submit" onClick={this.sendWaTemplate}
   disabled={!s.waConsent||!s.waTemplates.length||s.waLoading||s.loading||
     s.waParams.some((x:string)=>!x.trim())}>Поставить шаблон в очередь</button>
  <p className="modal-help">Meta может отклонить отправку из-за правил площадки. Статус «принято API» не равен «доставлено».</p>
  </>}
 </div>}
 {s.modal==='whatsapp'&&<div className="modal-form"><p className="modal-help">Введите только действительный токен Meta WhatsApp Cloud API и Идентификатор номера телефона. Сервер проверит их у Meta перед сохранением.</p><label>Идентификатор номера телефона<input value={s.connectPhone} onChange={(e:any)=>this.setState({connectPhone:e.target.value})} placeholder="123456789012345"/></label><label>WABA ID (для подписки на входящие)<input value={s.connectWaba} onChange={(e:any)=>this.setState({connectWaba:e.target.value})} placeholder="ID бизнес-аккаунта WhatsApp"/></label><label>Токен доступа Meta<input type="password" autoComplete="off" value={s.connectToken} onChange={(e:any)=>this.setState({connectToken:e.target.value})} placeholder="EAAG..."/></label><button className="btn primary wide" onClick={this.connectWhatsApp} disabled={!s.connectPhone||!s.connectToken||s.loading}>Проверить и подключить</button></div>}
 {s.modal==='register-phone'&&<div className="modal-form"><p className="modal-help">Зарегистрируйте подтверждённый у Meta номер с шестизначным PIN двухэтапной проверки. PIN не сохраняется в OSMANX. После операции потребуется входящий тест.</p><label>PIN из 6 цифр<input type="password" autoComplete="one-time-code" inputMode="numeric" maxLength={6} value={s.registrationPin} onChange={(e:any)=>this.setState({registrationPin:e.target.value.replace(/[^0-9]/g,'')})} placeholder="••••••"/></label><button className="btn primary wide" disabled={s.registrationPin.length!==6||s.loading} onClick={this.registerWhatsAppPhone}>Зарегистрировать у Meta</button></div>}
 {s.modal==='rotate'&&<div className="modal-form"><p className="modal-help">Новый токен должен принадлежать тому же аккаунту. После замены ботам требуется повторно проверить подписку на события.</p><label>Новый токен<input type="password" autoComplete="off" value={s.rotateToken} onChange={(e:any)=>this.setState({rotateToken:e.target.value})} placeholder="Новый официальный токен"/></label><button className="btn primary wide" disabled={s.rotateToken.length<10||s.loading} onClick={this.rotateChannelToken}>Проверить и заменить</button></div>}
 {s.modal==='bot'&&<div className="modal-form"><p className="modal-help">Официальное подключение {providerName(s.botProvider)}. Сначала будет проверен токен; приём сообщений заработает после подключения защищённого webhook на HTTPS.</p><label>Токен {s.botProvider==='vk'?'сообщества':'бота'}<input type="password" autoComplete="off" value={s.connectToken} onChange={(e:any)=>this.setState({connectToken:e.target.value})} placeholder="Токен официального API"/></label>{s.botProvider==='vk'&&<><label>ID сообщества<input value={s.botGroupId} onChange={(e:any)=>this.setState({botGroupId:e.target.value})} placeholder="123456789"/></label><label>Код подтверждения Callback API<input value={s.botConfirmation} onChange={(e:any)=>this.setState({botConfirmation:e.target.value})} placeholder="Строка подтверждения VK"/></label></>}<button className="btn primary wide" disabled={s.loading||!s.connectToken.trim()||(s.botProvider==='vk'&&(!s.botGroupId||!s.botConfirmation))} onClick={this.connectBot}>Проверить токен</button></div>}
 {s.modal==='reconcile'&&<div className="modal-form"><p className="modal-help">После сбоя сети сообщение могло дойти до сервиса. Перед подтверждением результата проверьте его непосредственно на площадке. Повторная отправка не выполняется.</p><label>Проверенный результат<select value={s.reconcileStatus} onChange={(e:any)=>this.setState({reconcileStatus:e.target.value})}><option value="accepted">Доставлено или принято площадкой</option><option value="failed">Не доставлено</option></select></label><label>Подтверждение проверки (обязательно)<textarea rows={3} value={s.reconcileEvidence} placeholder="Ссылка на переписку, дата проверки и имя проверяющего" onChange={(e:any)=>this.setState({reconcileEvidence:e.target.value})}/></label><label>Идентификатор сообщения на площадке (при наличии)<input value={s.reconcileExternalId} onChange={(e:any)=>this.setState({reconcileExternalId:e.target.value})}/></label><button className="btn primary wide" disabled={s.loading||s.reconcileEvidence.trim().length<8} onClick={this.reconcileDelivery}>Зафиксировать результат</button></div>}
 {s.modal==='retry-outbox'&&<div className="modal-form">
  <p className="modal-help">Площадка однозначно отклонила запрос. Проверьте в исходном сервисе, что сообщение не было доставлено. Не используйте эту функцию для таймаутов и неизвестного результата.</p>
  <label>Что проверили и где (минимум 12 символов)<textarea aria-label="Подтверждение отсутствия доставки" rows={3} minLength={12} maxLength={500} value={s.outboxRetryEvidence} onChange={(e:any)=>this.setState({outboxRetryEvidence:e.target.value})} placeholder="Проверил диалог клиента в исходной площадке, сообщения нет"/></label>
  <label className="wa-check"><input type="checkbox" checked={s.outboxRetryVerified} onChange={(e:any)=>this.setState({outboxRetryVerified:e.target.checked})}/> Я проверил отсутствие доставки и понимаю риск повторного сообщения.</label>
  <button className="btn primary wide" disabled={s.loading||!s.outboxRetryVerified||s.outboxRetryEvidence.trim().length<12} onClick={this.retryVerified}>Поставить повтор в очередь</button>
 </div>}
 {s.modal==='retry-inbound'&&<div className="modal-form">
  <p className="modal-help">Проверьте настройки подключения и причину ошибки перед повтором. Входящее событие хранится зашифрованным. Повторная обработка не отправляет исходящий ответ клиенту.</p>
  <label>Причина повторной попытки<textarea aria-label="Причина повтора входящего" rows={3} minLength={8} maxLength={300}
   value={s.inboundRetryReason} onChange={(e:any)=>this.setState({inboundRetryReason:e.target.value})}
   placeholder="Подключение восстановлено, проверил настройки и разрешаю повтор"/></label>
  <button className="btn primary wide" disabled={s.loading||s.inboundRetryReason.trim().length<8} onClick={this.retryInbound}>Вернуть входящее в очередь</button>
 </div>}
 {s.modal==='inbound-dismiss'&&<div className="modal-form">
  <p className="modal-help"><strong>Необратимая операция.</strong> Зашифрованное событие будет удалено из очереди. Оно не попадёт в переписку и его нельзя будет восстановить кнопкой повтора. Используйте только после документированной проверки источника.</p>
  <label>Причина закрытия
   <select aria-label="Категория закрытия входящего" value={s.inboundDismissCode} onChange={(e:any)=>this.setState({inboundDismissCode:e.target.value})}>
     <option value="unrecoverable">Источник не может быть восстановлен</option><option value="duplicate">Подтверждённый дубль</option>
     <option value="invalid_event">Некорректное событие</option><option value="other">Другая проверенная причина</option>
   </select></label>
  <label>Что проверили (без персональных данных)
    <textarea aria-label="Причина необратимого закрытия" rows={3} minLength={12} maxLength={300}
       value={s.inboundDismissReason} onChange={(e:any)=>this.setState({inboundDismissReason:e.target.value})}
       placeholder="Проверил журнал площадки; восстановление этого события невозможно"/></label>
  <label className="wa-check"><input type="checkbox" checked={s.inboundDismissConfirmed}
   onChange={(e:any)=>this.setState({inboundDismissConfirmed:e.target.checked})}/> Подтверждаю, что событие будет удалено без возможности восстановления.</label>
  <button className="btn primary wide" disabled={s.loading||!s.inboundDismissConfirmed||s.inboundDismissReason.trim().length<12}
    onClick={this.dismissInbound}>Необратимо закрыть и удалить</button>
 </div>}
 {s.modal==='inbound-repair'&&<div className="modal-form">
    <p className="modal-help">Исправляются только просроченные захваты и пустые технические записи. Работающие обработчики не останавливаются, тексты сообщений не просматриваются. Нарушенные связи компаний требуют отдельного аудита.</p>
    <label>Причина служебного восстановления<textarea rows={3} placeholder="Проверены зависшие захваты после перезапуска обработчика" value={s.inboundRepairReason}
       onChange={(e:any)=>this.setState({inboundRepairReason:e.target.value})}/></label>
    <label className="wa-check"><input type="checkbox" checked={s.inboundRepairConfirmed}
       onChange={(e:any)=>this.setState({inboundRepairConfirmed:e.target.checked})}/> Подтверждаю восстановление только просроченных заданий.</label>
    <button className="btn primary wide" disabled={s.loading||!s.inboundRepairConfirmed||s.inboundRepairReason.trim().length<12}
       onClick={this.repairInboundExpired}>Выполнить безопасное восстановление</button>
  </div>}
 {s.modal==='inbound-pause'&&<div className="modal-form">
  <p className="modal-help">{s.inboundPauseAction==='pause'?'После остановки новые webhook сохраняются в зашифрованную очередь, но не отображаются в Inbox до восстановления. Уже начатая обработка может завершиться.':'После возобновления накопленные события будут обрабатываться фоновыми обработчиками. Паузы отдельных каналов сохраняются.'}</p>
  <label>Причина действия<textarea aria-label="Причина изменения обработки входящих" rows={3} minLength={8} maxLength={160}
   value={s.inboundPauseReason} onChange={(e:any)=>this.setState({inboundPauseReason:e.target.value})}
   placeholder="Проверил состояние канала и разрешаю операцию"/></label>
  <button className="btn primary wide" disabled={s.loading||s.inboundPauseReason.trim().length<8} onClick={this.applyInboundPause}>
   {s.inboundPauseAction==='pause'?'Приостановить обработку':'Возобновить обработку'}</button>
 </div>}
 {s.modal==='inbound-batch'&&<div className="modal-form">
  <p className="modal-help">Предпросмотр определяет точный набор ошибок выбранного аккаунта. Подтверждение действует 90 секунд: если другой администратор изменит очередь, требуется новая проверка. Исходящие клиентам не отправляются.</p>
  <div className="ops-batch-preview" role="status"><span>Подготовлено к восстановлению</span><strong>{s.inboundBatchPreview?.count||0} событий</strong><small>Без раскрытия сообщений и данных клиентов. План ограничен 20 событиями.</small></div>
  <button className="btn ghost ops-review-refresh" disabled={s.loading} onClick={this.refreshInboundBatchPreview}>Обновить предпросмотр очереди</button>
  <label>Что проверено<textarea aria-label="Причина пакетного восстановления" rows={3} minLength={8} maxLength={300}
   value={s.inboundBatchReason} onChange={(e:any)=>this.setState({inboundBatchReason:e.target.value})}
   placeholder="Ключ расшифрования восстановлен, соединение проверено"/></label>
  <button className="btn primary wide" disabled={s.loading||!s.inboundBatchPreview?.count||s.inboundBatchReason.trim().length<8} onClick={this.retryInboundBatch}>Подтвердить восстановление {s.inboundBatchPreview?.count||0} событий</button>
 </div>}
 {s.modal==='invite'&&<div className="modal-form"><label>Почта сотрудника<input type="email" value={s.inviteEmail} onChange={(e:any)=>this.setState({inviteEmail:e.target.value})} placeholder="employee@company.com"/></label><label>Роль<select value={s.inviteRole} onChange={(e:any)=>this.setState({inviteRole:e.target.value})}><option value="operator">Оператор</option><option value="manager">Менеджер</option><option value="lead">Руководитель</option><option value="admin">Администратор</option></select></label>{s.inviteToken&&<div className="invite-result"><small>ТОКЕН ПРИГЛАШЕНИЯ</small><div className="invite-copy"><input readOnly value={s.inviteToken}/><button className="icon-btn" title="Скопировать" onClick={()=>{navigator.clipboard?.writeText(s.inviteToken);this.notify('Токен скопирован')}}><Icon name="copy"/></button></div><p>Передайте токен сотруднику. Отправка почты пока не настроена.</p></div>}<button className="btn primary wide" onClick={this.invite} disabled={!s.inviteEmail||s.loading}>Создать приглашение</button></div>}
 </div></div>}
 render(){const s=this.state;if(s.boot)return <div className="loading-screen"><span className="brand-mark">O<span>X</span></span><p>Загрузка защищённого пространства...</p></div>;if(!s.me)return this.renderAuth();return <div className={'app-shell '+(s.view==='inbox'?'quiet-inbox-app':'')}>{this.renderSidebar()}<main className="main-shell">{s.view!=='inbox'&&<div className="top-strip"><button className="icon-btn mobile-menu" onClick={()=>this.setState({sidebarOpen:true})}><Icon name="menu" size={20}/></button><div className="top-breadcrumb"><span>OSMANX OMNICHAT</span><Icon name="chevron" size={13}/><strong>{s.view==='start'?'Быстрый старт':NAV.find((n:any)=>n[0]===s.view)?.[2]||'Настройки'}</strong></div><div className="top-actions"><button className="icon-btn" onClick={this.toggleNotifications} title="Разрешить уведомления о сообщениях"><Icon name="bell" size={18}/></button>{s.alerts?.unanswered_over_sla>0&&<button className="sla-pill" onClick={()=>{this.changeView('inbox');this.notify('Просроченных обращений: '+s.alerts.unanswered_over_sla)}}><Icon name="clock" size={14}/>{s.alerts.unanswered_over_sla} SLA</button>}{s.me.organization.is_demo&&<span className="demo-label"><span className="dot green"/> ДЕМОРЕЖИМ</span>}<span className="top-date">{new Date().toLocaleDateString('ru-RU',{weekday:'short',day:'numeric',month:'short'})}</span><button className="icon-btn" title="Настройки" onClick={()=>this.changeView('settings')}><Icon name="settings" size={18}/></button></div></div>}<div className="main-body">{s.view==='start'?this.renderStart():s.view==='command'?this.renderCommand():s.view==='inbox'?this.renderInbox():s.view==='websites'?this.renderWebsites():s.view==='operations'?this.renderOperations():s.view==='contacts'?this.renderContacts():s.view==='deals'?this.renderDeals():s.view==='analytics'?this.renderAnalytics():s.view==='rules'?this.renderRules():s.view==='integrations'?this.renderIntegrations():s.view==='team'?this.renderTeam():this.renderSettings()}</div></main>{s.toast&&<div className="toast"><Icon name="info" size={17}/>{s.toast}<button onClick={()=>this.setState({toast:''})}><Icon name="close" size={14}/></button></div>}{s.modal&&this.renderModal()}</div>}
}
ReactDOM.render(<OmniApp/>,document.getElementById('root'));
