"""R28 delivery-aware SLA: a draft is not a provider-accepted answer.

All provider adapters are local fakes. The tests assert the real API/SQL semantics,
not delivery via an external social network.
"""
import asyncio
import time
from app import db
from app.db import (Organization, ChannelConnection, Conversation, Contact, Message,
                    OutgoingJob)
from app.integrations.base import AdapterError
from app.services import analytics, ingest_inbound, process_outbox
from conftest import register, start_demo


def _setup_live(client, provider='telegram'):
    owner=register(client)
    org=owner['organization']['id']
    with db.SessionLocal() as session:
        session.get(Organization,org).plan='business'
        session.get(Organization,org).sla_minutes=1
        ch=ChannelConnection(organization_id=org,provider=provider,name='Контроль',mode='live',
            external_account_id='r28-001',status='connected',encrypted_credentials='test-stub')
        session.add(ch);session.flush()
        ingest_inbound(session,channel=ch,external_chat_id='r28-chat',
            external_message_id='r28-in',sender_id='r28-customer',sender_name='Клиент',
            text='Есть свободное время?',timestamp=time.time()-250)
        session.commit()
        c=session.query(Conversation).filter_by(channel_id=ch.id).one()
        return org,c.id,c.version,ch.id


def _reply(client,conv_id,version):
    r=client.post('/api/conversations/'+conv_id+'/reply',json={
        'body':'Здравствуйте, да!', 'expected_version':version,
        'client_nonce':'r28-reply-idempotency'})
    assert r.status_code==201,r.text
    return r.json()['message']['id']


def test_queued_outgoing_is_not_a_successful_answer_across_all_three_views(client):
    org,conv,version,_=_setup_live(client)
    mid=_reply(client,conv,version)
    api=client.get('/api/analytics').json()
    assert api['no_response']==1
    assert api['sla_overdue']==1
    assert api['outgoing_pending']==1
    assert api['outgoing_attention']==0
    assert api['avg_first_reply_min'] is None
    assert api['avg_first_reply_basis']=='verified_since_r28'
    alerts=client.get('/api/alerts').json()
    assert alerts['unanswered_over_sla']==1
    command=client.get('/api/command-center').json()
    assert command['overdue']==1 and command['waiting']==1
    with db.SessionLocal() as session:
        assert session.get(Message,mid).response_confirmed_at is None
        assert session.get(Message,mid).delivery_status=='queued'


def test_provider_success_stamps_actual_acceptance_time_and_clears_sla(client,monkeypatch):
    org,conv,version,_=_setup_live(client)
    mid=_reply(client,conv,version)
    with db.SessionLocal() as session:
        created=session.get(Message,mid).created_at
    import app.services as services
    class FakeProvider:
        async def send_message(self,*args):
            return 'provider-accepted-r28'
    monkeypatch.setattr(services,'adapter_for',lambda p:FakeProvider())
    monkeypatch.setattr(services,'unseal',lambda _: {'access_token':'local-only'})
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    with db.SessionLocal() as session:
        row=session.get(Message,mid)
        assert row.delivery_status=='accepted'
        assert row.external_id=='provider-accepted-r28'
        assert created<=row.response_confirmed_at<=time.time()+1
    stats=client.get('/api/analytics').json()
    assert stats['no_response']==0 and stats['sla_overdue']==0
    assert stats['outgoing_pending']==0 and stats['outgoing_attention']==0
    assert stats['avg_first_reply_min']>=3.0
    assert client.get('/api/alerts').json()['unanswered_over_sla']==0
    command=client.get('/api/command-center').json()
    assert command['overdue']==0 and command['waiting']==0


def test_known_failure_and_uncertain_post_never_hide_unanswered_sla(client,monkeypatch):
    _org,conv,version,_ch=_setup_live(client)
    mid=_reply(client,conv,version)
    import app.services as services
    class FakeProvider:
        async def send_message(self,*args):
            raise AdapterError('API 403 rejected this message',retriable=False)
    monkeypatch.setattr(services,'adapter_for',lambda _:FakeProvider())
    monkeypatch.setattr(services,'unseal',lambda _: {'access_token':'local-only'})
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    stats=client.get('/api/analytics').json()
    assert stats['no_response']==1 and stats['sla_overdue']==1
    assert stats['outgoing_pending']==0 and stats['outgoing_attention']==1
    assert client.get('/api/alerts').json()['unanswered_over_sla']==1
    assert client.get('/api/command-center').json()['overdue']==1
    with db.SessionLocal() as session:
        assert session.get(Message,mid).response_confirmed_at is None


def test_legacy_unverified_accepted_does_not_invent_a_provider_ack(client):
    org,cid,version,_=_setup_live(client)
    mid=_reply(client,cid,version)
    with db.SessionLocal() as session:
        message=session.get(Message,mid)
        job=session.query(OutgoingJob).filter_by(message_id=mid).one()
        message.delivery_status='accepted'
        job.status='done'
        session.commit()
    stat=client.get('/api/analytics').json()
    assert stat['no_response']==1 and stat['sla_overdue']==1
    assert stat['outgoing_pending']==0
    assert stat['avg_first_reply_min'] is None


def test_legacy_delivered_has_status_evidence_but_no_fabricated_duration(client):
    _org,cid,version,_=_setup_live(client)
    mid=_reply(client,cid,version)
    with db.SessionLocal() as session:
        session.get(Message,mid).delivery_status='delivered'
        session.query(OutgoingJob).filter_by(message_id=mid).one().status='done'
        session.commit()
    stat=client.get('/api/analytics').json()
    assert stat['no_response']==0 and stat['sla_overdue']==0
    assert stat['avg_first_reply_min'] is None


def test_next_inbound_reopens_sla_even_after_earlier_verified_reply(client,monkeypatch):
    org,cid,version,chid=_setup_live(client)
    mid=_reply(client,cid,version)
    with db.SessionLocal() as session:
        row=session.get(Message,mid)
        row.created_at=time.time()-240
        row.response_confirmed_at=time.time()-230
        row.delivery_status='accepted'
        session.query(OutgoingJob).filter_by(message_id=mid).one().status='done'
        channel=session.get(ChannelConnection,chid)
        ingest_inbound(session,channel=channel,external_chat_id='r28-chat',
            external_message_id='r28-second-in',sender_id='r28-customer',
            sender_name='Клиент',text='А есть на завтра?',timestamp=time.time()-180)
        session.commit()
    stat=client.get('/api/analytics').json()
    assert stat['no_response']==1 and stat['sla_overdue']==1
    assert client.get('/api/command-center').json()['overdue']==1


def test_tenant_isolation_for_pending_and_confirmed_response_metrics(client):
    org,cid,version,chid=_setup_live(client)
    _reply(client,cid,version)
    with db.SessionLocal() as session:
        other=Organization(name='Другая компания',plan='business')
        session.add(other);session.flush()
        ch=ChannelConnection(organization_id=other.id,provider='telegram',name='Чужой',
                             external_account_id='r28-other',mode='live',status='connected')
        contact=Contact(organization_id=other.id,name='Другая переписка')
        session.add_all([ch,contact]);session.flush()
        conv=Conversation(organization_id=other.id,channel_id=ch.id,contact_id=contact.id,
                          external_chat_id='other-chat',last_inbound_at=time.time()-1000)
        session.add(conv);session.flush()
        for n in range(5):
            message=Message(organization_id=other.id,conversation_id=conv.id,
                            direction='out',body='Только у другой компании',
                            delivery_status='queued',created_at=time.time()-2)
            session.add(message);session.flush()
            session.add(OutgoingJob(organization_id=other.id,channel_id=ch.id,message_id=message.id))
        session.commit()
    stat=client.get('/api/analytics').json()
    assert stat['outgoing_pending']==1 and stat['no_response']==1
    assert stat['inbound']==1


def test_demo_inbox_has_verified_response_times_for_demo_not_as_external(client):
    demo=start_demo(client)
    with db.SessionLocal() as session:
        stats=analytics(session,demo['organization']['id'])
        assert stats['data_source']=='demo'
        assert stats['avg_first_reply_min'] is not None
        assert stats['avg_first_reply_min']>=0
        assert stats['avg_first_reply_basis']=='verified_since_r28'


def test_website_accepted_is_not_displayed_until_visitor_receipt(client):
    from test_website import site,visitor,send
    owner=register(client)
    with db.SessionLocal() as session:
        session.get(Organization,owner['organization']['id']).plan='business'
        session.commit()
    widget=site(client)
    token=visitor(client,widget)
    assert send(client,widget,token).status_code==201
    conv=client.get('/api/conversations').json()[0]
    r=client.post('/api/conversations/'+conv['id']+'/reply',json={
        'body':'Ответ на сайте','expected_version':conv['version'],
        'client_nonce':'r28-website-reply'})
    assert r.status_code==201,r.text
    outgoing_id=r.json()['message']['id']
    assert r.json()['message']['delivery_status']=='accepted'
    assert r.json()['message']['response_confirmed_at'] is None
    assert client.get('/api/analytics').json()['no_response']==1
    receipt=client.post('/api/public/widget/'+widget['key']+'/receipts',
        headers={'X-Widget-Session':token},json={'message_ids':[outgoing_id]})
    assert receipt.status_code==200 and receipt.json()['confirmed']==1
    with db.SessionLocal() as session:
        msg=session.get(Message,outgoing_id)
        assert msg.delivery_status=='delivered'
        assert msg.response_confirmed_at is not None
    assert client.get('/api/analytics').json()['no_response']==0
    assert client.get('/api/analytics').json()['avg_first_reply_min']>=0
    assert client.post('/api/public/widget/'+widget['key']+'/receipts',
        headers={'X-Widget-Session':token},json={'message_ids':[outgoing_id]}).json()['confirmed']==0


def test_website_other_visitor_receipt_cannot_earn_sla_credit(client):
    from test_website import site,visitor,send
    owner=register(client)
    widget=site(client)
    alice=visitor(client,widget,'Алиса')
    bob=visitor(client,widget,'Боб')
    assert send(client,widget,alice,body='Мой вопрос',nonce='r28-visitor-a').status_code==201
    conv=client.get('/api/conversations').json()[0]
    response=client.post('/api/conversations/'+conv['id']+'/reply',json={
        'body':'Алиса, привет','expected_version':conv['version'],
        'client_nonce':'r28-operator-website'})
    mid=response.json()['message']['id']
    receipt=client.post('/api/public/widget/'+widget['key']+'/receipts',
        headers={'X-Widget-Session':bob},json={'message_ids':[mid]})
    assert receipt.status_code==200 and receipt.json()['confirmed']==0
    with db.SessionLocal() as session:
        msg=session.get(Message,mid)
        assert msg.response_confirmed_at is None
        assert msg.delivery_status=='accepted'


def test_signed_whatsapp_delivery_reconciliation_records_proof_once(client):
    from app.provider_receipts import record_whatsapp_receipt,reconcile_whatsapp_receipt
    org,cid,version,chid=_setup_live(client,provider='whatsapp')
    mid=_reply(client,cid,version)
    with db.SessionLocal() as session:
        message=session.get(Message,mid)
        message.external_id='wamid.r28-test-provider'
        session.flush()
        channel=session.get(ChannelConnection,chid)
        assert record_whatsapp_receipt(session,channel,'wamid.r28-test-provider','delivered','r28-customer')
        assert reconcile_whatsapp_receipt(session,chid,'wamid.r28-test-provider')
        session.query(OutgoingJob).filter_by(message_id=mid).one().status='done'
        session.commit()
        msg=session.get(Message,mid)
        assert msg.delivery_status=='delivered'
        first_time=msg.response_confirmed_at
        assert first_time is not None
        assert record_whatsapp_receipt(session,channel,'wamid.r28-test-provider','read','r28-customer')
        assert reconcile_whatsapp_receipt(session,chid,'wamid.r28-test-provider')
        session.commit()
        assert session.get(Message,mid).response_confirmed_at==first_time
        assert session.get(Message,mid).delivery_status=='read'
    assert client.get('/api/analytics').json()['no_response']==0


def test_r27_to_r28_migration_preserves_real_records_without_fake_acceptance(tmp_path):
    import os
    import sqlite3
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    import subprocess
    import sys
    from pathlib import Path
    from app.db import assert_schema_current,engine_for
    project=Path(__file__).resolve().parents[2]
    database=tmp_path/'r27-with-existing-inbox.db'
    env=dict(os.environ,DATABASE_URL=f'sqlite:///{database}',PYTHONPATH='backend')
    command=[sys.executable,'-m','alembic','-c','backend/alembic.ini','upgrade']
    subprocess.run(command+['f27000a10001'],cwd=project,env=env,check=True,capture_output=True)
    with sqlite3.connect(database) as sql:
        sql.execute('INSERT INTO organizations(id,name,plan,is_demo,retention_days,sla_minutes,currency,timezone,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                    ('old-org','Компания до R28','business',0,365,5,'RUB','UTC',1234.0))
        sql.execute('INSERT INTO channel_connections(id,organization_id,provider,name,mode,status,created_at) VALUES(?,?,?,?,?,?,?)',
                    ('old-channel','old-org','telegram','Сохранённый канал','live','connected',1234.0))
        sql.execute('INSERT INTO contacts(id,organization_id,name,tags,stage,deal_confirmed,created_at) VALUES(?,?,?,?,?,?,?)',
                    ('old-contact','old-org','Клиент','[]','new',0,1234.0))
        sql.execute('INSERT INTO conversations(id,organization_id,channel_id,contact_id,external_chat_id,status,priority,pinned,archived,unread_count,version,last_message_at,last_inbound_at,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    ('old-conv','old-org','old-channel','old-contact','legacy-chat','new','normal',0,0,0,0,1234.0,1220.0,1200.0))
        sql.execute('INSERT INTO messages(id,organization_id,conversation_id,direction,kind,body,delivery_status,is_demo,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                    ('old-msg','old-org','old-conv','out','text','Старый принятый ответ','accepted',0,1234.0))
        sql.execute('INSERT INTO outgoing_jobs(id,organization_id,message_id,channel_id,status,attempts,next_attempt_at,created_at) VALUES(?,?,?,?,?,?,?,?)',
                    ('old-job','old-org','old-msg','old-channel','done',1,1234.0,1234.0))
        sql.commit()
    subprocess.run(command+['head'],cwd=project,env=env,check=True,capture_output=True)
    with sqlite3.connect(database) as sql:
        assert sql.execute('SELECT name FROM organizations WHERE id="old-org"').fetchone()==('Компания до R28',)
        assert sql.execute('SELECT name FROM channel_connections WHERE id="old-channel"').fetchone()==('Сохранённый канал',)
        assert sql.execute('SELECT body,delivery_status,response_confirmed_at FROM messages WHERE id="old-msg"').fetchone()==('Старый принятый ответ','accepted',None)
        assert sql.execute('SELECT status FROM outgoing_jobs WHERE id="old-job"').fetchone()==('done',)
        assert sql.execute('SELECT version_num FROM alembic_version').fetchone()==(ScriptDirectory.from_config(Config(str(project/'backend/alembic.ini'))).get_current_head(),)
    engine=engine_for(env['DATABASE_URL'])
    try:assert assert_schema_current(engine)
    finally:engine.dispose()
