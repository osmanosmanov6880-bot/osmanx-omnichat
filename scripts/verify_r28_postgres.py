"""R28 real PostgreSQL proof: tenant-isolated delivery-aware metrics.

Runs only when DATABASE_URL points to a migrated PostgreSQL server. Does NOT
contact social networks. Creates synthetic rows and removes all of them.
"""
from sqlalchemy.orm import Session
from app.db import (engine_for, assert_schema_current, Organization, ChannelConnection,
                    Contact, Conversation, Message, OutgoingJob, now)
from app.services import analytics


def main():
    engine=engine_for()
    if engine.dialect.name!='postgresql':
        raise RuntimeError('R28 PostgreSQL verification requires a real PostgreSQL DATABASE_URL')
    assert assert_schema_current(engine)
    try:
        with Session(engine) as session:
            organizations=[]
            conversations=[]
            channels=[]
            contacts=[]
            messages=[]
            jobs=[]
            for index in range(2):
                org=Organization(name=f'R28 PG test tenant {index}',plan='business',sla_minutes=1)
                session.add(org);session.flush();organizations.append(org)
                ch=ChannelConnection(organization_id=org.id,provider='telegram',name='R28 PG test',
                    mode='live',status='connected',external_account_id=f'r28pg-{org.id}')
                contact=Contact(organization_id=org.id,name='Synthetic customer')
                session.add_all([ch,contact]);session.flush();channels.append(ch);contacts.append(contact)
                stamp=now()-300
                conv=Conversation(organization_id=org.id,channel_id=ch.id,contact_id=contact.id,
                    external_chat_id='r28-pg-chat',last_inbound_at=stamp,last_message_at=now()-10)
                session.add(conv);session.flush();conversations.append(conv)
                incoming=Message(organization_id=org.id,conversation_id=conv.id,
                    external_id='r28-in',direction='in',body='Synthetic inbound',
                    created_at=stamp,delivery_status='delivered')
                outgoing=Message(organization_id=org.id,conversation_id=conv.id,
                    external_id='r28-out',direction='out',body='Synthetic response',
                    created_at=now()-10,delivery_status='queued')
                session.add_all([incoming,outgoing]);session.flush();messages.extend([incoming,outgoing])
                job=OutgoingJob(organization_id=org.id,message_id=outgoing.id,channel_id=ch.id,
                                status='queued',next_attempt_at=now())
                session.add(job);session.flush();jobs.append(job)
            session.commit()
            for org in organizations:
                assert analytics(session,org.id)['no_response']==1
                assert analytics(session,org.id)['outgoing_pending']==1
            outgoing=messages[1]
            outgoing.delivery_status='accepted'
            outgoing.response_confirmed_at=now()
            jobs[0].status='done'
            session.commit()
            good=analytics(session,organizations[0].id)
            other=analytics(session,organizations[1].id)
            assert good['no_response']==0 and good['sla_overdue']==0
            assert good['outgoing_pending']==0 and good['avg_first_reply_min'] is not None
            assert other['no_response']==1 and other['outgoing_pending']==1
            # A new inbound after an older *composed* reply reopens the SLA,
            # even if that old reply's API acceptance happened later.
            outgoing.created_at=now()-210
            session.commit()
            new_time=now()-130
            conversations[0].last_inbound_at=new_time
            more=Message(organization_id=organizations[0].id,conversation_id=conversations[0].id,
                direction='in',body='One more question',created_at=new_time)
            session.add(more);messages.append(more);session.commit()
            assert analytics(session,organizations[0].id)['no_response']==1
            # Keep CI DB clean for next independent verification stage.
            for job in jobs:session.delete(job)
            for message in messages:session.delete(message)
            session.flush()
            for conv in conversations:session.delete(conv)
            session.flush()
            for contact in contacts:session.delete(contact)
            for ch in channels:session.delete(ch)
            session.flush()
            for org in organizations:session.delete(org)
            session.commit()
        print('R28_POSTGRESQL_CONFIRMED_RESPONSE_AND_TENANT_ISOLATION=PASS')
    finally:
        engine.dispose()

if __name__=='__main__':main()
