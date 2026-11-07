"""Tenant-safe application features: quick replies, SLA, privacy, staff and exports."""
import json
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy import update, desc, case
from .db import (get_db, Organization, AuthSession, LoginFailure, OAuthState, PendingChannelSelection, User, Membership, ChannelConnection,
                 Contact, ContactIdentity, WhatsAppConsent, Conversation, Message, Note, AutomationRule, SavedInboxView,
                 WebhookEvent, ProviderDeliveryReceipt, ChannelDispatchLease, InboundJob, Invite, BillingEvent, AuditLog, OutgoingJob, QuickReply, WebsiteWidget, WebsiteVisitor, PublicRateBucket, WorkerHeartbeat, now)
from .auth import auth, audit, require_role
from .delivery_truth import confirmed_response
from .services import as_conversation, as_contact

router = APIRouter(prefix='/api', tags=['workspace'])

class TemplateInput(BaseModel):
    title: str = Field(min_length=2, max_length=90)
    body: str = Field(min_length=1, max_length=1000)

class AvailabilityInput(BaseModel):
    available: bool

class PrivacySettings(BaseModel):
    retention_days: int = Field(ge=30, le=3650)
    sla_minutes: int = Field(ge=1, le=120)

class DeleteInput(BaseModel):
    confirmation: str

SUPPORTED_CURRENCIES = {'RUB','USD','EUR','GBP','SEK','NOK','DKK','AED','SAR','KZT','TRY','INR','CAD','AUD','JPY','CHF','PLN','CZK','BRL','MXN','ZAR','GEL','AZN','UAH'}

class LocalizationInput(BaseModel):
    currency: str = Field(min_length=3,max_length=3)
    timezone: str = Field(min_length=2,max_length=64)

    @field_validator('currency')
    @classmethod
    def validate_currency(cls,value):
        if value.upper() not in SUPPORTED_CURRENCIES:raise ValueError('Unsupported ISO 4217 currency')
        return value.upper()

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls,value):
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
        try:ZoneInfo(value)
        except (ZoneInfoNotFoundError,ValueError):raise ValueError('Unknown IANA time zone')
        return value

@router.get('/organization/localization')
def get_localization(p=Depends(auth)):
    require_role(p,'owner','admin')
    return {'currency':p.org.currency,'timezone':p.org.timezone,'currencies':sorted(SUPPORTED_CURRENCIES)}

@router.patch('/organization/localization')
def set_localization(payload:LocalizationInput,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if payload.currency!=p.org.currency and db.query(Contact).filter(Contact.organization_id==p.org.id,Contact.deal_amount.isnot(None)).first():
        raise HTTPException(409,'Currency cannot be changed when existing deal amounts would be reinterpreted')
    p.org.currency=payload.currency;p.org.timezone=payload.timezone
    audit(db,p,'organization.localization_updated',p.org.id,f'{payload.currency}/{payload.timezone}')
    db.commit()
    return {'currency':p.org.currency,'timezone':p.org.timezone}

@router.get('/quick-replies')
def quick_replies(p=Depends(auth), db:Session=Depends(get_db)):
    return [{'id':r.id,'title':r.title,'body':r.body} for r in db.query(QuickReply).filter_by(organization_id=p.org.id).order_by(QuickReply.title).all()]

@router.post('/quick-replies', status_code=201)
def create_quick_reply(payload: TemplateInput, p=Depends(auth), db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    if db.query(QuickReply).filter_by(organization_id=p.org.id).count() >= 100:
        raise HTTPException(402,'Достигнут лимит шаблонов')
    item=QuickReply(organization_id=p.org.id,title=payload.title.strip(),body=payload.body.strip())
    db.add(item);db.flush();audit(db,p,'template.created',item.id);db.commit()
    return {'id':item.id,'title':item.title,'body':item.body}

@router.delete('/quick-replies/{template_id}')
def delete_quick_reply(template_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    item=db.query(QuickReply).filter_by(organization_id=p.org.id,id=template_id).first()
    if not item:raise HTTPException(404,'Шаблон не найден')
    audit(db,p,'template.deleted',item.id);db.delete(item);db.commit()
    return {'ok':True}

@router.post('/conversations/{conversation_id}/unread')
def mark_unread(conversation_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    c=db.query(Conversation).filter_by(organization_id=p.org.id,id=conversation_id).first()
    if not c: raise HTTPException(404,'Диалог не найден')
    if p.role in ('operator','manager') and c.assigned_user_id != p.user.id:raise HTTPException(403,'Нет доступа')
    # Inbound webhooks use atomic +1: marking unread must not write a stale
    # ORM counter over events that arrived in a different worker process.
    filters=[Conversation.id==c.id,Conversation.organization_id==p.org.id]
    if p.role in ('operator','manager'):
        filters.append(Conversation.assigned_user_id==p.user.id)
    changed=db.execute(update(Conversation).where(*filters).values(
        unread_count=case((Conversation.unread_count<1,1),else_=Conversation.unread_count),
        version=Conversation.version+1)).rowcount
    if changed!=1:
        db.rollback();raise HTTPException(409,'Диалог изменился. Обновите переписку.')
    audit(db,p,'conversation.unread',c.id);db.commit()
    return as_conversation(db,c)

@router.post('/conversations/{conversation_id}/archive')
def archive_conversation(conversation_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    c=db.query(Conversation).filter_by(organization_id=p.org.id,id=conversation_id).first()
    if not c:raise HTTPException(404,'Диалог не найден')
    if p.role in ('manager','operator') and c.assigned_user_id!=p.user.id:raise HTTPException(403,'Нет доступа')
    c.archived=True;c.status='closed';c.version+=1
    audit(db,p,'conversation.archived',c.id);db.commit()
    return as_conversation(db,c)

@router.get('/alerts')
def alerts(p=Depends(auth),db:Session=Depends(get_db)):
    conversations=db.query(Conversation).filter_by(organization_id=p.org.id).filter(Conversation.status!='closed').all()
    if p.role in ('manager','operator'):
        conversations=[c for c in conversations if c.assigned_user_id==p.user.id]
    pending=[]
    for c in conversations:
        if not c.last_inbound_at or now()-c.last_inbound_at < p.org.sla_minutes*60:continue
        answered=db.query(Message).filter(Message.organization_id==p.org.id, Message.conversation_id==c.id,
             confirmed_response(),Message.created_at>=c.last_inbound_at).first()
        if answered:continue
        pending.append({'conversation_id':c.id,'minutes_waiting':int((now()-c.last_inbound_at)//60),
                        'client':db.get(Contact,c.contact_id).name,'sla_minutes':p.org.sla_minutes})
    return {'unanswered_over_sla':len(pending),'items':pending[:30]}

@router.patch('/team/{user_id}/availability')
def set_availability(user_id:str,payload:AvailabilityInput,p=Depends(auth),db:Session=Depends(get_db)):
    if user_id!=p.user.id:require_role(p,'owner','admin','lead')
    membership=db.query(Membership).filter_by(organization_id=p.org.id,user_id=user_id,active=True).first()
    if not membership:raise HTTPException(404,'Сотрудник не найден')
    membership.available=payload.available
    audit(db,p,'team.availability',user_id,str(payload.available));db.commit()
    return {'user_id':user_id,'available':payload.available}

@router.patch('/team/{user_id}/role')
def change_role(user_id:str, payload:dict,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    member=db.query(Membership).filter_by(organization_id=p.org.id,user_id=user_id,active=True).first()
    if not member:raise HTTPException(404,'Сотрудник не найден')
    if member.role=='owner':raise HTTPException(403,'Изменение владельца требует отдельной процедуры')
    role=payload.get('role')
    if role not in ('admin','lead','manager','operator'):raise HTTPException(422,'Недопустимая роль')
    if p.role=='admin' and (member.role=='admin' or role=='admin'):raise HTTPException(403,'Только владелец может менять роль администратора')
    member.role=role;audit(db,p,'team.role_changed',user_id,role);db.commit()
    return {'user_id':user_id,'role':role}

@router.get('/organization/privacy')
def privacy(p=Depends(auth)):
    require_role(p,'owner','admin')
    return {'retention_days':p.org.retention_days,'sla_minutes':p.org.sla_minutes,'deletion_available':p.role=='owner'}

@router.patch('/organization/privacy')
def set_privacy(payload:PrivacySettings,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    p.org.retention_days=payload.retention_days;p.org.sla_minutes=payload.sla_minutes
    audit(db,p,'organization.privacy_updated',p.org.id, f'{payload.retention_days}d/{payload.sla_minutes}m');db.commit()
    return {'retention_days':p.org.retention_days,'sla_minutes':p.org.sla_minutes}

@router.get('/organization/export')
def export_data(p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    oid=p.org.id
    contacts=db.query(Contact).filter_by(organization_id=oid).all()
    convs=db.query(Conversation).filter_by(organization_id=oid).all()
    messages=db.query(Message).filter_by(organization_id=oid).all()
    notes=db.query(Note).filter_by(organization_id=oid).all()
    wa_consents=db.query(WhatsAppConsent).filter_by(organization_id=oid).all()
    return {'exported_at':datetime.now(timezone.utc).isoformat(),
      'organization':{'id':oid,'name':p.org.name},
      'contacts':[as_contact(c) for c in contacts],
      'conversations':[{'id':c.id,'contact_id':c.contact_id,'channel_id':c.channel_id,'status':c.status,'created_at':c.created_at} for c in convs],
      'messages':[{'id':m.id,'conversation_id':m.conversation_id,'direction':m.direction,'body':m.body,'kind':m.kind,'created_at':m.created_at,'delivery_status':m.delivery_status,'is_demo':m.is_demo} for m in messages],
      'notes':[{'id':n.id,'conversation_id':n.conversation_id,'body':n.body,'created_at':n.created_at} for n in notes],
      'whatsapp_consents':[{'contact_id':c.contact_id,'channel_id':c.channel_id,
        'recipient_id':c.recipient_id,'source':c.source,'captured_at':c.captured_at,
        'revoked_at':c.revoked_at} for c in wa_consents]}

@router.post('/contacts/{target_id}/merge/{source_id}')
def merge_contacts(target_id:str,source_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    """Manual identity linking only, cross-provider matching by name never performed."""
    require_role(p,'owner','admin','lead')
    if target_id==source_id:raise HTTPException(422,'Нужны два разных контакта')
    target=db.query(Contact).filter_by(id=target_id,organization_id=p.org.id).first()
    source=db.query(Contact).filter_by(id=source_id,organization_id=p.org.id).first()
    if not target or not source:raise HTTPException(404,'Контакт не найден')
    db.query(Conversation).filter_by(organization_id=p.org.id,contact_id=source.id).update({'contact_id':target.id},synchronize_session=False)
    db.query(ContactIdentity).filter_by(organization_id=p.org.id,contact_id=source.id).update({'contact_id':target.id},synchronize_session=False)
    db.query(WhatsAppConsent).filter_by(organization_id=p.org.id,contact_id=source.id).update({'contact_id':target.id},synchronize_session=False)
    target.tags=json.dumps(sorted(set(json.loads(target.tags or '[]')+json.loads(source.tags or '[]'))),ensure_ascii=False)
    audit(db,p,'contacts.manual_merge',target.id,f'from:{source.id}')
    db.delete(source);db.commit()
    return as_contact(target)

@router.post('/organization/delete')
def delete_workspace(payload:DeleteInput, response:Response,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner')
    if payload.confirmation != p.org.name:
        raise HTTPException(422,'Введите полное название организации для подтверждения')
    oid=p.org.id
    # Delete in child-first order; preserve other organizations' data and shared users.
    ch_ids=[x.id for x in db.query(ChannelConnection).filter_by(organization_id=oid).all()]
    from .db import DispatchPause, DeliveryTransition
    for model in (InboundJob, ChannelDispatchLease, DeliveryTransition, DispatchPause, OutgoingJob, Note, Message, WebsiteVisitor, AutomationRule, SavedInboxView, QuickReply, ContactIdentity, WhatsAppConsent,
                  Conversation, Contact, WebsiteWidget, ProviderDeliveryReceipt, ChannelConnection, BillingEvent, Invite, AuditLog):
        db.query(model).filter_by(organization_id=oid).delete(synchronize_session=False)
    for channel_id in ch_ids:
        pass  # WebhookEvent fingerprints contain no readable client content; TTL cleaner handles events.
    db.query(OAuthState).filter_by(organization_id=oid).delete(synchronize_session=False)
    db.query(PendingChannelSelection).filter_by(organization_id=oid).delete(synchronize_session=False)
    db.query(AuthSession).filter_by(organization_id=oid).delete(synchronize_session=False)
    members=db.query(Membership).filter_by(organization_id=oid).all()
    user_ids=[m.user_id for m in members]
    for m in members:db.delete(m)
    db.delete(p.org);db.flush()
    for user_id in user_ids:
        if not db.query(Membership).filter_by(user_id=user_id).first():
            db.query(AuthSession).filter_by(user_id=user_id).delete(synchronize_session=False)
            user=db.get(User,user_id)
            if user:db.delete(user)
    db.commit()
    from .auth import SESSION_COOKIE, CSRF_COOKIE
    response.delete_cookie(SESSION_COOKIE,path='/');response.delete_cookie(CSRF_COOKIE,path='/')
    return {'ok':True,'deleted_organization':oid}


def purge_expired(db:Session, *, message_limit_per_organization:int=2000):
    """Incremental tenant-scoped retention; no unbounded historical message loads."""
    if not 1<=message_limit_per_organization<=10000:
        raise ValueError('Invalid cleanup batch limit')
    total=0
    for org_id,days in db.query(Organization.id,Organization.retention_days).all():
        cutoff=now()-days*86400
        removed=0
        while removed<message_limit_per_organization:
            ids=[mid for (mid,) in db.query(Message.id).filter_by(organization_id=org_id)
                 .filter(Message.created_at<cutoff).order_by(Message.created_at,Message.id)
                 .limit(min(250,message_limit_per_organization-removed)).all()]
            if not ids:break
            from .db import DeliveryTransition
            job_ids=[x[0] for x in db.query(OutgoingJob.id).filter_by(organization_id=org_id).filter(OutgoingJob.message_id.in_(ids)).all()]
            if job_ids:
                db.query(DeliveryTransition).filter_by(organization_id=org_id).filter(DeliveryTransition.job_id.in_(job_ids)).delete(synchronize_session=False)
            db.query(OutgoingJob).filter_by(organization_id=org_id).filter(
                OutgoingJob.message_id.in_(ids)).delete(synchronize_session=False)
            total+=db.query(Message).filter_by(organization_id=org_id).filter(
                Message.id.in_(ids)).delete(synchronize_session=False)
            removed+=len(ids)
        total+=db.query(Note).filter_by(organization_id=org_id).filter(
            Note.created_at<cutoff).delete(synchronize_session=False)
        db.commit()
    clock=now()
    from .db import DeliveryTransition, DispatchPause
    for org_id,days in db.query(Organization.id,Organization.retention_days).all():
        db.query(DeliveryTransition).filter(DeliveryTransition.organization_id==org_id,DeliveryTransition.created_at<clock-days*86400).delete(synchronize_session=False)
    db.query(DispatchPause).filter(DispatchPause.expires_at.is_not(None),DispatchPause.expires_at<clock).delete(synchronize_session=False)
    from .inbound_jobs import expire_payloads
    expire_payloads(db, stamp=clock, limit=500)
    db.query(WebsiteVisitor).filter(WebsiteVisitor.expires_at<clock).delete(synchronize_session=False)
    db.query(AuthSession).filter(AuthSession.expires_at<clock).delete(synchronize_session=False)
    db.query(OAuthState).filter(OAuthState.expires_at<clock).delete(synchronize_session=False)
    db.query(PendingChannelSelection).filter(PendingChannelSelection.expires_at<clock).delete(synchronize_session=False)
    db.query(LoginFailure).filter(LoginFailure.attempted_at<clock-86400).delete(synchronize_session=False)
    db.query(WebhookEvent).filter(WebhookEvent.created_at<clock-30*86400).delete(synchronize_session=False)
    # Keep unmatched/out-of-order callback metadata briefly; never retain raw phone numbers.
    db.query(ProviderDeliveryReceipt).filter(ProviderDeliveryReceipt.last_seen_at<clock-30*86400).delete(synchronize_session=False)
    db.query(PublicRateBucket).filter(PublicRateBucket.created_at<clock-2*86400).delete(synchronize_session=False)
    db.query(WorkerHeartbeat).filter(WorkerHeartbeat.last_seen_at<clock-7*86400).delete(synchronize_session=False)
    db.commit()
    return total

class DeliveryResolution(BaseModel):
    status: str = Field(pattern='^(accepted|failed)$')
    evidence: str = Field(min_length=8,max_length=500)
    external_id: str | None = Field(default=None,max_length=250)

@router.get('/operations/outbox')
def operations_outbox(status:str='',p=Depends(auth),db:Session=Depends(get_db)):
    """Tenant-restricted failed/uncertain queue visibility; no credentials exposed."""
    require_role(p,'owner','admin','lead')
    query=db.query(OutgoingJob).filter_by(organization_id=p.org.id)
    if status:
        if status not in ('queued','processing','uncertain','failed','done','cancelled'):
            raise HTTPException(422,'Неизвестный статус')
        query=query.filter_by(status=status)
    # Put messages requiring human reconciliation first. Otherwise an older
    # uncertain send can disappear behind hundreds of newer successful sends.
    urgency=case((OutgoingJob.status=='uncertain',0),
                 (OutgoingJob.status=='failed',1),
                 (OutgoingJob.status=='processing',2),
                 (OutgoingJob.status=='queued',3),else_=4)
    jobs=query.order_by(urgency.asc(),desc(OutgoingJob.created_at)).limit(100).all()
    # Lightweight per-row eligibility, always scoped to this organization.
    from .outbox_control import retry_allowed
    result=[]
    for job in jobs:
        msg=db.query(Message).filter_by(id=job.message_id,organization_id=p.org.id).first()
        conv=db.query(Conversation).filter_by(id=msg.conversation_id,organization_id=p.org.id).first() if msg else None
        ch=db.query(ChannelConnection).filter_by(id=job.channel_id,organization_id=p.org.id).first()
        retry=bool(msg and conv and ch and retry_allowed(job,msg,conv,ch))
        result.append({'id':job.id,'message_id':job.message_id,'channel_id':job.channel_id,'status':job.status,
          'attempts':job.attempts,'last_error':job.last_error,'created_at':job.created_at,
          'processing_phase':('Подготовка до отправки' if job.claim_token and job.send_started_at is None
                              else 'Запрос передан площадке' if job.status=='processing'
                              else None),
          'can_cancel':bool(job.status=='queued' and msg and msg.delivery_status=='queued' and conv and ch and conv.channel_id==ch.id and msg.direction=='out'),
          'can_retry_verified':retry})
    return result

@router.post('/operations/outbox/{job_id}/resolve')
def resolve_uncertain_delivery(job_id:str,payload:DeliveryResolution,p=Depends(auth),db:Session=Depends(get_db)):
    """Never auto-resend unknown delivery; reconciliation requires a manual evidence note."""
    require_role(p,'owner','admin')
    job=db.query(OutgoingJob).filter_by(id=job_id,organization_id=p.org.id).first()
    if not job:raise HTTPException(404,'Задание не найдено')
    if job.status!='uncertain':raise HTTPException(409,'Это задание не требует ручной сверки')
    msg=db.query(Message).filter_by(id=job.message_id,organization_id=p.org.id).first()
    if not msg:raise HTTPException(409,'Исходное сообщение недоступно')
    # A second manager, or a delayed webhook, may change this job between
    # reading the row and writing the manual decision. Only one reconciler can
    # win this SQL compare-and-swap; never silently overwrite colleagues.
    target='done' if payload.status=='accepted' else 'failed'
    changed=db.execute(update(OutgoingJob).where(
        OutgoingJob.id==job.id,OutgoingJob.organization_id==p.org.id,
        OutgoingJob.status=='uncertain'
    ).values(status=target,claimed_at=None,claim_token=None,
             last_error=None if payload.status=='accepted' else 'Отправка не подтверждена вручную')).rowcount
    if changed!=1:
        db.rollback()
        raise HTTPException(409,'Задание уже проверено коллегой. Обновите состояние очереди.')
    values={'delivery_status':payload.status}
    if payload.external_id and payload.status=='accepted':
        values['external_id']=payload.external_id
    touched=db.execute(update(Message).where(
        Message.id==msg.id,Message.organization_id==p.org.id,
        Message.delivery_status=='uncertain'
    ).values(**values)).rowcount
    if touched!=1:
        db.rollback()
        raise HTTPException(409,'Статус сообщения изменился. Сверка не записана.')
    from .dispatch_control import record_transition
    job.status=target
    record_transition(db,job,'uncertain','manual_accepted' if target=='done' else 'manual_failed')
    audit(db,p,'outbox.manual_reconcile',job.id,f'{payload.status}: {payload.evidence}')
    db.commit()
    return {'id':job.id,'status':target,'delivery_status':payload.status,'verified_by':p.user.id}
