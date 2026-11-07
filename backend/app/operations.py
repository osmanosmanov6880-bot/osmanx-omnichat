"""Bounded, tenant-scoped operational health and delivery diagnostics.

Return aggregates from SQL, not all conversations or messages in application memory.
Provider tokens and message text are deliberately excluded from this endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, case, update, and_, or_
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Literal
import base64
import json
import hashlib
import hmac
from .db import get_db, Organization, ChannelConnection, Conversation, OutgoingJob, Message, AuditLog, ProviderDeliveryReceipt, ChannelDispatchLease, InboundJob, now
from .auth import auth, require_role, audit
from .worker_monitor import worker_health
from .inbound_jobs import pending_limit

router=APIRouter(prefix='/api/operations', tags=['operations'])

@router.get('/overview')
def operations_overview(p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p, 'owner', 'admin', 'lead')
    org_id = p.org.id
    paused_at = db.query(Organization.outbound_paused_at).filter_by(id=org_id).scalar()
    inbound_paused_at = db.query(Organization.inbound_paused_at).filter_by(id=org_id).scalar()
    clock = now()
    statuses = dict(db.query(OutgoingJob.status, func.count(OutgoingJob.id)).filter(
        OutgoingJob.organization_id == org_id).group_by(OutgoingJob.status).all())
    delayed = db.query(func.count(OutgoingJob.id)).filter(
        OutgoingJob.organization_id == org_id,
        OutgoingJob.status.in_(['queued', 'processing']),
        OutgoingJob.created_at < clock - 300).scalar() or 0
    channel_total = db.query(func.count(ChannelConnection.id)).filter_by(organization_id=org_id).scalar() or 0
    live_connected = db.query(func.count(ChannelConnection.id)).filter_by(
        organization_id=org_id, status='connected', mode='live').scalar() or 0
    paused_total = db.query(func.count(ChannelConnection.id)).filter(
        ChannelConnection.organization_id==org_id,
        ChannelConnection.mode=='live',
        ChannelConnection.outbound_paused_at.is_not(None)).scalar() or 0
    # Only aggregate slots owned by this tenant; never expose worker IDs or
    # competing organizations' queued messages to a customer dashboard.
    busy_senders = db.query(func.count(ChannelDispatchLease.channel_id)).filter(
        ChannelDispatchLease.organization_id==org_id,
        ChannelDispatchLease.expires_at>clock).scalar() or 0
    inbound_status = dict(db.query(InboundJob.status,func.count(InboundJob.id)).filter(
        InboundJob.organization_id==org_id).group_by(InboundJob.status).all())
    inbound_duplicates_day = db.query(func.coalesce(func.sum(InboundJob.duplicates),0)).filter(
        InboundJob.organization_id==org_id,
        InboundJob.created_at >= clock-86400).scalar() or 0
    inbound_failed_by_channel = dict(db.query(InboundJob.channel_id,func.count(InboundJob.id)).filter(
        InboundJob.organization_id==org_id,InboundJob.status=='failed',
        InboundJob.encrypted_event.is_not(None)).group_by(InboundJob.channel_id).all())
    inbound_pending_by_channel = dict(db.query(InboundJob.channel_id,func.count(InboundJob.id)).filter(
        InboundJob.organization_id==org_id,
        InboundJob.status.in_(['queued','retrying','processing'])).group_by(InboundJob.channel_id).all())
    active_inbound_slots = int(db.query(func.count(ChannelConnection.id)).filter(
        ChannelConnection.organization_id==org_id,
        ChannelConnection.inbound_processing_token.is_not(None),
        ChannelConnection.inbound_processing_until>clock).scalar() or 0)
    stalled_inbound_claims = int(db.query(func.count(InboundJob.id)).filter(
        InboundJob.organization_id==org_id,
        InboundJob.status=='processing',
        InboundJob.claim_expires_at<=clock).scalar() or 0)
    inbound_oldest = db.query(func.min(InboundJob.created_at)).filter(
        InboundJob.organization_id==org_id,
        InboundJob.status.in_(['queued','retrying','processing'])).scalar()
    messages_total = db.query(func.count(Message.id)).filter_by(organization_id=org_id).scalar() or 0
    # Only aggregate authenticated tenant's WhatsApp callback journal.
    receipts_day = db.query(func.count(ProviderDeliveryReceipt.channel_id)).filter(
        ProviderDeliveryReceipt.organization_id==org_id,
        ProviderDeliveryReceipt.last_seen_at >= clock - 86400).scalar() or 0
    conversations_total = db.query(func.count(Conversation.id)).filter_by(organization_id=org_id).scalar() or 0
    # Worker health is shared platform infrastructure, but no worker IDs, hosts,
    # other tenant volumes or tokens are exposed to a company's dashboard.
    worker=worker_health(db,clock)
    oldest_queued=db.query(func.min(OutgoingJob.created_at)).filter(
        OutgoingJob.organization_id==org_id,OutgoingJob.status=='queued').scalar()
    oldest_wait=int(max(0,clock-oldest_queued)) if oldest_queued is not None else None
    # Only aggregate the caller's organization. No worker IDs or content.
    preflight=(db.query(func.count(OutgoingJob.id)).filter(
        OutgoingJob.organization_id==org_id,OutgoingJob.status=='processing',
        OutgoingJob.claim_token.is_not(None),OutgoingJob.send_started_at.is_(None)).scalar() or 0)
    provider_started=(db.query(func.count(OutgoingJob.id)).filter(
        OutgoingJob.organization_id==org_id,OutgoingJob.status=='processing',
        OutgoingJob.send_started_at.is_not(None)).scalar() or 0)
    recovered_7d=(db.query(func.count(AuditLog.id)).filter(
        AuditLog.organization_id==org_id,
        AuditLog.action=='outbox.recovered_before_send',
        AuditLog.created_at>=clock-7*86400).scalar() or 0)
    if not statuses.get('queued',0) and not statuses.get('processing',0) and not live_connected:
        worker={'code':'not_needed','summary':'Нет внешних отправок для обработки',
                'active':worker['active'],'last_cycle_seconds_ago':worker['last_cycle_seconds_ago']}
    # A bounded result prevents a very large tenant from overwhelming its browser.
    channel_rows = (db.query(ChannelConnection).filter_by(organization_id=org_id)
                    .order_by(ChannelConnection.created_at.desc(), ChannelConnection.id)
                    .limit(201).all())
    channels = channel_rows[:200]
    return {
        'as_of': clock, 'organization_id': org_id,
        'channel_total': channel_total, 'live_connected_count': live_connected,
        'outbound_paused_channels': int(paused_total),
        'active_sender_accounts': int(busy_senders),
        'inbound': {key:int(inbound_status.get(key,0)) for key in (
            'queued','retrying','processing','failed','done','expired','dismissed')},
        'inbound_duplicates_recorded_24h':int(inbound_duplicates_day),
        'inbound_active_accounts': active_inbound_slots,
        'inbound_stalled_claims': stalled_inbound_claims,
        'organization_inbound_paused_at': inbound_paused_at,
        'inbound_paused_channels': int(db.query(func.count(ChannelConnection.id)).filter(
            ChannelConnection.organization_id==org_id,
            ChannelConnection.inbound_paused_at.is_not(None)).scalar() or 0),
        'inbound_delayed_over_10_min': int(db.query(func.count(InboundJob.id)).filter(
            InboundJob.organization_id==org_id,
            InboundJob.status.in_(['queued','retrying','processing']),
            InboundJob.created_at<clock-600).scalar() or 0),
        'inbound_oldest_pending_seconds':(int(max(0,clock-inbound_oldest))
            if inbound_oldest is not None else None),
        'organization_outbound_paused_at': paused_at,
        'channels_truncated': len(channel_rows)>200,
        'outbox': {name:statuses.get(name,0) for name in ('queued','processing','uncertain','failed','done','cancelled')},
        'outbox_delayed_over_5_min': delayed,
        'oldest_queued_seconds': oldest_wait,
        'preflight_in_progress':int(preflight),
        'provider_requests_in_progress':int(provider_started),
        'safe_recoveries_last_7_days':int(recovered_7d),
        'worker':worker,
        'messages_total': messages_total, 'conversations_total': conversations_total,
        'whatsapp_receipts_last_24h': int(receipts_day),
        'channels': [
            {'id':c.id, 'provider':c.provider, 'name':c.name, 'mode':c.mode,
             'status':c.status, 'outbound_paused_at':c.outbound_paused_at,
             'inbound_paused_at':c.inbound_paused_at,
             'inbound_processing': bool(c.inbound_processing_token and
                                        (c.inbound_processing_until or 0)>clock),
             'inbound_failed':int(inbound_failed_by_channel.get(c.id,0)),
             'inbound_pending':int(inbound_pending_by_channel.get(c.id,0)),
             'last_sync_at':c.last_sync_at,
             'last_error':(c.last_error or '')[:180]}
            for c in channels],
        'reconciliation_required':statuses.get('uncertain',0),
        'live_external_channels_verified':False,
        'note':'A connected credential is not evidence of live end-to-end send and receive validation.'}


@router.get('/inbound')
def inbound_operations(status: str = '', p=Depends(auth), db: Session=Depends(get_db)):
    """Encrypted inbound journal metadata; never show customer IDs or payloads."""
    require_role(p,'owner','admin','lead')
    if status and status not in {'queued','retrying','processing','failed','done','expired'}:
        raise HTTPException(422,'Неизвестный статус входящего события')
    query=db.query(InboundJob).filter(InboundJob.organization_id==p.org.id)
    if status:
        query=query.filter(InboundJob.status==status)
    rows=query.order_by(
        case((InboundJob.status=='failed',0),
             (InboundJob.status=='retrying',1),
             (InboundJob.status=='queued',2),else_=3),
        InboundJob.created_at.desc(),InboundJob.id).limit(100).all()
    # No ciphertext, fingerprint, contact identifier, provider account ID,
    # message text, signature or token in the browser/API response.
    return [{'id':r.id,'channel_id':r.channel_id,'provider':r.provider,
             'status':r.status,'attempts':r.attempts,'duplicates':r.duplicates,
             'last_error':r.last_error,'created_at':r.created_at,
             'processed_at':r.processed_at,'can_retry':r.status=='failed' and bool(r.encrypted_event)}
            for r in rows]


class InboundRetryProof(BaseModel):
    reason: str = Field(min_length=8,max_length=300)


@router.post('/inbound/{job_id}/retry')
def retry_inbound(job_id: str, payload:InboundRetryProof,
                  p=Depends(auth),db: Session=Depends(get_db)):
    require_role(p,'owner','admin')
    job=db.query(InboundJob).filter_by(id=job_id,organization_id=p.org.id).first()
    if job is None:
        raise HTTPException(404,'Входящее событие не найдено')
    if job.status!='failed' or not job.encrypted_event or job.created_at < now()-14*86400:
        raise HTTPException(409,'Событие нельзя безопасно вернуть в очередь')
    # SQL compare-and-set prevents two admins from overwriting one another.
    updated=db.execute(update(InboundJob).where(
        InboundJob.id==job_id,InboundJob.organization_id==p.org.id,
        InboundJob.status=='failed',InboundJob.encrypted_event.is_not(None),
        InboundJob.created_at>=now()-14*86400
    ).values(status='queued',attempts=0,next_attempt_at=now(),
             last_error=None,claim_token=None,claimed_at=None,
             claim_expires_at=None)).rowcount
    if updated!=1:
        raise HTTPException(409,'Событие уже изменилось. Обновите список.')
    audit(db,p,'inbound.manual_retry',job_id,payload.reason.strip())
    db.commit()
    return {'id':job_id,'status':'queued','message':'Событие возвращено в очередь и ожидает обработку'}


# R32 incident management: pause PROCESSING, never receipt, preserving the
# durable provider acknowledgement rule. Existing in-flight work can finish.
class InboundPauseAction(BaseModel):
    scope: str = Field(pattern='^(organization|channel)$')
    channel_id: str | None = Field(default=None,max_length=36)
    reason: str = Field(min_length=8,max_length=160)


def _inbound_pause_target(db, org_id, payload):
    if payload.scope == 'organization':
        if payload.channel_id:
            raise HTTPException(422, 'Для всей компании не нужен идентификатор аккаунта')
        return Organization, Organization.id == org_id
    if not payload.channel_id:
        raise HTTPException(422, 'Выберите аккаунт')
    ch = db.query(ChannelConnection.id).filter_by(
        organization_id=org_id, id=payload.channel_id, mode='live').first()
    if ch is None:
        raise HTTPException(404, 'Аккаунт не найден')
    return ChannelConnection, and_(ChannelConnection.id == payload.channel_id,
                                   ChannelConnection.organization_id == org_id)


@router.post('/inbound/pause')
def pause_inbound(payload: InboundPauseAction, p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if not payload.reason.strip() or len(payload.reason.strip())<8:
        raise HTTPException(422,'Укажите причину остановки')
    table, condition = _inbound_pause_target(db,p.org.id,payload)
    changed = db.execute(update(table).where(
        condition, table.inbound_paused_at.is_(None)
    ).values(inbound_paused_at=now(), inbound_paused_by=p.user.id,
             inbound_pause_reason=payload.reason.strip())).rowcount
    if changed != 1:
        raise HTTPException(409,'Обработка уже остановлена. Обновите страницу.')
    audit(db,p,'inbound.pause.'+payload.scope,payload.channel_id or p.org.id,
          payload.reason.strip())
    db.commit()
    return {'paused':True,'scope':payload.scope,'channel_id':payload.channel_id}


@router.post('/inbound/resume')
def resume_inbound(payload: InboundPauseAction, p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if not payload.reason.strip() or len(payload.reason.strip())<8:
        raise HTTPException(422,'Укажите причину возобновления')
    table, condition = _inbound_pause_target(db,p.org.id,payload)
    changed = db.execute(update(table).where(
        condition, table.inbound_paused_at.is_not(None)
    ).values(inbound_paused_at=None,inbound_paused_by=None,
             inbound_pause_reason=None)).rowcount
    if changed != 1:
        raise HTTPException(409,'Обработка уже включена. Обновите страницу.')
    audit(db,p,'inbound.resume.'+payload.scope,payload.channel_id or p.org.id,
          payload.reason.strip())
    db.commit()
    return {'paused':False,'scope':payload.scope,'channel_id':payload.channel_id}


_INBOUND_STATES={'queued','retrying','processing','failed','done','expired','dismissed'}


def _decode_inbound_cursor(value):
    try:
        raw=base64.urlsafe_b64decode(value+'='*(-len(value)%4))
        stamp, identity=json.loads(raw)
        if len(raw)>200 or not isinstance(stamp,(int,float)) or not isinstance(identity,str) or len(identity)!=36:
            raise ValueError('Invalid cursor')
        if not 0 < float(stamp) < now()+60:
            raise ValueError('Cursor timestamp')
        return stamp,identity
    except (ValueError,TypeError,UnicodeError,OverflowError,base64.binascii.Error) as exc:
        raise HTTPException(422,'Некорректный курсор входящих событий') from exc


def _inbound_list_item(r):
    return {'id':r.id,'channel_id':r.channel_id,'provider':r.provider,
            'status':r.status,'attempts':r.attempts,'duplicates':r.duplicates,
            'last_error':r.last_error,'created_at':r.created_at,
            'processed_at':r.processed_at, 'dismissed_at':r.dismissed_at,
            'dismissal_code':r.dismissal_code,
            'can_dismiss':bool(r.status=='failed' and r.encrypted_event),
            'can_retry':bool(r.status=='failed' and r.encrypted_event and
                             r.created_at >= now()-14*86400)}


@router.get('/inbound/triage')
def inbound_triage(status: str = '', channel_id: str = '', provider: str = '',
                   before: str = '', limit: int = 30,
                   p=Depends(auth),db: Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    if status and status not in _INBOUND_STATES:
        raise HTTPException(422,'Неизвестный статус')
    if len(channel_id)>36 or len(provider)>32 or len(before)>280:
        raise HTTPException(422,'Неверный фильтр')
    limit=max(1,min(limit,100))
    query=db.query(InboundJob).filter(InboundJob.organization_id==p.org.id)
    if channel_id:
        query=query.filter(InboundJob.channel_id==channel_id)
    if provider:
        query=query.filter(InboundJob.provider==provider)
    if status:
        query=query.filter(InboundJob.status==status)
    if before:
        stamp,ident=_decode_inbound_cursor(before)
        query=query.filter(or_(InboundJob.created_at<stamp,
                               and_(InboundJob.created_at==stamp,InboundJob.id<ident)))
    rows=query.order_by(InboundJob.created_at.desc(),InboundJob.id.desc()).limit(limit+1).all()
    page=rows[:limit]
    cursor=None
    if len(rows)>limit and page:
        last=page[-1]
        cursor=base64.urlsafe_b64encode(json.dumps([last.created_at,last.id],separators=(',',':')).encode()).decode().rstrip('=')
    return {'items':[_inbound_list_item(x) for x in page], 'next_cursor':cursor}


class InboundBatchRetryProof(BaseModel):
    channel_id: str = Field(min_length=1,max_length=36)
    reason: str = Field(min_length=8,max_length=300)
    limit: int = Field(default=20,ge=1,le=25)


@router.post('/inbound/retry-batch')
def retry_inbound_batch(payload:InboundBatchRetryProof,
                        p=Depends(auth),db: Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if len(payload.reason.strip())<8:
        raise HTTPException(422,'Укажите причину восстановления')
    channel=db.query(ChannelConnection.id).filter_by(
        id=payload.channel_id,organization_id=p.org.id,mode='live').first()
    if not channel:
        raise HTTPException(404,'Аккаунт не найден')
    cutoff=now()-14*86400
    candidates=db.query(InboundJob.id).filter(
        InboundJob.organization_id==p.org.id,
        InboundJob.channel_id==payload.channel_id,
        InboundJob.status=='failed',
        InboundJob.encrypted_event.is_not(None),
        InboundJob.created_at>=cutoff
    ).order_by(InboundJob.created_at,InboundJob.id).limit(payload.limit).all()
    recovered=0
    for (identifier,) in candidates:
        updated=db.execute(update(InboundJob).where(
            InboundJob.id==identifier,InboundJob.organization_id==p.org.id,
            InboundJob.channel_id==payload.channel_id,
            InboundJob.status=='failed',InboundJob.encrypted_event.is_not(None),
            InboundJob.created_at>=cutoff
        ).values(status='queued',attempts=0,next_attempt_at=now(),
                 last_error=None,claim_token=None,claimed_at=None,
                 claim_expires_at=None)).rowcount
        recovered+=updated
    if recovered==0:
        raise HTTPException(409,'Подходящих событий для безопасного повтора нет')
    audit(db,p,'inbound.batch_retry',payload.channel_id,
          f'events={recovered}; '+payload.reason.strip())
    db.commit()
    return {'channel_id':payload.channel_id,'requeued':recovered,
            'message':'События возвращены в очередь; содержимое клиентов не раскрывается'}


# R33 / Block 2: a terminal, auditable operator decision (NO outbound request).
class InboundDismissProof(BaseModel):
    reason: str = Field(min_length=12,max_length=300)
    code: Literal['duplicate','invalid_event','unrecoverable','other']
    confirm_permanent_loss: bool


@router.post('/inbound/{job_id}/dismiss')
def dismiss_inbound(job_id:str, proof:InboundDismissProof,
                    p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if not proof.confirm_permanent_loss:
        raise HTTPException(422,'Подтвердите необратимое удаление события')
    if len(proof.reason.strip()) < 12:
        raise HTTPException(422,'Укажите причину закрытия события')
    stamp=now()
    # Atomic status guard: no incoming processing, retry or competing manager
    # can undo this decision. The ciphertext is erased in the same SQL UPDATE.
    changed=db.execute(update(InboundJob).where(
        InboundJob.id==job_id,InboundJob.organization_id==p.org.id,
        InboundJob.status=='failed',InboundJob.encrypted_event.is_not(None)
    ).values(status='dismissed',encrypted_event=None,dismissed_at=stamp,
             dismissed_by=p.user.id,dismissal_code=proof.code,
             next_attempt_at=stamp,claim_token=None,claim_expires_at=None,
             claimed_at=None)).rowcount
    if changed!=1:
        raise HTTPException(409,'Событие изменилось или не найдено. Обновите список.')
    audit(db,p,'inbound.dismiss',job_id,
          'code='+proof.code+'; '+proof.reason.strip())
    db.commit()
    return {'id':job_id,'status':'dismissed','payload_deleted':True,
            'message':'Событие закрыто с удалением шифротекста; восстановить его нельзя'}


# R33 / Block 3: tenant-scoped channel health without any message content.
@router.get('/inbound/health')
def inbound_channel_health(limit:int=50,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    limit=max(1,min(limit,100))
    clock=now()
    capacity=pending_limit()
    statuses=('queued','retrying','processing','failed')
    grouped=db.query(
        InboundJob.channel_id, InboundJob.status,
        func.count(InboundJob.id), func.min(InboundJob.created_at)
    ).filter(InboundJob.organization_id==p.org.id,
             InboundJob.status.in_(statuses),
             InboundJob.encrypted_event.is_not(None)
    ).group_by(InboundJob.channel_id,InboundJob.status).all()
    by_channel={}
    for cid,status,count,oldest in grouped:
        metrics=by_channel.setdefault(cid,{'queued':0,'retrying':0,'processing':0,'failed':0,'oldest':None})
        metrics[status]=int(count)
        metrics['oldest']=oldest if metrics['oldest'] is None else min(metrics['oldest'],oldest)
    stalled = dict(db.query(InboundJob.channel_id,func.count(InboundJob.id)).filter(
        InboundJob.organization_id==p.org.id,
        InboundJob.status=='processing',
        InboundJob.claim_expires_at<=clock
    ).group_by(InboundJob.channel_id).all())
    channels=db.query(ChannelConnection).filter_by(organization_id=p.org.id,mode='live').all()
    items=[]
    for channel in channels:
        metrics=by_channel.get(channel.id,{'queued':0,'retrying':0,'processing':0,'failed':0,'oldest':None})
        pending=sum(metrics[k] for k in statuses)
        wait=max(0,int(clock-metrics['oldest'])) if metrics['oldest'] is not None else None
        ratio=round(pending*100/capacity,1)
        busy=bool(channel.inbound_processing_token and
                  (channel.inbound_processing_until or 0)>clock)
        stuck=int(stalled.get(channel.id,0))
        severity=('critical' if ratio>=90 or stuck or metrics['failed']>0 or
                  (wait is not None and wait>=1800) else
                  'warning' if ratio>=60 or (wait is not None and wait>=600)
                  else 'healthy')
        items.append({'channel_id':channel.id,'channel_name':channel.name,
                      'provider':channel.provider, 'paused':channel.inbound_paused_at is not None,
                      'pending':pending,'queued':metrics['queued'],'retrying':metrics['retrying'],
                      'processing':metrics['processing'],'failed':metrics['failed'],
                      'actively_processing':busy,'stalled_claims':stuck,
                      'oldest_pending_seconds':wait,'capacity_limit':capacity,
                      'capacity_percent':ratio,'severity':severity})
    priority={'critical':0,'warning':1,'healthy':2}
    items.sort(key=lambda x:(priority[x['severity']],-x['failed'],
                              -x['pending'],x['channel_id']))
    return {'as_of':clock,'capacity_per_channel':capacity,
            'total_live_channels':len(items),'channels':items[:limit],
            'truncated':len(items)>limit,
            'critical_count':sum(x['severity']=='critical' for x in items),
            'warning_count':sum(x['severity']=='warning' for x in items)}


# R34 Block 3: two-phase, operator-reviewed bulk inbound recovery.
# A confirmation is bound to one authenticated session, tenant, channel and
# exact queue snapshot. No messages, provider IDs or ciphertext are returned.
class InboundBatchPreviewRequest(BaseModel):
    channel_id: str = Field(min_length=1,max_length=36)
    limit: int = Field(default=20,ge=1,le=25)


class InboundBatchConfirmRequest(BaseModel):
    proof: str = Field(min_length=40,max_length=4096)
    reason: str = Field(min_length=8,max_length=300)


def _eligible_failed_ids(db, org_id, channel_id, limit):
    return [j for (j,) in db.query(InboundJob.id).filter(
        InboundJob.organization_id==org_id,
        InboundJob.channel_id==channel_id,
        InboundJob.status=='failed',
        InboundJob.encrypted_event.is_not(None),
        InboundJob.created_at>=now()-14*86400
    ).order_by(InboundJob.created_at,InboundJob.id).limit(limit).all()]


def _batch_sign(p, data):
    # Session's server-stored CSRF digest is unknown to client-side JavaScript.
    # The signed proof is a time-limited snapshot, NOT a general access token.
    return hmac.new(p.session.csrf_hash.encode('ascii'),data,
                    hashlib.sha256).hexdigest()


@router.post('/inbound/retry-batch/preview')
def preview_inbound_batch(payload:InboundBatchPreviewRequest,
                          p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    channel=db.query(ChannelConnection.id).filter_by(
        id=payload.channel_id,organization_id=p.org.id,mode='live').first()
    if not channel:
        raise HTTPException(404,'Аккаунт не найден')
    ids=_eligible_failed_ids(db,p.org.id,payload.channel_id,payload.limit)
    issued=int(now())
    statement={'v':1,'org':p.org.id,'user':p.user.id,
               'channel':payload.channel_id,'limit':payload.limit,
               'ids':ids,'expires':issued+90}
    raw=json.dumps(statement,separators=(',',':'),sort_keys=True).encode()
    encoded=base64.urlsafe_b64encode(raw).decode().rstrip('=')
    proof=encoded+'.'+_batch_sign(p,raw)
    return {'count':len(ids),'channel_id':payload.channel_id,
            'expires_at':issued+90,'proof':proof,
            'notice':'Подтвердите проверку до повтора; план отменяется при изменении очереди.'}


@router.post('/inbound/retry-batch-confirm')
def confirm_inbound_batch(payload:InboundBatchConfirmRequest,
                          p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if len(payload.reason.strip())<8:
        raise HTTPException(422,'Укажите результат проверки и причину повтора')
    try:
        encoded,signature=payload.proof.split('.')
        raw=base64.urlsafe_b64decode(encoded+'='*(-len(encoded)%4))
        if len(raw)>2800 or len(signature)!=64 or not hmac.compare_digest(
                signature,_batch_sign(p,raw)):
            raise ValueError('Proof signature mismatch')
        statement=json.loads(raw)
        if (statement.get('v')!=1 or statement.get('org')!=p.org.id or
            statement.get('user')!=p.user.id or
            not isinstance(statement.get('expires'),int) or
            statement['expires']<now() or
            statement['expires']>now()+91 or
            not isinstance(statement.get('limit'),int) or
            not 1<=statement['limit']<=25 or
            not isinstance(statement.get('channel'),str) or
            not isinstance(statement.get('ids'),list) or
            any(not isinstance(j,str) or len(j)!=36 for j in statement['ids'])):
            raise ValueError('Proof scope or expiry mismatch')
    except (ValueError,TypeError,KeyError,UnicodeError,base64.binascii.Error) as exc:
        raise HTTPException(409,'Предпросмотр устарел или недействителен. Обновите его.') from exc
    channel_id=statement['channel']
    channel=db.query(ChannelConnection.id).filter_by(
        id=channel_id,organization_id=p.org.id,mode='live').first()
    if not channel:
        raise HTTPException(404,'Аккаунт не найден')
    selected=statement['ids']
    if not selected:
        raise HTTPException(409,'Нет событий для восстановления')
    # Same ordered snapshot: no broad INSERT, and no unexpected newly failed
    # events can ride on an old operator approval.
    if _eligible_failed_ids(db,p.org.id,channel_id,statement['limit'])!=selected:
        raise HTTPException(409,'Состояние очереди изменилось. Обновите предпросмотр.')
    cutoff=now()-14*86400
    for identifier in selected:
        updated=db.execute(update(InboundJob).where(
            InboundJob.id==identifier,InboundJob.organization_id==p.org.id,
            InboundJob.channel_id==channel_id,InboundJob.status=='failed',
            InboundJob.encrypted_event.is_not(None),
            InboundJob.created_at>=cutoff
        ).values(status='queued',attempts=0,next_attempt_at=now(),
                 last_error=None,claim_token=None,claimed_at=None,
                 claim_expires_at=None)).rowcount
        if updated!=1:
            db.rollback()
            raise HTTPException(409,'Параллельное изменение событий. Обновите предпросмотр.')
    audit(db,p,'inbound.reviewed_batch_retry',channel_id,
          f'events={len(selected)}; '+payload.reason.strip())
    db.commit()
    return {'channel_id':channel_id,'requeued':len(selected),
            'message':'Проверенные события возвращены в очередь без раскрытия данных клиентов'}


# R35: explicit, tenant-scoped integrity inspection and bounded repair.
# GET is read-only; POST requires a reason and intentionally does not recover
# live workers or any unknown/cross-tenant binding.
from .inbound_maintenance import integrity_report, repair_expired

class InboundRepairRequest(BaseModel):
    reason: str = Field(min_length=12, max_length=300)
    confirm_expired_only: bool


@router.get('/inbound/integrity')
def inbound_integrity(p=Depends(auth), db:Session=Depends(get_db)):
    require_role(p, 'owner', 'admin', 'lead')
    return integrity_report(db, p.org.id)


@router.post('/inbound/repair-expired')
def inbound_repair_expired(payload:InboundRepairRequest,
                           p=Depends(auth), db:Session=Depends(get_db)):
    require_role(p, 'owner', 'admin')
    if not payload.confirm_expired_only or len(payload.reason.strip())<12:
        raise HTTPException(422, 'Подтвердите проверку просроченных захватов и укажите причину')
    result=repair_expired(db,p.org.id,limit=50)
    audit(db,p,'inbound.repair_expired',p.org.id,
          'changes='+str(result['changes'])+'; '+payload.reason.strip())
    db.commit()
    return result
