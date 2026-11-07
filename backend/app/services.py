"""Message normalization, deterministic rules, analytics and durable outgoing queue."""
import asyncio
import json
import math
import time
import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from sqlalchemy import update, delete, or_, select, func, and_, case, exists
from .db import (Organization, Contact, Conversation, ChannelConnection, Message, Note,
                 AutomationRule, OutgoingJob, AuditLog, Membership, ContactIdentity, WhatsAppConsent, now, uid)
from .auth import audit
from .integrations.adapters import adapter_for, unseal
from .integrations.base import AdapterError
from .delivery_truth import confirmed_response

VALID_STATUSES = {'new','in_progress','waiting','closed'}
VALID_STAGES = {'new','interested','negotiation','payment','success','lost'}

def as_message(m):
    return dict(id=m.id, direction=m.direction, body=m.body, kind=m.kind, created_at=m.created_at, delivery_status=m.delivery_status, response_confirmed_at=m.response_confirmed_at, is_demo=m.is_demo, attachment=json.loads(m.attachment) if m.attachment else None)

def as_conversation(db, c):
    contact = db.get(Contact, c.contact_id)
    ch = db.get(ChannelConnection, c.channel_id)
    org = db.get(Organization, c.organization_id)
    org_paused = bool(org and org.outbound_paused_at is not None)
    last = db.query(Message).filter_by(organization_id=c.organization_id,conversation_id=c.id).order_by(Message.created_at.desc(),Message.id.desc()).first()
    return dict(id=c.id, contact_id=c.contact_id, contact_name=contact.name, channel_id=ch.id, channel=ch.provider, channel_name=ch.name, channel_mode=ch.mode, outbound_paused=(bool(ch.outbound_paused_at is not None) or org_paused) if ch.mode=='live' else False, organization_outbound_paused=org_paused, status=c.status, priority=c.priority, assigned_user_id=c.assigned_user_id, reply_lock_owner_id=c.reply_lock_owner_id if c.reply_lock_expires_at and c.reply_lock_expires_at>now() else None, reply_lock_expires_at=c.reply_lock_expires_at if c.reply_lock_expires_at and c.reply_lock_expires_at>now() else None, pinned=c.pinned, archived=c.archived, unread_count=c.unread_count, version=c.version,
        whatsapp_window_open=(bool(c.last_inbound_at and now()-c.last_inbound_at<24*3600) if ch.provider=='whatsapp' else None),
        last_message_at=c.last_message_at, last_message=last.body[:140] if last else '', stage=contact.stage, tags=json.loads(contact.tags or '[]'), created_at=c.created_at)

def as_contact(c):
    return dict(id=c.id,name=c.name,phone=c.phone,email=c.email,tags=json.loads(c.tags or '[]'),stage=c.stage,deal_amount=c.deal_amount,deal_confirmed=c.deal_confirmed,next_followup_at=c.next_followup_at)

def run_rules(db, org_id, conv, message):
    if message.direction != 'in': return
    rules = db.query(AutomationRule).filter_by(organization_id=org_id,event='message_received',enabled=True).all()
    contact = db.get(Contact, conv.contact_id)
    for rule in rules:
        match = rule.condition_type == 'always' or (rule.condition_type == 'contains' and bool(rule.condition_value) and rule.condition_value.lower() in message.body.lower())
        if not match: continue
        if rule.action_type == 'tag' and rule.action_value:
            tags = json.loads(contact.tags or '[]')
            if rule.action_value not in tags:
                tags.append(rule.action_value)
                contact.tags = json.dumps(tags, ensure_ascii=False)
        elif rule.action_type == 'priority':
            conv.pinned = True
        elif rule.action_type == 'status' and rule.action_value in VALID_STATUSES:
            conv.status = rule.action_value
            if rule.action_value == 'closed': conv.archived = True
        elif rule.action_type == 'assign_least_busy' and not conv.assigned_user_id:
            choices = db.query(Membership).filter_by(organization_id=org_id,active=True,available=True).filter(Membership.role.in_(['operator','manager'])).all()
            if choices:
                workloads = {m.user_id: db.query(Conversation).filter_by(organization_id=org_id,assigned_user_id=m.user_id).filter(Conversation.status!='closed').count() for m in choices}
                conv.assigned_user_id = min(workloads, key=lambda u: (workloads[u],u))

def _insert_if_absent(db, model, values, *, unique_columns):
    """Atomic, transaction-local claim for SQLite and PostgreSQL.

    Do not SELECT/INSERT under concurrent first inbound events: independent
    webhook workers can observe an absent chat or external identity together.
    INSERT .. ON CONFLICT DO NOTHING waits for the winner on PostgreSQL, then
    lets the loser use the committed entity without rolling back its webhook
    reservation or accidentally writing duplicate inbound counters.
    """
    dialect=db.get_bind().dialect.name
    if dialect=='postgresql':
        from sqlalchemy.dialects.postgresql import insert
    elif dialect=='sqlite':
        from sqlalchemy.dialects.sqlite import insert
    else:
        raise RuntimeError('Idempotent inbound writes require SQLite or PostgreSQL')
    result=db.execute(insert(model).values(**values).on_conflict_do_nothing(
        index_elements=unique_columns))
    return result.rowcount==1


def _inbound_time(value):
    """Ignore invalid/untrusted timestamps instead of poisoning Inbox order."""
    stamp=now()
    try:
        incoming=float(value) if value is not None else stamp
    except (ValueError,TypeError,OverflowError):
        return stamp
    if not math.isfinite(incoming) or incoming<946684800 or incoming>stamp+300:
        return stamp
    return incoming


def ingest_inbound(db, *, channel, external_chat_id, external_message_id, sender_id, sender_name, text, timestamp=None, kind='text', history=False, attachment=None):
    """Transactionally idempotent first contact, chat and inbound message.

    The database must enforce identity/chat/message uniqueness. All three
    claims and the unread increment live in the caller's transaction; failed
    delivery of a webhook HTTP response can therefore be retried safely.
    """
    if not external_message_id or not external_chat_id or not sender_id:
        return None
    chat_id=str(external_chat_id)
    event_id=str(external_message_id)
    user_id=str(sender_id)
    if max(len(chat_id),len(event_id),len(user_id))>250:
        raise ValueError('Внешний идентификатор превышает 250 символов')
    event_time=_inbound_time(timestamp)
    tenant=channel.organization_id
    conv=db.query(Conversation).filter_by(channel_id=channel.id,
                external_chat_id=chat_id,organization_id=tenant).first()
    if conv is None:
        identity=db.query(ContactIdentity).filter_by(
            organization_id=tenant,channel_id=channel.id,
            external_user_id=user_id).first()
        contact=None
        candidate=None
        identity_id=None
        identity_created=False
        if identity is not None:
            contact=db.query(Contact).filter_by(id=identity.contact_id,
                                                 organization_id=tenant).first()
        if contact is None:
            # The contact row is speculative until the identity claim wins.
            # A losing worker deletes its unused row in the SAME transaction.
            candidate=Contact(organization_id=tenant,
                name=(str(sender_name or f'Клиент {user_id[-6:]}'))[:160])
            db.add(candidate)
            db.flush()
            identity_id=uid()
            identity_created=_insert_if_absent(db,ContactIdentity,dict(
                id=identity_id,organization_id=tenant,contact_id=candidate.id,
                channel_id=channel.id,external_user_id=user_id),
                unique_columns=['channel_id','external_user_id'])
            if identity_created:
                contact=candidate
            else:
                # Unique index guarantees a single winning identity.  The
                # conflict wait makes its row visible under READ COMMITTED.
                db.delete(candidate)
                db.flush()
                identity=db.query(ContactIdentity).filter_by(
                    organization_id=tenant,channel_id=channel.id,
                    external_user_id=user_id).one()
                contact=db.query(Contact).filter_by(id=identity.contact_id,
                                                     organization_id=tenant).one()
        conversation_id=uid()
        won=_insert_if_absent(db,Conversation,dict(
            id=conversation_id,organization_id=tenant,channel_id=channel.id,
            contact_id=contact.id,external_chat_id=chat_id,
            external_recipient_id=user_id,status='new',last_message_at=event_time),
            unique_columns=['channel_id','external_chat_id'])
        if won:
            conv=db.get(Conversation,conversation_id)
        else:
            # A different webhook already created this chat.  The speculative
            # identity/contact must not persist as an orphan in that case.
            if identity_created:
                db.execute(delete(ContactIdentity).where(
                    ContactIdentity.id==identity_id,
                    ContactIdentity.organization_id==tenant,
                    ContactIdentity.channel_id==channel.id))
                db.delete(candidate)
                db.flush()
            conv=db.query(Conversation).filter_by(channel_id=channel.id,
                external_chat_id=chat_id,organization_id=tenant).one()
    message_id=uid()
    written=_insert_if_absent(db,Message,dict(
        id=message_id,organization_id=tenant,conversation_id=conv.id,
        external_id=event_id,body=text or '[Медиа]',kind=kind,direction='in',
        attachment=json.dumps(attachment,ensure_ascii=False) if attachment else None,
        created_at=event_time,delivery_status='delivered',is_demo=(channel.mode=='demo')),
        unique_columns=['conversation_id','external_id'])
    if not written:
        # Distinct requests for the SAME provider event are valid retries.
        # No rule, unread or version increment should be run again.
        return db.query(Message).filter_by(organization_id=tenant,
            conversation_id=conv.id,external_id=event_id).one()
    msg=db.get(Message,message_id)
    updated=db.execute(update(Conversation).where(
        Conversation.id==conv.id,
        Conversation.organization_id==tenant,
        Conversation.channel_id==channel.id,
    ).values(
        unread_count=Conversation.unread_count+(0 if history else 1),
        version=Conversation.version+1,
        last_message_at=case(
            (Conversation.last_message_at < event_time,event_time),
            else_=Conversation.last_message_at),
        last_inbound_at=case(
            (or_(Conversation.last_inbound_at.is_(None),
                 Conversation.last_inbound_at < event_time),event_time),
            else_=Conversation.last_inbound_at),
        archived=False,
        status=case((Conversation.status=='closed','new'),else_=Conversation.status),
    ).execution_options(synchronize_session=False)).rowcount
    if updated!=1:
        raise RuntimeError('Диалог больше не принадлежит подключённому каналу')
    db.refresh(conv)
    if not history:run_rules(db, tenant,conv,msg)
    db.flush()
    return msg

def analytics(db, org_id):
    """Tenant-scoped KPIs without loading entire historical message tables.

    Only the last seven days' inbound timestamps are loaded for chart bucketing.
    Counts and revenue are aggregated in the database. First-response average
    uses only R28 provider API acceptance / website render timestamps, never
    a queued message's composition time. Organization IANA timezone is used.
    """
    from sqlalchemy import and_, case, exists, func, select
    from datetime import time as date_time
    from .db import Organization

    org = db.get(Organization,org_id)
    sla_seconds = 60*(org.sla_minutes if org else 5)
    clock=now()
    n_conv = db.query(func.count(Conversation.id)).filter(
        Conversation.organization_id==org_id).scalar() or 0
    n_closed = db.query(func.count(Conversation.id)).filter(
        Conversation.organization_id==org_id,Conversation.status=='closed').scalar() or 0
    n_inbound = db.query(func.count(Message.id)).filter(
        Message.organization_id==org_id,Message.direction=='in').scalar() or 0
    # Real provider acceptance / website display is timestamped from R28 onward.
    # Old composition timestamps are NOT substituted into this KPI.
    first_inbound=(db.query(Message.conversation_id.label('conversation_id'),
                func.min(Message.created_at).label('first_at'))
              .filter(Message.organization_id==org_id,Message.direction=='in')
              .group_by(Message.conversation_id).subquery())
    first_confirmed=(db.query(Message.conversation_id.label('conversation_id'),
                        func.min(Message.response_confirmed_at).label('confirmed_at'))
              .filter(Message.organization_id==org_id,confirmed_response(),
                      Message.response_confirmed_at.is_not(None))
              .group_by(Message.conversation_id).subquery())
    avg_reply=(db.query(func.avg((first_confirmed.c.confirmed_at-first_inbound.c.first_at)/60))
               .select_from(first_confirmed)
               .join(first_inbound,first_inbound.c.conversation_id==first_confirmed.c.conversation_id)
               .filter(first_confirmed.c.confirmed_at>=first_inbound.c.first_at).scalar())
    responded_after_last=exists(select(Message.id).where(
        Message.organization_id==org_id,
        Message.conversation_id==Conversation.id,
        confirmed_response(),Message.created_at>=Conversation.last_inbound_at))
    unanswered=db.query(func.count(Conversation.id)).filter(
        Conversation.organization_id==org_id,
        Conversation.last_inbound_at.is_not(None),~responded_after_last).scalar() or 0
    sla_overdue=db.query(func.count(Conversation.id)).filter(
        Conversation.organization_id==org_id,Conversation.status!='closed',
        Conversation.last_inbound_at.is_not(None),
        Conversation.last_inbound_at<clock-sla_seconds,
        ~responded_after_last).scalar() or 0
    outgoing_pending=(db.query(func.count(OutgoingJob.id)).filter(
        OutgoingJob.organization_id==org_id,
        OutgoingJob.status.in_(['queued','processing'])).scalar() or 0)
    outgoing_attention=(db.query(func.count(OutgoingJob.id)).filter(
        OutgoingJob.organization_id==org_id,
        OutgoingJob.status.in_(['failed','uncertain'])).scalar() or 0)

    by_channel=dict(db.query(ChannelConnection.provider,func.count(Conversation.id))
                    .join(Conversation,Conversation.channel_id==ChannelConnection.id)
                    .filter(Conversation.organization_id==org_id,
                            ChannelConnection.organization_id==org_id)
                    .group_by(ChannelConnection.provider).all())
    raw_workload=db.query(Conversation.assigned_user_id,func.count(Conversation.id)).filter(
        Conversation.organization_id==org_id).group_by(Conversation.assigned_user_id).all()
    workload={identity or 'unassigned':count for identity,count in raw_workload}

    # Avoid scanning old rows for the chart, including on very large tenants.
    zone=ZoneInfo((org.timezone if org else None) or 'UTC')
    today=datetime.fromtimestamp(clock,zone).date()
    earliest=today-timedelta(days=6)
    lower=datetime.combine(earliest,date_time.min,zone).timestamp()
    upper=datetime.combine(today+timedelta(days=1),date_time.min,zone).timestamp()
    recent=db.query(Message.created_at).filter(
        Message.organization_id==org_id,Message.direction=='in',
        Message.created_at>=lower,Message.created_at<upper).all()
    buckets=Counter(datetime.fromtimestamp(ts,zone).date() for (ts,) in recent)
    timeline=[{'day':(today-timedelta(days=i)).strftime('%d.%m'),
               'count':buckets[today-timedelta(days=i)]} for i in range(6,-1,-1)]

    is_confirmed=and_(Contact.stage=='success',Contact.deal_confirmed.is_(True),
                       Contact.deal_amount.is_not(None))
    is_potential=and_(Contact.deal_confirmed.is_(False),
                      Contact.stage.notin_(['lost','success']))
    r=db.query(func.coalesce(func.sum(case((is_confirmed,Contact.deal_amount),else_=0)),0),
               func.sum(case((is_confirmed,1),else_=0)),
               func.coalesce(func.sum(case((is_potential,Contact.deal_amount),else_=0)),0))        .filter(Contact.organization_id==org_id).one()
    confirmed_revenue,confirmed_deals,potential_revenue=r
    has_demo=db.query(Message.id).filter(Message.organization_id==org_id,
                                         Message.is_demo.is_(True)).limit(1).first() is not None
    return dict(
        sla_overdue=sla_overdue,conversations=n_conv,inbound=n_inbound,
        no_response=unanswered,closed=n_closed,
        avg_first_reply_min=round(float(avg_reply),1) if avg_reply is not None else None,
        avg_first_reply_basis='verified_since_r28',
        outgoing_pending=outgoing_pending,outgoing_attention=outgoing_attention,
        by_channel=by_channel,days=timeline,workload=workload,
        confirmed_revenue=float(confirmed_revenue),confirmed_deals=int(confirmed_deals or 0),
        potential_revenue=float(potential_revenue),
        conversion_pct=round(100*int(confirmed_deals or 0)/n_conv,1) if n_conv else 0,
        currency=(org.currency if org else 'RUB'),
        timezone=(org.timezone if org else 'UTC'),
        data_source='demo' if has_demo else 'recorded')

log=logging.getLogger('omnichat.outbox')


async def process_outbox(db_factory, limit=20):
    """Fair, tenant-scoped dispatch: one in-flight POST per channel, not one
    message per polling interval. Round-robin passes let one busy account
    drain multiple messages sequentially while respecting global job budget.
    """
    remaining=max(0,min(int(limit),100))
    total=0
    while remaining>0:
        completed=await _process_outbox_round(db_factory,remaining)
        if completed<=0:
            break
        total+=completed
        remaining-=completed
    return total


async def _process_outbox_round(db_factory, limit=20):
    """One per-channel round; SQL sender slots fence independent workers.

    R23 separates *preflight* (safe to reclaim) from committed send-start
    (unknown outcome after crash). R27 also fences the sender account itself.
    """
    from .outbox_recovery import recover_stale_jobs, mark_send_started, claim_heartbeat
    from .channel_dispatch import reserve as reserve_sender, release as release_sender
    from .db import ChannelDispatchLease
    from .dispatch_control import allowed_to_claim, is_paused, record_transition
    from sqlalchemy.orm import aliased

    processed=0
    with db_factory() as db:
        recover_stale_jobs(db)
        if limit <= 0:
            return 0
        clock=now()
        processing=aliased(OutgoingJob)
        ranked=select(
            OutgoingJob.id.label('job_id'),
            OutgoingJob.channel_id.label('channel_id'),
            OutgoingJob.organization_id.label('org_id'),
            OutgoingJob.created_at.label('created'),
            func.row_number().over(
                partition_by=OutgoingJob.organization_id,
                order_by=(OutgoingJob.created_at.asc(),OutgoingJob.id.asc())
            ).label('tenant_position'),
            func.row_number().over(
                partition_by=OutgoingJob.channel_id,
                order_by=(OutgoingJob.created_at.asc(),OutgoingJob.id.asc())
            ).label('channel_position')
        ).outerjoin(ChannelConnection,and_(
            ChannelConnection.id==OutgoingJob.channel_id,
            ChannelConnection.organization_id==OutgoingJob.organization_id
        )).outerjoin(Organization, Organization.id==OutgoingJob.organization_id
        ).outerjoin(ChannelDispatchLease,ChannelDispatchLease.channel_id==OutgoingJob.channel_id).where(
            OutgoingJob.status=='queued',OutgoingJob.next_attempt_at<=clock,
            allowed_to_claim(OutgoingJob.organization_id,OutgoingJob.channel_id,clock),
            # Skip accounts with live processing, including pre-R27 workers that
            # do not own a sender slot. Do not block healthy companies.
            ~exists(select(processing.id).where(
                processing.channel_id==OutgoingJob.channel_id,
                processing.status=='processing')),
            or_(ChannelDispatchLease.channel_id.is_(None),
                ChannelDispatchLease.expires_at<=clock),
            # Tenant-wide incident pause excludes ALL the company's jobs before
            # LIMIT, so a paused tenant cannot crowd out healthy businesses.
            or_(Organization.outbound_paused_at.is_(None),Organization.id.is_(None)),
            or_(ChannelConnection.rate_limited_until.is_(None),
                ChannelConnection.rate_limited_until<=clock,
                ChannelConnection.id.is_(None)),
            # Exclude accounts in manual emergency pause BEFORE pagination;
            # suspended tenant work must not starve other tenants.
            or_(ChannelConnection.outbound_paused_at.is_(None),
                ChannelConnection.id.is_(None))).subquery()
        selected=db.execute(select(ranked.c.job_id,ranked.c.channel_id,
            ranked.c.org_id).where(ranked.c.channel_position==1).order_by(
            ranked.c.tenant_position.asc(),ranked.c.created.asc(),
            ranked.c.job_id.asc()).limit(limit)).all()

    for job_id,channel_id,org_id in selected:
        token=uid()
        # Reserve the account's sender slot BEFORE claiming the queued job.
        # All API and worker processes coordinate through the same SQL row.
        if not reserve_sender(db_factory,channel_id,org_id,token):
            continue
        try:
            with db_factory() as db:
                stamp=now()
                claim=db.execute(update(OutgoingJob).where(
                    OutgoingJob.id==job_id,OutgoingJob.status=='queued',
                    OutgoingJob.channel_id==channel_id,
                    OutgoingJob.organization_id==org_id,
                    OutgoingJob.next_attempt_at<=stamp,
                    allowed_to_claim(OutgoingJob.organization_id,OutgoingJob.channel_id,stamp),
                    ~exists(select(Organization.id).where(Organization.id==OutgoingJob.organization_id,Organization.outbound_paused_at.is_not(None))),
                    ~exists(select(ChannelConnection.id).where(ChannelConnection.id==OutgoingJob.channel_id,ChannelConnection.organization_id==OutgoingJob.organization_id,ChannelConnection.outbound_paused_at.is_not(None)))
                ).values(status='processing',claimed_at=stamp,claim_token=token,
                         send_started_at=None,attempts=OutgoingJob.attempts+1)).rowcount
                if claim==1:
                    claimed=db.get(OutgoingJob,job_id)
                    record_transition(db,claimed,'queued','claimed')
                db.commit()
        except Exception:
            release_sender(db_factory,channel_id,org_id,token)
            raise
        if claim!=1:
            release_sender(db_factory,channel_id,org_id,token)
            continue

        pulse=asyncio.create_task(claim_heartbeat(
            db_factory,job_id,token,lease_channel_id=channel_id))
        try:
            with db_factory() as db:
                job=db.get(OutgoingJob,job_id)
                message=db.get(Message,job.message_id) if job else None
                channel=db.get(ChannelConnection,job.channel_id) if job else None
                org=db.get(Organization,job.organization_id) if job else None
                conv=db.get(Conversation,message.conversation_id) if message else None

                def settle(status, delivery, *, error=None, retry_at=None, external_id=None):
                    """Atomically finish ONLY the still-owned attempt."""
                    values={'status':status,'claimed_at':None,'claim_token':None,
                            'last_error':error}
                    if retry_at is not None:
                        values['next_attempt_at']=retry_at
                    if status=='queued':
                        # 429/definitive transient failure was not accepted as
                        # a message; future attempts need a fresh send marker.
                        values['send_started_at']=None
                    changed=db.execute(update(OutgoingJob).where(
                        OutgoingJob.id==job_id,OutgoingJob.status=='processing',
                        OutgoingJob.claim_token==token
                    ).values(**values)).rowcount
                    if changed!=1:
                        db.rollback()
                        log.warning('Provider result cannot finalize: job ownership changed')
                        return False
                    if message and message.organization_id==job.organization_id:
                        message.delivery_status=delivery
                        if status=='done':
                            message.external_id=external_id or f'local-out-{message.id}'
                            # 2xx from the official provider proves API acceptance,
                            # not delivery to the recipient and not that they read it.
                            message.response_confirmed_at=now()
                    if channel and channel.organization_id==job.organization_id:
                        channel.last_error=error
                        if status=='done':
                            channel.outbound_api_accepted_at=now()
                    job.status=status
                    event=('api_accepted' if status=='done' else
                           'hard_fail' if status=='failed' else
                           'uncertain' if status=='uncertain' else
                           'retry_scheduled')
                    record_transition(db,job,'processing',event)
                    db.commit()
                    return True

                # Re-evaluate account cooldown AFTER claiming. Another worker
                # could have encountered HTTP 429 between batch selection and
                # this statement. No external API call has started.
                if (channel and channel.organization_id==job.organization_id and
                    channel.rate_limited_until and channel.rate_limited_until>now()):
                    # Giving back a claim does not consume an external attempt.
                    changed=db.execute(update(OutgoingJob).where(
                        OutgoingJob.id==job_id,OutgoingJob.status=='processing',
                        OutgoingJob.claim_token==token,OutgoingJob.send_started_at.is_(None)
                    ).values(status='queued',claimed_at=None,claim_token=None,
                             attempts=case((OutgoingJob.attempts>0,OutgoingJob.attempts-1),else_=0),
                             next_attempt_at=channel.rate_limited_until)).rowcount
                    db.commit()
                    if changed!=1:
                        log.warning('Outbox cooldown return lost job claim')
                    continue

                # Manual incident pause is distinct from provider 429 cooldown.
                # A claimed preflight is returned to the queue without an HTTP
                # attempt. Inbound webhooks and already-started requests continue.
                if is_paused(db,job.organization_id,job.channel_id) or (
                    org and org.outbound_paused_at is not None) or (
                    channel and channel.organization_id==job.organization_id and
                    channel.outbound_paused_at is not None):
                    from .outbox_recovery import release_paused_preflight
                    release_paused_preflight(db,job_id,token,job.organization_id)
                    continue

                if (not message or not channel or not conv or
                    message.organization_id!=job.organization_id or
                    channel.organization_id!=job.organization_id or
                    conv.organization_id!=job.organization_id or
                    message.conversation_id!=conv.id or conv.channel_id!=channel.id or
                    channel.id!=job.channel_id or channel.mode!='live' or
                    channel.status!='connected'):
                    settle('failed','failed',error='Несовпадение организации, диалога или канала')
                    continue

                sent_started=False
                try:
                    template_mode=(message.kind=='whatsapp_template')
                    if template_mode:
                        if channel.provider!='whatsapp':
                            raise AdapterError('Шаблон WhatsApp не может быть отправлен через другой канал')
                        consent=db.query(WhatsAppConsent).filter_by(
                            organization_id=job.organization_id,channel_id=channel.id,
                            contact_id=conv.contact_id,
                            recipient_id=conv.external_recipient_id).first()
                        if not consent or consent.revoked_at is not None:
                            raise AdapterError('Согласие WhatsApp отозвано или не было подтверждено')
                    elif channel.provider in ('whatsapp','instagram','messenger') and (
                        not conv.last_inbound_at or now()-conv.last_inbound_at>24*3600):
                        raise AdapterError('24-часовое окно ответа закрыто; требуется разрешённый шаблон или новый ответ клиента')

                    credentials=unseal(channel.encrypted_credentials)
                    if credentials.get('expires_at') and credentials['expires_at']<now()+300:
                        if channel.provider not in ('instagram','avito'):
                            raise AdapterError('Срок действия токена истёк; необходимо обновить подключение')
                        refreshed=await adapter_for(channel.provider).refresh_credentials(credentials)
                        if refreshed.get('expires_in'):
                            refreshed['expires_at']=now()+int(refreshed['expires_in'])
                        elif refreshed.get('expires_at') and refreshed['expires_at']<=now():
                            raise AdapterError('Сервис не вернул новый срок действия токена')
                        credentials=refreshed
                        from .integrations.adapters import seal
                        channel.encrypted_credentials=seal(credentials)
                        channel.token_expires_at=credentials.get('expires_at')
                        channel.last_verified_at=now()
                        db.commit()
                    credentials['_outgoing_message_id']=message.id
                    adapter=adapter_for('whatsapp' if template_mode else channel.provider)
                    payload=None
                    if template_mode:
                        payload=json.loads(message.attachment or '{}')
                        # Structural validation BEFORE persisting send_started.
                        for field in ('template_name','language','parameters'):
                            if field not in payload:
                                raise AdapterError('Неверный формат сохранённого шаблона WhatsApp')

                    # This transaction COMMIT is the safety boundary: a crashed
                    # worker may only be auto-recovered if this step was absent.
                    if not mark_send_started(db,job.id,token,job.organization_id,
                                             dispatch_token=token):
                        # Pause may have been committed after the earlier
                        # preflight check. Return only this unstarted claim.
                        from .outbox_recovery import release_paused_preflight
                        if not release_paused_preflight(db,job.id,token,job.organization_id):
                            log.warning('Send checkpoint rejected: claim was already lost')
                        continue
                    sent_started=True
                    if template_mode:
                        external_id=await adapter.send_template(
                            credentials,channel,conv,payload['template_name'],
                            payload['language'],payload['parameters'])
                    else:
                        external_id=await adapter.send_message(
                            credentials,channel,conv,message.body)
                    if settle('done','accepted',external_id=external_id):
                        # A delivery callback may have arrived before the API
                        # response was committed. Reconcile in a NEW transaction
                        # to also cover races with the webhook's own commit.
                        if channel.provider=='whatsapp' and external_id:
                            try:
                                from .provider_receipts import reconcile_whatsapp_receipt
                                with db_factory() as receipt_session:
                                    reconcile_whatsapp_receipt(receipt_session,channel.id,external_id)
                                    receipt_session.commit()
                            except Exception:
                                # Never undo/duplicate an already accepted API
                                # response because a receipt lookup failed.
                                log.exception('Deferred provider receipt reconciliation failed')
                        processed+=1
                except AdapterError as exc:
                    error=str(exc)[:320]
                    backoff=min(300,5*2**job.attempts)
                    if exc.rate_limited:
                        backoff=exc.retry_after or backoff
                        pause_until=now()+backoff
                        # Use a SQL max-if-greater rather than a stale ORM
                        # value; concurrent 429s must not shorten cooldown.
                        db.execute(update(ChannelConnection).where(
                            ChannelConnection.id==channel.id,
                            ChannelConnection.organization_id==job.organization_id
                        ).values(rate_limited_until=case(
                            (ChannelConnection.rate_limited_until>pause_until,
                             ChannelConnection.rate_limited_until),
                            else_=pause_until)))
                    if exc.uncertain:
                        status,delivery='uncertain','uncertain'
                    elif exc.retriable and job.attempts<4:
                        status,delivery='queued','queued'
                    else:
                        status,delivery='failed','failed'
                    if settle(status,delivery,error=error,
                              retry_at=now()+backoff if status=='queued' else None):
                        processed+=1
                except Exception:
                    # Unexpected exceptions AFTER the marker may represent a
                    # delivered POST: never blindly retry. Before it, the
                    # request was not sent but the local preflight still failed.
                    status='uncertain' if sent_started else 'failed'
                    error=('Неожиданная ошибка отправки. Проверить у провайдера'
                           if sent_started else 'Ошибка подготовки до отправки. Проверьте интеграцию.')
                    if settle(status,status,error=error):
                        processed+=1
        finally:
            pulse.cancel()
            try:
                await pulse
            except asyncio.CancelledError:
                pass
            try:
                release_sender(db_factory,channel_id,org_id,token)
            except Exception:
                # An expired slot will be re-claimable; never clear a newer
                # owner's slot if a stale former worker wakes up later.
                log.exception('Cannot release sender slot; TTL will expire')
    return processed
