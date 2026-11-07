"""Meta-approved, text-only WhatsApp templates with recorded customer opt-in.

No unofficial APIs. No guesses about template approval. This module checks the
current APPROVED status with the official WABA message_templates endpoint.
Only simple body-only text templates are supported in this first increment.
"""
from __future__ import annotations

import json
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import update, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .auth import auth, audit, can_view, require_role
from .db import (get_db, now, ChannelConnection, Conversation, Contact,
                 Message, OutgoingJob, WhatsAppConsent)
from .services import as_conversation, as_message
from .integrations.adapters import adapter_for, unseal
from .integrations.base import AdapterError

router=APIRouter(prefix='/api', tags=['whatsapp-approved-templates'])
TEMPLATE_NAME = re.compile(r'^[a-z0-9_]{1,512}$')
LANGUAGE = re.compile(r'^[a-z]{2}(?:_[A-Z]{2})?$')
MARKER = re.compile(r'\{\{([1-9][0-9]*)\}\}')


def supported_template(data):
    """Whitelist only templates whose body we can exactly preview and send."""
    if not isinstance(data,dict) or data.get('status')!='APPROVED':return None
    name=str(data.get('name') or '')
    language=str(data.get('language') or '')
    if not TEMPLATE_NAME.fullmatch(name) or not LANGUAGE.fullmatch(language):return None
    components=data.get('components')
    if not isinstance(components,list) or len(components)!=1 or not isinstance(components[0],dict):return None
    body_component=components[0]
    if str(body_component.get('type','')).upper()!='BODY':return None
    body=body_component.get('text')
    if not isinstance(body,str) or not body.strip() or len(body)>1024:return None
    indexes=[int(x) for x in MARKER.findall(body)]
    count=max(indexes, default=0)
    if count>8 or set(indexes)!=set(range(1,count+1)):return None
    if '{{' in MARKER.sub('',body) or '}}' in MARKER.sub('',body):return None
    return {'name':name,'language':language,'body':body,'param_count':count}


def render_template(body,parameters):
    return MARKER.sub(lambda m:parameters[int(m.group(1))-1],body)


def scoped_whatsapp(db, principal, conversation_id):
    conversation=db.query(Conversation).filter_by(id=conversation_id,
        organization_id=principal.org.id).first()
    if not conversation:raise HTTPException(404,'Диалог не найден')
    if not can_view(principal,conversation):raise HTTPException(403,'Диалог не назначен вам')
    channel=db.query(ChannelConnection).filter_by(id=conversation.channel_id,
        organization_id=principal.org.id).first()
    if not channel or channel.provider!='whatsapp':
        raise HTTPException(422,'Эта функция доступна только для WhatsApp')
    if principal.org.is_demo or channel.mode!='live':
        raise HTTPException(403,'Для шаблонов требуется настоящий разрешённый WhatsApp Business API')
    return conversation,channel


def current_consent(db,conversation,channel):
    return db.query(WhatsAppConsent).filter_by(organization_id=conversation.organization_id,
        contact_id=conversation.contact_id,channel_id=channel.id,
        recipient_id=conversation.external_recipient_id).first()


class ConsentRecord(BaseModel):
    source: str = Field(min_length=8,max_length=240)
    confirmed: bool
    @field_validator('source')
    @classmethod
    def non_blank(cls,value):
        value=value.strip()
        if len(value)<8:raise ValueError('Опишите, где и когда клиент дал согласие')
        return value


class TemplateReply(BaseModel):
    name: str = Field(min_length=1,max_length=512)
    language: str = Field(min_length=2,max_length=5)
    parameters: list[str] = Field(default_factory=list,max_length=8)
    expected_version: int = Field(ge=0)
    client_nonce: str = Field(min_length=8,max_length=100)
    @field_validator('name')
    @classmethod
    def name_ok(cls,v):
        if not TEMPLATE_NAME.fullmatch(v):raise ValueError('Недопустимое имя шаблона')
        return v
    @field_validator('language')
    @classmethod
    def language_ok(cls,v):
        if not LANGUAGE.fullmatch(v):raise ValueError('Недопустимый язык шаблона')
        return v
    @field_validator('parameters')
    @classmethod
    def params_ok(cls,values):
        if any(not isinstance(x,str) or not x.strip() or len(x)>200 or '\n' in x for x in values):
            raise ValueError('Параметры должны быть короткими непустыми строками')
        return values


@router.get('/conversations/{conversation_id}/whatsapp-templates')
async def list_templates(conversation_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    conversation,channel=scoped_whatsapp(db,p,conversation_id)
    if channel.status!='connected':raise HTTPException(409,'Канал ещё не проверен входящим сообщением')
    try:
        templates=await adapter_for('whatsapp').approved_text_templates(unseal(channel.encrypted_credentials))
    except AdapterError as exc:
        raise HTTPException(503,'Не удалось получить одобренные шаблоны. Проверьте WABA ID, права токена и подключение.') from exc
    consent=current_consent(db,conversation,channel)
    return {'templates':templates,
            'consent_recorded':bool(consent and consent.revoked_at is None),
            'approval_note':'Список проверен в официальном WhatsApp Business API; это не подтверждение доставки'}


@router.post('/conversations/{conversation_id}/whatsapp-consent')
def record_consent(conversation_id:str,payload:ConsentRecord,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    conversation,channel=scoped_whatsapp(db,p,conversation_id)
    if not payload.confirmed:
        raise HTTPException(422,'Сотрудник обязан подтвердить наличие согласия клиента')
    if not conversation.external_recipient_id:
        raise HTTPException(422,'Нет подтверждённого идентификатора получателя')
    consent=current_consent(db,conversation,channel)
    if consent is None:
        consent=WhatsAppConsent(organization_id=p.org.id, contact_id=conversation.contact_id,
            channel_id=channel.id, recipient_id=conversation.external_recipient_id)
        db.add(consent)
    consent.source=payload.source
    consent.captured_at=now()
    consent.revoked_at=None
    consent.recorded_by=p.user.id
    audit(db,p,'whatsapp.consent.recorded',conversation.id,'Recorded by employee; not platform-verified')
    db.commit()
    return {'consent_recorded':True,'verified_by_provider':False}


@router.post('/conversations/{conversation_id}/whatsapp-consent/revoke')
def revoke_consent(conversation_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    conversation,channel=scoped_whatsapp(db,p,conversation_id)
    consent=current_consent(db,conversation,channel)
    if consent and consent.revoked_at is None:
        consent.revoked_at=now()
        audit(db,p,'whatsapp.consent.revoked',conversation.id)
        db.commit()
    return {'consent_recorded':False}


@router.post('/conversations/{conversation_id}/whatsapp-template',status_code=201)
async def send_template(conversation_id:str,payload:TemplateReply,p=Depends(auth),db:Session=Depends(get_db)):
    conversation,channel=scoped_whatsapp(db,p,conversation_id)
    if channel.status!='connected':raise HTTPException(409,'Подключение WhatsApp не готово')
    if not conversation.external_recipient_id:
        raise HTTPException(422,'Нет получателя WhatsApp для этого диалога')
    existing=db.query(Message).filter_by(organization_id=p.org.id,
        conversation_id=conversation.id,client_nonce=payload.client_nonce).first()
    if existing:
        meta=json.loads(existing.attachment or '{}')
        if (existing.kind=='whatsapp_template' and
            meta.get('template_name')==payload.name and
            meta.get('language')==payload.language and
            meta.get('parameters')==payload.parameters):
            return {'message':as_message(existing),'conversation':as_conversation(db,conversation),'duplicate':True}
        raise HTTPException(409,'Этот идентификатор отправки уже используется для другого сообщения')
    consent=current_consent(db,conversation,channel)
    if not consent or consent.revoked_at is not None:
        raise HTTPException(409,'До отправки требуется зафиксированное согласие получателя')
    if conversation.reply_lock_owner_id and conversation.reply_lock_expires_at and \
        conversation.reply_lock_expires_at>now() and conversation.reply_lock_owner_id!=p.user.id:
        raise HTTPException(409,'Другой сотрудник сейчас отвечает в этом диалоге')
    try:
        approved=await adapter_for('whatsapp').approved_text_templates(unseal(channel.encrypted_credentials))
    except AdapterError as exc:
        raise HTTPException(503,'Не удалось повторно проверить статус шаблона в Meta') from exc
    selection=next((t for t in approved if t['name']==payload.name and t['language']==payload.language),None)
    if not selection:
        raise HTTPException(409,'Шаблон не одобрен Meta или не поддерживается этой версией')
    if len(payload.parameters)!=selection['param_count']:
        raise HTTPException(422,'Число параметров не совпадает с утверждённым шаблоном')
    result=db.execute(update(Conversation).where(Conversation.id==conversation.id,
        Conversation.organization_id==p.org.id, Conversation.version==payload.expected_version,
        or_(Conversation.reply_lock_owner_id.is_(None),
            Conversation.reply_lock_owner_id==p.user.id,
            Conversation.reply_lock_expires_at.is_(None),
            Conversation.reply_lock_expires_at<=now())).values(version=Conversation.version+1))
    if result.rowcount!=1:
        db.rollback();raise HTTPException(409,'Диалог изменился. Обновите переписку и повторите действие.')
    created=now()
    metadata={'template_name':payload.name,'language':payload.language,
              'parameters':payload.parameters}
    message=Message(organization_id=p.org.id,conversation_id=conversation.id,
        external_id='client-'+payload.client_nonce, client_nonce=payload.client_nonce,
        direction='out',kind='whatsapp_template',
        body=render_template(selection['body'],payload.parameters),
        attachment=json.dumps(metadata,ensure_ascii=False),delivery_status='queued',
        is_demo=False,author_user_id=p.user.id,created_at=created)
    db.add(message);db.flush()
    db.add(OutgoingJob(organization_id=p.org.id,message_id=message.id,channel_id=channel.id))
    conversation.version=payload.expected_version+1
    conversation.last_message_at=created
    if not conversation.first_reply_at:conversation.first_reply_at=created
    if conversation.status=='new':conversation.status='in_progress'
    audit(db,p,'whatsapp.template.queued',conversation.id,payload.name)
    try:db.commit()
    except IntegrityError:
        db.rollback();raise HTTPException(409,'Сообщение уже поставлено в очередь')
    db.refresh(conversation)
    return {'message':as_message(message),'conversation':as_conversation(db,conversation),
            'duplicate':False,'note':'Шаблон поставлен в очередь; доставка клиенту пока не подтверждена'}
