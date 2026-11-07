"""R36 on R35: tenant-scoped outbound safety controls and privacy-safe delivery telemetry.

Dispatch pause gates protect *new* outbound claims. Already in-flight provider
requests cannot be recalled; no endpoint claims otherwise.
"""
from __future__ import annotations

import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Response, Query
from pydantic import BaseModel, Field
from sqlalchemy import delete, exists, func, or_, select
from sqlalchemy.orm import Session

from .auth import auth, audit, require_role
from .db import (ChannelConnection, DeliveryTransition, DispatchPause, OutgoingJob,
                 get_db, now, uid)
from .worker_monitor import worker_health

router = APIRouter(prefix='/api/operations', tags=['dispatch-safety'])
ALL_CHANNELS = '*'
REASON_CODES = {'maintenance', 'provider_outage', 'credential_rotation', 'incident'}


class PauseRequest(BaseModel):
    channel_id: str | None = Field(default=None, max_length=36)
    reason_code: str = Field(pattern='^(maintenance|provider_outage|credential_rotation|incident)$')
    minutes: int | None = Field(default=None, ge=5, le=1440)


class ResumeRequest(BaseModel):
    channel_id: str | None = Field(default=None, max_length=36)


def allowed_to_claim(org_column, channel_column, timestamp: float):
    """One SQL NOT EXISTS guard used in selection AND conditional claim.

    The clause is explicitly correlated to the owning OutgoingJob; PostgreSQL
    and SQLite therefore evaluate it for each candidate job independently.
    """
    active = exists(select(DispatchPause.id).where(
        DispatchPause.organization_id == org_column,
        DispatchPause.channel_id.in_([ALL_CHANNELS, channel_column]),
        or_(DispatchPause.expires_at.is_(None), DispatchPause.expires_at > timestamp)
    ).correlate(OutgoingJob))
    return ~active


def is_paused(db: Session, org_id: str, channel_id: str, timestamp: float | None = None):
    stamp = now() if timestamp is None else timestamp
    return db.query(DispatchPause.id).filter(
        DispatchPause.organization_id == org_id,
        DispatchPause.channel_id.in_([ALL_CHANNELS, channel_id]),
        or_(DispatchPause.expires_at.is_(None), DispatchPause.expires_at > stamp)
    ).first() is not None


def record_transition(db: Session, job: OutgoingJob, old: str, event: str):
    """Append-only transition record. No message bodies, tokens or provider errors."""
    db.add(DeliveryTransition(
        organization_id=job.organization_id, job_id=job.id,
        status_from=old, status_to=job.status, event_code=event,
        attempts=job.attempts
    ))


def validate_channel(db: Session, org_id: str, channel_id: str | None):
    if channel_id is None:
        return ALL_CHANNELS
    if not db.query(ChannelConnection.id).filter_by(id=channel_id, organization_id=org_id).first():
        raise HTTPException(404, 'Канал не найден в этой компании')
    return channel_id


def active_pauses(db: Session, org_id: str):
    stamp = now()
    return db.query(DispatchPause).filter(
        DispatchPause.organization_id == org_id,
        or_(DispatchPause.expires_at.is_(None), DispatchPause.expires_at > stamp)
    ).order_by(DispatchPause.created_at.desc()).limit(201).all()


def pause_response(db, org_id):
    rows = active_pauses(db, org_id)
    return {'pauses': [
        {'channel_id':None if v.channel_id == ALL_CHANNELS else v.channel_id,
         'reason_code':v.reason_code, 'expires_at':v.expires_at,
         'created_at':v.created_at}
        for v in rows[:200]], 'truncated': len(rows)>200,
        'note':'Пауза запрещает новые захваты; уже начатый запрос к провайдеру может завершиться.'}


@router.get('/dispatch-pauses')
def list_dispatch_pauses(p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p, 'owner', 'admin', 'lead')
    return pause_response(db, p.org.id)


@router.post('/dispatch-pauses')
def pause_dispatch(payload: PauseRequest, p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p, 'owner', 'admin')
    target=validate_channel(db, p.org.id, payload.channel_id)
    expiry=now()+payload.minutes*60 if payload.minutes is not None else None
    data={'reason_code':payload.reason_code, 'expires_at':expiry, 'created_at':now(),
          'actor_user_id':p.user.id}
    values={'id':uid(), 'organization_id':p.org.id, 'channel_id':target, **data}
    # A single database upsert also handles simultaneous pause requests safely.
    dialect=db.get_bind().dialect.name
    if dialect=='sqlite':
        from sqlalchemy.dialects.sqlite import insert
    elif dialect=='postgresql':
        from sqlalchemy.dialects.postgresql import insert
    else:
        raise HTTPException(503,'Этот тип базы не поддерживает атомарные паузы')
    statement=insert(DispatchPause).values(**values)
    db.execute(statement.on_conflict_do_update(
        index_elements=['organization_id','channel_id'],set_=data))
    audit(db,p,'dispatch.paused',None, f'channel={target};reason={payload.reason_code};minutes={payload.minutes}')
    db.commit()
    return pause_response(db,p.org.id)


@router.post('/dispatch-pauses/resume')
def resume_dispatch(payload: ResumeRequest, p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p, 'owner', 'admin')
    target=validate_channel(db,p.org.id,payload.channel_id)
    result=db.execute(delete(DispatchPause).where(
        DispatchPause.organization_id==p.org.id,DispatchPause.channel_id==target))
    audit(db,p,'dispatch.resumed',None, f'channel={target};was_paused={bool(result.rowcount)}')
    db.commit()
    return pause_response(db,p.org.id)


@router.get('/delivery-events')
def delivery_events(job_id: str = Query(default='', max_length=36), p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    if not job_id or len(job_id)>36:
        raise HTTPException(422,'Укажите идентификатор задания')
    if not db.query(OutgoingJob.id).filter_by(id=job_id,organization_id=p.org.id).first():
        raise HTTPException(404,'Задание не найдено')
    rows=db.query(DeliveryTransition).filter_by(
        organization_id=p.org.id, job_id=job_id
    ).order_by(DeliveryTransition.created_at.desc(),DeliveryTransition.id.desc()).limit(101).all()
    return {'events': [dict(event_code=v.event_code, from_status=v.status_from,
           to_status=v.status_to, attempts=v.attempts, at=v.created_at)
           for v in rows[:100]], 'truncated':len(rows)>100}


def telemetry_summary(db: Session, org_id: str, moment: float | None = None):
    clock=now() if moment is None else moment
    hour=clock-3600
    day=clock-86400
    statuses=dict(db.query(OutgoingJob.status,func.count(OutgoingJob.id)).filter(
        OutgoingJob.organization_id==org_id).group_by(OutgoingJob.status).all())
    events=dict(db.query(DeliveryTransition.event_code,func.count(DeliveryTransition.id)).filter(
        DeliveryTransition.organization_id==org_id,
        DeliveryTransition.created_at>=day
    ).group_by(DeliveryTransition.event_code).all())
    hourly=dict(db.query(DeliveryTransition.event_code,func.count(DeliveryTransition.id)).filter(
        DeliveryTransition.organization_id==org_id,
        DeliveryTransition.created_at>=hour
    ).group_by(DeliveryTransition.event_code).all())
    delayed=db.query(func.count(OutgoingJob.id)).filter(
        OutgoingJob.organization_id==org_id,OutgoingJob.status=='queued',
        OutgoingJob.created_at<clock-300).scalar() or 0
    worker=worker_health(db,clock)
    uncertain=int(statuses.get('uncertain',0))
    queued=int(statuses.get('queued',0))
    recent_failed=int(hourly.get('hard_fail',0)+hourly.get('blocked_integrity',0))
    alerts=[]
    if uncertain:alerts.append({'code':'uncertain','severity':'attention','count':uncertain})
    if queued and worker['code']=='offline':alerts.append({'code':'worker_offline','severity':'attention','count':queued})
    if delayed:alerts.append({'code':'queue_delayed','severity':'attention','count':int(delayed)})
    if recent_failed >= 3:alerts.append({'code':'recent_failures','severity':'attention','count':recent_failed})
    active=active_pauses(db,org_id)
    if active:alerts.append({'code':'delivery_paused','severity':'info','count':len(active)})
    return {
        'generated_at':clock, 'window_seconds':86400,
        'outbox':{key:int(statuses.get(key,0)) for key in ('queued','processing','uncertain','failed','done')},
        'events_24h':{key:int(value) for key,value in sorted(events.items())},
        'events_1h':{key:int(value) for key,value in sorted(hourly.items())},
        'delayed_queued_over_5m':int(delayed),
        'worker':{key:worker[key] for key in ('code','online') if key in worker},'alerts':alerts,
        'note':'События учитываются только после включения R36; принятый API запрос не означает доставку клиенту.'}


@router.get('/delivery-telemetry')
def delivery_telemetry(p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    return telemetry_summary(db,p.org.id)


@router.get('/support-bundle')
def support_bundle(response:Response,p=Depends(auth),db:Session=Depends(get_db)):
    """Privacy-first self-contained incident summary: no personal identifiers or content."""
    require_role(p,'owner','admin')
    response.headers['Cache-Control']='no-store, private'
    response.headers['X-Content-Type-Options']='nosniff'
    summary=telemetry_summary(db,p.org.id)
    body={
        'schema':'osmanx-omnichat-r36-support-v1',
        'generated_at':summary['generated_at'],
        'scope':'authenticated-tenant-aggregates',
        'telemetry':summary,
        'pauses':[
            {'scope':'all' if x.channel_id==ALL_CHANNELS else 'one-channel',
             'reason_code':x.reason_code,'expires_at':x.expires_at}
            for x in active_pauses(db,p.org.id)[:200]],
        'excludes':['messages','contacts','credentials','webhook-payloads',
                    'user-identifiers','channel-identifiers','provider-errors'],
    }
    canonical=json.dumps(body,sort_keys=True,ensure_ascii=False,separators=(',',':'))
    body['sha256']=hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    return body
