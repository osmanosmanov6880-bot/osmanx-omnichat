"""R31 durable inbound ingress: authenticated event -> encrypted SQL inbox -> idempotent ingest.

Persistence commits before provider HTTP acknowledgement. DB claims fence competing
workers and expired claims are safe to retry because the message and event IDs are
unique in the same transaction as the final successful claim resolution.
"""
import hashlib
import json
import logging
import os
from sqlalchemy import update, or_, func, select, exists
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from .db import InboundJob, ChannelConnection, Organization, Conversation, Message, now, uid
from .integrations.adapters import seal, unseal
from .integrations.base import AdapterError
from .services import ingest_inbound

log = logging.getLogger('omnichat.inbound')
MAX_ATTEMPTS = 5
CLAIM_TTL = 120
CHANNEL_TTL = 120
VALID_RETRY = ('queued', 'retrying')
ACTIVE_PAYLOAD_STATUSES = ('queued', 'retrying', 'processing', 'failed')

class InboundCapacityExceeded(Exception):
    """Ingress is intentionally unacknowledged: the provider should retry."""

class InboundProcessingPaused(Exception):
    """An active claim was paused before it could be ingested."""

class InboundPayloadUnreadable(Exception):
    """Encrypted content cannot be opened with the configured key ring."""

class InboundPayloadInvalid(Exception):
    """Decrypted event does not satisfy the versioned ingress contract."""


def pending_limit():
    try:
        return max(1, min(50000, int(os.getenv('INBOUND_MAX_PENDING_PER_CHANNEL', '5000'))))
    except (TypeError, ValueError):
        return 5000


def _active_org(db):
    return exists(select(Organization.id).where(
        Organization.id == InboundJob.organization_id,
        Organization.inbound_paused_at.is_(None)))


def _active_channel(db):
    return exists(select(ChannelConnection.id).where(
        ChannelConnection.id == InboundJob.channel_id,
        ChannelConnection.organization_id == InboundJob.organization_id,
        ChannelConnection.inbound_paused_at.is_(None)))



def _insert(db):
    dialect = db.get_bind().dialect.name
    if dialect == 'sqlite':
        return sqlite_insert(InboundJob)
    if dialect == 'postgresql':
        return pg_insert(InboundJob)
    raise RuntimeError('Only SQLite and PostgreSQL support durable inbound claims')


def stage(db, *, channel, external_chat_id, external_message_id, sender_id,
          sender_name=None, text='', timestamp=None, kind='text', attachment=None,
          history=False):
    """Stage only AFTER provider auth + shape validation. Caller commits before ack.

    No provider token, signature, raw webhook or plaintext client message is
    stored in the queue. Even chat/member identifiers are only in ciphertext.
    """
    chat_id = str(external_chat_id or '')
    message_id = str(external_message_id or '')
    user_id = str(sender_id or '')
    if not chat_id or not message_id or not user_id:
        return None
    if max(len(chat_id), len(message_id), len(user_id)) > 250:
        raise ValueError('Provider identity exceeds maximum length')
    if channel.mode != 'live':
        raise ValueError('Durable inbox is for authenticated live channels only')
    normalized = {
        'external_chat_id': chat_id, 'external_message_id': message_id,
        'sender_id': user_id, 'sender_name': str(sender_name or '')[:160],
        'text': str(text or '[Медиа]')[:4000],
        'timestamp': timestamp, 'kind': str(kind or 'text')[:32],
        'attachment': attachment if isinstance(attachment, dict) else None,
        'history': bool(history),
    }
    encoded = json.dumps(normalized, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    if len(encoded.encode('utf8')) > 25000:
        raise ValueError('Provider event payload exceeds safe bounds')
    key = hashlib.sha256(json.dumps([channel.provider, chat_id, message_id],
                                  ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    stamp = now()
    # PostgreSQL's channel-row lock serializes capacity admissions across
    # independent webhook/API servers; SQLite serializes subsequent writes.
    # Duplicate callbacks remain accepted even when the queue is full.
    if db.get_bind().dialect.name == 'postgresql':
        db.query(ChannelConnection.id).filter(
            ChannelConnection.id == channel.id,
            ChannelConnection.organization_id == channel.organization_id
        ).with_for_update().one()
    existing = db.query(InboundJob.id).filter_by(
        channel_id=channel.id, fingerprint=key).scalar()
    if existing is None:
        backlog = db.query(func.count(InboundJob.id)).filter(
            InboundJob.channel_id == channel.id,
            InboundJob.status.in_(ACTIVE_PAYLOAD_STATUSES),
            InboundJob.encrypted_event.is_not(None)).scalar() or 0
        if backlog >= pending_limit():
            raise InboundCapacityExceeded('Encrypted inbound queue at capacity')
    created_id = uid()
    inserted = db.execute(_insert(db).values(
        id=created_id, organization_id=channel.organization_id,
        channel_id=channel.id, provider=channel.provider, fingerprint=key,
        encrypted_event=seal(normalized), status='queued', attempts=0,
        duplicates=0, next_attempt_at=stamp, created_at=stamp
    ).on_conflict_do_nothing(index_elements=['channel_id', 'fingerprint'])).rowcount
    if inserted:
        return created_id
    # Keep a bounded duplicate counter, without re-encrypting or rewriting the
    # original, already processed customer message. SQL increment is atomic.
    db.execute(update(InboundJob).where(
        InboundJob.channel_id == channel.id,
        InboundJob.fingerprint == key
    ).values(duplicates=func.min(InboundJob.duplicates + 1, 2147483647)
             if db.get_bind().dialect.name == 'sqlite'
             else func.least(InboundJob.duplicates + 1, 2147483647)))
    return db.query(InboundJob.id).filter_by(channel_id=channel.id, fingerprint=key).scalar()


def _release_channel(db, job_id, token):
    """Release only our own channel lease, never a newer worker's claim."""
    return db.execute(update(ChannelConnection).where(
        ChannelConnection.inbound_processing_token == token,
        ChannelConnection.inbound_processing_job_id == job_id
    ).values(inbound_processing_token=None,
             inbound_processing_job_id=None,inbound_processing_until=None)).rowcount


def _claim(db_factory, job_id, *, stamp=None):
    stamp = now() if stamp is None else stamp
    token = uid()
    with db_factory() as db:
        # Stage 1: acquire an account-wide slot. Row-level UPDATE implements a
        # real cross-process CAS on PostgreSQL, and a serialized write on SQLite.
        # Claim and lease are committed atomically: a lost job CAS rolls BOTH back.
        entry=db.query(InboundJob.channel_id,InboundJob.organization_id).filter(
            InboundJob.id==job_id).first()
        if entry is None:
            return None
        changed_slot=db.execute(update(ChannelConnection).where(
            ChannelConnection.id==entry.channel_id,
            ChannelConnection.organization_id==entry.organization_id,
            or_(ChannelConnection.inbound_processing_until.is_(None),
                ChannelConnection.inbound_processing_until<=stamp)
        ).values(inbound_processing_token=token,inbound_processing_job_id=job_id,
                 inbound_processing_until=stamp+CHANNEL_TTL)).rowcount
        if changed_slot!=1:
            return None
        changed=db.execute(update(InboundJob).where(
            InboundJob.id==job_id,InboundJob.channel_id==entry.channel_id,
            InboundJob.organization_id==entry.organization_id,
            or_(
                (InboundJob.status.in_(VALID_RETRY)) & (InboundJob.next_attempt_at<=stamp),
                (InboundJob.status=='processing') & (InboundJob.claim_expires_at<=stamp)),
            InboundJob.attempts<MAX_ATTEMPTS,
            InboundJob.encrypted_event.is_not(None),
            _active_org(db),_active_channel(db)
        ).values(status='processing',attempts=InboundJob.attempts+1,
                 claim_token=token,claimed_at=stamp,
                 claim_expires_at=stamp+CLAIM_TTL)).rowcount
        if changed!=1:
            db.rollback()  # An unavailable job cannot monopolize this channel.
            return None
        db.execute(update(ChannelConnection).where(
            ChannelConnection.id==entry.channel_id,
            ChannelConnection.inbound_processing_token==token
        ).values(inbound_last_dispatched_at=stamp))
        # Tenant-level checkpoint commits together with the job/channel CAS.
        # A failed claim cannot advance either fairness cursor.
        db.execute(update(Organization).where(
            Organization.id==entry.organization_id
        ).values(inbound_last_dispatched_at=stamp))
        db.commit()
    return token


def process_one(db_factory, job_id, *, stamp=None):
    """Return 1 only for newly ingested message, 0 for duplicates or failures.

    A failure is contained to this job; other tenants are not blocked.
    Errors returned to operators use fixed codes, NEVER provider payloads.
    """
    token = _claim(db_factory, job_id, stamp=stamp)
    if not token:
        return 0
    try:
        with db_factory() as db:
            job = db.query(InboundJob).filter_by(id=job_id, claim_token=token,
                                                  status='processing').first()
            if job is None:
                return 0
            channel = db.query(ChannelConnection).filter_by(
                id=job.channel_id, organization_id=job.organization_id,
                provider=job.provider, mode='live').first()
            if channel is None or channel.status not in ('connected', 'pending_webhook'):
                raise RuntimeError('channel_unavailable')
            # Lock the tenant row on PostgreSQL. A pause request waits for any
            # currently ingesting message; after it commits, new work cannot start.
            organization = db.query(Organization).filter_by(
                id=job.organization_id).with_for_update().first()
            if organization is None or organization.inbound_paused_at is not None:
                raise InboundProcessingPaused()
            if channel.inbound_paused_at is not None:
                raise InboundProcessingPaused()
            try:
                event = unseal(job.encrypted_event)
            except AdapterError as exc:
                # Wrong/missing rotation keys must not burn five retries in a
                # loop. Keep ciphertext for an authorized recovery after repair.
                raise InboundPayloadUnreadable() from exc
            if not isinstance(event,dict) or not all(
                isinstance(event.get(k),str) and event[k] for k in
                ('external_chat_id','external_message_id','sender_id')):
                raise InboundPayloadInvalid()
            from .webhooks import reserve_event
            # Previous releases already reserved some of these fingerprints in
            # webhook_events. Message uniqueness remains authoritative.
            legacy_key = hashlib.sha256(
                f'r31:{job.channel_id}:{job.fingerprint}'.encode()).hexdigest()
            first = reserve_event(db, job.provider, legacy_key)
            msg = None
            preexisting = db.query(Message.id).join(Conversation,
                Message.conversation_id==Conversation.id).filter(
                Conversation.organization_id==job.organization_id,
                Conversation.channel_id==job.channel_id,
                Conversation.external_chat_id==event['external_chat_id'],
                Message.external_id==event['external_message_id']).first() is not None
            if first and not preexisting:
                msg = ingest_inbound(
                    db, channel=channel, external_chat_id=event['external_chat_id'],
                    external_message_id=event['external_message_id'],
                    sender_id=event['sender_id'], sender_name=event.get('sender_name'),
                    text=event.get('text') or '[Медиа]',
                    timestamp=event.get('timestamp'), kind=event.get('kind', 'text'),
                    attachment=event.get('attachment'), history=event.get('history', False))
            committed = db.execute(update(InboundJob).where(
                InboundJob.id == job_id, InboundJob.claim_token == token,
                InboundJob.status == 'processing', InboundJob.claim_expires_at > now()
            ).values(status='done', encrypted_event=None, processed_at=now(),
                     claim_token=None, claim_expires_at=None, claimed_at=None,
                     last_error=None)).rowcount
            if committed != 1:
                raise RuntimeError('lost_claim')
            # The channel CAS is in the SAME transaction as message ingestion
            # and completion. An expired/replaced owner cannot commit a late
            # message or overwrite a newer worker's decision.
            lease_valid=db.execute(update(ChannelConnection).where(
                ChannelConnection.id==job.channel_id,
                ChannelConnection.organization_id==job.organization_id,
                ChannelConnection.inbound_processing_token==token,
                ChannelConnection.inbound_processing_job_id==job_id,
                ChannelConnection.inbound_processing_until>now()
            ).values(inbound_processing_token=None,
                     inbound_processing_job_id=None,
                     inbound_processing_until=None)).rowcount
            if lease_valid != 1:
                raise RuntimeError('lost_channel_lease')
            if msg is not None:
                channel.status = 'connected'
                channel.webhook_verified_at = now()
                channel.last_sync_at = now()
                channel.last_error = None
            db.commit()
            return int(msg is not None)
    except InboundProcessingPaused:
        # No provider request and no message write happened: restore the
        # reserved attempt without burning the retry budget during a pause.
        with db_factory() as db:
            db.execute(update(InboundJob).where(
                InboundJob.id == job_id, InboundJob.claim_token == token,
                InboundJob.status == 'processing'
            ).values(status='queued', attempts=InboundJob.attempts-1,
                     next_attempt_at=now(), claimed_at=None, claim_token=None,
                     claim_expires_at=None))
            _release_channel(db,job_id,token)
            db.commit()
        return 0
    except Exception as exc:
        # Roll back ingest + idempotency reservation if something failed.
        # Keep the encrypted event for an automatic retry or manual recovery.
        error_code = ('encryption_key_unavailable' if isinstance(exc,InboundPayloadUnreadable)
                      else 'invalid_encrypted_event' if isinstance(exc,InboundPayloadInvalid)
                      else type(exc).__name__[:70])
        log.warning('Inbound ingest deferred: job=%s code=%s', job_id, error_code)
        with db_factory() as db:
            attempt = db.query(InboundJob.attempts).filter_by(
                id=job_id, claim_token=token, status='processing').scalar()
            if attempt is not None:
                target = 'failed' if (attempt >= MAX_ATTEMPTS or
                    isinstance(exc,(InboundPayloadUnreadable,InboundPayloadInvalid))) else 'retrying'
                wait = min(300, 5 * (2 ** max(0, attempt-1)))
                db.execute(update(InboundJob).where(
                    InboundJob.id == job_id, InboundJob.claim_token == token,
                    InboundJob.status == 'processing'
                ).values(status=target, next_attempt_at=now()+wait,
                         claimed_at=None, claim_token=None, claim_expires_at=None,
                         last_error=error_code))
                _release_channel(db,job_id,token)
                db.commit()
        return 0


def process_batch(db_factory, *, limit=40, only_ids=None):
    """Bounded worker pass. Atomic claims permit multiple independent servers."""
    size = max(0, min(int(limit), 100))
    if not size:
        return 0
    with db_factory() as db:
        clock = now()
        # An interrupted fifth attempt otherwise remains 'processing' forever.
        # Quarantine it instead of re-dispatching beyond the retry limit.
        db.execute(update(InboundJob).where(
            InboundJob.status=='processing',
            InboundJob.claim_expires_at<=clock,
            InboundJob.attempts>=MAX_ATTEMPTS
        ).values(status='failed',claim_token=None,claim_expires_at=None,
                 claimed_at=None,last_error='worker_claim_expired'))
        db.commit()
        # R33: SQL window ranking gives each active channel one opportunity
        # before assigning a second, third, ... slot to a busy channel.
        # A persisted last-dispatched checkpoint makes even limit=1 fair across
        # repeated worker passes. IDs are re-validated by _claim's atomic CAS.
        queue = db.query(
            InboundJob.id.label('job_id'),
            InboundJob.channel_id.label('channel_id'),
            func.row_number().over(
                partition_by=InboundJob.channel_id,
                order_by=(InboundJob.created_at, InboundJob.id)).label('position')
        ).filter(
            or_((InboundJob.status.in_(VALID_RETRY)) & (InboundJob.next_attempt_at <= clock),
                (InboundJob.status == 'processing') & (InboundJob.claim_expires_at <= clock)),
            InboundJob.attempts < MAX_ATTEMPTS,
            InboundJob.encrypted_event.is_not(None),
            _active_org(db), _active_channel(db))
        if only_ids is not None:
            identifiers = list(dict.fromkeys(only_ids))[:100]
            if not identifiers:
                return 0
            queue = queue.filter(InboundJob.id.in_(identifiers))
        ranked = queue.subquery()
        # First rank waiting jobs WITHIN one organization, rotating channels.
        # Then offer organizations a turn before taking their second job.  A
        # persisted organization checkpoint prevents starvation with limit=1
        # over repeated worker runs even if another tenant owns many channels.
        per_org = db.query(
            ranked.c.job_id.label('job_id'),
            ranked.c.channel_id.label('channel_id'),
            ChannelConnection.organization_id.label('org_id'),
            func.row_number().over(
                partition_by=ChannelConnection.organization_id,
                order_by=(ranked.c.position,
                          func.coalesce(ChannelConnection.inbound_last_dispatched_at, 0.0),
                          ranked.c.channel_id, ranked.c.job_id)
            ).label('org_position')
        ).join(ChannelConnection, ChannelConnection.id == ranked.c.channel_id).subquery()
        candidates = [j for (j,) in db.query(per_org.c.job_id).join(
            Organization, Organization.id == per_org.c.org_id
        ).order_by(
            per_org.c.org_position,
            func.coalesce(Organization.inbound_last_dispatched_at, 0.0),
            per_org.c.org_id, per_org.c.channel_id, per_org.c.job_id
        ).limit(size).all()]
    return sum(process_one(db_factory, item) for item in candidates)


def expire_payloads(db, *, stamp=None, limit=500):
    """Erase expired PII and old completed metadata in bounded batches."""
    clock = now() if stamp is None else stamp
    batch = max(1, min(int(limit), 2000))
    expired = [x.id for x in db.query(InboundJob.id).filter(
        InboundJob.status.in_(('queued', 'retrying', 'processing', 'failed')),
        InboundJob.created_at < clock - 14*86400
    ).order_by(InboundJob.created_at).limit(batch).all()]
    if expired:
        db.query(InboundJob).filter(InboundJob.id.in_(expired)).update(
            {'encrypted_event': None, 'status': 'expired', 'claim_token': None,
             'claim_expires_at': None, 'last_error': 'retention_expired'},
            synchronize_session=False)
    # Job fingerprints carry only digests. Old successful/expired metadata may
    # be deleted; SQL message uniqueness still protects recent webhook replay.
    old = [x.id for x in db.query(InboundJob.id).filter(
        InboundJob.status.in_(('done', 'expired', 'dismissed')),
        InboundJob.created_at < clock - 30*86400
    ).order_by(InboundJob.created_at).limit(batch).all()]
    if old:
        db.query(InboundJob).filter(InboundJob.id.in_(old)).delete(synchronize_session=False)
    return {'payloads_erased': len(expired), 'metadata_deleted': len(old)}
