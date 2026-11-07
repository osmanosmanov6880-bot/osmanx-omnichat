#!/usr/bin/env python3
"""R31 real PostgreSQL multi-process encrypted inbound claim + dedup proof.

Run only with an ephemeral migrated PostgreSQL database and encryption key.
Four independent OS processes race on one incoming event. No external APIs.
"""
import multiprocessing as mp
import os
from sqlalchemy.orm import Session
from app.db import (engine_for, assert_schema_current, Organization,
                    ChannelConnection, Contact, ContactIdentity, Conversation,
                    Message, InboundJob)
from app.inbound_jobs import stage, process_one


def stage_worker(url, channel_id, barrier, result):
    engine=engine_for(url)
    try:
        with Session(engine) as session:
            channel=session.get(ChannelConnection,channel_id)
            barrier.wait(timeout=25)
            identifier=stage(session,channel=channel,
                external_chat_id='test-r31-customer',
                external_message_id='test-r31-event-one',
                sender_id='test-r31-customer',sender_name='R31 synthetic',
                text='R31 synthetic encrypted event')
            session.commit()
            result.put(('ok',identifier))
    except Exception as exc:
        result.put(('error',type(exc).__name__))
    finally:engine.dispose()


def process_worker(url,job_id,barrier,result):
    engine=engine_for(url)
    try:
        barrier.wait(timeout=25)
        answer=process_one(lambda:Session(engine),job_id)
        result.put(('ok',answer))
    except Exception as exc:
        result.put(('error',type(exc).__name__))
    finally:engine.dispose()


def race(func,url,argument):
    context=mp.get_context('fork')
    barrier=context.Barrier(4)
    results=context.Queue()
    workers=[context.Process(target=func,args=(url,argument,barrier,results)) for _ in range(4)]
    for worker in workers:worker.start()
    outcome=[results.get(timeout=35) for _ in workers]
    for worker in workers:
        worker.join(35)
        assert worker.exitcode==0,(worker.pid,worker.exitcode)
    assert all(x[0]=='ok' for x in outcome),outcome
    return [x[1] for x in outcome]


def main():
    url=os.getenv('DATABASE_URL','')
    engine=engine_for(url)
    if engine.dialect.name!='postgresql':
        raise RuntimeError('R31 concurrency proof REQUIRES a real PostgreSQL instance')
    assert assert_schema_current(engine)
    # This proof uses synthetic-only data in ephemeral CI. Generate a temporary
    # encryption key when none was supplied; never touch a production key.
    if not os.getenv('INTEGRATION_ENCRYPTION_KEY'):
        from cryptography.fernet import Fernet
        os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode('ascii')
    with Session(engine) as session:
        org=Organization(name='R31 isolated PostgreSQL encrypted webhook test')
        session.add(org);session.flush()
        channel=ChannelConnection(organization_id=org.id,name='R31 synthetic PG',
            provider='telegram',mode='live',status='connected')
        session.add(channel);session.commit()
        org_id,channel_id=org.id,channel.id
    try:
        staged=race(stage_worker,url,channel_id)
        assert len(set(staged))==1,staged
        job_id=staged[0]
        with Session(engine) as session:
            job=session.get(InboundJob,job_id)
            assert job.organization_id==org_id
            assert job.status=='queued' and job.duplicates==3
            assert job.encrypted_event is not None
            assert 'synthetic encrypted event' not in job.encrypted_event
        outcomes=race(process_worker,url,job_id)
        assert sorted(outcomes)==[0,0,0,1],outcomes
        with Session(engine) as session:
            job=session.get(InboundJob,job_id)
            assert job.status=='done' and job.encrypted_event is None
            assert job.attempts==1
            conv=session.query(Conversation).filter_by(organization_id=org_id).one()
            assert conv.unread_count==1
            assert session.query(Contact).filter_by(organization_id=org_id).count()==1
            assert session.query(Message).filter_by(organization_id=org_id).count()==1
        print('R31_POSTGRESQL_4_PROCESS_STAGE_AND_4_PROCESS_CLAIM=PASS')
    finally:
        with Session(engine) as session:
            session.query(InboundJob).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Message).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Conversation).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(ContactIdentity).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Contact).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(ChannelConnection).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Organization).filter_by(id=org_id).delete(synchronize_session=False)
            session.commit()
        engine.dispose()


if __name__=='__main__':
    main()
