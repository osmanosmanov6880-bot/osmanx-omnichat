#!/usr/bin/env python3
"""R32 PostgreSQL capacity admission and pause/claim race.

Requires a migrated, isolated PostgreSQL database. Runs real OS processes,
not in-memory mocks; never contacts a social-network API.
"""
import multiprocessing as mp
import os
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.db import (engine_for, assert_schema_current, Organization,
    ChannelConnection, InboundJob, Contact, ContactIdentity, Conversation, Message,
    WebhookEvent)
from app.inbound_jobs import stage, process_batch, InboundCapacityExceeded


def stage_proc(url, channel_id, index, barrier, out):
    os.environ['INBOUND_MAX_PENDING_PER_CHANNEL']='2'
    engine=engine_for(url)
    try:
        with Session(engine) as session:
            ch=session.get(ChannelConnection,channel_id)
            barrier.wait(timeout=20)
            try:
                jid=stage(session,channel=ch,external_chat_id=f'r32-synthetic-{index}',
                    external_message_id=f'r32-event-{index}',sender_id=f'r32-synthetic-{index}',
                    text='R32 synthetic encrypted-only event')
                session.commit()
                out.put(('stored',jid))
            except InboundCapacityExceeded:
                session.rollback()
                out.put(('capacity',None))
    except Exception as exc:
        out.put(('error',type(exc).__name__))
    finally:
        engine.dispose()


def retry_proc(url, identifier, barrier, out):
    engine=engine_for(url)
    try:
        barrier.wait(timeout=20)
        with Session(engine) as session:
            changed=session.execute(update(InboundJob).where(
                InboundJob.id==identifier,InboundJob.status=='failed',
                InboundJob.encrypted_event.is_not(None)
            ).values(status='queued',attempts=0)).rowcount
            session.commit()
            out.put(('ok',changed))
    except Exception as exc:
        out.put(('error',type(exc).__name__))
    finally:engine.dispose()


def race(fn,url,job_id):
    context=mp.get_context('fork')
    barrier=context.Barrier(4 if fn is stage_proc else 2)
    result=context.Queue()
    if fn is stage_proc:
        workers=[context.Process(target=fn,args=(url,job_id,n,barrier,result)) for n in range(4)]
    else:
        workers=[context.Process(target=fn,args=(url,job_id,barrier,result)) for _ in range(2)]
    for worker in workers:worker.start()
    outputs=[result.get(timeout=40) for _ in workers]
    for worker in workers:
        worker.join(40)
        assert worker.exitcode==0,(worker.pid,worker.exitcode)
    assert not any(a=='error' for a,_ in outputs),outputs
    return outputs


def main():
    url=os.getenv('DATABASE_URL','')
    engine=engine_for(url)
    if engine.dialect.name!='postgresql':
        raise RuntimeError('PostgreSQL R32 race test requires a running PostgreSQL server')
    assert assert_schema_current(engine)
    if not os.getenv('INTEGRATION_ENCRYPTION_KEY'):
        from cryptography.fernet import Fernet
        os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
    with Session(engine) as session:
        org=Organization(name='R32 ephemeral PostgreSQL stage capacity test',inbound_paused_at=0.1)
        session.add(org);session.flush()
        ch=ChannelConnection(organization_id=org.id,provider='telegram',name='R32 synthetic',mode='live',status='connected')
        session.add(ch);session.commit()
        org_id,channel_id=org.id,ch.id
    try:
        outcomes=race(stage_proc,url,channel_id)
        assert [x[0] for x in outcomes].count('stored')==2,outcomes
        assert [x[0] for x in outcomes].count('capacity')==2,outcomes
        with Session(engine) as session:
            jobs=session.query(InboundJob).filter_by(channel_id=channel_id).all()
            assert len(jobs)==2 and all(j.encrypted_event for j in jobs)
        assert process_batch(lambda:Session(engine))==0
        with Session(engine) as session:
            session.execute(update(Organization).where(Organization.id==org_id).values(inbound_paused_at=None))
            session.commit()
        assert process_batch(lambda:Session(engine))==2
        with Session(engine) as session:
            item=session.query(InboundJob).filter_by(channel_id=channel_id).first()
            # Reproduce one failed job, retain encrypted payload for admin triage
            second=stage(session,channel=session.get(ChannelConnection,channel_id),
                external_chat_id='failed',external_message_id='failed',sender_id='failed',text='test')
            session.execute(update(InboundJob).where(InboundJob.id==second).values(status='failed',attempts=5))
            session.commit()
        results=race(retry_proc,url,second)
        assert sorted(v for _,v in results)==[0,1],results
        print('R32_POSTGRESQL_4_PROCESS_CAPACITY_AND_CAS_RETRY=PASS')
    finally:
        with Session(engine) as session:
            session.query(InboundJob).filter_by(organization_id=org_id).delete(synchronize_session=False)
            # This ephemeral test creates its own provider receipt rows.
            session.query(Message).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Conversation).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(ContactIdentity).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Contact).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(ChannelConnection).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Organization).filter_by(id=org_id).delete(synchronize_session=False)
            session.commit()
        engine.dispose()

if __name__=='__main__': main()
