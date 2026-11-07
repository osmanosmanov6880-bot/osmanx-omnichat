"""R26 CI ONLY: PostgreSQL 16 concurrent tenant-wide incident stop.

Requires a disposable PostgreSQL database already migrated to head. Does not
contact message providers, print access tokens, or change production data.
"""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy import update
from sqlalchemy.orm import Session, sessionmaker
from app.db import (Organization,ChannelConnection,Contact,Conversation,
                    Message,OutgoingJob,engine_for,assert_schema_current,uid,now)
from app.outbox_recovery import mark_send_started,release_paused_preflight

url=os.getenv('DATABASE_URL','')
if not url.startswith(('postgresql://','postgresql+psycopg://')) or os.getenv('APP_ENV')=='production':
    raise SystemExit('Refusing PostgreSQL test outside disposable CI database')
engine=engine_for(url)
assert engine.dialect.name=='postgresql'
assert assert_schema_current(engine)
SessionFactory=sessionmaker(engine)
with SessionFactory() as session:
    org=Organization(name='R26 isolated incident test '+uid()[:8])
    session.add(org);session.flush()
    ch=ChannelConnection(organization_id=org.id,provider='telegram',name='R26 test bot',
        mode='live',status='connected')
    contact=Contact(organization_id=org.id,name='R26 test visitor')
    session.add_all([ch,contact]);session.flush()
    conversation=Conversation(organization_id=org.id,channel_id=ch.id,
        contact_id=contact.id,external_chat_id='r26-ci-chat')
    session.add(conversation);session.flush()
    msg=Message(organization_id=org.id,conversation_id=conversation.id,
        direction='out',body='Test only',delivery_status='queued')
    session.add(msg);session.flush()
    claim_token=uid()
    job=OutgoingJob(organization_id=org.id,channel_id=ch.id,message_id=msg.id,
        status='processing',claim_token=claim_token,claimed_at=now(),attempts=1)
    session.add(job);session.commit()
    org_id,job_id,channel_id=org.id,job.id,ch.id

barrier=Barrier(2)

def contender(stamp):
    barrier.wait(timeout=10)
    with SessionFactory() as session:
        changed=session.execute(update(Organization).where(
            Organization.id==org_id, Organization.outbound_paused_at.is_(None))
            .values(outbound_paused_at=stamp)).rowcount
        session.commit()
    return changed

with ThreadPoolExecutor(max_workers=2) as pool:
    jobs=[pool.submit(contender,now()),pool.submit(contender,now()+1)]
    results=[task.result(timeout=20) for task in jobs]
assert sorted(results)==[0,1],results
with SessionFactory() as session:
    paused=session.get(Organization,org_id).outbound_paused_at
    assert paused is not None
    assert not mark_send_started(session,job_id,claim_token,org_id)
    assert release_paused_preflight(session,job_id,claim_token,org_id)
    assert session.get(OutgoingJob,job_id).status=='queued'
with SessionFactory() as session:
    bad=session.execute(update(Organization).where(
        Organization.id==org_id,Organization.outbound_paused_at==paused+1)
        .values(outbound_paused_at=None)).rowcount
    assert bad==0
    changed=session.execute(update(Organization).where(
        Organization.id==org_id,Organization.outbound_paused_at==paused)
        .values(outbound_paused_at=None)).rowcount
    session.commit()
    assert changed==1
print('R26 PostgreSQL 16: CAS pause race, pre-send checkpoint, safe reclaim and guarded resume PASS')
engine.dispose()
