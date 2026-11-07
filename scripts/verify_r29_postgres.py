#!/usr/bin/env python3
"""R29 actual PostgreSQL concurrent inbound and read-version CAS.

Requires migrated ephemeral PostgreSQL (DATABASE_URL) and SQLAlchemy psycopg.
The only messages are synthetic; no live social network is contacted.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.db import (engine_for, assert_schema_current, Organization,
                    ChannelConnection, Contact, Conversation, Message, now)
from app.services import ingest_inbound


def main():
    engine=engine_for()
    if engine.dialect.name!='postgresql':
        raise RuntimeError('R29 concurrency test requires a real PostgreSQL DATABASE_URL')
    assert assert_schema_current(engine)
    with Session(engine) as session:
        org=Organization(name='R29 isolated PostgreSQL concurrency test')
        session.add(org);session.flush()
        channel=ChannelConnection(organization_id=org.id,provider='telegram',
            name='R29 test sender',mode='live',status='connected')
        contact=Contact(organization_id=org.id,name='Synthetic visitor')
        session.add_all([channel,contact]);session.flush()
        last=now()-100
        conv=Conversation(organization_id=org.id,channel_id=channel.id,
            contact_id=contact.id,external_chat_id='r29-pg-conversation',
            external_recipient_id='r29-synthetic-user',status='new',
            unread_count=1,version=10,last_inbound_at=last,last_message_at=last)
        session.add(conv);session.commit()
        org_id,channel_id,conv_id,contact_id=org.id,channel.id,conv.id,contact.id

    before=now()
    barrier=Barrier(4)
    def sender(index):
        with Session(engine) as session:
            # Force all four database sessions to hold *stale* ORM snapshots.
            cached=session.get(Conversation,conv_id)
            assert cached.unread_count==1 and cached.version==10
            channel=session.get(ChannelConnection,channel_id)
            barrier.wait(timeout=15)
            ingest_inbound(session,channel=channel,
                external_chat_id='r29-pg-conversation',
                external_message_id=f'r29-pg-event-{index}',
                sender_id='r29-synthetic-user',sender_name='Test visitor',
                text=f'Independent event {index}',timestamp=before-index*5)
            session.commit()
            return True
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            assert all(pool.map(sender,range(4)))
        with Session(engine) as session:
            c=session.get(Conversation,conv_id)
            assert c.unread_count==5 and c.version==14,(c.unread_count,c.version)
            assert c.last_inbound_at==before
            assert c.last_message_at==before
            assert session.query(Message).filter_by(conversation_id=conv_id).count()==4
            # Old read snapshot must not erase one of the four new messages.
            changed=session.execute(update(Conversation).where(
                Conversation.id==conv_id,Conversation.organization_id==org_id,
                Conversation.version==10).values(unread_count=0,
                    version=Conversation.version+1)).rowcount
            assert changed==0
            session.rollback()
            assert session.get(Conversation,conv_id).unread_count==5
            current=session.get(Conversation,conv_id)
            changed=session.execute(update(Conversation).where(
                Conversation.id==conv_id,Conversation.organization_id==org_id,
                Conversation.version==14).values(unread_count=0,
                    version=Conversation.version+1)).rowcount
            assert changed==1
            session.commit()
            session.refresh(current)
            assert current.unread_count==0 and current.version==15
        print('R29_POSTGRESQL_PARALLEL_INBOUND_AND_READ_CAS=PASS')
    finally:
        with Session(engine) as session:
            session.query(Message).filter_by(conversation_id=conv_id).delete()
            session.query(Conversation).filter_by(id=conv_id).delete()
            session.query(Contact).filter_by(id=contact_id).delete()
            session.query(ChannelConnection).filter_by(id=channel_id).delete()
            session.query(Organization).filter_by(id=org_id).delete()
            session.commit()
        engine.dispose()


if __name__=='__main__':main()
