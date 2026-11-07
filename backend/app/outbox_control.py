"""R22: tenant-scoped, race-safe human controls for queued outbound messages.

Cancellation is a database compare-and-swap against 'queued': if another worker
has claimed a POST, this operation MUST return 409 rather than promise that a
potentially sent message was canceled. Retry is restricted to an explicit HTTP
4xx rejection, never a timeout, a 5xx uncertainty, or manually reconciled jobs.
"""
from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import update
from sqlalchemy.orm import Session

from .auth import audit, auth, can_view, require_role
from .db import ChannelConnection, Conversation, Message, OutgoingJob, get_db, now
from .dispatch_control import record_transition

router = APIRouter(prefix='/api/operations/outbox', tags=['operations'])

# 408/409 have ambiguous semantics for POST; 429 is a definitive rejection,
# handled by automatic backoff rather than an immediate operator retry.
DEFINITE_REJECTION = re.compile(r'^API (400|401|402|403|404|405|410|412|413|415|422):')


class RetryProof(BaseModel):
    verified_not_delivered: bool
    evidence: str = Field(min_length=12, max_length=500)

    @field_validator('evidence')
    @classmethod
    def meaningful_evidence(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 12:
            raise ValueError('Опишите проверку доставки минимум в 12 символах')
        return cleaned


def _find_job(db: Session, organization_id: str, job_id: str):
    job = db.query(OutgoingJob).filter_by(
        id=job_id, organization_id=organization_id
    ).first()
    if not job:
        raise HTTPException(404, 'Исходящая отправка не найдена')
    message = db.query(Message).filter_by(
        id=job.message_id, organization_id=organization_id
    ).first()
    if not message:
        raise HTTPException(409, 'Связанное сообщение недоступно')
    conv = db.query(Conversation).filter_by(
        id=message.conversation_id, organization_id=organization_id
    ).first()
    channel = db.query(ChannelConnection).filter_by(
        id=job.channel_id, organization_id=organization_id
    ).first()
    if not conv or not channel or conv.channel_id != job.channel_id or message.direction != 'out':
        raise HTTPException(409, 'Связи сообщения и канала изменились — проверьте данные')
    return job, message, conv, channel


def _has_provider_ack(message) -> bool:
    # Outgoing messages initially use a synthetic client-<nonce> identity to
    # dedupe browser retries. It is NOT a provider acknowledgment.
    local_identity = 'client-' + message.client_nonce if message.client_nonce else None
    return bool(message.external_id and message.external_id != local_identity)


def retry_allowed(job, message, conv, channel) -> bool:
    """Fail closed: unknown delivery is not a verified provider refusal."""
    return bool(
        job.status == 'failed'
        and message.delivery_status == 'failed'
        and not _has_provider_ack(message)
        and DEFINITE_REJECTION.match(job.last_error or '')
        and channel.mode == 'live'
        and channel.status == 'connected'
        and channel.id == conv.channel_id
        and message.organization_id == job.organization_id == channel.organization_id == conv.organization_id
    )


@router.post('/{job_id}/cancel')
def cancel_queued(job_id: str, p=Depends(auth), db: Session = Depends(get_db)):
    """Cancel only while the worker has NOT claimed the message."""
    require_role(p, 'owner', 'admin', 'lead')
    job, message, conv, channel = _find_job(db, p.org.id, job_id)
    if job.status != 'queued' or message.delivery_status != 'queued':
        raise HTTPException(409, 'Отправка уже началась или её статус изменился. Обновите данные.')
    changed = db.execute(update(OutgoingJob).where(
        OutgoingJob.id == job.id,
        OutgoingJob.organization_id == p.org.id,
        OutgoingJob.status == 'queued',
    ).values(status='cancelled', claimed_at=None, claim_token=None, last_error=None)).rowcount
    if changed != 1:
        db.rollback()
        raise HTTPException(409, 'Отправка уже захвачена обработчиком. Проверьте результат.')
    updated = db.execute(update(Message).where(
        Message.id == message.id,
        Message.organization_id == p.org.id,
        Message.delivery_status == 'queued',
    ).values(delivery_status='cancelled')).rowcount
    if updated != 1:
        db.rollback()
        raise HTTPException(409, 'Сообщение изменилось — отмена не выполнена')
    job.status='cancelled'
    record_transition(db, job, 'queued', 'operator_cancelled')
    audit(db, p, 'outbox.cancel_before_send', job.id,
          'Отменено до захвата обработчиком; сетевой запрос не выполнялся')
    db.commit()
    return {'id': job.id, 'status': 'cancelled', 'delivery_status': 'cancelled',
            'guarantee': 'Отменено до начала обработки'}


@router.post('/{job_id}/retry-verified')
def retry_after_explicit_refusal(job_id: str, payload: RetryProof,
                                 p=Depends(auth), db: Session = Depends(get_db)):
    """Manual retry only after a *definitive* provider 4xx refusal.

    An operator cannot force retry of ambiguous POSTs, API-accepted responses,
    or a manual 'not found' reconciliation of a previously uncertain send.
    """
    require_role(p, 'owner', 'admin')
    if not payload.verified_not_delivered:
        raise HTTPException(422, 'Подтвердите проверку отсутствия доставки в исходной площадке')
    job, message, conv, channel = _find_job(db, p.org.id, job_id)
    if not retry_allowed(job, message, conv, channel):
        raise HTTPException(409, 'Повтор возможен только после однозначного отказа API 4xx')
    changed = db.execute(update(OutgoingJob).where(
        OutgoingJob.id == job.id,
        OutgoingJob.organization_id == p.org.id,
        OutgoingJob.status == 'failed',
        OutgoingJob.last_error == job.last_error,
    ).values(status='queued', attempts=0, claimed_at=None, claim_token=None,
             send_started_at=None, next_attempt_at=now(), last_error=None)).rowcount
    if changed != 1:
        db.rollback()
        raise HTTPException(409, 'Задание изменилось. Проверьте состояние очереди.')
    updated = db.execute(update(Message).where(
        Message.id == message.id,
        Message.organization_id == p.org.id,
        Message.delivery_status == 'failed',
        # Never retry a message that already has a real provider ack. The
        # local client-<nonce> marker is merely an idempotency placeholder.
        Message.external_id == message.external_id,
    ).values(delivery_status='queued')).rowcount
    if updated != 1:
        db.rollback()
        raise HTTPException(409, 'Состояние сообщения изменилось. Повтор не выполнен.')
    job.status='queued'
    job.attempts=0
    record_transition(db, job, 'failed', 'operator_verified_retry')
    audit(db, p, 'outbox.retry_after_verified_refusal', job.id,
          'Явный отказ площадки. Подтверждено отсутствие доставки: '+payload.evidence.strip())
    db.commit()
    return {'id': job.id, 'status': 'queued', 'delivery_status': 'queued',
            'note': 'Новая попытка поставлена в очередь; доставка не гарантирована'}
