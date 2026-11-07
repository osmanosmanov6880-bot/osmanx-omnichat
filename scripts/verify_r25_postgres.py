"""Real PostgreSQL CI guard: pausing a channel prevents a stale send checkpoint.

Requires a migrated disposable `omnichat_ci` database (PostgreSQL 16), never
production. Does NOT call provider APIs or use customer credentials.
"""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy import update, func
from sqlalchemy.orm import sessionmaker
from app.db import (Organization,ChannelConnection,Contact,Conversation,Message,
                    OutgoingJob,engine_for,assert_schema_current,now)
from app.outbox_recovery import mark_send_started, release_paused_preflight

url=os.getenv('DATABASE_URL','')
if (not url.startswith(('postgresql://','postgresql+psycopg://')) or
        os.getenv('APP_ENV')=='production' or 'omnichat_ci' not in url):
    raise SystemExit('R25 SQL verification requires ONLY disposable PostgreSQL omnichat_ci')
engine=engine_for(url)
assert engine.dialect.name=='postgresql'
assert assert_schema_current(engine)
Session=sessionmaker(bind=engine,expire_on_commit=False)
try:
    with Session() as db:
        org=Organization(name='R25 disposable emergency pause verification')
        db.add(org);db.flush()
        ch=ChannelConnection(organization_id=org.id,provider='telegram',
            name='R25 CI channel',mode='live',status='connected')
        contact=Contact(organization_id=org.id,name='CI contact')
        db.add_all([ch,contact]);db.flush()
        conv=Conversation(organization_id=org.id,channel_id=ch.id,
            contact_id=contact.id,external_chat_id='r25-disposable')
        db.add(conv);db.flush()
        msg=Message(organization_id=org.id,conversation_id=conv.id,
            direction='out',body='R25 dry test, do not send',delivery_status='queued')
        db.add(msg);db.flush()
        job=OutgoingJob(organization_id=org.id,message_id=msg.id,
            channel_id=ch.id,status='processing',claim_token='r25-ci-claim',
            claimed_at=now(),attempts=1)
        db.add(job);db.commit()
        org_id,channel_id,job_id=org.id,ch.id,job.id
    with Session() as db:
        changed=db.execute(update(ChannelConnection).where(
            ChannelConnection.id==channel_id,ChannelConnection.organization_id==org_id,
            ChannelConnection.outbound_paused_at.is_(None)
        ).values(outbound_paused_at=now(),outbound_pause_reason='security_review')).rowcount
        db.commit()
        assert changed==1
    with Session() as db:
        assert not mark_send_started(db,job_id,'r25-ci-claim',org_id)
        assert release_paused_preflight(db,job_id,'r25-ci-claim',org_id)
        job=db.get(OutgoingJob,job_id)
        db.refresh(job)
        assert job.status=='queued' and job.attempts==0
    # Two administrators using independent database sessions must never both
    # report a newly acquired pause (compare-and-swap).
    with Session() as db:
        db.execute(update(ChannelConnection).where(ChannelConnection.id==channel_id)
                   .values(outbound_paused_at=None,outbound_pause_reason=None))
        db.commit()
    barrier=Barrier(2)
    def pause_again(stamp):
        barrier.wait(timeout=10)
        with Session() as db:
            changed=db.execute(update(ChannelConnection).where(
                ChannelConnection.id==channel_id,ChannelConnection.organization_id==org_id,
                ChannelConnection.outbound_paused_at.is_(None)
            ).values(outbound_paused_at=stamp,outbound_pause_reason='security_review')).rowcount
            db.commit()
            return changed
    with ThreadPoolExecutor(max_workers=2) as pool:
        fs=[pool.submit(pause_again,now()+i) for i in (0,1)]
        assert sorted(f.result(timeout=20) for f in fs)==[0,1]
    with Session() as db:
        ch=db.get(ChannelConnection,channel_id)
        assert ch.outbound_paused_at is not None
        assert db.query(OutgoingJob).filter_by(organization_id=org_id,
                                               status='queued').count()==1
    print('R25_POSTGRES_PAUSE_PASS: real SQL checkpoint gate + competing admins + safe requeue')
finally:
    engine.dispose()
