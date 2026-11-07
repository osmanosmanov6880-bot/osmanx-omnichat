#!/usr/bin/env python3
"""R34 real PostgreSQL process contention: one inbound channel slot for four workers.

Only run against an isolated PostgreSQL CI database. Not a SQLite simulation.
"""
import multiprocessing as mp
import os
import time
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.db import engine_for, assert_schema_current, Organization, ChannelConnection, InboundJob
from app.inbound_jobs import stage, _claim, _release_channel


def contend(url, job_id, barrier, outcome):
    engine=engine_for(url)
    try:
        barrier.wait(timeout=30)
        token=_claim(lambda:Session(engine),job_id)
        outcome.put(('ok',job_id,token))
    except Exception as exc:
        outcome.put(('error',job_id,type(exc).__name__))
    finally:
        engine.dispose()


def parallel(url, jobs):
    ctx=mp.get_context('fork')
    barrier=ctx.Barrier(len(jobs))
    q=ctx.Queue()
    children=[ctx.Process(target=contend,args=(url,jid,barrier,q)) for jid in jobs]
    for child in children: child.start()
    try:
        rows=[q.get(timeout=90) for _ in children]
    finally:
        for child in children: child.join(timeout=30)
    assert all(child.exitcode==0 for child in children),[(x.pid,x.exitcode) for x in children]
    assert all(x[0]=='ok' for x in rows),rows
    return rows


def main():
    url=os.getenv('DATABASE_URL','')
    engine=engine_for(url)
    if engine.dialect.name!='postgresql':
        raise RuntimeError('Requires PostgreSQL, refuses to treat SQLite as proof')
    assert assert_schema_current(engine)
    if not os.getenv('INTEGRATION_ENCRYPTION_KEY'):
        from cryptography.fernet import Fernet
        os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
    with Session(engine) as s:
        org=Organization(name='Ephemeral R34 SQL slot contention test')
        s.add(org);s.flush()
        c=ChannelConnection(organization_id=org.id,name='Single account',provider='telegram',mode='live',status='connected')
        other=ChannelConnection(organization_id=org.id,name='Independent account',provider='vk',mode='live',status='connected')
        s.add_all([c,other]);s.flush()
        oid,cid,other_id=org.id,c.id,other.id
        ids=[]
        for n in range(4):
            ids.append(stage(s,channel=c,external_chat_id=f'r34-chat-{n}',
                  external_message_id=f'r34-msg-{n}',sender_id=f'r34-sender-{n}',
                  text='Synthetic R34 CI only'))
        other_job=stage(s,channel=other,external_chat_id='r34-independent',
                  external_message_id='r34-independent',sender_id='r34-independent',
                  text='Synthetic CI only')
        s.commit()
    try:
        outcomes=parallel(url,ids)
        winners=[(jid,token) for state,jid,token in outcomes if token]
        assert len(winners)==1,outcomes
        owned_job,owned_token=winners[0]
        independent=_claim(lambda:Session(engine),other_job)
        assert independent is not None,'One slow channel blocked unrelated account'
        with Session(engine) as s:
            assert s.get(ChannelConnection,cid).inbound_processing_token==owned_token
            assert s.query(InboundJob).filter_by(channel_id=cid,status='processing').count()==1
            # Another processor can acquire after a crashed lease expires,
            # but an old token cannot release its new successor's slot.
            s.execute(update(ChannelConnection).where(ChannelConnection.id==cid)
                      .values(inbound_processing_until=time.time()-1))
            s.execute(update(InboundJob).where(InboundJob.id==owned_job)
                      .values(claim_expires_at=time.time()-1))
            s.commit()
        successor=next(j for j in ids if j!=owned_job)
        replacement=_claim(lambda:Session(engine),successor)
        assert replacement and replacement!=owned_token
        with Session(engine) as s:
            assert _release_channel(s,owned_job,owned_token)==0
            s.rollback()
            assert s.get(ChannelConnection,cid).inbound_processing_token==replacement
        print('R34_POSTGRES_FOUR_PROCESSES_FENCED_ACCOUNT_CLAIM=PASS')
    finally:
        with Session(engine) as s:
            s.query(InboundJob).filter_by(organization_id=oid).delete(synchronize_session=False)
            s.query(ChannelConnection).filter_by(organization_id=oid).delete(synchronize_session=False)
            s.query(Organization).filter_by(id=oid).delete(synchronize_session=False)
            s.commit()
        engine.dispose()


if __name__=='__main__':main()
