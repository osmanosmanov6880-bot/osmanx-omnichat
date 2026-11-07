"""R23 real PostgreSQL 16 validation for a disposable CI database.

No customer data, no provider calls. Requires DATABASE_URL and already migrated
schema. Runs crash recovery in two competing SQL sessions; exactly one should
move a job out of processing per original claim.
"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy.orm import sessionmaker
from app.db import (engine_for,assert_schema_current,Organization,ChannelConnection,
                    Contact,Conversation,Message,OutgoingJob,AuditLog,now)
from app.outbox_recovery import recover_stale_jobs,mark_send_started,refresh_claim

url=os.environ.get('DATABASE_URL','')
if not url.startswith(('postgresql://','postgresql+psycopg://')) or os.environ.get('APP_ENV')=='production':
    raise SystemExit('R23 SQL verification is only allowed on ephemeral CI PostgreSQL')
engine=engine_for(url)
assert engine.dialect.name=='postgresql'
assert_schema_current(engine)
Session=sessionmaker(bind=engine,expire_on_commit=False)
try:
    with Session() as session:
        org=Organization(name='R23 isolated SQL recovery verification')
        session.add(org);session.flush()
        ch=ChannelConnection(organization_id=org.id,provider='telegram',mode='live',
                             name='R23 CI test channel',status='connected')
        contact=Contact(organization_id=org.id,name='CI contact')
        session.add_all([ch,contact]);session.flush()
        conv=Conversation(organization_id=org.id,channel_id=ch.id,contact_id=contact.id,
                          external_chat_id='r23-postgres-ci')
        session.add(conv);session.flush()
        ids=[]
        for i in range(2):
            msg=Message(organization_id=org.id,conversation_id=conv.id,direction='out',
                        body=f'CI body {i}',delivery_status='queued')
            session.add(msg);session.flush()
            job=OutgoingJob(organization_id=org.id,message_id=msg.id,channel_id=ch.id,
                            status='processing',attempts=1,next_attempt_at=0,
                            claimed_at=now()-360,claim_token=f'r23-test-token-{i}',
                            send_started_at=(now()-362) if i else None)
            session.add(job);session.flush()
            ids.append(job.id)
        session.commit()

    barrier=Barrier(2)
    def worker():
        barrier.wait(timeout=8)
        with Session() as session:
            return recover_stale_jobs(session)
    with ThreadPoolExecutor(max_workers=2) as pool:
        fs=[pool.submit(worker) for _ in range(2)]
        outcomes=[x.result(timeout=20) for x in fs]
    assert sum(x['before_send'] for x in outcomes)==1,outcomes
    assert sum(x['possibly_sent'] for x in outcomes)==1,outcomes
    with Session() as session:
        preflight=session.get(OutgoingJob,ids[0])
        sent=session.get(OutgoingJob,ids[1])
        assert preflight.status=='queued' and preflight.attempts==0
        assert sent.status=='uncertain'
        assert session.query(AuditLog).filter_by(
            organization_id=org.id,action='outbox.recovered_before_send').count()==1
        assert session.query(AuditLog).filter_by(
            organization_id=org.id,action='outbox.uncertain_after_interruption').count()==1
        assert not mark_send_started(session,ids[0],'r23-test-token-0',org.id)
    assert not refresh_claim(Session,ids[0],'r23-test-token-0')
    print('R23 POSTGRES 16: 2-worker race, preflight safe, post-send uncertain, CAS and audit verified')
finally:
    engine.dispose()
