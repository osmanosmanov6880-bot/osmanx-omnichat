"""Database-backed lease for platform-wide periodic jobs.

Only one worker polls Avito / runs retention cleanup at a time. The lease is
not exactly-once external delivery: ingestion still needs message deduplication.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from sqlalchemy import update
from sqlalchemy.exc import OperationalError
from .db import SchedulerLease, now, uid

log=logging.getLogger('omnichat.scheduler')
_ALLOWED={'avito_sync','retention_cleanup'}


def acquire(db_factory,name,*,seconds=300,stamp=None):
    if name not in _ALLOWED or not 3<=seconds<=3600:
        raise ValueError('Invalid scheduler lease')
    stamp=now() if stamp is None else stamp
    owner=uid()
    try:
        with db_factory() as db:
            count=db.execute(update(SchedulerLease).where(
                SchedulerLease.name==name,SchedulerLease.expires_at<=stamp).values(
                owner_id=owner,acquired_at=stamp,renewed_at=stamp,expires_at=stamp+seconds)).rowcount
            if not count:
                dialect=db.bind.dialect.name
                if dialect=='sqlite':
                    from sqlalchemy.dialects.sqlite import insert
                elif dialect=='postgresql':
                    from sqlalchemy.dialects.postgresql import insert
                else:raise RuntimeError('Only SQLite and PostgreSQL supported')
                count=db.execute(insert(SchedulerLease).values(name=name,owner_id=owner,
                    acquired_at=stamp,renewed_at=stamp,expires_at=stamp+seconds)
                    .on_conflict_do_nothing(index_elements=['name'])).rowcount
            db.commit()
        return owner if count==1 else None
    except OperationalError:
        log.warning('Scheduler lease unavailable; skip %s',name)
        return None


def renew(db_factory,name,owner,*,seconds=300,stamp=None):
    if name not in _ALLOWED or not owner:return False
    stamp=now() if stamp is None else stamp
    with db_factory() as db:
        changed=db.execute(update(SchedulerLease).where(SchedulerLease.name==name,
            SchedulerLease.owner_id==owner,SchedulerLease.expires_at>stamp)
            .values(renewed_at=stamp,expires_at=stamp+seconds)).rowcount
        db.commit()
    return changed==1


def release(db_factory,name,owner):
    if name not in _ALLOWED or not owner:return False
    with db_factory() as db:
        changed=db.execute(update(SchedulerLease).where(SchedulerLease.name==name,
            SchedulerLease.owner_id==owner).values(expires_at=0.0)).rowcount
        db.commit()
    return changed==1


@asynccontextmanager
async def held_task(db_factory,name,*,seconds=600):
    owner=acquire(db_factory,name,seconds=seconds)
    if not owner:
        yield False
        return
    parent=asyncio.current_task()
    lost=False
    async def refresh():
        nonlocal lost
        while True:
            await asyncio.sleep(max(1,seconds/4))
            try:active=renew(db_factory,name,owner,seconds=seconds)
            except Exception:
                log.exception('Could not renew scheduler lease')
                active=False
            if not active:
                lost=True
                if parent and not parent.done():parent.cancel()
                return
    guard=asyncio.create_task(refresh())
    try:
        yield True
        if lost:raise RuntimeError('Scheduler lease expired while running')
    finally:
        guard.cancel()
        try:await guard
        except asyncio.CancelledError:pass
        try:release(db_factory,name,owner)
        except Exception:log.exception('Could not release scheduler lease')


async def run_avito_sync(db_factory):
    async with held_task(db_factory,'avito_sync') as allowed:
        if not allowed:return 0
        from .synchronizers import sync_all_avito
        return await sync_all_avito(db_factory)


async def run_retention_cleanup(db_factory):
    async with held_task(db_factory,'retention_cleanup') as allowed:
        if not allowed:return False
        from .extras import purge_expired
        def task():
            with db_factory() as session:purge_expired(session)
        await asyncio.to_thread(task)
        return True
