"""Durable, multi-process worker health signals.

Independent heartbeat ticks distinguish a live event loop from actual completed
outbox cycles. Dashboard returns only aggregate signals, never server identity,
credentials, other tenant workloads or secret exception messages.
"""
import asyncio
import logging
from sqlalchemy import func, update
from .db import WorkerHeartbeat, now, uid

log=logging.getLogger('omnichat.worker_monitor')
HEARTBEAT_INTERVAL=8
HEARTBEAT_TIMEOUT=40
CYCLE_TIMEOUT=120


def start_worker(db_factory, kind='worker', worker_id=None):
    if kind not in ('worker','api'):
        raise ValueError('Unknown background worker kind')
    worker_id=worker_id or uid()
    stamp=now()
    with db_factory() as session:
        session.add(WorkerHeartbeat(worker_id=worker_id,kind=kind,started_at=stamp,
                                    last_seen_at=stamp,stopped_at=None))
        session.commit()
    return worker_id


def pulse(db_factory, worker_id):
    with db_factory() as session:
        session.execute(update(WorkerHeartbeat).where(WorkerHeartbeat.worker_id==worker_id,
            WorkerHeartbeat.stopped_at.is_(None)).values(last_seen_at=now()))
        session.commit()


def finish_cycle(db_factory, worker_id, *, processed=0, succeeded=True):
    """No provider-specific messages or access tokens are ever stored here."""
    with db_factory() as session:
        job=session.query(WorkerHeartbeat).filter_by(worker_id=worker_id,stopped_at=None).first()
        if job:
            job.last_seen_at=now()
            if succeeded:
                job.last_cycle_at=now()
                job.processed_jobs+=max(0,int(processed))
                job.error_count=0
            else:
                job.error_count+=1
            session.commit()


def stop_worker(db_factory, worker_id):
    with db_factory() as session:
        session.execute(update(WorkerHeartbeat).where(WorkerHeartbeat.worker_id==worker_id)
                        .values(stopped_at=now()))
        session.commit()


async def heartbeat_loop(db_factory, worker_id, interval=HEARTBEAT_INTERVAL):
    """Keep heartbeats separate from slow HTTP calls in the outbox worker."""
    try:
        while True:
            await asyncio.sleep(interval)
            try:
                pulse(db_factory, worker_id)
            except Exception:
                log.exception('Unable to update background-worker heartbeat')
    finally:
        try:
            stop_worker(db_factory, worker_id)
        except Exception:
            log.exception('Unable to mark worker stopped')


def worker_health(session, moment=None):
    stamp=now() if moment is None else moment
    recent=(session.query(WorkerHeartbeat).filter(
        WorkerHeartbeat.stopped_at.is_(None),
        WorkerHeartbeat.last_seen_at>=stamp-HEARTBEAT_TIMEOUT).all())
    active=len(recent)
    good=[x for x in recent if x.last_cycle_at and x.last_cycle_at>=stamp-CYCLE_TIMEOUT]
    latest=max((x.last_cycle_at for x in recent if x.last_cycle_at),default=None)
    if good:
        code='working';summary='Очередь обрабатывается'
    elif active:
        code='checking';summary='Обработчик запущен, ожидаем завершения цикла'
    else:
        code='offline';summary='Фоновый обработчик не отвечает'
    return {'code':code,'summary':summary,'active':bool(active),
            'last_cycle_seconds_ago':int(stamp-latest) if latest is not None else None}
