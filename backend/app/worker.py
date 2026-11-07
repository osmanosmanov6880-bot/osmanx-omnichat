"""Dedicated worker for encrypted inbound recovery and safe outbound sends.

Both queues use SQL ownership/claim fencing. Uncertain provider POST results
remain quarantined; inbound messages can safely re-ingest idempotently.
"""
import asyncio
import logging
import os
import signal
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2]/'.env',override=False)
from . import db
from .services import process_outbox
from .scheduler_lease import run_avito_sync, run_retention_cleanup


logging.basicConfig(level=os.environ.get('LOG_LEVEL','INFO'))
log=logging.getLogger('omnichat.worker')

async def cycle(index:int):
    if not db.SessionLocal:
        raise RuntimeError('Database not initialized')
    from .inbound_jobs import process_batch
    received=await asyncio.to_thread(process_batch, db.SessionLocal, limit=40)
    sent=await process_outbox(db.SessionLocal)
    if index%12==0 and os.getenv('ENABLE_AVITO_POLLING','true').lower()=='true':
        await run_avito_sync(db.SessionLocal)
    if index%20==0:
        await run_retention_cleanup(db.SessionLocal)
    return sent + received

async def main():
    if os.getenv('APP_ENV')=='production' and not os.getenv('DATABASE_URL','').startswith(('postgresql://','postgresql+psycopg://')):
        raise RuntimeError('Production worker requires PostgreSQL')
    engine=db.initialize()
    stop=asyncio.Event()
    loop=asyncio.get_running_loop()
    for s in (signal.SIGTERM,signal.SIGINT):
        try:loop.add_signal_handler(s,stop.set)
        except NotImplementedError:pass
    from .worker_monitor import start_worker, heartbeat_loop, finish_cycle
    heartbeat_id=start_worker(db.SessionLocal,kind='worker')
    heartbeat_task=asyncio.create_task(heartbeat_loop(db.SessionLocal,heartbeat_id))
    log.info('OMNICHAT worker started')
    index=0
    while not stop.is_set():
        index+=1
        try:
            sent=await cycle(index)
            finish_cycle(db.SessionLocal,heartbeat_id,processed=sent)
            if sent:log.info('Outbox processed %s jobs',sent)
        except Exception:
            log.exception('Worker cycle failed')
            try:finish_cycle(db.SessionLocal,heartbeat_id,succeeded=False)
            except Exception:log.exception('Could not record failed cycle')
        try:await asyncio.wait_for(stop.wait(),timeout=3)
        except asyncio.TimeoutError:pass
    heartbeat_task.cancel()
    try:await heartbeat_task
    except asyncio.CancelledError:pass
    log.info('OMNICHAT worker stopped cleanly')
    engine.dispose()

if __name__=='__main__':
    asyncio.run(main())
