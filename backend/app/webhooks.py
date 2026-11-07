"""Webhook ingress with required Meta HMAC verification and idempotent writes."""
import hashlib
import hmac
import json
import os
import math
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from .db import SessionLocal, ChannelConnection, Conversation, Message, WebhookEvent, now
from .services import ingest_inbound
from .delivery_state import advance_delivery_state
from .provider_receipts import record_whatsapp_receipt, reconcile_whatsapp_receipt
from .inbound_jobs import stage as stage_inbound_job, process_batch as process_inbound_batch, InboundCapacityExceeded

router=APIRouter(prefix='/api/webhooks',tags=['webhooks'])

MAX_META_EVENTS=500

def validate_meta_envelope(data,kind):
    if not isinstance(data,dict) or data.get('object')!=kind:
        raise HTTPException(422,'Некорректный тип webhook')
    entries=data.get('entry',[])
    if not isinstance(entries,list):raise HTTPException(422,'Некорректный список событий')
    count=0
    for entry in entries:
        if not isinstance(entry,dict):raise HTTPException(422,'Повреждённое событие')
        if kind=='whatsapp_business_account':
            changes=entry.get('changes',[])
            if not isinstance(changes,list):raise HTTPException(422,'Некорректные изменения WhatsApp')
            for change in changes:
                if not isinstance(change,dict):raise HTTPException(422,'Некорректное изменение WhatsApp')
                value=change.get('value',{})
                if not isinstance(value,dict):raise HTTPException(422,'Некорректный payload WhatsApp')
                if not isinstance(value.get('metadata',{}),dict):raise HTTPException(422,'Некорректные метаданные')
                for field in ('messages','statuses','contacts'):
                    batch=value.get(field,[])
                    if not isinstance(batch,list) or any(not isinstance(item,dict) for item in batch):
                        raise HTTPException(422,'Некорректные данные WhatsApp')
                    count+=len(batch)
                    for item in batch:
                        if field=='messages':
                            if item.get('text') is not None and not isinstance(item['text'],dict):
                                raise HTTPException(422,'Некорректный текст WhatsApp')
                            kind_name=item.get('type')
                            if kind_name in ('image','video','document','audio','sticker') and (
                                item.get(kind_name) is not None and not isinstance(item[kind_name],dict)):
                                raise HTTPException(422,'Некорректное вложение WhatsApp')
                        if field=='contacts' and item.get('profile') is not None and not isinstance(item['profile'],dict):
                            raise HTTPException(422,'Некорректный профиль WhatsApp')
        else:
            batch=entry.get('messaging',[])
            if not isinstance(batch,list) or any(not isinstance(item,dict) for item in batch):
                raise HTTPException(422,'Некорректные данные Meta')
            count+=len(batch)
            for item in batch:
                for field in ('sender','recipient','message'):
                    if item.get(field) is not None and not isinstance(item[field],dict):
                        raise HTTPException(422,'Некорректный формат Meta')
                msg=item.get('message') or {}
                if msg.get('attachments') is not None and (
                    not isinstance(msg['attachments'],list) or
                    any(not isinstance(a,dict) for a in msg['attachments'])):
                    raise HTTPException(422,'Некорректное вложение Meta')
        if count>MAX_META_EVENTS:raise HTTPException(413,'Слишком много событий в одном webhook')
    return data


def safe_provider_time(value,*,milliseconds=False):
    fallback=now()
    try:
        moment=float(value)
        if milliseconds:moment/=1000
    except (ValueError,TypeError,OverflowError):return fallback
    if not math.isfinite(moment) or moment<946684800 or moment>fallback+300:return fallback
    return moment



def reserve_event(db, provider: str, fingerprint: str) -> bool:
    """DB-enforced idempotency; safe when two API workers receive one event.

    An INSERT ... ON CONFLICT DO NOTHING is atomic, unlike checking SELECT
    and then inserting. It participates in the same transaction as ingest.
    If ingest fails, rollback releases the reservation for the provider retry.
    """
    dialect=db.get_bind().dialect.name
    if dialect == 'sqlite':
        stmt=sqlite_insert(WebhookEvent)
    elif dialect == 'postgresql':
        stmt=postgres_insert(WebhookEvent)
    else:
        raise RuntimeError('Webhook receipt backend must be SQLite or PostgreSQL')
    result=db.execute(stmt.values(provider=provider,fingerprint=fingerprint)
                      .on_conflict_do_nothing(index_elements=['provider','fingerprint']))
    return result.rowcount == 1

def stage_verified_inbound(db, **kwargs):
    try:
        return stage_inbound_job(db, **kwargs)
    except InboundCapacityExceeded as exc:
        # Never acknowledge a message we did not durably store. Provider
        # retry is necessary; the response contains no customer data.
        raise HTTPException(503, 'Очередь входящих заполнена; повторите запрос',
                            headers={'Retry-After':'30'}) from exc
    except (ValueError, TypeError, OverflowError) as exc:
        raise HTTPException(422, 'Некорректные данные входящего события') from exc


def finish_staged(ids):
    """Fast inline delivery for existing UX; worker guarantees eventual recovery."""
    return process_inbound_batch(db_session, limit=min(100, len(ids)), only_ids=ids) if ids else 0


def verify_meta(raw:bytes, header:str,provider:str):
    if provider=='instagram':
        secret=os.getenv('INSTAGRAM_APP_SECRET_WEBHOOK') or os.getenv('INSTAGRAM_APP_SECRET') or os.getenv('META_APP_SECRET')
    elif provider=='messenger':
        secret=os.getenv('FACEBOOK_APP_SECRET') or os.getenv('META_APP_SECRET')
    else:
        secret=os.getenv('WHATSAPP_APP_SECRET') or os.getenv('META_APP_SECRET')
    if not secret or not header.startswith('sha256='):
        raise HTTPException(403,'Проверка подписи webhook не настроена')
    expected=hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest()
    if not hmac.compare_digest(header.removeprefix('sha256='),expected):
        raise HTTPException(403,'Неверная подпись webhook')

def db_session():
    from . import db
    if db.SessionLocal is None:db.initialize()
    return db.SessionLocal()

@router.get('/{provider}')
def verify_subscription(provider:str,hub_mode:str=Query('',alias='hub.mode'),hub_challenge:str=Query('',alias='hub.challenge'),hub_verify_token:str=Query('',alias='hub.verify_token')):
    if provider not in ('instagram','whatsapp','messenger'):raise HTTPException(404)
    expected=os.getenv('META_WEBHOOK_VERIFY_TOKEN','')
    if not expected or hub_mode!='subscribe' or not hmac.compare_digest(expected,hub_verify_token):raise HTTPException(403)
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(hub_challenge)

@router.post('/whatsapp')
async def whatsapp_webhook(req:Request):
    raw=await req.body()
    if len(raw)>3*1024*1024:raise HTTPException(413)
    verify_meta(raw,req.headers.get('X-Hub-Signature-256',''),'whatsapp')
    try:data=json.loads(raw)
    except (ValueError,UnicodeDecodeError):raise HTTPException(422,'Некорректный JSON')
    validate_meta_envelope(data,'whatsapp_business_account')
    job_ids=[]
    receipt_ids=[]
    with db_session() as db:
        for entry in data.get('entry',[]):
            for change in entry.get('changes',[]):
                value=change.get('value',{})
                phone_id=str(value.get('metadata',{}).get('phone_number_id',''))
                if not phone_id:continue
                channel=db.query(ChannelConnection).filter(ChannelConnection.provider=='whatsapp',ChannelConnection.external_account_id==phone_id,ChannelConnection.mode=='live',ChannelConnection.status.in_(['connected','pending_webhook'])).first()
                if not channel:continue
                names={c.get('wa_id'):c.get('profile',{}).get('name') for c in value.get('contacts',[])}
                for item in value.get('messages',[]):
                    event_id=item.get('id')
                    if not event_id:continue
                    sender=str(item.get('from') or '')
                    kind=item.get('type','unsupported')
                    body=item.get('text',{}).get('body') if kind=='text' else f'[WhatsApp: {kind}]'
                    attachment=None
                    if kind in ('image','video','document','audio','sticker'):
                        media=item.get(kind) or {}
                        attachment={'provider':'whatsapp','type':kind,'media_id':str(media.get('id','')),'mime_type':str(media.get('mime_type',''))[:100]}
                        if media.get('caption'):body=str(media['caption'])[:4000]
                    if sender:
                        job_id=stage_verified_inbound(db,channel=channel,external_chat_id=sender,
                            external_message_id=event_id,sender_id=sender,sender_name=names.get(sender),
                            text=body,kind=kind,timestamp=safe_provider_time(item.get('timestamp')),
                            attachment=attachment)
                        if job_id:job_ids.append(job_id)
                for status in value.get('statuses',[]):
                    ext_id=status.get('id');state=status.get('status')
                    if not isinstance(ext_id,str) or state not in ('sent','delivered','read','failed'):
                        continue
                    recipient=status.get('recipient_id')
                    if record_whatsapp_receipt(db,channel,ext_id,state,recipient):
                        reconcile_whatsapp_receipt(db,channel.id,ext_id)
                        receipt_ids.append((channel.id,ext_id))
        db.commit()  # Durable events are committed BEFORE any provider HTTP success response.
    accepted=finish_staged(job_ids)
    # A second *post-commit* pass closes the race where a provider callback
    # and the outbox API acknowledgment commit at almost the same instant.
    if receipt_ids:
        with db_session() as db:
            for channel_id,ext_id in dict.fromkeys(receipt_ids):
                reconcile_whatsapp_receipt(db,channel_id,ext_id)
            db.commit()
    return {'ok':True,'accepted':accepted}

@router.post('/instagram')
async def instagram_webhook(req:Request):
    raw=await req.body()
    if len(raw)>3*1024*1024:raise HTTPException(413)
    verify_meta(raw,req.headers.get('X-Hub-Signature-256',''),'instagram')
    try:data=json.loads(raw)
    except (ValueError,UnicodeDecodeError):raise HTTPException(422,'Некорректный JSON')
    validate_meta_envelope(data,'instagram')
    job_ids=[]
    with db_session() as db:
        for entry in data.get('entry',[]):
            acct=str(entry.get('id',''))
            channel=db.query(ChannelConnection).filter(ChannelConnection.provider=='instagram',ChannelConnection.external_account_id==acct,ChannelConnection.mode=='live',ChannelConnection.status.in_(['connected','pending_webhook'])).first()
            if not channel:continue
            for item in entry.get('messaging',[]):
                message=item.get('message') or {}
                ext_id=message.get('mid');sender=str(item.get('sender',{}).get('id',''))
                if not ext_id or not sender or sender==acct or message.get('is_echo'):continue
                text=message.get('text') or '[Instagram: вложение]'
                attachment=None
                if message.get('attachments'):
                    item_attachment=message['attachments'][0]
                    payload=item_attachment.get('payload') or {}
                    url=payload.get('url')
                    attachment={'provider':'instagram','type':item_attachment.get('type','other')}
                    if isinstance(url,str) and url.startswith('https://'):attachment['url']=url
                job_id=stage_verified_inbound(db,channel=channel,external_chat_id=sender,
                    external_message_id=ext_id,sender_id=sender,sender_name=None,text=text,
                    timestamp=safe_provider_time(item.get('timestamp'),milliseconds=True),
                    kind='attachment' if attachment else 'text',attachment=attachment)
                if job_id:job_ids.append(job_id)
        db.commit()
    return {'ok':True,'accepted':finish_staged(job_ids)}

@router.post('/messenger')
async def facebook_messenger_webhook(req:Request):
    """Meta Page webhooks route only by verified Page ID and signed payload.

    Page-scoped sender IDs are never merged across pages or tenants by name.
    """
    raw=await req.body()
    if len(raw)>3*1024*1024:raise HTTPException(413)
    verify_meta(raw,req.headers.get('X-Hub-Signature-256',''),'messenger')
    try:data=json.loads(raw)
    except (ValueError,UnicodeDecodeError):raise HTTPException(422,'Некорректный JSON')
    validate_meta_envelope(data,'page')
    job_ids=[]
    with db_session() as db:
        for entry in data.get('entry',[]):
            page_id=str(entry.get('id') or '')
            ch=db.query(ChannelConnection).filter(ChannelConnection.provider=='messenger',
                ChannelConnection.external_account_id==page_id,ChannelConnection.mode=='live',
                ChannelConnection.status.in_(['pending_webhook','connected'])).first()
            if not ch:continue
            for item in entry.get('messaging',[]):
                msg=item.get('message') or {}
                sender=str((item.get('sender') or {}).get('id') or '')
                recipient=str((item.get('recipient') or {}).get('id') or '')
                mid=str(msg.get('mid') or '')
                if not sender or not mid or sender==page_id or (recipient and recipient!=page_id) or msg.get('is_echo'):
                    continue
                attachment=None
                if msg.get('attachments'):
                    first=msg['attachments'][0]
                    attachment={'provider':'messenger','type':first.get('type','other')}
                    payload=first.get('payload') or {}
                    if isinstance(payload.get('url'),str) and payload['url'].startswith('https://'):
                        attachment['url']=payload['url']
                job_id=stage_verified_inbound(db,channel=ch,external_chat_id=sender,
                    external_message_id=mid,sender_id=sender,sender_name=None,
                    text=msg.get('text') or '[Медиа Messenger]',
                    timestamp=safe_provider_time(item.get('timestamp'),milliseconds=True),
                    kind='attachment' if attachment else 'text',attachment=attachment)
                if job_id:job_ids.append(job_id)
        db.commit()
    return {'ok':True,'accepted':finish_staged(job_ids)}

# Avito webhook intentionally NOT exposed without a verified subscription and origin/auth scheme.
# Integration via permitted Avito OAuth is possible; inbound Avito subscription implementation
# remains blocked until tested with an approved merchant account and current specification.


# Separate, per-channel signed callbacks. The UUID alone grants no access.
# A valid signed event is the sole source of incoming data; no social-account scraping.
def get_signed_channel(db,provider,channel_id,signature,header_name):
    from .integrations.adapters import unseal
    channel=db.query(ChannelConnection).filter_by(id=channel_id,provider=provider,mode='live').first()
    if not channel or channel.status not in ('connected','pending_webhook') or not channel.encrypted_credentials:
        raise HTTPException(404,'Канал не найден')
    credentials=unseal(channel.encrypted_credentials)
    expected=str(credentials.get('webhook_secret') or '')
    if not expected or not hmac.compare_digest(expected,signature or ''):
        raise HTTPException(403,f'Неверный секрет {header_name}')
    return channel,credentials

def safe_json(raw):
    if len(raw)>1024*1024:raise HTTPException(413,'Слишком большое webhook-событие')
    try:
        data=json.loads(raw)
        if not isinstance(data,dict):raise ValueError('Не объект')
        return data
    except (ValueError,UnicodeDecodeError) as exc:raise HTTPException(422,'Некорректный JSON') from exc

def _bot_object(value, field):
    """An authenticated bot callback is still untrusted JSON.

    Reject malformed subtrees as a client/provider error, not an uncaught
    AttributeError that causes needless webhook retries and 500 responses.
    """
    if value is None:
        return {}
    if not isinstance(value,dict):
        raise HTTPException(422,f'Некорректное поле webhook: {field}')
    return value


def _bot_attachments(value):
    if value is None:
        return []
    if not isinstance(value,list) or len(value)>100:
        raise HTTPException(422,'Некорректный список вложений')
    return value


def inbound_event(db,provider,channel,external_chat_id,message_id,sender_id,sender_name,text,timestamp,kind='text',attachment=None):
    if not external_chat_id or not message_id or not sender_id:return None
    return stage_verified_inbound(db,channel=channel,external_chat_id=external_chat_id,
        external_message_id=message_id,sender_id=sender_id,sender_name=sender_name,
        text=text,timestamp=timestamp,kind=kind,attachment=attachment)

@router.post('/telegram/{channel_id}')
async def telegram_bot_webhook(channel_id:str,req:Request):
    payload=safe_json(await req.body())
    with db_session() as db:
        ch,_=get_signed_channel(db,'telegram',channel_id,req.headers.get('X-Telegram-Bot-Api-Secret-Token',''),'X-Telegram-Bot-Api-Secret-Token')
        msg=_bot_object(payload.get('message'),'message')
        sender=_bot_object(msg.get('from'),'message.from')
        chat=_bot_object(msg.get('chat'),'message.chat')
        if not msg or sender.get('is_bot') or not chat.get('id') or not msg.get('message_id'):
            return {'ok':True,'accepted':0}
        name=' '.join(str(sender.get(k) or '') for k in ('first_name','last_name')).strip() or sender.get('username') or str(chat['id'])
        body=msg.get('text') or msg.get('caption') or '[Медиа Telegram]'
        media=next((k for k in ('photo','document','video','audio','voice','sticker') if k in msg),None)
        got=inbound_event(db,'telegram',ch,chat['id'],msg['message_id'],sender.get('id') or chat['id'],name,body,msg.get('date'),kind=media or 'text',attachment={'provider':'telegram','type':media} if media else None)
        db.commit()
    return {'ok':True,'accepted':finish_staged([got] if got else [])}

@router.post('/vk/{channel_id}')
async def vk_community_webhook(channel_id:str,req:Request):
    payload=safe_json(await req.body())
    with db_session() as db:
        ch=db.query(ChannelConnection).filter_by(id=channel_id,provider='vk',mode='live').first()
        if not ch or ch.status not in ('connected','pending_webhook') or not ch.encrypted_credentials:raise HTTPException(404,'Сообщество не найдено')
        from .integrations.adapters import unseal
        credentials=unseal(ch.encrypted_credentials)
        expected=credentials.get('webhook_secret','')
        if not expected or not hmac.compare_digest(str(payload.get('secret','')),expected):raise HTTPException(403,'Неверный секрет Callback API')
        if str(payload.get('group_id'))!=ch.external_account_id:raise HTTPException(403,'Сообщество не совпадает с подключённым')
        if payload.get('type')=='confirmation':
            return PlainTextResponse(credentials.get('confirmation_token',''))
        if payload.get('type')!='message_new':return PlainTextResponse('ok')
        m=_bot_object(_bot_object(payload.get('object'),'object').get('message'),'object.message')
        if not m or not m.get('id') or not m.get('from_id') or m.get('out'):
            return PlainTextResponse('ok')
        peer=str(m.get('peer_id') or m['from_id'])
        sender=str(m['from_id'])
        got=inbound_event(db,'vk',ch,peer,m['id'],sender,f'Клиент VK {sender}',m.get('text') or '[Вложение VK]',m.get('date'),kind='attachment' if m.get('attachments') else 'text',attachment={'provider':'vk','type':'attachment'} if m.get('attachments') else None)
        db.commit()
    finish_staged([got] if got else [])
    return PlainTextResponse('ok')

@router.post('/max/{channel_id}')
async def max_bot_webhook(channel_id:str,req:Request):
    payload=safe_json(await req.body())
    with db_session() as db:
        ch,_=get_signed_channel(db,'max',channel_id,req.headers.get('X-Max-Bot-Api-Secret',''),'X-Max-Bot-Api-Secret')
        if payload.get('update_type')!='message_created':return {'ok':True,'accepted':0}
        msg=_bot_object(payload.get('message'),'message')
        sender=_bot_object(msg.get('sender'),'message.sender')
        recipient=_bot_object(msg.get('recipient'),'message.recipient')
        body=_bot_object(msg.get('body'),'message.body')
        if sender.get('is_bot') or not sender.get('user_id') or not body.get('mid'):
            return {'ok':True,'accepted':0}
        if recipient.get('chat_type')=='dialog':
            dest='user:'+str(sender['user_id'])
        elif recipient.get('chat_id'):
            dest='chat:'+str(recipient['chat_id'])
        else:return {'ok':True,'accepted':0}
        name=' '.join(str(sender.get(k) or '') for k in ('first_name','last_name')).strip() or sender.get('username') or str(sender['user_id'])
        media=_bot_attachments(body.get('attachments'))
        got=inbound_event(db,'max',ch,dest,body['mid'],sender['user_id'],name,body.get('text') or '[Медиа MAX]',safe_provider_time(msg.get('timestamp') or payload.get('timestamp'),milliseconds=True),kind='attachment' if media else 'text',attachment={'provider':'max','type':'attachment'} if media else None)
        db.commit()
    return {'ok':True,'accepted':finish_staged([got] if got else [])}
