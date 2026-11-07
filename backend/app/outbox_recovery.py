"""R23: delivery-safe crash recovery and per-attempt claim ownership.

Core invariant: marker send_started_at is committed BEFORE a user-message POST
can be attempted. A crashed preparation can be reclaimed; a possible POST
must be quarantined, never blindly retried.

Old R22 processing rows have no claim_token. They are deliberately treated as
potentially sent, even after migration. A live worker refreshes claimed_at
through an independent DB session while a provider request is in flight.
"""
from __future__ import annotations

import asyncio
import logging

from sqlalchemy import update, case, or_, select, exists
from .db import AuditLog, Message, OutgoingJob, ChannelConnection, Organization, ChannelDispatchLease, now

log=logging.getLogger('omnichat.outbox_recovery')
STALE_AFTER_SECONDS=120
CLAIM_HEARTBEAT_INTERVAL=15


def recover_stale_jobs(db, *, stamp: float | None = None, limit: int = 300) -> dict:
    """Bounded cross-tenant recovery using conditional SQL transitions."""
    stamp=now() if stamp is None else stamp
    if not 1 <= limit <= 300:
        raise ValueError('Recovery batch size must be 1..300')
    cutoff=stamp-STALE_AFTER_SECONDS
    rows=(db.query(OutgoingJob.id,OutgoingJob.organization_id,
                   OutgoingJob.message_id,OutgoingJob.claim_token,
                   OutgoingJob.send_started_at)
            .filter(OutgoingJob.status=='processing',
                    or_(OutgoingJob.claimed_at.is_(None),OutgoingJob.claimed_at<cutoff))
            .order_by(OutgoingJob.claimed_at.asc(),OutgoingJob.id.asc())
            .limit(limit).all())
    totals={'before_send':0,'possibly_sent':0}
    for job_id,org_id,message_id,claim_token,started in rows:
        base=(OutgoingJob.id==job_id,
              OutgoingJob.organization_id==org_id,
              OutgoingJob.status=='processing',
              or_(OutgoingJob.claimed_at.is_(None),OutgoingJob.claimed_at<cutoff))
        if claim_token and started is None:
            # The R23 attempt never reached mark_send_started(), thus the user
            # message POST could not have begun. Requeue only if the original
            # claim token is still current and marker still absent.
            changed=db.execute(update(OutgoingJob).where(
                *base, OutgoingJob.claim_token==claim_token,
                OutgoingJob.send_started_at.is_(None)
            ).values(status='queued',claimed_at=None,claim_token=None,
                     next_attempt_at=stamp+1,
                     attempts=case((OutgoingJob.attempts>0,OutgoingJob.attempts-1),else_=0),
                     last_error='Подготовка прервана до отправки. Безопасно возвращено в очередь.')).rowcount
            if changed:
                db.execute(update(Message).where(
                    Message.id==message_id,Message.organization_id==org_id,
                    Message.delivery_status.in_(['queued','processing'])
                ).values(delivery_status='queued'))
                db.add(AuditLog(organization_id=org_id,user_id=None,
                    action='outbox.recovered_before_send',entity_id=job_id,
                    detail='Автоматическое восстановление до начала HTTP-отправки'))
                totals['before_send']+=1
        else:
            # send_started_at is durable, or it is an untagged legacy R22 job.
            # Either way delivery outcome might be unknown: NEVER auto-resend.
            guarded=[*base]
            if claim_token:
                guarded.append(OutgoingJob.claim_token==claim_token)
            else:
                guarded.append(OutgoingJob.claim_token.is_(None))
            if started is None:
                guarded.append(OutgoingJob.send_started_at.is_(None))
            else:
                guarded.append(OutgoingJob.send_started_at==started)
            changed=db.execute(update(OutgoingJob).where(*guarded).values(
                status='uncertain',claimed_at=None,claim_token=None,
                last_error='Возможная отправка при остановке обработчика. Проверьте у площадки.')).rowcount
            if changed:
                db.execute(update(Message).where(
                    Message.id==message_id,Message.organization_id==org_id,
                    Message.delivery_status.in_(['queued','processing'])
                ).values(delivery_status='uncertain'))
                db.add(AuditLog(organization_id=org_id,user_id=None,
                    action='outbox.uncertain_after_interruption',entity_id=job_id,
                    detail='Сбой после начала отправки либо старое задание без метки'))
                totals['possibly_sent']+=1
    db.commit()
    return totals


def mark_send_started(db, job_id: str, claim_token: str, org_id: str, *,
                      dispatch_token: str | None = None) -> bool:
    """The LAST durable gate before calling an external send_message/template."""
    stamp=now()
    slot_guard = ([exists(select(ChannelDispatchLease.channel_id).where(
        ChannelDispatchLease.channel_id==OutgoingJob.channel_id,
        ChannelDispatchLease.organization_id==org_id,
        ChannelDispatchLease.owner_token==dispatch_token,
        ChannelDispatchLease.expires_at>stamp))] if dispatch_token else [])
    changed=db.execute(update(OutgoingJob).where(
        OutgoingJob.id==job_id,OutgoingJob.organization_id==org_id,
        OutgoingJob.status=='processing',OutgoingJob.claim_token==claim_token,
        OutgoingJob.send_started_at.is_(None),
        *slot_guard,
        # The last durable pre-HTTP gate must inspect the channel's *current*
        # pause state, not an ORM object cached before another process paused.
        exists(select(ChannelConnection.id).where(
            ChannelConnection.id==OutgoingJob.channel_id,
            ChannelConnection.organization_id==org_id,
            ChannelConnection.outbound_paused_at.is_(None))),
        # Check the current organization row in SQL, not a cached ORM object.
        exists(select(Organization.id).where(
            Organization.id==org_id,Organization.outbound_paused_at.is_(None)))
    ).values(send_started_at=stamp,claimed_at=stamp)).rowcount
    db.commit()
    return changed==1


def release_paused_preflight(db, job_id: str, claim_token: str, org_id: str) -> bool:
    """Give back a claimed-but-UNSENT job if its account is paused.

    This is a SQL compare-and-swap: a former worker cannot reset someone
    else's claim, an external POST checkpoint, or a resumed channel. No
    attempt is consumed, and no user message is marked sent.
    """
    paused=or_(
        exists(select(ChannelConnection.id).where(
            ChannelConnection.id==OutgoingJob.channel_id,
            ChannelConnection.organization_id==org_id,
            ChannelConnection.outbound_paused_at.is_not(None))),
        exists(select(Organization.id).where(
            Organization.id==org_id,Organization.outbound_paused_at.is_not(None))))
    changed=db.execute(update(OutgoingJob).where(
        OutgoingJob.id==job_id, OutgoingJob.organization_id==org_id,
        OutgoingJob.claim_token==claim_token, OutgoingJob.status=='processing',
        OutgoingJob.send_started_at.is_(None),paused
    ).values(status='queued', claimed_at=None, claim_token=None,
             attempts=case((OutgoingJob.attempts>0,OutgoingJob.attempts-1),else_=0),
             last_error=None, next_attempt_at=now()+1)).rowcount
    db.commit()
    return changed==1


def refresh_claim(db_factory, job_id: str, claim_token: str,
                  *, lease_channel_id: str | None = None) -> bool:
    with db_factory() as session:
        stamp=now()
        if lease_channel_id:
            # Renew the slot and the job *in one transaction*. A stale process
            # may not revive a claim after another sender obtained the slot.
            from .channel_dispatch import renew_in_session
            if not renew_in_session(session,lease_channel_id,claim_token,stamp=stamp):
                session.rollback()
                return False
        changed=session.execute(update(OutgoingJob).where(
            OutgoingJob.id==job_id,OutgoingJob.claim_token==claim_token,
            OutgoingJob.status=='processing'
        ).values(claimed_at=stamp)).rowcount
        if changed!=1:
            session.rollback()
            return False
        session.commit()
    return True


async def claim_heartbeat(db_factory, job_id: str, claim_token: str,
                          *, interval: float | None = None,
                          lease_channel_id: str | None = None):
    """Renew only this claim; a former worker cannot renew the replacement."""
    delay=CLAIM_HEARTBEAT_INTERVAL if interval is None else interval
    if delay <= 0:
        raise ValueError('Invalid heartbeat interval')
    while True:
        await asyncio.sleep(delay)
        try:
            if not refresh_claim(db_factory,job_id,claim_token,
                                 lease_channel_id=lease_channel_id):
                log.warning('Outgoing job ownership lost, heartbeat stopped')
                return
        except Exception:
            # A DB failure is NOT permission to send a duplicate. A timed-out
            # claim with a durable send marker is quarantined as uncertain.
            log.exception('Could not renew outgoing claim; retrying heartbeat')
