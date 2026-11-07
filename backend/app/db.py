"""SQLAlchemy persistence. SQLite for zero-setup local development; PostgreSQL in production."""
import os
import time
import uuid
from sqlalchemy import create_engine, Column, String, Float, ForeignKey, Integer, Boolean, Text, UniqueConstraint, Index, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def uid():
    return str(uuid.uuid4())

def now():
    return time.time()


def engine_for(url=None):
    url = url or os.getenv('DATABASE_URL', 'sqlite:///./omnichat.db')
    options = {'connect_args': {'check_same_thread': False}} if url.startswith('sqlite') else {'pool_pre_ping': True}
    return create_engine(url, **options)

class Base(DeclarativeBase):
    pass

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(String(36), primary_key=True, default=uid)
    name = Column(String(160), nullable=False)
    plan = Column(String(32), nullable=False, default='starter')
    is_demo = Column(Boolean, default=False, nullable=False)
    retention_days = Column(Integer, nullable=False, default=365)
    sla_minutes = Column(Integer, nullable=False, default=5)
    currency = Column(String(3), nullable=False, default='RUB')
    timezone = Column(String(64), nullable=False, default='UTC')
    # R26: tenant-wide emergency stop; inbound webhooks and direct website chat
    # are independent. A manual resume must never clear per-channel pauses.
    outbound_paused_at = Column(Float)
    outbound_paused_by = Column(String(36))
    outbound_pause_reason = Column(String(40))
    # R32: inbound processing can be suspended while authenticated webhook
    # arrivals keep entering the encrypted SQL journal.
    inbound_paused_at = Column(Float)
    inbound_paused_by = Column(String(36))
    inbound_pause_reason = Column(String(160))
    # R35: persistent checkpoint for fair processing across organizations.
    inbound_last_dispatched_at = Column(Float)
    created_at = Column(Float, default=now, nullable=False)

class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True, default=uid)
    email = Column(String(250), unique=True, nullable=False, index=True)
    password_hash = Column(String(300), nullable=False)
    name = Column(String(120), nullable=False)
    created_at = Column(Float, default=now, nullable=False)

class Membership(Base):
    __tablename__ = 'memberships'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    role = Column(String(24), nullable=False, default='operator')
    active = Column(Boolean, default=True, nullable=False)
    available = Column(Boolean, default=True, nullable=False)
    __table_args__ = (UniqueConstraint('organization_id', 'user_id'),)

class AuthSession(Base):
    __tablename__ = 'auth_sessions'
    id_hash = Column(String(64), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    csrf_hash = Column(String(64), nullable=False)
    expires_at = Column(Float, nullable=False)
    created_at = Column(Float, default=now)

class LoginFailure(Base):
    """Password-attempt receipt for shared-database login abuse protection.

    No plaintext email or password is stored. Attempts expire automatically.
    """
    __tablename__ = 'login_failures'
    id = Column(String(36), primary_key=True, default=uid)
    email_digest = Column(String(64), nullable=False)
    attempted_at = Column(Float, nullable=False, default=now)
    __table_args__ = (Index('ix_login_failure_identity_time', 'email_digest', 'attempted_at'),)

class PublicRateBucket(Base):
    """Shared fixed-window abuse guard for unauthenticated write endpoints.

    Digest protects client IPs in database snapshots; a short TTL in the
    maintenance worker bounds storage. No raw IP, cookie or account password.
    """
    __tablename__ = 'public_rate_buckets'
    scope = Column(String(60), primary_key=True)
    actor_digest = Column(String(64), primary_key=True)
    window_start = Column(Integer, primary_key=True)
    attempts = Column(Integer, nullable=False, default=0)
    created_at = Column(Float, nullable=False, default=now)
    __table_args__ = (Index('ix_public_rate_bucket_cleanup', 'created_at'),)

class OAuthState(Base):
    __tablename__ = 'oauth_states'
    state_hash = Column(String(64), primary_key=True)
    user_id = Column(String(36), nullable=False)
    organization_id = Column(String(36), nullable=False)
    provider = Column(String(24), nullable=False)
    expires_at = Column(Float, nullable=False)

class PendingChannelSelection(Base):
    """Encrypted, time-limited OAuth assets available for an explicit user selection."""
    __tablename__ = 'pending_channel_selections'
    id = Column(String(36), primary_key=True, default=uid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    provider = Column(String(32), nullable=False)
    encrypted_payload = Column(Text, nullable=False)
    expires_at = Column(Float, nullable=False)
    created_at = Column(Float, default=now, nullable=False)
    __table_args__ = (Index('ix_pending_channel_selection_owner','organization_id','user_id'),)

class ChannelConnection(Base):
    __tablename__ = 'channel_connections'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    provider = Column(String(32), nullable=False)
    name = Column(String(100), nullable=False)
    external_account_id = Column(String(150))
    mode = Column(String(20), nullable=False, default='live')
    status = Column(String(24), nullable=False, default='disconnected')
    encrypted_credentials = Column(Text)
    last_sync_at = Column(Float)
    last_verified_at = Column(Float)
    webhook_verified_at = Column(Float)
    webhook_registered_at = Column(Float)
    webhook_provider_verified_at = Column(Float)
    outbound_api_accepted_at = Column(Float)
    last_probe_at = Column(Float)
    rate_limited_until = Column(Float)
    # R25: emergency PAUSE applies only to new outbound HTTP sends. Inbound
    # webhooks and already-started external HTTP requests remain independent.
    outbound_paused_at = Column(Float)
    outbound_paused_by = Column(String(36))
    outbound_pause_reason = Column(String(40))
    inbound_paused_at = Column(Float)
    inbound_paused_by = Column(String(36))
    inbound_pause_reason = Column(String(160))
    # R33: database-wide fair inbound scheduling checkpoint (never customer data).
    inbound_last_dispatched_at = Column(Float)
    # R34: one inbound DB lease per external account, shared by all servers.
    # Never expose the owner token to clients or write it to application logs.
    inbound_processing_token = Column(String(36))
    inbound_processing_job_id = Column(String(36))
    inbound_processing_until = Column(Float)
    token_expires_at = Column(Float)
    last_error = Column(Text)
    created_at = Column(Float, default=now, nullable=False)
    __table_args__ = (
        Index('channel_provider_ext_idx', 'provider', 'external_account_id'),
        # Prevent routing one live external identity to two tenants, even under concurrent requests.
        # Demo accounts and disconnected historical connections are intentionally excluded.
        Index('uq_live_channel_identity', 'provider', 'external_account_id', unique=True,
            sqlite_where=text("mode = 'live' AND status != 'disconnected' AND external_account_id IS NOT NULL"),
            postgresql_where=text("mode = 'live' AND status != 'disconnected' AND external_account_id IS NOT NULL")),
    )

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    phone = Column(String(80))
    email = Column(String(250))
    tags = Column(Text, default='[]', nullable=False)
    stage = Column(String(40), default='new', nullable=False)
    deal_amount = Column(Float)
    deal_confirmed = Column(Boolean, default=False, nullable=False)
    next_followup_at = Column(Float)
    created_at = Column(Float, default=now)

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    channel_id = Column(String(36), ForeignKey('channel_connections.id'), nullable=False)
    contact_id = Column(String(36), ForeignKey('contacts.id'), nullable=False)
    external_chat_id = Column(String(250), nullable=False)
    external_recipient_id = Column(String(250))
    status = Column(String(30), nullable=False, default='new')
    priority = Column(String(12), nullable=False, default='normal')
    assigned_user_id = Column(String(36), ForeignKey('users.id'))
    pinned = Column(Boolean, default=False, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    unread_count = Column(Integer, default=0, nullable=False)
    reply_lock_owner_id = Column(String(36))
    reply_lock_expires_at = Column(Float)
    version = Column(Integer, default=0, nullable=False)
    last_message_at = Column(Float, default=now, nullable=False)
    last_inbound_at = Column(Float)
    first_reply_at = Column(Float)
    sla_warned_at = Column(Float)
    created_at = Column(Float, default=now, nullable=False)
    __table_args__ = (UniqueConstraint('channel_id', 'external_chat_id'),
        Index('ix_conversation_tenant_priority','organization_id','priority','last_message_at'),
        Index('ix_conversation_tenant_queue','organization_id','archived','status','last_message_at'))

class SavedInboxView(Base):
    __tablename__ = 'saved_inbox_views'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    creator_user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(64), nullable=False)
    filters_json = Column(Text, nullable=False, default='{}')
    shared = Column(Boolean, nullable=False, default=False)
    created_at = Column(Float, nullable=False, default=now)
    __table_args__ = (UniqueConstraint('organization_id','creator_user_id','name'),)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey('conversations.id'), nullable=False, index=True)
    external_id = Column(String(250))
    client_nonce = Column(String(100))
    direction = Column(String(12), nullable=False)
    kind = Column(String(32), default='text', nullable=False)
    body = Column(Text, nullable=False, default='')
    attachment = Column(Text)
    delivery_status = Column(String(24), nullable=False, default='delivered')
    # R28: first verified provider API acceptance / visitor widget rendering.
    # Null for queued/failed/uncertain and legacy sends without a reliable receipt.
    response_confirmed_at = Column(Float)
    author_user_id = Column(String(36))
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(Float, default=now, nullable=False)
    __table_args__ = (UniqueConstraint('conversation_id', 'external_id'), UniqueConstraint('conversation_id', 'client_nonce'),
        Index('ix_message_tenant_conversation_direction_date','organization_id','conversation_id','direction','created_at'),
        Index('ix_message_history_cursor','organization_id','conversation_id','created_at','id'))

class Note(Base):
    __tablename__ = 'notes'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey('conversations.id'), nullable=False, index=True)
    author_user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(Float, default=now)

class AutomationRule(Base):
    __tablename__ = 'automation_rules'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    event = Column(String(40), nullable=False)
    condition_type = Column(String(40), nullable=False)
    condition_value = Column(String(200), default='')
    action_type = Column(String(40), nullable=False)
    action_value = Column(String(200), default='')
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(Float, default=now)

class QuickReply(Base):
    __tablename__ = 'quick_replies'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    title = Column(String(90), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(Float, default=now)

class SchedulerLease(Base):
    __tablename__='scheduler_leases'
    name=Column(String(60),primary_key=True)
    owner_id=Column(String(36),nullable=False)
    acquired_at=Column(Float,nullable=False)
    renewed_at=Column(Float,nullable=False)
    expires_at=Column(Float,nullable=False)
    __table_args__=(Index('ix_scheduler_leases_expiry','expires_at'),)

class ChannelDispatchLease(Base):
    """Cross-worker serialization for one external sender account (R27).

    Expiry is a crash fallback; owner_token fences obsolete workers. An
    expired record can be acquired, never removed by a former owner.
    """
    __tablename__='channel_dispatch_leases'
    channel_id=Column(String(36),ForeignKey('channel_connections.id'),primary_key=True)
    organization_id=Column(String(36),nullable=False,index=True)
    owner_token=Column(String(36),nullable=False)
    acquired_at=Column(Float,nullable=False)
    renewed_at=Column(Float,nullable=False)
    expires_at=Column(Float,nullable=False)
    __table_args__=(Index('ix_channel_dispatch_expiry','expires_at'),)


class WhatsAppConsent(Base):
    __tablename__ = 'whatsapp_consents'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    contact_id = Column(String(36), ForeignKey('contacts.id'), nullable=False)
    channel_id = Column(String(36), ForeignKey('channel_connections.id'), nullable=False)
    recipient_id = Column(String(250), nullable=False)
    source = Column(String(240), nullable=False, default='')
    captured_at = Column(Float, nullable=False, default=now)
    revoked_at = Column(Float)
    recorded_by = Column(String(36), ForeignKey('users.id'))
    __table_args__ = (UniqueConstraint('channel_id','recipient_id',name='uq_whatsapp_consent_channel_recipient'),)

class ContactIdentity(Base):
    __tablename__ = 'contact_identities'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    contact_id = Column(String(36), ForeignKey('contacts.id'), nullable=False, index=True)
    channel_id = Column(String(36), ForeignKey('channel_connections.id'), nullable=False)
    external_user_id = Column(String(250), nullable=False)
    __table_args__ = (UniqueConstraint('channel_id', 'external_user_id'),)

class ProviderDeliveryReceipt(Base):
    """Bounded WhatsApp callback journal for receipts arriving before API ack.

    No customer message body, contact name or raw recipient address is stored.
    The message is matched later by exact channel + provider message ID.
    """
    __tablename__ = 'provider_delivery_receipts'
    channel_id = Column(String(36), ForeignKey('channel_connections.id'), primary_key=True)
    external_message_id = Column(String(250), primary_key=True)
    organization_id = Column(String(36), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    recipient_digest = Column(String(64))
    first_seen_at = Column(Float, nullable=False)
    last_seen_at = Column(Float, nullable=False)
    __table_args__ = (Index('ix_provider_receipts_cleanup','last_seen_at'),)

class InboundJob(Base):
    """R31 durable, encrypted inbound queue scoped to one tenant and channel.

    The encrypted minimal event is erased immediately after successful ingestion.
    A bounded retention job erases failed and abandoned payloads as well.
    """
    __tablename__ = 'inbound_jobs'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    channel_id = Column(String(36), ForeignKey('channel_connections.id'), nullable=False, index=True)
    provider = Column(String(32), nullable=False)
    fingerprint = Column(String(64), nullable=False)
    encrypted_event = Column(Text)
    status = Column(String(24), nullable=False, default='queued')
    attempts = Column(Integer, nullable=False, default=0)
    duplicates = Column(Integer, nullable=False, default=0)
    next_attempt_at = Column(Float, nullable=False, default=now)
    claimed_at = Column(Float)
    claim_token = Column(String(36))
    claim_expires_at = Column(Float)
    last_error = Column(String(90))
    created_at = Column(Float, nullable=False, default=now)
    processed_at = Column(Float)
    # R33 terminal disposition: encrypted source is erased when an operator
    # confirms the incident is resolved without importing the message.
    dismissed_at = Column(Float)
    dismissed_by = Column(String(36))
    dismissal_code = Column(String(32))
    __table_args__ = (
        UniqueConstraint('channel_id', 'fingerprint', name='uq_inbound_channel_fingerprint'),
        Index('ix_inbound_jobs_poll', 'status', 'next_attempt_at'),
        Index('ix_inbound_jobs_tenant_status', 'organization_id', 'status', 'created_at'),
        Index('ix_inbound_jobs_claim_expiry', 'status', 'claim_expires_at'),
        Index('ix_inbound_jobs_ready_channel', 'channel_id', 'status', 'next_attempt_at', 'created_at'),
    )


class WebhookEvent(Base):
    __tablename__ = 'webhook_events'
    id = Column(String(36), primary_key=True, default=uid)
    provider = Column(String(32), nullable=False)
    fingerprint = Column(String(64), nullable=False)
    created_at = Column(Float, default=now)
    __table_args__ = (UniqueConstraint('provider', 'fingerprint'),)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36))
    action = Column(String(90), nullable=False)
    entity_id = Column(String(36))
    detail = Column(Text)
    created_at = Column(Float, default=now)

class Invite(Base):
    __tablename__ = 'invites'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), nullable=False)
    email = Column(String(250), nullable=False)
    role = Column(String(24), nullable=False)
    token_hash = Column(String(64), nullable=False, unique=True)
    expires_at = Column(Float, nullable=False)
    accepted_at = Column(Float)

class BillingEvent(Base):
    __tablename__ = 'billing_events'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), nullable=False)
    type = Column(String(30), nullable=False)
    detail = Column(Text, nullable=False, default='{}')
    created_at = Column(Float, default=now)


_engine = None
SessionLocal = None

def assert_schema_current(engine):
    """Refuse to boot against an unmigrated/stale production database."""
    from pathlib import Path
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    from sqlalchemy import inspect
    config=Config(str(Path(__file__).resolve().parents[1]/'alembic.ini'))
    config.set_main_option('script_location',str(Path(__file__).resolve().parents[1]/'alembic'))
    script=ScriptDirectory.from_config(config)
    expected=set(script.get_heads())
    if not inspect(engine).has_table('alembic_version'):
        raise RuntimeError('Database migrations missing: run alembic upgrade head first')
    with engine.connect() as conn:
        current={r[0] for r in conn.execute(text('SELECT version_num FROM alembic_version'))}
    if not current or current != expected:
        raise RuntimeError('Database schema revision mismatch: run alembic upgrade head first')
    return True


def initialize(url=None):
    global _engine, SessionLocal
    new_engine = engine_for(url)
    try:
        if os.getenv('APP_ENV')=='production':
            # Production startup must never invent tables around a missing
            # migration; migrations are applied by a separate deployment step.
            assert_schema_current(new_engine)
        else:
            Base.metadata.create_all(bind=new_engine)
    except Exception:
        new_engine.dispose()
        raise
    _engine = new_engine
    SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
    return _engine

def get_db():
    if SessionLocal is None:
        initialize()
    with SessionLocal() as db:
        yield db

class OutgoingJob(Base):
    __tablename__ = 'outgoing_jobs'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), nullable=False, index=True)
    message_id = Column(String(36), ForeignKey('messages.id'), nullable=False, unique=True)
    channel_id = Column(String(36), ForeignKey('channel_connections.id'), nullable=False)
    status = Column(String(25), nullable=False, default='queued')
    attempts = Column(Integer, default=0, nullable=False)
    next_attempt_at = Column(Float, default=now, nullable=False)
    claimed_at = Column(Float)
    claim_token = Column(String(36))
    send_started_at = Column(Float)
    last_error = Column(Text)
    created_at = Column(Float, default=now, nullable=False)
    __table_args__ = (Index('ix_outgoing_due','status','next_attempt_at','organization_id','created_at'),
                      Index('ix_outgoing_processing','status','claimed_at'),
                      Index('ix_outgoing_account_status','channel_id','status'))

class WorkerHeartbeat(Base):
    # A non-secret worker liveness record. Multiple API/worker processes share it.
    __tablename__ = 'worker_heartbeats'
    worker_id = Column(String(64), primary_key=True)
    kind = Column(String(16), nullable=False)  # api or worker
    started_at = Column(Float, nullable=False)
    last_seen_at = Column(Float, nullable=False)
    last_cycle_at = Column(Float)
    stopped_at = Column(Float)
    error_count = Column(Integer, nullable=False, default=0)
    processed_jobs = Column(Integer, nullable=False, default=0)
    __table_args__ = (Index('ix_worker_heartbeats_status','stopped_at','last_seen_at'),)

class WebsiteWidget(Base):
    __tablename__ = 'website_widgets'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    channel_id = Column(String(36), ForeignKey('channel_connections.id'), nullable=False, unique=True)
    public_key = Column(String(64), nullable=False, unique=True, index=True)
    allowed_origins = Column(Text, nullable=False, default='[]')
    greeting = Column(String(240), nullable=False, default='Здравствуйте! Чем можем вам помочь?')
    accent = Column(String(7), nullable=False, default='#6489F5')
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(Float, default=now, nullable=False)

class WebsiteVisitor(Base):
    __tablename__ = 'website_visitors'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False, index=True)
    widget_id = Column(String(36), ForeignKey('website_widgets.id'), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True)
    conversation_id = Column(String(36), ForeignKey('conversations.id'))
    nickname = Column(String(80), nullable=False)
    expires_at = Column(Float, nullable=False)
    last_activity_at = Column(Float, nullable=False)
    created_at = Column(Float, default=now, nullable=False)


class DispatchPause(Base):
    """Tenant/channel dispatch gate: '*' means all external channels for tenant."""
    __tablename__ = 'dispatch_pauses'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), nullable=False)
    channel_id = Column(String(36), nullable=False)  # '*' or tenant-owned channel ID
    reason_code = Column(String(40), nullable=False)
    expires_at = Column(Float)
    created_at = Column(Float, default=now, nullable=False)
    actor_user_id = Column(String(36), nullable=False)
    __table_args__ = (
        UniqueConstraint('organization_id','channel_id',name='uq_dispatch_pause_scope'),
        Index('ix_dispatch_pause_org_expiry','organization_id','expires_at'),
    )



class DeliveryTransition(Base):
    """Immutable delivery state receipt without message bodies or credentials."""
    __tablename__ = 'delivery_transitions'
    id = Column(String(36), primary_key=True, default=uid)
    organization_id = Column(String(36), nullable=False)
    job_id = Column(String(36), nullable=False)
    status_from = Column(String(25), nullable=False)
    status_to = Column(String(25), nullable=False)
    event_code = Column(String(40), nullable=False)
    attempts = Column(Integer, nullable=False)
    created_at = Column(Float, default=now, nullable=False)
    __table_args__ = (
        Index('ix_delivery_transition_org_time','organization_id','created_at'),
        Index('ix_delivery_transition_job_time','organization_id','job_id','created_at'),
    )


