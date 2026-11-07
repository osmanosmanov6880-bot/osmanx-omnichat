"""Disposable PostgreSQL integration check for R22 cancel/claim race.

Requires migrated ephemeral CI DATABASE_URL. Never run against user data.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import os
import sys
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
from app.db import (Organization, ChannelConnection, Contact, Conversation,
                    Message, OutgoingJob, assert_schema_current, engine_for)

url = os.getenv('DATABASE_URL','')
if not url.startswith(('postgresql://','postgresql+psycopg://')) or os.getenv('APP_ENV')=='production':
    raise SystemExit('R22 postgres race test requires disposable CI PostgreSQL')
engine = engine_for(url)
assert_schema_current(engine)
Session = sessionmaker(bind=engine)
try:
    with Session() as db:
        org=Organization(name='R22 ephemeral CI organization')
        db.add(org);db.flush()
        channel=ChannelConnection(organization_id=org.id,provider='telegram',name='R22 CI',mode='live',status='connected')
        contact=Contact(organization_id=org.id,name='Disposable CI contact')
        db.add_all([channel,contact]);db.flush()
        conv=Conversation(organization_id=org.id,channel_id=channel.id,contact_id=contact.id,
                          external_chat_id='r22-ci-visitor')
        db.add(conv);db.flush()
        message=Message(organization_id=org.id,conversation_id=conv.id,
                        direction='out',body='CI test',delivery_status='queued')
        db.add(message);db.flush()
        job=OutgoingJob(organization_id=org.id,message_id=message.id,channel_id=channel.id)
        db.add(job);db.commit()
        job_id=job.id;org_id=org.id
    gate=Barrier(2)
    def compete(state):
        with Session() as db:
            gate.wait(timeout=12)
            count=db.execute(update(OutgoingJob).where(
                OutgoingJob.id==job_id,OutgoingJob.organization_id==org_id,
                OutgoingJob.status=='queued').values(status=state)).rowcount
            db.commit()
            return count
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(compete,state) for state in ('cancelled','processing')]
        assert sorted(f.result(timeout=20) for f in futures)==[0,1]
    with Session() as db:
        status=db.get(OutgoingJob,job_id).status
        assert status in ('processing','cancelled')
        print('POSTGRES_R22_CANCEL_CLAIM_CAS=PASS',status)
finally:
    engine.dispose()
