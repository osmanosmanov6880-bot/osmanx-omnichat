"""Permitted backfill/synchronization only. Never scrape websites or private accounts."""
import json
import logging
from sqlalchemy.orm import Session
from .db import ChannelConnection, Conversation, Contact, Message, now
from .services import ingest_inbound
from .integrations.adapters import adapter_for, seal, unseal
from .integrations.base import AdapterError

log = logging.getLogger('omnichat.sync')

def _text(message):
    content=message.get('content') or {}
    if isinstance(content,dict):
        value=content.get('text')
        if isinstance(value,str):return value
    return message.get('text') or '[Медиа или служебное сообщение]'

async def sync_avito(db:Session, channel:ChannelConnection):
    """Uses Avito's officially documented getChatsV2 + getMessagesV3 operations.

    Polling provides a conservative fallback while webhook origin verification is unavailable.
    No claim of real-time SLA or complete history: provider limits may truncate backfill.
    """
    if channel.provider!='avito' or channel.mode!='live' or channel.status not in ('connected','pending_sync'):
        raise AdapterError('Синхронизация разрешена только для реально подключённого Авито')
    adapter=adapter_for('avito')
    credentials=unseal(channel.encrypted_credentials)
    if credentials.get('expires_at') and credentials['expires_at']<now()+120:
        credentials=await adapter.refresh_credentials(credentials)
        credentials['expires_at']=now()+int(credentials.get('expires_in',86400))
        channel.encrypted_credentials=seal(credentials)
    account_id=str(channel.external_account_id)
    credentials['account_id']=account_id
    chats=await adapter.get_conversations(credentials)
    if not isinstance(chats,list):raise AdapterError('Авито вернул непредусмотренный формат чатов')
    accepted=0
    for chat in chats[:70]:
        chat_id=str(chat.get('id') or '')
        if not chat_id:continue
        users=chat.get('users') or []
        other=next((u for u in users if str(u.get('id',''))!=account_id),{})
        sender_id=str(other.get('id') or chat.get('user_id') or chat_id)
        sender_name=other.get('name') or 'Покупатель Авито'
        messages=await adapter.get_messages(credentials,chat_id)
        for item in sorted(messages,key=lambda m:float(m.get('created') or m.get('created_at') or 0)):
            message_id=str(item.get('id') or '')
            if not message_id:continue
            author_id=str(item.get('author_id') or item.get('sender_id') or '')
            direction=item.get('direction')
            from_business=direction=='out' or (author_id and author_id==account_id)
            timestamp=float(item.get('created') or item.get('created_at') or now())
            kind=str(item.get('type') or 'text')
            if from_business:
                c=db.query(Conversation).filter_by(channel_id=channel.id,external_chat_id=chat_id,organization_id=channel.organization_id).first()
                if c and not db.query(Message).filter_by(organization_id=channel.organization_id,conversation_id=c.id,external_id=message_id).first():
                    db.add(Message(organization_id=channel.organization_id,conversation_id=c.id,external_id=message_id,
                        direction='out',body=_text(item),kind=kind,created_at=timestamp,delivery_status='delivered',response_confirmed_at=timestamp,is_demo=False))
                    if not c.first_reply_at:c.first_reply_at=timestamp
                    c.last_message_at=max(c.last_message_at,timestamp)
                continue
            if author_id and author_id!=sender_id and author_id!=account_id:
                sender_id=author_id
            existing=db.query(Message).join(Conversation,Conversation.id==Message.conversation_id).filter(
                Message.organization_id==channel.organization_id,Conversation.channel_id==channel.id,
                Conversation.external_chat_id==chat_id,Message.external_id==message_id).first()
            if existing:continue
            msg=ingest_inbound(db,channel=channel,external_chat_id=chat_id,
                 external_message_id=message_id,sender_id=sender_id,sender_name=sender_name,
                 text=_text(item),timestamp=timestamp,kind=kind,history=True)
            if msg:accepted+=1
    channel.last_error=None
    channel.last_sync_at=now()
    channel.status='connected'
    channel.last_verified_at=now()
    db.commit()
    return {'chats_scanned':len(chats[:70]), 'new_inbound_messages':accepted}

async def sync_all_avito(db_factory,limit=5):
    total=0
    with db_factory() as db:
        channels=db.query(ChannelConnection).filter(ChannelConnection.provider=='avito',ChannelConnection.mode=='live',ChannelConnection.status.in_(['connected','pending_sync'])).order_by(ChannelConnection.last_sync_at.asc()).limit(limit).all()
        for channel in channels:
            if channel.last_sync_at and now()-channel.last_sync_at<45:continue
            try:
                await sync_avito(db,channel)
                total+=1
            except AdapterError as exc:
                db.rollback()
                channel=db.get(ChannelConnection,channel.id)
                channel.last_error=str(exc)[:200];db.commit()
                log.warning('Avito sync error: channel_id=%s, reason=%s',channel.id,exc)
    return total
