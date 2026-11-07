#!/usr/bin/env python3
"""Real PostgreSQL-only R35 tenant fairness + four independent repair processes.

This is a CI-only scenario. It refuses SQLite and remote PostgreSQL endpoints.
"""
import multiprocessing as mp
import os
import time
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.db import (engine_for, assert_schema_current, Organization,
    ChannelConnection, InboundJob, Message, Conversation, ContactIdentity, Contact)
from app.inbound_jobs import stage, process_batch, _claim
from app.inbound_maintenance import repair_expired


def repair_worker(url, org_id, barrier, result):
    engine=engine_for(url)
    try:
        barrier.wait(timeout=30)
        with Session(engine) as db:
            row=repair_expired(db,org_id)
            db.commit()
        result.put(('ok',row['retrying'],row['expired_slots_released']))
    except Exception as exc:
        result.put(('error',type(exc).__name__))
    finally:
        engine.dispose()


def main():
    url=os.getenv('DATABASE_URL','')
    if 'localhost' not in url and '127.0.0.1' not in url:
        raise RuntimeError('R35 multi-process integration must run on an isolated LOCAL PostgreSQL CI database')
    engine=engine_for(url)
    if engine.dialect.name!='postgresql':
        raise RuntimeError('R35 real PostgreSQL integration refuses SQLite simulation')
    assert assert_schema_current(engine)
    if not os.getenv('INTEGRATION_ENCRYPTION_KEY'):
        from cryptography.fernet import Fernet
        os.environ['INTEGRATION_ENCRYPTION_KEY']=Fernet.generate_key().decode()
    with Session(engine) as db:
        big=Organization(name='R35 isolated large tenant')
        tiny=Organization(name='R35 isolated small tenant')
        db.add_all([big,tiny]);db.flush()
        orgs=(big.id,tiny.id)
        for idx in range(7):
            channel=ChannelConnection(organization_id=big.id,name='Many '+str(idx),
                 provider='telegram',mode='live',status='connected')
            db.add(channel);db.flush()
            stage(db,channel=channel,external_chat_id='r35-big-chat-'+str(idx),
                  external_message_id='r35-big-msg-'+str(idx),
                  sender_id='r35-big-user-'+str(idx),text='Synthetic CI payload')
        small_channel=ChannelConnection(organization_id=tiny.id,name='Small tenant',
            provider='telegram',mode='live',status='connected')
        db.add(small_channel);db.flush()
        small_job=stage(db,channel=small_channel,external_chat_id='r35-small-chat',
            external_message_id='r35-small-msg',sender_id='r35-small-user',
            text='Synthetic CI payload')
        db.commit()
    try:
        factory=lambda:Session(engine)
        assert process_batch(factory,limit=1)==1
        assert process_batch(factory,limit=1)==1
        with Session(engine) as db:
            assert db.get(InboundJob,small_job).status=='done', 'Large tenant starved small one'
            assert db.query(InboundJob).filter_by(organization_id=orgs[0],status='done').count()==1
            assert all(db.get(Organization,x).inbound_last_dispatched_at for x in orgs)
        with Session(engine) as db:
            channel=ChannelConnection(organization_id=orgs[1],name='R35 repair race',
                 provider='vk',mode='live',status='connected')
            db.add(channel);db.flush()
            expired=stage(db,channel=channel,external_chat_id='r35-race',
                 external_message_id='r35-race',sender_id='r35-race',text='Synthetic CI')
            channel_id=channel.id
            db.commit()
        token=_claim(factory,expired)
        assert token
        with Session(engine) as db:
            db.execute(update(ChannelConnection).where(ChannelConnection.id==channel_id)
                .values(inbound_processing_until=time.time()-3))
            db.execute(update(InboundJob).where(InboundJob.id==expired)
                .values(claim_expires_at=time.time()-3))
            db.commit()
        ctx=mp.get_context('fork')
        barrier=ctx.Barrier(4)
        output=ctx.Queue()
        children=[ctx.Process(target=repair_worker,args=(url,orgs[1],barrier,output)) for _ in range(4)]
        for process in children: process.start()
        try:
            outcomes=[output.get(timeout=90) for _ in children]
        finally:
            for process in children:process.join(timeout=30)
        assert all(p.exitcode==0 for p in children),[(p.pid,p.exitcode) for p in children]
        assert all(x[0]=='ok' for x in outcomes),outcomes
        assert sum(x[1] for x in outcomes)==1,outcomes
        assert sum(x[2] for x in outcomes)==1,outcomes
        with Session(engine) as db:
            assert db.get(InboundJob,expired).status=='retrying'
            assert db.get(ChannelConnection,channel_id).inbound_processing_token is None
        print('R35_POSTGRES_TENANT_FAIRNESS_AND_FOUR_WORKER_REPAIR=PASS')
    finally:
        with Session(engine) as db:
            for klass in (Message, ContactIdentity, Conversation, Contact, InboundJob,ChannelConnection,Organization):
                db.query(klass).filter(klass.organization_id.in_(orgs) if klass!=Organization
                    else klass.id.in_(orgs)).delete(synchronize_session=False)
            db.commit()
        engine.dispose()

if __name__=='__main__':main()
