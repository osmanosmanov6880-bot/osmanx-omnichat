"""R22: no false cancellation, manual retry only for provably rejected POSTs.

All channels are dummy local connectors; no real provider message is sent.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from sqlalchemy import update

from app import db
from app.auth import audit
from app.db import (Organization, Membership, ChannelConnection, Contact,
                    Conversation, Message, OutgoingJob, AuditLog, now)
from app.services import ingest_inbound, process_outbox
from conftest import register


def seed(client, *, email='r22@example.org'):
    me=register(client,email=email)
    org=me['organization']['id']
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=org,provider='telegram',name='R22 test bot',
                             mode='live',status='connected',encrypted_credentials='mock-test-value',
                             external_account_id='r22-bot')
        session.add(ch);session.flush()
        ingest_inbound(session,channel=ch,external_chat_id='r22-chat',
                       external_message_id='r22-first-inbound',sender_id='r22-customer',
                       sender_name='Клиент',text='Здравствуйте, сколько стоит?')
        session.commit()
        c=session.query(Conversation).filter_by(channel_id=ch.id).one()
        conv_id,version=c.id,c.version
    response=client.post('/api/conversations/'+conv_id+'/reply',json={
        'body':'Здравствуйте, всё подскажем.',
        'expected_version':version,'client_nonce':'r22-outbound-nonce'})
    assert response.status_code==201,response.text
    with db.SessionLocal() as session:
        job=session.query(OutgoingJob).filter_by(organization_id=org).one()
        return org,conv_id,job.id,job.message_id,ch.id


def test_cancel_queued_message_before_any_provider_call(client, monkeypatch):
    org,conv_id,job_id,message_id,channel_id=seed(client)
    response=client.post('/api/operations/outbox/'+job_id+'/cancel')
    assert response.status_code==200,response.text
    assert response.json()['status']=='cancelled'
    import app.services as svc
    monkeypatch.setattr(svc,'adapter_for',lambda _: (_ for _ in ()).throw(
        AssertionError('Cancelled message must never leave the server')))
    assert asyncio.run(process_outbox(db.SessionLocal))==0
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,job_id).status=='cancelled'
        assert session.get(Message,message_id).delivery_status=='cancelled'
        audit_row=session.query(AuditLog).filter_by(organization_id=org,action='outbox.cancel_before_send').one()
        assert audit_row.entity_id==job_id
    counts=client.get('/api/operations/overview').json()['outbox']
    assert counts['cancelled']==1 and counts['queued']==0
    rows=client.get('/api/operations/outbox?status=cancelled').json()
    assert len(rows)==1 and rows[0]['status']=='cancelled' and not rows[0]['can_cancel']
    assert client.post('/api/operations/outbox/'+job_id+'/cancel').status_code==409


def test_cannot_cancel_processing_accepted_failed_or_unknown(client):
    org,conv_id,job_id,message_id,channel_id=seed(client)
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        job.status='processing';job.claimed_at=now()
        session.commit()
    assert client.post('/api/operations/outbox/'+job_id+'/cancel').status_code==409
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        job.status='uncertain'
        msg=session.get(Message,message_id)
        msg.delivery_status='uncertain'
        session.commit()
    assert client.post('/api/operations/outbox/'+job_id+'/cancel').status_code==409
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        job.status='done'
        msg=session.get(Message,message_id)
        msg.delivery_status='accepted'
        session.commit()
    assert client.post('/api/operations/outbox/'+job_id+'/cancel').status_code==409


def test_worker_claim_and_cancel_are_mutually_exclusive(client, monkeypatch):
    org,conv_id,job_id,message_id,channel_id=seed(client)
    import app.services as svc
    sent=[]
    class FakeAdapter:
        async def send_message(self,*args):
            sent.append('called')
            await asyncio.sleep(0.05)
            return 'provider-message-r22'
    monkeypatch.setattr(svc,'adapter_for',lambda _:FakeAdapter())
    monkeypatch.setattr(svc,'unseal',lambda _: {'access_token':'test-only'})
    # The worker gets the claim before the cancellation endpoint is called.
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        job.status='processing'
        job.claimed_at=now()
        session.commit()
    cancelled=client.post('/api/operations/outbox/'+job_id+'/cancel')
    assert cancelled.status_code==409
    assert sent==[]
    with db.SessionLocal() as session:
        assert session.get(Message,message_id).delivery_status=='queued'


def test_concurrent_compare_and_swap_cancel_and_claim_exactly_one_wins(client):
    org,conv_id,job_id,message_id,channel_id=seed(client)
    barrier=Barrier(2)
    def action(state):
        with db.SessionLocal() as session:
            barrier.wait(timeout=5)
            result=session.execute(update(OutgoingJob).where(
                OutgoingJob.id==job_id,OutgoingJob.organization_id==org,
                OutgoingJob.status=='queued').values(status=state)).rowcount
            session.commit()
            return result
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(action,s) for s in ('cancelled','processing')]
        assert sorted(f.result(timeout=10) for f in futures)==[0,1]
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,job_id).status in ('cancelled','processing')


def test_retry_only_after_explicit_4xx_and_human_verification(client):
    org,conv_id,job_id,message_id,channel_id=seed(client)
    url='/api/operations/outbox/'+job_id+'/retry-verified'
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id);job.status='failed';job.last_error='API 403: Проверка прав'
        session.get(Message,message_id).delivery_status='failed'
        session.commit()
    view=client.get('/api/operations/outbox').json()[0]
    assert view['can_retry_verified'] is True
    false=client.post(url,json={'verified_not_delivered':False,'evidence':'Проверено на площадке вручную'})
    assert false.status_code==422
    short=client.post(url,json={'verified_not_delivered':True,'evidence':'short'})
    assert short.status_code==422
    spaces=client.post(url,json={'verified_not_delivered':True,'evidence':'                    '})
    assert spaces.status_code==422
    yes=client.post(url,json={'verified_not_delivered':True,
                               'evidence':'Проверил исходный чат; сообщение отсутствует'})
    assert yes.status_code==200,yes.text
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        assert job.status=='queued' and job.attempts==0 and job.last_error is None
        assert session.get(Message,message_id).delivery_status=='queued'
        log=session.query(AuditLog).filter_by(action='outbox.retry_after_verified_refusal',organization_id=org).one()
        assert log.entity_id==job_id
    assert client.post(url,json={'verified_not_delivered':True,
                                  'evidence':'Проверил исходный чат; сообщение отсутствует'}).status_code==409


def test_uncertain_manually_reconciled_failed_still_cannot_retry(client):
    org,conv_id,job_id,message_id,channel_id=seed(client)
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id);job.status='uncertain'
        session.get(Message,message_id).delivery_status='uncertain';session.commit()
    resolved=client.post('/api/operations/outbox/'+job_id+'/resolve',json={
        'status':'failed','evidence':'Доставка не обнаружена в панели'})
    assert resolved.status_code==200,resolved.text
    response=client.post('/api/operations/outbox/'+job_id+'/retry-verified',json={
        'verified_not_delivered':True,'evidence':'Проверено в исходном мессенджере'})
    assert response.status_code==409
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,job_id).status=='failed'
    assert client.get('/api/operations/outbox').json()[0]['can_retry_verified'] is False


def test_cannot_retry_ambiguous_errors_or_already_accepted_message(client):
    org,conv_id,job_id,message_id,channel_id=seed(client)
    url='/api/operations/outbox/'+job_id+'/retry-verified'
    for text in ('API 500: uncertainty','API 408: timeout','API 409: unknown',
                 'Неожиданная ошибка отправки', 'API 429: rate limited'):
        with db.SessionLocal() as session:
            job=session.get(OutgoingJob,job_id);job.status='failed';job.last_error=text
            msg=session.get(Message,message_id);msg.delivery_status='failed';msg.external_id=None
            session.commit()
        response=client.post(url,json={'verified_not_delivered':True,'evidence':'Проверено вручную: не доставлено'})
        assert response.status_code==409,text
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id);job.status='failed';job.last_error='API 400: rejected'
        msg=session.get(Message,message_id);msg.external_id='provider-earlier-id'
        session.commit()
    assert client.post(url,json={'verified_not_delivered':True,
                  'evidence':'Проверено вручную: не доставлено'}).status_code==409


def test_operator_and_lead_privilege_boundary(client):
    org,conv_id,job_id,message_id,channel_id=seed(client)
    with db.SessionLocal() as session:
        membership=session.query(Membership).filter_by(organization_id=org).first()
        membership.role='operator';session.commit()
    assert client.post('/api/operations/outbox/'+job_id+'/cancel').status_code==403
    with db.SessionLocal() as session:
        membership=session.query(Membership).filter_by(organization_id=org).first()
        membership.role='lead';session.commit()
    assert client.post('/api/operations/outbox/'+job_id+'/retry-verified',json={
        'verified_not_delivered':True,'evidence':'Проверил исходный чат, не доставлено'}).status_code==403
    assert client.post('/api/operations/outbox/'+job_id+'/cancel').status_code==200


def test_cross_tenant_jobs_never_can_be_cancelled_or_retried(client):
    org,conv_id,job_id,message_id,channel_id=seed(client)
    with db.SessionLocal() as session:
        other=Organization(name='Чужой бизнес')
        session.add(other);session.flush()
        foreign_channel=ChannelConnection(organization_id=other.id,provider='telegram',
            name='Private',mode='live',status='connected')
        foreign_contact=Contact(organization_id=other.id,name='Private contact')
        session.add_all([foreign_channel,foreign_contact]);session.flush()
        foreign_conv=Conversation(organization_id=other.id,channel_id=foreign_channel.id,
              contact_id=foreign_contact.id,external_chat_id='external-private')
        session.add(foreign_conv);session.flush()
        foreign_msg=Message(organization_id=other.id,conversation_id=foreign_conv.id,
                            direction='out',body='Чужой ответ',delivery_status='queued')
        session.add(foreign_msg);session.flush()
        foreign_job=OutgoingJob(organization_id=other.id,message_id=foreign_msg.id,
                                channel_id=foreign_channel.id,status='queued')
        session.add(foreign_job);session.commit()
        secret_id=foreign_job.id
    assert client.post('/api/operations/outbox/'+secret_id+'/cancel').status_code==404
    assert client.post('/api/operations/outbox/'+secret_id+'/retry-verified',json={
        'verified_not_delivered':True,'evidence':'Проверено в исходной площадке'}).status_code==404
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,secret_id).status=='queued'
        assert session.get(Message,foreign_msg.id).body=='Чужой ответ'
    listed=client.get('/api/operations/outbox?status=queued').json()
    assert not any(row['id']==secret_id for row in listed)


def test_verified_retry_flows_through_worker_once_with_local_adapter(client,monkeypatch):
    org,conv_id,job_id,message_id,channel_id=seed(client)
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id);job.status='failed';job.last_error='API 403: отказ площадки'
        session.get(Message,message_id).delivery_status='failed'
        session.commit()
    verified=client.post('/api/operations/outbox/'+job_id+'/retry-verified',json={
        'verified_not_delivered':True,
        'evidence':'Сообщение не найдено в исходном сервисе, причина исправлена'})
    assert verified.status_code==200,verified.text
    import app.services as service
    outgoing=[]
    class FakeAdapter:
        async def send_message(self,credentials,channel,conv,body):
            outgoing.append((channel.id,body))
            return 'r22-provider-confirmed-0001'
    monkeypatch.setattr(service,'adapter_for',lambda provider: FakeAdapter())
    monkeypatch.setattr(service,'unseal',lambda _: {'access_token':'fake-local-only'})
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert asyncio.run(process_outbox(db.SessionLocal))==0
    assert len(outgoing)==1
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        msg=session.get(Message,message_id)
        assert job.status=='done' and msg.delivery_status=='accepted'
        assert msg.external_id=='r22-provider-confirmed-0001'
        assert outgoing[0][0]==channel_id
