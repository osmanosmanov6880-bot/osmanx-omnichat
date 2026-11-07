#!/usr/bin/env python3
"""R27 actual PostgreSQL independent-OS-process sender serialization.

Run *only* with migrated ephemeral PostgreSQL and fake provider adapters:
  DATABASE_URL=postgresql+psycopg://... PYTHONPATH=backend python scripts/verify_r27_postgres.py

Requires two spawned Python processes, separate DB connections and a
blocked provider call. This script never sends a real social API request.
"""
from __future__ import annotations

import asyncio
import multiprocessing
import os
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from sqlalchemy.orm import sessionmaker
from app.db import (engine_for, ChannelDispatchLease, ChannelConnection,
                    Organization, Contact, Conversation, Message, OutgoingJob, uid, now)


def _connection_factory():
    engine=engine_for()
    return engine,sessionmaker(bind=engine,expire_on_commit=False,autoflush=False)


def contender(channel,org,token,ready,signal,events):
    from app.channel_dispatch import reserve
    engine,factory=_connection_factory()
    try:
        ready.put(token)
        if not signal.wait(10):
            events.put(('error',token,'start_timeout'))
            return
        result=reserve(factory,channel,org,token)
        events.put(('claim',token,result))
    except Exception as exc:
        events.put(('error',token,type(exc).__name__))
    finally:
        engine.dispose()


def worker(name,started,unblock,events,*,hold=False):
    import app.services as svc
    engine,factory=_connection_factory()
    try:
        svc.unseal=lambda _: {'access_token':'local-fake-only'}
        class Provider:
            async def send_message(self,credentials,channel,conv,text):
                events.put(('send',name,text))
                if hold:
                    started.set()
                    await asyncio.to_thread(unblock.wait,10)
                return 'postgres-local-accepted-'+uid()
        svc.adapter_for=lambda _:Provider()
        result=asyncio.run(svc.process_outbox(factory))
        events.put(('processed',name,result))
    except Exception as exc:
        events.put(('error',name,type(exc).__name__))
    finally:
        engine.dispose()


def main():
    url=os.getenv('DATABASE_URL','')
    if not url.startswith(('postgresql+psycopg://','postgresql://')):
        raise SystemExit('R27 PostgreSQL test requires a real PostgreSQL URL')
    engine,factory=_connection_factory()
    if engine.dialect.name!='postgresql':
        raise SystemExit('R27 PostgreSQL test refuses a non-PostgreSQL driver')
    from app.db import assert_schema_current
    assert_schema_current(engine)
    try:
        with factory() as session:
            org=Organization(name='R27 CI sender slot process test')
            session.add(org);session.flush()
            channel=ChannelConnection(organization_id=org.id,provider='telegram',
                name='R27 CI test sender',mode='live',status='connected')
            contact=Contact(organization_id=org.id,name='R27 CI customer')
            session.add_all([channel,contact]);session.flush()
            conv=Conversation(organization_id=org.id,channel_id=channel.id,
                contact_id=contact.id,external_chat_id='r27-pg-chat',
                last_inbound_at=now())
            session.add(conv);session.flush()
            for n in (1,2):
                msg=Message(organization_id=org.id,conversation_id=conv.id,
                    direction='out',body='CI answer '+str(n),delivery_status='queued')
                session.add(msg);session.flush()
                session.add(OutgoingJob(organization_id=org.id,message_id=msg.id,
                    channel_id=channel.id,status='queued',created_at=now()+n*.001))
            session.commit()
            channel_id,org_id=channel.id,org.id

        ctx=multiprocessing.get_context('spawn')
        ready=ctx.Queue();events=ctx.Queue();signal=ctx.Event()
        processes=[ctx.Process(target=contender,args=(channel_id,org_id,who,ready,signal,events))
                   for who in ('first','second')]
        for proc in processes:proc.start()
        assert {ready.get(timeout=12) for _ in processes}=={'first','second'}
        signal.set()
        claims=[events.get(timeout=12) for _ in processes]
        for proc in processes:
            proc.join(12)
            assert proc.exitcode==0,proc.exitcode
        assert all(row[0]=='claim' for row in claims),claims
        assert sum(int(row[2]) for row in claims)==1,claims
        with factory() as session:
            item=session.get(ChannelDispatchLease,channel_id)
            assert item.owner_token in ('first','second')
            item.expires_at=0
            session.commit()

        started=ctx.Event();unblock=ctx.Event();events=ctx.Queue()
        first=ctx.Process(target=worker,args=('first',started,unblock,events),kwargs={'hold':True})
        first.start()
        assert started.wait(12),'First process never reached fake provider'
        second=ctx.Process(target=worker,args=('second',started,unblock,events))
        second.start();second.join(12)
        assert second.exitcode==0
        # The first POST is still waiting; a parallel worker cannot send a
        # different reply via the same account even with separate DB sessions.
        # Exactly two events are expected before unblocking A. Queue.empty()
        # is unreliable across processes; wait for the concrete events.
        interim=[events.get(timeout=8) for _ in range(2)]
        assert ('processed','second',0) in interim,interim
        assert sum(1 for row in interim if row[0]=='send')==1,interim
        unblock.set();first.join(12)
        assert first.exitcode==0
        third=ctx.Process(target=worker,args=('third',started,unblock,events))
        third.start();third.join(12)
        assert third.exitcode==0
        events_list=interim+[events.get(timeout=8) for _ in range(3)]
        assert ('processed','first',1) in events_list,events_list
        assert ('processed','third',1) in events_list,events_list
        assert len([e for e in events_list if e[0]=='send'])==2,events_list
        with factory() as session:
            assert session.query(OutgoingJob).filter_by(organization_id=org_id,status='done').count()==2
            assert session.get(ChannelDispatchLease,channel_id).expires_at==0
        print('R27_POSTGRES_MULTIPROCESS_SENDER_SLOTS=PASS')
        print('R27_POSTGRES_SENDS=2_NO_OVERLAP')
    finally:
        engine.dispose()


if __name__=='__main__':
    main()
