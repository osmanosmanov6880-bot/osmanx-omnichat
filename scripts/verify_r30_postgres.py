#!/usr/bin/env python3
"""R30 real PostgreSQL first-contact races. Only synthetic data, no providers.

Requires DATABASE_URL=postgresql+psycopg://... against migrated ephemeral DB.
Uses four independent SQLAlchemy transactions and barrier-synchronized threads.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy.orm import Session
from app.db import (engine_for, assert_schema_current, Organization,
                    ChannelConnection, Contact, ContactIdentity, Conversation, Message)
from app.services import ingest_inbound


def main():
    engine=engine_for()
    if engine.dialect.name!='postgresql':
        raise RuntimeError('R30 concurrency proof requires a real PostgreSQL instance')
    assert assert_schema_current(engine)
    with Session(engine) as session:
        org=Organization(name='R30 isolated PG first inbound concurrent test')
        session.add(org)
        session.flush()
        channel=ChannelConnection(organization_id=org.id,name='Synthetic R30 test channel',
            provider='telegram',mode='live',status='connected')
        session.add(channel)
        session.commit()
        tenant_id,channel_id=org.id,channel.id

    def race(events, chat, sender):
        barrier=Barrier(len(events))
        def ingest(index):
            with Session(engine) as s:
                ch=s.get(ChannelConnection,channel_id)
                barrier.wait(timeout=25)
                who=sender[index] if isinstance(sender,list) else sender
                msg=ingest_inbound(s,channel=ch,external_chat_id=chat,
                    external_message_id=events[index],sender_id=who,
                    sender_name=who,text='Synthetic concurrent first inbound')
                result=msg.id
                s.commit()
                return result
        with ThreadPoolExecutor(max_workers=len(events)) as pool:
            return list(pool.map(ingest,range(len(events))))

    try:
        messages=race(['a','b','c','d'],'first-visitor-chat','one-visitor')
        assert len(set(messages))==4
        with Session(engine) as s:
            conv=s.query(Conversation).filter_by(organization_id=tenant_id,
                channel_id=channel_id,external_chat_id='first-visitor-chat').one()
            assert conv.unread_count==4 and conv.version==4
            assert s.query(Contact).filter_by(organization_id=tenant_id).count()==1
            assert s.query(ContactIdentity).filter_by(organization_id=tenant_id).count()==1
            assert s.query(Message).filter_by(organization_id=tenant_id).count()==4

        replay=race(['same','same','same'],'duplicated-initial','one-visitor')
        assert len(set(replay))==1, 'Only one persisted row for repeated event'
        with Session(engine) as s:
            duplicated=s.query(Conversation).filter_by(organization_id=tenant_id,
                external_chat_id='duplicated-initial').one()
            assert duplicated.unread_count==1 and duplicated.version==1
            assert s.query(Message).filter_by(conversation_id=duplicated.id).count()==1

        group=race(['event-p1','event-p2'],'group-with-two-participants',
                   ['participant-one','participant-two'])
        assert len(set(group))==2
        with Session(engine) as s:
            grp=s.query(Conversation).filter_by(organization_id=tenant_id,
                external_chat_id='group-with-two-participants').one()
            assert grp.unread_count==2 and grp.version==2
            # The losing speculative contact/identity is discarded; we still
            # have exactly one person for this single external conversation.
            assert s.query(Contact).filter_by(organization_id=tenant_id).count()==2
            assert s.query(ContactIdentity).filter_by(organization_id=tenant_id).count()==2
            assert s.query(Conversation).filter_by(organization_id=tenant_id).count()==3
            assert s.query(Message).filter_by(organization_id=tenant_id).count()==7
        print('R30_POSTGRESQL_FIRST_CONTACT_4_WORKERS_DUPLICATE_GROUP=PASS')
    finally:
        with Session(engine) as s:
            s.query(Message).filter_by(organization_id=tenant_id).delete(synchronize_session=False)
            s.query(Conversation).filter_by(organization_id=tenant_id).delete(synchronize_session=False)
            s.query(ContactIdentity).filter_by(organization_id=tenant_id).delete(synchronize_session=False)
            s.query(Contact).filter_by(organization_id=tenant_id).delete(synchronize_session=False)
            s.query(ChannelConnection).filter_by(organization_id=tenant_id).delete(synchronize_session=False)
            s.query(Organization).filter_by(id=tenant_id).delete(synchronize_session=False)
            s.commit()
        engine.dispose()


if __name__=='__main__':
    main()
