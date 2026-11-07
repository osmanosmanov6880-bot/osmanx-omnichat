"""R27: a database-fenced sender slot per external account.

The queue may contain many conversations for one WhatsApp/Telegram account.
A sender slot prevents independent worker processes from issuing overlapping
POSTs through that account. Slots are owned by the same UUID as the job's
fenced claim; the last pre-HTTP checkpoint verifies both claims together.

A lease is NOT an exactly-once delivery guarantee. If a worker loses its lease
while a request is in progress, the R23 durable send marker still quarantines
an unknown outcome instead of blindly repeating the same message.
"""
from sqlalchemy import update, select
from sqlalchemy.exc import OperationalError

from .db import ChannelConnection, ChannelDispatchLease, now

DEFAULT_LEASE_SECONDS = 180  # >120s stale-job window; heartbeat every 15s


def reserve(db_factory, channel_id: str, org_id: str, token: str, *,
            seconds: int = DEFAULT_LEASE_SECONDS, stamp: float | None = None) -> bool:
    if not channel_id or not org_id or not token or not 30 <= seconds <= 3600:
        raise ValueError('Некорректная блокировка отправителя')
    stamp = now() if stamp is None else stamp
    try:
        with db_factory() as db:
            # Never let an inconsistent/corrupt outbox row reserve an account
            # belonging to another tenant. The last pre-HTTP gate checks again.
            belongs=db.execute(select(ChannelConnection.id).where(
                ChannelConnection.id==channel_id,
                ChannelConnection.organization_id==org_id)).scalar_one_or_none()
            if belongs is None:
                return False
            changed = db.execute(update(ChannelDispatchLease).where(
                ChannelDispatchLease.channel_id == channel_id,
                ChannelDispatchLease.organization_id == org_id,
                ChannelDispatchLease.expires_at <= stamp,
            ).values(owner_token=token, acquired_at=stamp,
                     renewed_at=stamp, expires_at=stamp + seconds)).rowcount
            if not changed:
                if db.bind.dialect.name == 'sqlite':
                    from sqlalchemy.dialects.sqlite import insert
                elif db.bind.dialect.name == 'postgresql':
                    from sqlalchemy.dialects.postgresql import insert
                else:
                    raise RuntimeError('Поддерживаются SQLite и PostgreSQL')
                changed = db.execute(insert(ChannelDispatchLease).values(
                    channel_id=channel_id, organization_id=org_id,
                    owner_token=token, acquired_at=stamp,
                    renewed_at=stamp, expires_at=stamp + seconds,
                ).on_conflict_do_nothing(index_elements=['channel_id'])).rowcount
            db.commit()
            return changed == 1
    except OperationalError:
        # Busy DB is NOT permission to send an unprotected provider request.
        return False


def release(db_factory, channel_id: str, org_id: str, token: str) -> bool:
    if not channel_id or not org_id or not token:
        return False
    with db_factory() as db:
        changed=db.execute(update(ChannelDispatchLease).where(
            ChannelDispatchLease.channel_id==channel_id,
            ChannelDispatchLease.organization_id==org_id,
            ChannelDispatchLease.owner_token==token,
        ).values(expires_at=0.0)).rowcount
        db.commit()
    return changed == 1


def renew_in_session(session, channel_id: str, token: str, *,
                     stamp: float | None = None,
                     seconds: int = DEFAULT_LEASE_SECONDS) -> bool:
    stamp = now() if stamp is None else stamp
    changed=session.execute(update(ChannelDispatchLease).where(
        ChannelDispatchLease.channel_id==channel_id,
        ChannelDispatchLease.owner_token==token,
        ChannelDispatchLease.expires_at>stamp,
    ).values(renewed_at=stamp,expires_at=stamp+seconds)).rowcount
    return changed==1
