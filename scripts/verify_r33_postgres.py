#!/usr/bin/env python3
"""R33 PostgreSQL 16: independent processes, fair claims and competing disposal.

Must run only on an isolated migrated PostgreSQL database. No social API calls.
A successful CI execution must be evidenced separately from local SQLite QA.
"""
import multiprocessing as mp
import os
import time
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.db import (engine_for, assert_schema_current, Organization, ChannelConnection,
    InboundJob, Message, Conversation, ContactIdentity, Contact, WebhookEvent)
from app.inbound_jobs import stage, process_batch


def consume_proc(url, barrier, output):
    engine=engine_for(url)
    try:
        barrier.wait(timeout=25)
        count=0
        for _ in range(7):
            count+=process_batch(lambda:Session(engine),limit=1)
            time.sleep(.025)
        output.put(('ok',count))
    except Exception as exc:
        output.put(('error',type(exc).__name__+':'+str(exc)[:160]))
    finally:
        engine.dispose()


def dispose_proc(url, jid, barrier, output):
    engine=engine_for(url)
    try:
        barrier.wait(timeout=25)
        with Session(engine) as session:
            affected=session.execute(update(InboundJob).where(
                InboundJob.id==jid,InboundJob.status=='failed',
                InboundJob.encrypted_event.is_not(None)
            ).values(status='dismissed',encrypted_event=None,
                     dismissal_code='invalid_event',dismissed_at=time.time())).rowcount
            session.commit()
            output.put(('ok',affected))
    except Exception as exc:
        output.put(('error',type(exc).__name__+':'+str(exc)[:160]))
    finally:
        engine.dispose()


def in_processes(fn,args,count):
    ctx=mp.get_context('fork')
    barrier=ctx.Barrier(count)
    output=ctx.Queue()
    procs=[ctx.Process(target=fn,args=(*args,barrier,output)) for _ in range(count)]
    for proc in procs:proc.start()
    try:
        results=[output.get(timeout=75) for _ in procs]
    finally:
        for proc in procs:proc.join(timeout=30)
    assert all(proc.exitcode==0 for proc in procs),[(p.pid,p.exitcode) for p in procs]
    assert all(label=='ok' for label,_ in results),results
    return [value for _,value in results]


def main():
    url=os.getenv('DATABASE_URL','')
    engine=engine_for(url)
    if engine.dialect.name!='postgresql':
        raise RuntimeError('R33 validation requires live PostgreSQL, not SQLite')
    assert assert_schema_current(engine)
    if not os.getenv('INTEGRATION_ENCRYPTION_KEY'):
        from cryptography.fernet import Fernet
        os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
    with Session(engine) as session:
        org=Organization(name='R33 ephemeral fair inbound queue QA')
        session.add(org);session.flush()
        ch1=ChannelConnection(organization_id=org.id,name='R33 flood',
                              provider='telegram',mode='live',status='connected')
        ch2=ChannelConnection(organization_id=org.id,name='R33 new customer',
                              provider='instagram',mode='live',status='connected')
        session.add_all([ch1,ch2]);session.commit()
        org_id,flood,new=org.id,ch1.id,ch2.id
    try:
        with Session(engine) as session:
            source=session.get(ChannelConnection,flood)
            for idx in range(15):
                stage(session,channel=source,external_chat_id=f'r33-{idx}',
                      external_message_id=f'r33-{idx}',sender_id=f'r33-{idx}',
                      text='Synthetic migration-free test')
            singleton=stage(session,channel=session.get(ChannelConnection,new),
                            external_chat_id='r33-singleton',
                            external_message_id='r33-singleton',
                            sender_id='r33-singleton',text='Test only')
            session.commit()
        # Verify fairness across two sequential 1-slot cycles even with 15
        # earlier events in the other channel.
        assert process_batch(lambda:Session(engine),limit=1)==1
        assert process_batch(lambda:Session(engine),limit=1)==1
        with Session(engine) as session:
            assert session.get(InboundJob,singleton).status=='done'
        scores=in_processes(consume_proc,(url,),4)
        assert sum(scores)>0,scores
        process_batch(lambda:Session(engine),limit=100)
        with Session(engine) as session:
            done=session.query(InboundJob).filter_by(organization_id=org_id,status='done').count()
            assert done==16,done
            count=session.query(Message).filter_by(organization_id=org_id).count()
            assert count==16,count
            channel=session.get(ChannelConnection,flood)
            assert channel.inbound_last_dispatched_at is not None
            to_close=stage(session,channel=channel,
                           external_chat_id='r33-unrecoverable',
                           external_message_id='r33-unrecoverable',
                           sender_id='r33-unrecoverable',text='Encrypted test event')
            session.execute(update(InboundJob).where(InboundJob.id==to_close)
                            .values(status='failed',attempts=5))
            session.commit()
        result=in_processes(dispose_proc,(url,to_close),2)
        assert sorted(result)==[0,1],result
        with Session(engine) as session:
            record=session.get(InboundJob,to_close)
            assert record.status=='dismissed' and record.encrypted_event is None
        print('R33_POSTGRESQL_FAIR_CLAIM_4_PROCESSES_AND_DISPOSITION_CAS=PASS')
    finally:
        with Session(engine) as session:
            jobs=session.query(InboundJob).filter_by(organization_id=org_id).all()
            # Remove synthetic global webhook-reservation keys related only to
            # this ephemeral R33 fixture before removing the tenant.
            import hashlib
            for job in jobs:
                fingerprint=hashlib.sha256(
                    f'r31:{job.channel_id}:{job.fingerprint}'.encode()).hexdigest()
                session.query(WebhookEvent).filter_by(provider=job.provider,
                    fingerprint=fingerprint).delete(synchronize_session=False)
            session.query(InboundJob).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Message).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Conversation).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(ContactIdentity).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Contact).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(ChannelConnection).filter_by(organization_id=org_id).delete(synchronize_session=False)
            session.query(Organization).filter_by(id=org_id).delete(synchronize_session=False)
            session.commit()
        engine.dispose()


if __name__=='__main__':main()
