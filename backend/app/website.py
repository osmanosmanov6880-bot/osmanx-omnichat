"""First-party embeddable website channel: real delivery without third-party keys.

The public widget key identifies a business, NEVER authorizes reading messages.
Visitors receive opaque, individually revocable bearer tokens stored as SHA256 only.
"""
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import urlsplit
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import desc, update
from sqlalchemy.orm import Session
from .db import (get_db, ChannelConnection, Conversation, Contact, Message,
                 Organization, WebsiteWidget, WebsiteVisitor, now)
from .auth import auth, audit, require_role, MAX_CHANNELS
from .services import ingest_inbound, as_message

router = APIRouter(prefix='/api', tags=['website chat'])


def public_id():
    return secrets.token_urlsafe(24)


def normalize_origin(value):
    value = value.strip().rstrip('/')
    parsed = urlsplit(value)
    localhost = parsed.hostname in ('localhost', '127.0.0.1')
    if (parsed.scheme != 'https' and not (localhost and parsed.scheme == 'http')) or not parsed.netloc:
        raise ValueError('Для публичных сайтов используйте HTTPS (HTTP разрешён только на localhost)')
    if parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('Укажите только адрес источника, например https://store.example.com')
    if parsed.hostname is None or any(c.isspace() for c in value):
        raise ValueError('Некорректный адрес сайта')
    if parsed.port is not None and not (0 < parsed.port < 65536):
        raise ValueError('Недопустимый порт')
    return value.lower()


class WebsiteInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    allowed_origins: list[str] = Field(min_length=1, max_length=15)
    greeting: str = Field(default='Здравствуйте! Чем можем вам помочь?', max_length=240)
    accent: str = Field(default='#90B7A7', pattern=r'^#[0-9a-fA-F]{6}$')

    @field_validator('allowed_origins')
    @classmethod
    def validate_origins(cls, values):
        cleaned = [normalize_origin(value) for value in values]
        if len(set(cleaned)) != len(cleaned):
            raise ValueError('Адреса сайтов не должны повторяться')
        return cleaned


class WidgetSettings(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    allowed_origins: list[str] = Field(min_length=1, max_length=15)
    greeting: str = Field(default='Здравствуйте! Чем можем вам помочь?', max_length=240)
    accent: str = Field(default='#90B7A7', pattern=r'^#[0-9a-fA-F]{6}$')
    enabled: bool = True

    @field_validator('allowed_origins')
    @classmethod
    def validate_origins(cls, values):
        return WebsiteInput.validate_origins(values)


class VisitorInput(BaseModel):
    name: str = Field(default='Посетитель сайта', min_length=1, max_length=80)


class VisitorMessage(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    client_nonce: str = Field(min_length=8, max_length=100, pattern=r'^[a-zA-Z0-9_-]+$')


class WebsiteReceipt(BaseModel):
    message_ids: list[str] = Field(min_length=1,max_length=100)
    @field_validator('message_ids')
    @classmethod
    def valid_ids(cls,values):
        from uuid import UUID
        for value in values:
            try:
                if str(UUID(value))!=value.lower():raise ValueError('Invalid ID')
            except (TypeError,ValueError,AttributeError) as exc:
                raise ValueError('Некорректный идентификатор') from exc
        return list(dict.fromkeys(values))

def widget_view(widget, channel):
    return {'id':widget.id, 'channel_id':widget.channel_id, 'key':widget.public_key,
            'name':channel.name, 'allowed_origins':json.loads(widget.allowed_origins),
            'greeting':widget.greeting, 'accent':widget.accent, 'enabled':widget.enabled,
            'status':channel.status, 'is_demo':channel.mode == 'demo', 'created_at':widget.created_at}


def get_owned_widget(db, org_id, widget_id):
    widget = db.query(WebsiteWidget).filter_by(id=widget_id, organization_id=org_id).first()
    if not widget:
        raise HTTPException(404, 'Виджет не найден')
    return widget


def get_public_widget(db, key):
    widget = db.query(WebsiteWidget).filter_by(public_key=key, enabled=True).first()
    if widget is None:
        raise HTTPException(404, 'Виджет недоступен')
    channel = db.query(ChannelConnection).filter_by(id=widget.channel_id, organization_id=widget.organization_id).first()
    if not channel or channel.status != 'connected' or channel.provider != 'website':
        raise HTTPException(404, 'Виджет недоступен')
    return widget, channel


def get_visitor(db, widget, token):
    if not token or len(token) > 256:
        raise HTTPException(401, 'Необходима сессия посетителя')
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    visitor = db.query(WebsiteVisitor).filter_by(widget_id=widget.id, token_hash=token_hash,
                                                  organization_id=widget.organization_id).first()
    if not visitor or visitor.expires_at < now():
        raise HTTPException(401, 'Сессия посетителя истекла')
    return visitor


def visitor_token(request):
    return request.headers.get('X-Widget-Session', '')


@router.get('/website-widgets')
def list_widgets(p=Depends(auth), db:Session=Depends(get_db)):
    require_role(p, 'owner', 'admin', 'lead')
    widgets=db.query(WebsiteWidget).filter_by(organization_id=p.org.id).all()
    return [widget_view(w, db.get(ChannelConnection,w.channel_id)) for w in widgets]


@router.post('/website-widgets', status_code=201)
def create_widget(payload:WebsiteInput, p=Depends(auth), db:Session=Depends(get_db)):
    require_role(p, 'owner', 'admin')
    count=db.query(ChannelConnection).filter_by(organization_id=p.org.id).count()
    if count>=MAX_CHANNELS[p.org.plan]:
        raise HTTPException(402, 'Достигнут лимит каналов текущего тарифа')
    channel=ChannelConnection(organization_id=p.org.id, provider='website',name=payload.name.strip(),
                              external_account_id=None, mode='demo' if p.org.is_demo else 'live',
                              status='connected')
    db.add(channel);db.flush()
    widget=WebsiteWidget(organization_id=p.org.id,channel_id=channel.id,public_key=public_id(),
                         allowed_origins=json.dumps(payload.allowed_origins),greeting=payload.greeting.strip(),
                         accent=payload.accent)
    db.add(widget);db.flush();audit(db,p,'website_widget.created',widget.id)
    db.commit()
    return widget_view(widget, channel)


@router.patch('/website-widgets/{widget_id}')
def update_widget(widget_id:str,payload:WidgetSettings,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p, 'owner', 'admin')
    widget=get_owned_widget(db,p.org.id,widget_id)
    channel=db.get(ChannelConnection,widget.channel_id)
    channel.name=payload.name.strip()
    widget.allowed_origins=json.dumps(payload.allowed_origins)
    widget.greeting=payload.greeting.strip()
    widget.accent=payload.accent
    widget.enabled=payload.enabled
    channel.status='connected' if payload.enabled else 'disconnected'
    audit(db,p,'website_widget.updated',widget.id)
    db.commit()
    return widget_view(widget,channel)


@router.post('/website-widgets/{widget_id}/rotate-key')
def rotate_key(widget_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    widget=get_owned_widget(db,p.org.id,widget_id)
    widget.public_key=public_id()
    audit(db,p,'website_widget.rotated',widget.id)
    db.commit()
    return widget_view(widget,db.get(ChannelConnection,widget.channel_id))


@router.get('/public/widget/{public_key}/bootstrap')
def widget_bootstrap(public_key:str,db:Session=Depends(get_db)):
    widget,channel=get_public_widget(db,public_key)
    org=db.get(Organization,widget.organization_id)
    return {'title':channel.name,'company':org.name,'greeting':widget.greeting,
            'accent':widget.accent,'is_demo':org.is_demo}


@router.post('/public/widget/{public_key}/session',status_code=201)
def start_session(public_key:str,payload:VisitorInput,request:Request,db:Session=Depends(get_db)):
    from .main import throttle
    from .public_limits import enforce_public_limit
    widget,channel=get_public_widget(db,public_key)
    # Per-site, per-ASGI-client quota is shared by all API instances.
    enforce_public_limit(db,request,'widget:'+public_key[:30],limit=12,period=3600)
    throttle(request,'widget_session:'+public_key,12,3600)
    token=secrets.token_urlsafe(48)
    visitor=WebsiteVisitor(organization_id=widget.organization_id,widget_id=widget.id,
                           token_hash=hashlib.sha256(token.encode()).hexdigest(),
                           nickname=payload.name.strip() or 'Посетитель сайта',
                           expires_at=now()+30*86400,last_activity_at=now())
    db.add(visitor);db.commit()
    return {'visitor_token':token,'expires_at':visitor.expires_at,'is_demo':channel.mode=='demo'}


@router.get('/public/widget/{public_key}/messages')
def visitor_messages(public_key:str,request:Request,db:Session=Depends(get_db)):
    widget,channel=get_public_widget(db,public_key)
    visitor=get_visitor(db,widget,visitor_token(request))
    if not visitor.conversation_id:
        return {'messages':[],'conversation_created':False}
    msgs=db.query(Message).filter_by(organization_id=widget.organization_id,conversation_id=visitor.conversation_id).order_by(desc(Message.created_at)).limit(100).all()
    return {'messages':[{'id':m.id,'body':m.body,'direction':m.direction,'created_at':m.created_at,
                         'delivery_status':m.delivery_status,'is_demo':m.is_demo} for m in reversed(msgs)],
            'conversation_created':True}


@router.post('/public/widget/{public_key}/receipts')
def confirm_widget_delivery(public_key:str,payload:WebsiteReceipt,request:Request,db:Session=Depends(get_db)):
    widget,channel=get_public_widget(db,public_key)
    visitor=get_visitor(db,widget,visitor_token(request))
    if not visitor.conversation_id:return {'confirmed':0}
    result=db.execute(update(Message).where(
        Message.id.in_(payload.message_ids),
        Message.organization_id==widget.organization_id,
        Message.conversation_id==visitor.conversation_id,
        Message.direction=='out',Message.delivery_status=='accepted'
    ).values(delivery_status='delivered',response_confirmed_at=now()))
    db.commit()
    return {'confirmed':result.rowcount or 0}

@router.post('/public/widget/{public_key}/messages',status_code=201)
def send_visitor_message(public_key:str,payload:VisitorMessage,request:Request,db:Session=Depends(get_db)):
    from .main import throttle
    widget,channel=get_public_widget(db,public_key)
    visitor=get_visitor(db,widget,visitor_token(request))
    if not payload.body.strip():raise HTTPException(422,'Empty message')
    chat_id='visitor:'+visitor.id
    external_id='web:'+visitor.id+':'+payload.client_nonce
    if visitor.conversation_id:
        # Replays must be idempotent even after the quota is reached or when
        # the browser retried because a network response was lost.
        duplicate=db.query(Message).filter_by(
            organization_id=widget.organization_id,
            conversation_id=visitor.conversation_id,
            external_id=external_id).first()
        if duplicate:
            return {'message_id':duplicate.id,'conversation_created':True,'is_demo':channel.mode=='demo'}
        # Database-backed quota is shared by all API processes. The in-memory
        # limiter below is kept as a cheap first line of defence.
        recent=db.query(Message).filter_by(
            organization_id=widget.organization_id,
            conversation_id=visitor.conversation_id,
            direction='in').filter(Message.created_at>=now()-3600).count()
        if recent >= 90:
            raise HTTPException(429,'Слишком много сообщений за час. Повторите позже.')
    # Quotas are per authenticated visitor, not per entire site behind one proxy.
    throttle(request,'widget_send:'+visitor.id,90,3600)
    msg=ingest_inbound(db,channel=channel,external_chat_id=chat_id,external_message_id=external_id,
                       sender_id=visitor.id,sender_name=visitor.nickname,text=payload.body.strip())
    visitor.last_activity_at=now()
    if visitor.conversation_id is None:
        conv=db.query(Conversation).filter_by(channel_id=channel.id,external_chat_id=chat_id,
                                             organization_id=channel.organization_id).one()
        visitor.conversation_id=conv.id
    db.commit()
    return {'message_id':msg.id, 'conversation_created':True, 'is_demo':channel.mode=='demo'}
