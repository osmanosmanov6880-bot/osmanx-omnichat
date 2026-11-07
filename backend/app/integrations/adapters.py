"""Official HTTP API adapters. Live calls are never made from demo connections."""
import json
import hashlib
import secrets
import os
from urllib.parse import quote
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import httpx
from cryptography.fernet import Fernet, MultiFernet
from .base import AdapterError, Capabilities

GRAPH_VERSION = os.getenv('META_GRAPH_VERSION', 'v25.0')

def cryptor():
    key = os.getenv('INTEGRATION_ENCRYPTION_KEY','').strip()
    if not key:raise AdapterError('Для реальных подключений настройте INTEGRATION_ENCRYPTION_KEY')
    old=[x.strip() for x in os.getenv('INTEGRATION_ENCRYPTION_PREVIOUS_KEYS','').split(',') if x.strip()]
    if len(old)>5:raise AdapterError('Слишком много резервных ключей')
    try:return MultiFernet([Fernet(k.encode('ascii')) for k in dict.fromkeys([key]+old)])
    except Exception as exc:raise AdapterError('Некорректный ключ шифрования интеграций') from exc

def seal(data):
    return cryptor().encrypt(json.dumps(data, ensure_ascii=False).encode('utf-8')).decode('ascii')

def unseal(token):
    if not token: raise AdapterError('Нет действующих учётных данных')
    try:
        return json.loads(cryptor().decrypt(token.encode('ascii')).decode('utf-8'))
    except Exception as exc:
        raise AdapterError('Не удалось расшифровать учётные данные') from exc

def _retry_after_seconds(value):
    if not value:return None
    try:delay=float(value.strip())
    except (ValueError,OverflowError):
        try:
            dt=parsedate_to_datetime(value)
            if dt.tzinfo is None:dt=dt.replace(tzinfo=timezone.utc)
            delay=(dt-datetime.now(timezone.utc)).total_seconds()
        except (ValueError,TypeError,OverflowError):return None
    if not 0<=delay<float('inf'):return None
    return max(1,min(3600,int(delay+0.99999)))

async def call(method, url, *, headers=None, params=None, data=None, json_data=None):
    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
            resp = await client.request(method, url, headers=headers, params=params, data=data, json=json_data)
        if resp.status_code >= 400:
            if resp.status_code == 429:
                raise AdapterError('Площадка временно ограничила запросы (429)',
                    retriable=True,rate_limited=True,
                    retry_after=_retry_after_seconds(resp.headers.get('Retry-After')))
            if resp.status_code >= 500 and method == 'POST':
                raise AdapterError('Результат отправки неизвестен после ошибки платформы',uncertain=True)
            try:
                detail = resp.json().get('error', {})
                detail = detail.get('message', detail) if isinstance(detail, dict) else detail
            except Exception:
                detail = resp.text[:180]
            raise AdapterError(f'API {resp.status_code}: {str(detail)[:160]}', retriable=(method=='GET' and (resp.status_code in (408,409,425,429) or resp.status_code>=500)), uncertain=(method=='POST' and (resp.status_code in (408,409) or resp.status_code>=500)))
        return resp.json()
    except httpx.TimeoutException as exc:
        # On a POST the platform may have accepted the message even if HTTP response is lost.
        # Never silently resend an uncertain request: a duplicate reply harms customer trust.
        raise AdapterError('Время ожидания API истекло. Проверьте доставку у провайдера перед повтором.', retriable=(method=='GET'), uncertain=(method=='POST')) from exc
    except httpx.TransportError as exc:
        raise AdapterError('Сеть провайдера временно недоступна; проверьте статус доставки', retriable=(method=='GET'), uncertain=(method=='POST')) from exc

class DemoAdapter:
    provider = 'demo'
    def get_capabilities(self):
        return Capabilities(send_text=True, receive_text=True)
    async def validate_credentials(self, credentials): return {'id':'demo', 'name':'Тестовый канал'}
    async def send_message(self, credentials, channel, conversation, text, message_id=None):
        raise AdapterError('Тестовые сообщения сохраняются внутри Demo Mode, внешний API не вызывается')
    async def connect(self, credentials): return await self.validate_credentials(credentials)
    async def get_conversations(self, credentials): return []
    async def get_messages(self, credentials, chat_id): return []
    async def receive_messages(self, payload): return []
    async def refresh_credentials(self, credentials): return credentials
    async def disconnect(self, credentials): return None

class WhatsAppAdapter(DemoAdapter):
    provider = 'whatsapp'
    def get_capabilities(self): return Capabilities(templates=True, attachments=True, requires_customer_window=True)
    async def validate_credentials(self, credentials):
        phone_id = str(credentials.get('phone_number_id', '')).strip()
        token = str(credentials.get('access_token', '')).strip()
        if not phone_id.isdigit() or not token: raise AdapterError('Укажите Phone Number ID и официальный access token')
        result = await call('GET', f'https://graph.facebook.com/{GRAPH_VERSION}/{quote(phone_id)}', headers={'Authorization':f'Bearer {token}'}, params={'fields':'display_phone_number,verified_name'})
        return {'id':phone_id,'name':result.get('verified_name') or result.get('display_phone_number') or f'WhatsApp {phone_id}'}
    async def send_message(self, credentials, channel, conversation, text, message_id=None):
        phone_id = str(credentials['phone_number_id'])
        result = await call('POST',f'https://graph.facebook.com/{GRAPH_VERSION}/{quote(phone_id)}/messages',headers={'Authorization':f"Bearer {credentials['access_token']}"},json_data={'messaging_product':'whatsapp','to':conversation.external_recipient_id, 'type':'text','text':{'body':text}})
        try: return result['messages'][0]['id']
        except (KeyError, IndexError): raise AdapterError('WhatsApp не подтвердил приём сообщения', uncertain=True)

    async def approved_text_templates(self, credentials):
        """Fetch current Meta status; do not trust a local label as approval.

        Supports ONLY body-text templates with no buttons, headers or media.
        Pagination uses Graph cursors on the same fixed API host/path.
        """
        from ..whatsapp_templates import supported_template
        phone_id=str(credentials.get('phone_number_id') or '')
        waba_id=str(credentials.get('waba_id') or '')
        token=str(credentials.get('access_token') or '')
        if not phone_id.isdigit() or not waba_id.isdigit() or not token:
            raise AdapterError('Для шаблонов нужны проверенные Phone Number ID, WABA ID и токен Meta')
        url=f'https://graph.facebook.com/{GRAPH_VERSION}/{quote(waba_id)}/message_templates'
        headers={'Authorization':f'Bearer {token}'}
        approved=[]
        seen=set()
        cursor=None
        for _ in range(5):  # No unbounded WABA catalog scan from one request.
            params={'fields':'name,language,status,components','limit':100}
            if cursor:params['after']=cursor
            response=await call('GET',url,headers=headers,params=params)
            items=response.get('data')
            if not isinstance(items,list):
                raise AdapterError('Meta не вернула каталог шаблонов')
            for item in items:
                template=supported_template(item)
                if not template:continue
                identity=(template['name'],template['language'])
                if identity not in seen:
                    approved.append(template)
                    seen.add(identity)
            nxt=(response.get('paging') or {}).get('cursors') or {}
            new_cursor=nxt.get('after') if isinstance(nxt,dict) else None
            if not new_cursor or not isinstance(new_cursor,str) or len(new_cursor)>300 or new_cursor==cursor or len(items)<100:
                break
            cursor=new_cursor
        return approved

    async def send_template(self, credentials, channel, conversation, name, language, parameters):
        """Verify approval again immediately before the actual provider POST."""
        available=await self.approved_text_templates(credentials)
        chosen=next((x for x in available if x['name']==name and x['language']==language),None)
        if not chosen:
            raise AdapterError('Шаблон не одобрен Meta или имеет неподдерживаемые компоненты')
        if len(parameters)!=chosen['param_count']:
            raise AdapterError('Количество параметров шаблона не совпадает с утверждённым')
        if not conversation.external_recipient_id:
            raise AdapterError('У получателя отсутствует WhatsApp ID')
        phone_id=str(credentials['phone_number_id'])
        payload={'messaging_product':'whatsapp','to':str(conversation.external_recipient_id),
                 'type':'template','template':{'name':name,'language':{'code':language}}}
        if parameters:
            payload['template']['components']=[{'type':'body','parameters':[
                {'type':'text','text':value} for value in parameters]}]
        result=await call('POST',f'https://graph.facebook.com/{GRAPH_VERSION}/{quote(phone_id)}/messages',
            headers={'Authorization':f"Bearer {credentials['access_token']}"},json_data=payload)
        try:return str(result['messages'][0]['id'])
        except (KeyError,IndexError,TypeError):
            raise AdapterError('Meta не подтвердила приём шаблонного сообщения',uncertain=True)

class InstagramAdapter(DemoAdapter):
    provider = 'instagram'
    def get_capabilities(self): return Capabilities(attachments=True, requires_customer_window=True)
    async def validate_credentials(self, credentials):
        token = credentials.get('access_token')
        if not token: raise AdapterError('Нет токена Instagram Login')
        result = await call('GET',f'https://graph.instagram.com/{GRAPH_VERSION}/me',headers={'Authorization':f'Bearer {token}'},params={'fields':'id,username,user_id'})
        account_id = str(result.get('user_id') or result.get('id') or '')
        if not account_id: raise AdapterError('Instagram не вернул идентификатор аккаунта')
        return {'id':account_id,'name':'@'+result.get('username','Instagram')}
    async def refresh_credentials(self, credentials):
        result = await call('GET','https://graph.instagram.com/refresh_access_token',params={'grant_type':'ig_refresh_token','access_token':credentials['access_token']})
        import time
        return {**credentials,'access_token':result['access_token'],'expires_at':time.time()+int(result.get('expires_in',5184000))}
    async def send_message(self, credentials, channel, conversation, text, message_id=None):
        account_id = channel.external_account_id
        result = await call('POST',f'https://graph.instagram.com/{GRAPH_VERSION}/{quote(account_id)}/messages',headers={'Authorization':f"Bearer {credentials['access_token']}"},json_data={'recipient':{'id':conversation.external_recipient_id},'message':{'text':text}})
        
        message_id = result.get('message_id') or result.get('id')
        if not message_id: raise AdapterError('Instagram не подтвердил приём сообщения', uncertain=True)
        return str(message_id)

class AvitoAdapter(DemoAdapter):
    provider = 'avito'
    def get_capabilities(self): return Capabilities(history_sync=True, attachments=True)
    async def validate_credentials(self, credentials):
        token = credentials.get('access_token')
        if not token: raise AdapterError('Нет OAuth access token Авито')
        result = await call('GET','https://api.avito.ru/core/v1/accounts/self',headers={'Authorization':f'Bearer {token}'})
        account_id = result.get('id') or result.get('user_id')
        if account_id is None: raise AdapterError('Авито не вернул ID бизнес-аккаунта')
        return {'id':str(account_id), 'name':result.get('name') or result.get('name_normalized') or f'Авито #{account_id}'}
    async def send_message(self, credentials, channel, conversation, text, message_id=None):
        account_id = quote(channel.external_account_id, safe='')
        chat_id = quote(conversation.external_chat_id, safe='')
        result = await call('POST',f'https://api.avito.ru/messenger/v1/accounts/{account_id}/chats/{chat_id}/messages',headers={'Authorization':f"Bearer {credentials['access_token']}"},json_data={'type':'text','message':{'text':text}})
        
        message_id = result.get('id') or result.get('message_id')
        if not message_id: raise AdapterError('Авито не подтвердил приём сообщения', uncertain=True)
        return str(message_id)
    async def get_conversations(self, credentials):
        account_id = str(credentials.get('account_id',''))
        if not account_id: raise AdapterError('Нет ID аккаунта для синхронизации')
        result = await call('GET',f'https://api.avito.ru/messenger/v2/accounts/{quote(account_id)}/chats',headers={'Authorization':f"Bearer {credentials['access_token']}"},params={'limit':100,'offset':0})
        return result.get('chats', [])
    async def get_messages(self, credentials, chat_id):
        account_id = str(credentials.get('account_id',''))
        if not account_id: raise AdapterError('Не указан ID продавца Авито')
        result = await call('GET',f'https://api.avito.ru/messenger/v3/accounts/{quote(account_id)}/chats/{quote(str(chat_id),safe="")}/messages/',
            headers={'Authorization':f"Bearer {credentials['access_token']}"},params={'limit':100,'offset':0})
        return result.get('messages',[])
    async def refresh_credentials(self, credentials):
        cid, secret = os.getenv('AVITO_CLIENT_ID'), os.getenv('AVITO_CLIENT_SECRET')
        if not cid or not secret or not credentials.get('refresh_token'):
            raise AdapterError('Нет refresh token или параметров приложения Авито')
        data = await call('POST','https://api.avito.ru/token',data={'grant_type':'refresh_token','client_id':cid,'client_secret':secret,'refresh_token':credentials['refresh_token']})
        return {**credentials, **{k:v for k,v in data.items() if k in ('access_token','refresh_token','expires_in')}}

class TelegramAdapter(DemoAdapter):
    """Official Telegram Bot API. This is NOT access to a person's private Telegram inbox."""
    provider = 'telegram'
    def get_capabilities(self):return Capabilities(send_text=True, receive_text=True, attachments=False)
    async def validate_credentials(self, credentials):
        token = credentials.get('access_token','')
        if not token or ':' not in token:raise AdapterError('Нужен токен Telegram-бота от BotFather')
        data = await call('GET',f'https://api.telegram.org/bot{quote(token,safe=":")}/getMe')
        if not data.get('ok') or not (data.get('result') or {}).get('is_bot'):
            raise AdapterError('Telegram не подтвердил бота')
        bot = data['result']
        return {'id':str(bot['id']),'name':'@'+bot.get('username','telegram_bot')}
    async def send_message(self,credentials,channel,conversation,text,message_id=None):
        token = credentials['access_token']
        result = await call('POST',f'https://api.telegram.org/bot{quote(token,safe=":")}/sendMessage',json_data={'chat_id':conversation.external_chat_id,'text':text})
        if not result.get('ok') or not (result.get('result') or {}).get('message_id'):
            raise AdapterError('Telegram не подтвердил сообщение',uncertain=True)
        return str(result['result']['message_id'])

class VKAdapter(DemoAdapter):
    """VK community messages via a group access token; never personal user DM access."""
    provider='vk'
    def get_capabilities(self):return Capabilities(send_text=True,receive_text=True)
    async def validate_credentials(self,credentials):
        token=credentials.get('access_token')
        group_id=str(credentials.get('group_id',''))
        if not token or not group_id.isdigit():raise AdapterError('Требуется токен сообщества ВКонтакте и ID сообщества')
        data=await call('GET','https://api.vk.ru/method/groups.getById',params={'access_token':token,'v':'5.199','group_id':group_id})
        if data.get('error'):raise AdapterError('ВКонтакте отклонил токен или ID сообщества')
        response=data.get('response')
        groups=response.get('groups') if isinstance(response,dict) else response
        group=(groups or [None])[0] if isinstance(groups,list) else None
        if not group or str(group.get('id'))!=group_id:raise AdapterError('Сообщество ВКонтакте не подтверждено')
        return {'id':group_id,'name':group.get('name') or f'ВКонтакте #{group_id}'}
    async def send_message(self,credentials,channel,conversation,text,message_id=None):
        seed=str(message_id or credentials.get('_outgoing_message_id') or secrets.token_hex(12))
        random_id=int.from_bytes(hashlib.sha256(seed.encode()).digest()[:4],'big')&0x7fffffff
        data=await call('POST','https://api.vk.ru/method/messages.send',data={'access_token':credentials['access_token'],'v':'5.199','peer_id':conversation.external_chat_id,'random_id':str(random_id),'message':text})
        if data.get('error'):raise AdapterError('ВКонтакте отклонил отправку: '+str(data['error'].get('error_msg',''))[:120])
        if not data.get('response'):raise AdapterError('ВКонтакте не подтвердил отправку',uncertain=True)
        return str(data['response'])

class MaxAdapter(DemoAdapter):
    """Official MAX Bot API, private dialog with the bot or authorized group."""
    provider='max'
    def get_capabilities(self):return Capabilities(send_text=True,receive_text=True)
    async def validate_credentials(self,credentials):
        token=credentials.get('access_token','')
        if not token:raise AdapterError('Требуется действительный токен бота MAX')
        info=await call('GET','https://platform-api2.max.ru/me',headers={'Authorization':token})
        if not info.get('is_bot') or info.get('user_id') is None:raise AdapterError('MAX не подтвердил бота')
        return {'id':str(info['user_id']),'name':info.get('name') or info.get('username') or f'MAX #{info["user_id"]}'}
    async def send_message(self,credentials,channel,conversation,text,message_id=None):
        if len(text)>4000:raise AdapterError('MAX допускает не более 4000 символов')
        dest=str(conversation.external_chat_id)
        if dest.startswith('user:'):
            params={'user_id':dest.removeprefix('user:')}
        elif dest.startswith('chat:'):
            params={'chat_id':dest.removeprefix('chat:')}
        else:raise AdapterError('Неизвестный тип диалога MAX')
        result=await call('POST','https://platform-api2.max.ru/messages',headers={'Authorization':credentials['access_token']},params=params,json_data={'text':text})
        body=(result.get('message') or {}).get('body') or {}
        if not body.get('mid'):raise AdapterError('MAX не подтвердил приём сообщения',uncertain=True)
        return str(body['mid'])

class MessengerAdapter(DemoAdapter):
    """Facebook Messenger conversations belonging to an authorized Facebook Page.

    A Page token is required; a personal Facebook account token is never stored as
    a messaging connection. Business owner must grant Page messaging permissions.
    """
    provider = 'messenger'
    def get_capabilities(self):
        return Capabilities(send_text=True, receive_text=True, attachments=True, requires_customer_window=True)
    async def validate_credentials(self, credentials):
        token=credentials.get('access_token')
        page_id=str(credentials.get('page_id') or '')
        if not token or not page_id.isdigit():
            raise AdapterError('Нужны ID Facebook-страницы и принадлежащий ей Page access token')
        info=await call('GET',f'https://graph.facebook.com/{GRAPH_VERSION}/{quote(page_id)}',
            headers={'Authorization':f'Bearer {token}'},params={'fields':'id,name'})
        if str(info.get('id'))!=page_id:
            raise AdapterError('Facebook не подтвердил владение выбранной страницей')
        return {'id':page_id,'name':str(info.get('name') or f'Messenger Page {page_id}')}
    async def send_message(self,credentials,channel,conversation,text,message_id=None):
        result=await call('POST',f'https://graph.facebook.com/{GRAPH_VERSION}/{quote(channel.external_account_id)}/messages',
            headers={'Authorization':f"Bearer {credentials['access_token']}"},
            json_data={'recipient':{'id':conversation.external_recipient_id},
                'messaging_type':'RESPONSE','message':{'text':text}})
        mid=result.get('message_id')
        if not mid:raise AdapterError('Meta Messenger не подтвердил сообщение',uncertain=True)
        return str(mid)

ADAPTERS = {'avito':AvitoAdapter(), 'instagram':InstagramAdapter(), 'whatsapp':WhatsAppAdapter(), 'telegram':TelegramAdapter(), 'vk':VKAdapter(), 'max':MaxAdapter(), 'messenger':MessengerAdapter()}

def adapter_for(provider):
    if provider not in ADAPTERS: raise AdapterError('Неподдерживаемый канал')
    return ADAPTERS[provider]
