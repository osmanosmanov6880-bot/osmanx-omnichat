"""R26 owner-controlled tenant-wide outbound incident containment.

Exactly one organization is affected per atomic SQL statement. Inbound webhooks,
website-widget messages and outgoing sends already past their durable checkpoint
are not claimed to have been canceled.
"""
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import update
from sqlalchemy.orm import Session
from .db import get_db, Organization, now
from .auth import auth, require_role, audit

router = APIRouter(prefix='/api/operations', tags=['operations'])


class PauseAllOutgoing(BaseModel):
    reason: Literal['security_review','provider_incident','configuration_review','operator_request']
    acknowledge_inflight: Literal[True]


class ResumeAllOutgoing(BaseModel):
    expected_paused_at: float = Field(gt=0)
    acknowledge_inflight: Literal[True]


@router.post('/outbound/pause')
def pause_all_outgoing(payload: PauseAllOutgoing,
                       p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if p.org.is_demo:
        raise HTTPException(403,'Аварийная остановка предназначена для рабочих каналов')
    stamp=now()
    updated=db.execute(update(Organization).where(
        Organization.id==p.org.id,Organization.is_demo.is_(False),
        Organization.outbound_paused_at.is_(None))
        .values(outbound_paused_at=stamp,outbound_paused_by=p.user.id,
                outbound_pause_reason=payload.reason)).rowcount
    if updated!=1:
        db.rollback()
        raise HTTPException(409,'Исходящие всей компании уже приостановлены. Обновите состояние.')
    audit(db,p,'organization.outbound_paused',p.org.id,payload.reason)
    db.commit()
    return {'outbound_paused':True,'outbound_paused_at':stamp,
            'message':'Новые исходящие всех рабочих каналов остановлены. Входящие работают. Уже начатые отправки могут завершиться.'}


@router.post('/outbound/resume')
def resume_all_outgoing(payload: ResumeAllOutgoing,
                        p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if p.org.is_demo:
        raise HTTPException(403,'Аварийная остановка предназначена для рабочих каналов')
    updated=db.execute(update(Organization).where(
        Organization.id==p.org.id,Organization.is_demo.is_(False),
        Organization.outbound_paused_at==payload.expected_paused_at)
        .values(outbound_paused_at=None,outbound_paused_by=None,
                outbound_pause_reason=None)).rowcount
    if updated!=1:
        db.rollback()
        raise HTTPException(409,'Состояние компании изменилось. Обновите страницу перед возобновлением.')
    audit(db,p,'organization.outbound_resumed',p.org.id,'manual_review_completed')
    db.commit()
    return {'outbound_paused':False,'outbound_paused_at':None,
            'message':'Глобальная пауза снята. Индивидуальные остановки каналов и лимиты площадок остаются в силе.'}
