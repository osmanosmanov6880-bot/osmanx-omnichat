"""Non-duplicating delivery when POST outcomes are uncertain or a worker crashes."""
import asyncio
import time
from app import db
from app.db import ChannelConnection, Conversation, Message, OutgoingJob
from app.integrations.base import AdapterError
from app.services import ingest_inbound, process_outbox
from conftest import register


def make_live_queued_reply(client):
    org=register(client)
    org_id=org['organization']['id']
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=org_id,provider='whatsapp',name='Test WABA',external_account_id='771177',mode='live',status='connected',encrypted_credentials='mocked')
        session.add(ch);session.flush()
        ingest_inbound(session,channel=ch,external_chat_id='77090020011',external_message_id='wa-in-1',sender_id='77090020011',sender_name='Tester',text='Можно ответить?')
        session.commit()
        conv=session.query(Conversation).filter_by(channel_id=ch.id).one()
        conv_id,version=conv.id,conv.version
    created=client.post('/api/conversations/'+conv_id+'/reply',json={'body':'Да, можно','expected_version':version,'client_nonce':'nonce-for-uncertain-delivery'})
    assert created.status_code==201,created.text
    with db.SessionLocal() as session:
        job=session.query(OutgoingJob).one()
        return job.id,job.message_id


def test_provider_network_timeout_is_uncertain_and_never_replayed(client,monkeypatch):
    job_id,message_id=make_live_queued_reply(client)
    import app.services as services
    calls=[]
    class TimeoutProvider:
        async def send_message(self,*args):
            calls.append('send')
            raise AdapterError('Запрос мог быть доставлен',uncertain=True)
    monkeypatch.setattr(services,'adapter_for',lambda _:TimeoutProvider())
    monkeypatch.setattr(services,'unseal',lambda _: {'access_token':'mocked'})
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert asyncio.run(process_outbox(db.SessionLocal))==0
    assert calls==['send']
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,job_id).status=='uncertain'
        assert session.get(Message,message_id).delivery_status=='uncertain'
    listing=client.get('/api/operations/outbox?status=uncertain')
    assert listing.status_code==200 and listing.json()[0]['id']==job_id
    assert client.post('/api/operations/outbox/'+job_id+'/resolve',json={
        'status':'accepted','evidence':'Проверено по статусу провайдера','external_id':'wamid.verified'
    }).status_code==200
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,job_id).status=='done'
        assert session.get(Message,message_id).external_id=='wamid.verified'
    assert client.post('/api/operations/outbox/'+job_id+'/resolve',json={
        'status':'failed','evidence':'Повторное изменение запрещено'
    }).status_code==409


def test_orphaned_worker_claim_quarantined_not_retried(client,monkeypatch):
    job_id,message_id=make_live_queued_reply(client)
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        job.status='processing';job.claimed_at=time.time()-250
        session.commit()
    import app.services as services
    class ShouldNotBeCalled:
        async def send_message(self,*args):
            raise AssertionError('A stale in-flight POST must never be replayed')
    monkeypatch.setattr(services,'adapter_for',lambda _:ShouldNotBeCalled())
    assert asyncio.run(process_outbox(db.SessionLocal))==0
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,job_id).status=='uncertain'
        assert session.get(Message,message_id).delivery_status=='uncertain'
