"""Regression of v1.6-v1.8 mechanisms reconstructed from available v1.5.

Tests are run with ephemeral SQLite and mock provider HTTP, not live channels.
"""
import asyncio
import hashlib
import hmac
import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import httpx
import pytest
from app import db
from app.db import ChannelConnection, Contact, Conversation, Message, OutgoingJob, SchedulerLease
from app.scheduler_lease import acquire, release, renew
from app.integrations.adapters import call, seal
from app.integrations.base import AdapterError
from app.services import ingest_inbound, process_outbox
from conftest import register
from test_website import site, visitor, send


def test_recovered_scheduler_lease_two_workers_and_expiry(client):
    gate=Barrier(2)
    def contender():
        gate.wait(timeout=5)
        return acquire(db.SessionLocal,'avito_sync',seconds=60)
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(contender) for _ in range(2)]
        results=[f.result(timeout=8) for f in jobs]
    owners=[x for x in results if x]
    assert len(owners)==1
    assert not release(db.SessionLocal,'avito_sync','other-worker')
    assert release(db.SessionLocal,'avito_sync',owners[0])
    assert acquire(db.SessionLocal,'avito_sync',seconds=60) is not None


def test_recovered_429_post_stays_retryable_and_explicit(client,monkeypatch):
    real=httpx.AsyncClient
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw:real(transport=httpx.MockTransport(
        lambda request: httpx.Response(429,headers={'Retry-After':'120'})),**kw))
    with pytest.raises(AdapterError) as caught:
        asyncio.run(call('POST','https://example.invalid/wa/messages',json_data={'a':1}))
    error=caught.value
    assert error.rate_limited is True
    assert error.retriable is True
    assert not error.uncertain
    assert error.retry_after==120


def test_recovered_outbox_skips_paused_channel_and_keeps_other_running(client,monkeypatch):
    profile=register(client,email='restore-priority@example.org')
    oid=profile['organization']['id']
    with db.SessionLocal() as session:
        ids=[]
        for label in ('paused','active'):
            ch=ChannelConnection(organization_id=oid,name=label,provider='telegram',
                external_account_id=label,mode='live',status='connected',
                encrypted_credentials=seal({'access_token':'dummy'}),
                rate_limited_until=time.time()+600 if label=='paused' else None)
            contact=Contact(organization_id=oid,name=label)
            session.add_all([ch,contact]);session.flush()
            conv=Conversation(organization_id=oid,channel_id=ch.id,contact_id=contact.id,
                external_chat_id=label)
            session.add(conv);session.flush()
            msg=Message(organization_id=oid,conversation_id=conv.id,
                direction='out',body='Здравствуйте',delivery_status='queued',created_at=time.time())
            session.add(msg);session.flush()
            job=OutgoingJob(organization_id=oid,channel_id=ch.id,message_id=msg.id)
            session.add(job);session.flush()
            ids.append((ch.id,job.id))
        session.commit()
    import app.services as service
    calls=[]
    class FakeProvider:
        async def send_message(self,credentials,channel,conversation,body):
            calls.append(channel.name)
            return 'provider.accepted'
    monkeypatch.setattr(service,'adapter_for',lambda _: FakeProvider())
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert calls==['active']
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,ids[0][1]).status=='queued'
        assert session.get(OutgoingJob,ids[1][1]).status=='done'


def test_recovered_widget_receipt_does_not_ack_another_visitor(client):
    register(client,email='widget-owner-recover@example.org')
    widget=site(client)
    one=visitor(client,widget,'Посетитель 1')
    two=visitor(client,widget,'Посетитель 2')
    assert send(client,widget,one,nonce='nonce-one-good',body='Вопрос 1').status_code==201
    assert send(client,widget,two,nonce='nonce-two-good',body='Вопрос 2').status_code==201
    convs=client.get('/api/conversations').json()
    assert len(convs)==2
    for c in convs:
        if c['contact_name']=='Посетитель 1':first=c
    result=client.post('/api/conversations/'+first['id']+'/reply',json={
        'body':'Ответ первому','expected_version':first['version'], 'client_nonce':'reply-one-unique'})
    assert result.status_code==201,result.text
    msg_id=result.json()['message']['id']
    assert result.json()['message']['delivery_status']=='accepted'
    url=f"/api/public/widget/{widget['key']}/receipts"
    assert client.post(url,headers={'X-Widget-Session':two},json={'message_ids':[msg_id]}).json()['confirmed']==0
    assert client.post(url,headers={'X-Widget-Session':one},json={'message_ids':[msg_id]}).json()['confirmed']==1
    assert client.post(url,headers={'X-Widget-Session':one},json={'message_ids':[msg_id]}).json()['confirmed']==0


def test_recovered_webhook_rejects_large_and_malformed_signed_batch(client):
    reg=register(client,email='webhook-recover@example.org')
    with db.SessionLocal() as session:
        session.add(ChannelConnection(organization_id=reg['organization']['id'],
            name='WA',provider='whatsapp',mode='live',status='connected',external_account_id='101010'))
        session.commit()
    payload={'object':'whatsapp_business_account','entry':[{'changes':[{'value':{
        'metadata':{'phone_number_id':'101010'},'messages':[{'id':str(i)} for i in range(501)]}}]}]}
    raw=json.dumps(payload).encode()
    sig='sha256='+hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
    result=client.post('/api/webhooks/whatsapp',content=raw,headers={'X-Hub-Signature-256':sig})
    assert result.status_code==413,result.text
    with db.SessionLocal() as session:
        assert session.query(Message).count()==0
    payload['entry']=[{'changes':'broken'}]
    raw=json.dumps(payload).encode()
    sig='sha256='+hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
    assert client.post('/api/webhooks/whatsapp',content=raw,headers={'X-Hub-Signature-256':sig}).status_code==422
