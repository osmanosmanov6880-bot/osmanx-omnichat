"""R35 tenant-scoped, bounded inbound integrity report and guarded repair.

Only expired claims or ciphertext-free jobs can change. Nothing is decrypted,
resent to a provider, or silently deleted by this module. No foreign tenant
identifier or customer payload is exposed in the report.
"""
from sqlalchemy import and_, exists, func, or_, select, update
from .db import ChannelConnection, InboundJob, now
from .inbound_jobs import MAX_ATTEMPTS


def _matching_channel():
    return exists(select(ChannelConnection.id).where(
        ChannelConnection.id == InboundJob.channel_id,
        ChannelConnection.organization_id == InboundJob.organization_id
    ).correlate(InboundJob))


def _active_job_for_slot(clock):
    return exists(select(InboundJob.id).where(
        InboundJob.id == ChannelConnection.inbound_processing_job_id,
        InboundJob.organization_id == ChannelConnection.organization_id,
        InboundJob.channel_id == ChannelConnection.id,
        InboundJob.claim_token == ChannelConnection.inbound_processing_token,
        InboundJob.status == 'processing',
        InboundJob.claim_expires_at > clock
    ).correlate(ChannelConnection))


def _expired_slots(clock):
    return and_(
        ChannelConnection.inbound_processing_token.is_not(None),
        ChannelConnection.inbound_processing_until.is_not(None),
        ChannelConnection.inbound_processing_until <= clock,
        ~_active_job_for_slot(clock)
    )


def integrity_report(db, organization_id, *, stamp=None):
    clock = now() if stamp is None else stamp
    scoped_jobs = InboundJob.organization_id == organization_id
    stale_jobs = db.query(func.count(InboundJob.id)).join(
        ChannelConnection,
        and_(ChannelConnection.id == InboundJob.channel_id,
             ChannelConnection.organization_id == InboundJob.organization_id)
    ).filter(
        scoped_jobs,
        InboundJob.status == 'processing',
        InboundJob.claim_expires_at.is_not(None),
        InboundJob.claim_expires_at <= clock,
        or_(ChannelConnection.inbound_processing_until.is_(None),
            ChannelConnection.inbound_processing_until <= clock)
    ).scalar() or 0
    stale_slots = db.query(func.count(ChannelConnection.id)).filter(
        ChannelConnection.organization_id == organization_id,
        _expired_slots(clock)
    ).scalar() or 0
    missing_payload = db.query(func.count(InboundJob.id)).filter(
        scoped_jobs,
        InboundJob.status.in_(('queued', 'retrying', 'failed')),
        InboundJob.encrypted_event.is_(None)
    ).scalar() or 0
    bad_binding = db.query(func.count(InboundJob.id)).filter(
        scoped_jobs, ~_matching_channel()
    ).scalar() or 0
    return {'as_of':clock, 'expired_claims':int(stale_jobs),
            'expired_channel_slots':int(stale_slots),
            'missing_payload':int(missing_payload),
            'invalid_channel_bindings':int(bad_binding),
            'can_auto_repair':int(stale_jobs + stale_slots + missing_payload),
            'manual_review_required':int(bad_binding),
            'notice':'Отчёт содержит только счётчики; сообщения и идентификаторы клиентов не раскрываются.'}


def repair_expired(db, organization_id, *, stamp=None, limit=50):
    """CAS-only repair, bounded per category; caller audits and commits.

    Safe with concurrent consumers: a live channel lease is never released;
    an expired job can be moved only after its claim elapsed and only when its
    associated channel lease has also expired. Old workers lose their CAS.
    """
    clock = now() if stamp is None else stamp
    batch = max(1, min(int(limit), 100))
    eligible_jobs = [item[0] for item in db.query(InboundJob.id).join(
        ChannelConnection,
        and_(ChannelConnection.id == InboundJob.channel_id,
             ChannelConnection.organization_id == InboundJob.organization_id)
    ).filter(
        InboundJob.organization_id == organization_id,
        InboundJob.status == 'processing',
        InboundJob.claim_expires_at.is_not(None),
        InboundJob.claim_expires_at <= clock,
        or_(ChannelConnection.inbound_processing_until.is_(None),
            ChannelConnection.inbound_processing_until <= clock)
    ).order_by(InboundJob.claim_expires_at,InboundJob.id).limit(batch).all()]
    moved_retry = 0
    moved_review = 0
    for job_id in eligible_jobs:
        predicate = (
            InboundJob.id == job_id,
            InboundJob.organization_id == organization_id,
            InboundJob.status == 'processing',
            InboundJob.claim_expires_at.is_not(None),
            InboundJob.claim_expires_at <= clock
        )
        # A job that used up its attempt budget goes to human review; one that
        # still has attempts can safely be retried by the idempotent importer.
        moved_retry += db.execute(update(InboundJob).where(
            *predicate, InboundJob.attempts < MAX_ATTEMPTS,
            InboundJob.encrypted_event.is_not(None),
            exists(select(ChannelConnection.id).where(
                ChannelConnection.id == InboundJob.channel_id,
                ChannelConnection.organization_id == organization_id,
                or_(ChannelConnection.inbound_processing_until.is_(None),
                    ChannelConnection.inbound_processing_until <= clock)
            ))
        ).values(status='retrying',next_attempt_at=clock,
                 claim_token=None,claimed_at=None,claim_expires_at=None,
                 last_error='recovered_expired_claim')).rowcount
        moved_review += db.execute(update(InboundJob).where(
            *predicate, InboundJob.attempts >= MAX_ATTEMPTS,
            InboundJob.encrypted_event.is_not(None),
            exists(select(ChannelConnection.id).where(
                ChannelConnection.id == InboundJob.channel_id,
                ChannelConnection.organization_id == organization_id,
                or_(ChannelConnection.inbound_processing_until.is_(None),
                    ChannelConnection.inbound_processing_until <= clock)
            ))
        ).values(status='failed',claim_token=None,claimed_at=None,
                 claim_expires_at=None,last_error='worker_claim_expired')).rowcount
    stale_slots = [x.id for x in db.query(ChannelConnection.id).filter(
        ChannelConnection.organization_id == organization_id,
        _expired_slots(clock)
    ).order_by(ChannelConnection.id).limit(batch).all()]
    cleaned_slots = 0
    for channel_id in stale_slots:
        cleaned_slots += db.execute(update(ChannelConnection).where(
            ChannelConnection.id == channel_id,
            ChannelConnection.organization_id == organization_id,
            _expired_slots(clock)
        ).values(inbound_processing_token=None,
                 inbound_processing_job_id=None,
                 inbound_processing_until=None)).rowcount
    empty_ids = [x.id for x in db.query(InboundJob.id).filter(
        InboundJob.organization_id == organization_id,
        InboundJob.status.in_(('queued','retrying','failed')),
        InboundJob.encrypted_event.is_(None)
    ).order_by(InboundJob.created_at,InboundJob.id).limit(batch).all()]
    empty_fixed = 0
    for job_id in empty_ids:
        empty_fixed += db.execute(update(InboundJob).where(
            InboundJob.id == job_id, InboundJob.organization_id == organization_id,
            InboundJob.status.in_(('queued','retrying','failed')),
            InboundJob.encrypted_event.is_(None)
        ).values(status='expired',last_error='payload_missing',
                 claim_token=None,claimed_at=None,claim_expires_at=None)).rowcount
    return {'retrying':int(moved_retry),'requires_review':int(moved_review),
            'expired_slots_released':int(cleaned_slots),
            'missing_payload_quarantined':int(empty_fixed),
            'changes':int(moved_retry+moved_review+cleaned_slots+empty_fixed),
            'limit_per_category':batch,
            'notice':'Активные захваты не затрагиваются; события клиентов не удаляются.'}
