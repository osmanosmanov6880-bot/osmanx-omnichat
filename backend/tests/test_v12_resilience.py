"""V1.2: atomically reserved webhooks, strict tenant outbox, bounded SQL metrics."""
import asyncio
import hashlib
import hmac
import json
import time
from sqlalchemy import func
from app import db
from app.db import (Organization,ChannelConnection,Contact,Conversation,Message,
                    OutgoingJob,WebhookEvent)
from app.services import process_outbox
from app.webhooks import reserve_event
from conftest import register,start_demo


def test_webhook_receipt_insert_is_atomic_and_rollback_allows_retry(client):
    register(client,email='webhook-receipts@example.org')
    with db.SessionLocal() as session:
        assert reserve_event(session,'instagram','duplicate-event-1') is True
        assert reserve_event(session,'instagram','duplicate-event-1') is False
        session.rollback()  # webhook processor crashed before ingest commit
    with db.SessionLocal() as session:
        assert reserve_event(session,'instagram','duplicate-event-1') is True
        session.commit()
    with db.SessionLocal() as session:
        assert reserve_event(session,'instagram','duplicate-event-1') is False
        assert reserve_event(session,'messenger','duplicate-event-1') is True
        session.commit()
        assert session.query(WebhookEvent).count() == 2


def test_signed_meta_duplicate_webhook_has_one_message_and_one_receipt(client):
    owner=register(client,email='hmac-v12@example.org')
    with db.SessionLocal() as session:
        session.add(ChannelConnection(organization_id=owner['organization']['id'],
            provider='instagram',name='Official test',external_account_id='account-84',
            mode='live',status='connected'))
        session.commit()
    payload={'object':'instagram','entry':[{'id':'account-84','messaging':[
        {'sender':{'id':'visitor-23'},'recipient':{'id':'account-84'},
         'timestamp':int(time.time()*1000),'message':{'mid':'same-event-882','text':'Здравствуйте!'}}]}]}
    raw=json.dumps(payload).encode()
    signature='sha256='+hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
    for expected in (1,0,0):
        result=client.post('/api/webhooks/instagram',content=raw,
            headers={'X-Hub-Signature-256':signature})
        assert result.status_code==200,result.text
        assert result.json()['accepted']==expected
    with db.SessionLocal() as session:
        assert session.query(Message).filter_by(organization_id=owner['organization']['id']).count()==1
        assert session.query(WebhookEvent).filter_by(provider='instagram').count()==1


def test_corrupt_cross_company_job_never_sends_foreign_message(client,monkeypatch):
    owner=register(client,email='outbox-v12@example.org')
    org_a=owner['organization']['id']
    with db.SessionLocal() as session:
        org_b=Organization(name='Другой бизнес',plan='business')
        session.add(org_b);session.flush()
        bad_message=Message(organization_id=org_b.id,conversation_id='',direction='out',
                            body='Чужой секрет',delivery_status='queued')
        a_ch=ChannelConnection(organization_id=org_a,provider='telegram',name='One',
                               status='connected',mode='live',encrypted_credentials='dummy')
        b_ch=ChannelConnection(organization_id=org_b.id,provider='telegram',name='Two',
                               status='connected',mode='live',encrypted_credentials='dummy2')
        a_contact=Contact(organization_id=org_a,name='Первый')
        b_contact=Contact(organization_id=org_b.id,name='Второй')
        session.add_all([a_ch,b_ch,a_contact,b_contact]);session.flush()
        a_conv=Conversation(organization_id=org_a,channel_id=a_ch.id,contact_id=a_contact.id,
                            external_chat_id='111')
        b_conv=Conversation(organization_id=org_b.id,channel_id=b_ch.id,contact_id=b_contact.id,
                            external_chat_id='222')
        session.add_all([a_conv,b_conv]);session.flush()
        bad_message.conversation_id=b_conv.id
        session.add(bad_message);session.flush()
        job=OutgoingJob(organization_id=org_a,message_id=bad_message.id,channel_id=a_ch.id)
        session.add(job);session.commit()
        job_id=job.id; message_id=bad_message.id
    import app.services as service
    monkeypatch.setattr(service,'adapter_for',lambda _: (_ for _ in ()).throw(
        AssertionError('NO foreign provider call is allowed')))
    assert asyncio.run(process_outbox(db.SessionLocal))==0
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        assert job.status=='failed'
        assert session.get(Message,message_id).body=='Чужой секрет'
        assert session.get(Message,message_id).delivery_status=='queued'


def test_ops_summary_counts_tenant_only_and_sanitizes_channel(client):
    owner=register(client,email='ops-v12@example.org')
    org_a=owner['organization']['id']
    with db.SessionLocal() as session:
        org_b=Organization(name='Чужая компания')
        session.add(org_b);session.flush()
        for org_id,channel_name in [(org_a,'Личный канал'),(org_b.id,'Посторонний канал')]:
            channel=ChannelConnection(organization_id=org_id,provider='telegram',name=channel_name,
                                      mode='live',status='connected',last_error='Секретная причина')
            contact=Contact(organization_id=org_id,name='Тест')
            session.add_all([channel,contact]);session.flush()
            conv=Conversation(organization_id=org_id,channel_id=channel.id,
                              contact_id=contact.id,external_chat_id=org_id)
            session.add(conv);session.flush()
            for i in range(30 if org_id==org_b.id else 2):
                session.add(Message(organization_id=org_id,conversation_id=conv.id,
                    direction='in',body=f'Тест {i}',is_demo=False))
        session.commit()
    result=client.get('/api/operations/overview')
    assert result.status_code==200,result.text
    data=result.json()
    assert data['messages_total']==2 and data['conversations_total']==1
    assert data['channel_total']==1 and data['live_connected_count']==1
    assert len(data['channels'])==1
    assert data['channels'][0]['name']=='Личный канал'
    assert 'encrypted_credentials' not in str(data)
    assert data['channels_truncated'] is False


def test_analytics_uses_sql_counts_without_loading_all_message_entities(client):
    owner=start_demo(client)
    oid=owner['organization']['id']
    with db.SessionLocal() as session:
        ch=session.query(ChannelConnection).filter_by(organization_id=oid).first()
        conv=session.query(Conversation).filter_by(channel_id=ch.id).first()
        for n in range(70):
            session.add(Message(organization_id=oid,conversation_id=conv.id,
                                direction='in',body='Историческое сообщение',
                                created_at=time.time()-90*86400-n, is_demo=True))
        session.commit()
    with db.SessionLocal() as session:
        from app.services import analytics
        result=analytics(session,oid)
        assert result['inbound'] >= 70
        assert len(result['days'])==7
        assert result['data_source']=='demo'
        # The SQL aggregation must not materialize every message ORM object.
        assert sum(isinstance(obj,Message) for obj in session.identity_map.values())==0


def test_concurrent_webhook_reservations_accept_one_event(client):
    """Two independent DB sessions racing for the same message identity."""
    from concurrent.futures import ThreadPoolExecutor
    import threading
    gate=threading.Barrier(2)
    def reserve():
        with db.SessionLocal() as session:
            gate.wait(timeout=4)
            got=reserve_event(session,'telegram','race-unique-999')
            time.sleep(.08)
            session.commit()
            return got
    with ThreadPoolExecutor(max_workers=2) as pool:
        a=pool.submit(reserve)
        b=pool.submit(reserve)
        results=[a.result(timeout=5),b.result(timeout=5)]
    assert sorted(results)==[False,True]
    with db.SessionLocal() as session:
        assert session.query(WebhookEvent).filter_by(fingerprint='race-unique-999').count()==1


def test_unknown_delivery_is_visible_even_after_hundreds_of_successful_sends(client):
    owner=register(client,email='stale-jobs@example.org')
    oid=owner['organization']['id']
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=oid,provider='telegram',name='Outbox test',
                             mode='live',status='connected')
        contact=Contact(organization_id=oid,name='Клиент')
        session.add_all([ch,contact]);session.flush()
        conv=Conversation(organization_id=oid,channel_id=ch.id,
                          contact_id=contact.id,external_chat_id='test')
        session.add(conv);session.flush()
        for i in range(130):
            message=Message(organization_id=oid,conversation_id=conv.id,direction='out',body=str(i))
            session.add(message);session.flush()
            session.add(OutgoingJob(organization_id=oid,message_id=message.id,channel_id=ch.id,
                status='uncertain' if i==0 else 'done',created_at=time.time()+i))
        session.commit()
    summary=client.get('/api/operations/overview')
    assert summary.status_code==200 and summary.json()['reconciliation_required']==1
    page=client.get('/api/operations/outbox')
    assert page.status_code==200 and len(page.json())==100
    assert page.json()[0]['status']=='uncertain'
    assert all(row['status']=='done' for row in page.json()[1:])
    assert client.get('/api/operations/outbox?status=uncertain').json()[0]['status']=='uncertain'


def test_two_workers_cannot_claim_the_same_outbound_reply(client,monkeypatch):
    owner=register(client,email='parallel-workers@example.org')
    org=owner['organization']['id']
    from app.services import ingest_inbound
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=org,provider='telegram',name='Outgoing queue',
                                  mode='live',status='connected',encrypted_credentials='mocked',
                                  external_account_id='test-bot')
        session.add(channel);session.flush()
        ingest_inbound(session,channel=channel,external_chat_id='44444',
            external_message_id='in-123',sender_id='123',sender_name='Клиент',text='Добрый день')
        session.commit()
        conversation=session.query(Conversation).filter_by(channel_id=channel.id).one()
        conv_id,version=conversation.id,conversation.version
    response=client.post('/api/conversations/'+conv_id+'/reply',json={
        'body':'Здравствуйте!', 'expected_version':version,'client_nonce':'single-send-worker-race'})
    assert response.status_code==201,response.text
    import app.services as service
    calls=[]
    class FakeAdapter:
        async def send_message(self,*args):
            calls.append('send')
            await asyncio.sleep(.035)
            return 'provider-ack-1'
    monkeypatch.setattr(service,'adapter_for',lambda _: FakeAdapter())
    monkeypatch.setattr(service,'unseal',lambda _: {'access_token':'fake'})
    async def race():
        return await asyncio.gather(process_outbox(db.SessionLocal),process_outbox(db.SessionLocal))
    assert sum(asyncio.run(race()))==1
    assert calls==['send']
    with db.SessionLocal() as session:
        assert session.query(OutgoingJob).one().status=='done'
