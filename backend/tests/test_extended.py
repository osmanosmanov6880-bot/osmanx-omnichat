"""Extended integration regressions: outbox, WS auth, signatures, retention, media and plan enforcement."""
import asyncio
import hashlib
import hmac
import json
import time
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app import db
from app.db import ChannelConnection, Conversation, Message, OutgoingJob
from app.services import ingest_inbound, process_outbox
from app.extras import purge_expired
from conftest import start_demo, register


def test_readiness_and_static_browser_assets(client):
    assert client.get('/api/health').status_code==200
    ready=client.get('/api/health/ready')
    assert ready.status_code==200 and ready.json()['database']=='ok'
    assert client.get('/').status_code==200
    assert client.get('/assets/app.js').status_code==200
    assert client.get('/assets/vendor/react-fragment-polyfill.js').status_code==200
    assert "type=\"importmap\"" not in client.get('/').text
    assert 'script-src' in client.get('/').headers['Content-Security-Policy']


def test_websocket_auth_origin_and_ready(client):
    start_demo(client)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect('/api/ws',headers={'origin':'https://hostile.example'}) as ws:
            ws.receive_json()
    with client.websocket_connect('/api/ws',headers={'origin':'http://testserver'}) as ws:
        first=ws.receive_json()
        assert first['event']=='ready'


def test_whatsapp_outbox_exactly_once_by_nonce(client, monkeypatch):
    org=register(client)
    import app.services as service
    class FakeProvider:
        def __init__(self):self.sent=[]
        async def send_message(self,credentials,channel,conversation,text):
            self.sent.append((conversation.external_recipient_id,text))
            return 'wamid.fake-delivery-001'
    fake=FakeProvider()
    monkeypatch.setattr(service,'adapter_for',lambda provider:fake)
    monkeypatch.setattr(service,'unseal',lambda _: {'access_token':'mocked'})
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=org['organization']['id'],provider='whatsapp',name='Stub',external_account_id='881181',mode='live',status='connected',encrypted_credentials='mocked')
        session.add(ch);session.flush()
        msg=ingest_inbound(session,channel=ch,external_chat_id='79210010022',external_message_id='webhook-1',sender_id='79210010022',sender_name='Покупатель',text='Можно сегодня?')
        session.commit()
        conv=session.query(Conversation).filter_by(channel_id=ch.id).first()
        conv_id,version=conv.id,conv.version
    body={'body':'Да, сегодня можно','expected_version':version,'client_nonce':'fixed-client-nonce-001'}
    created=client.post('/api/conversations/'+conv_id+'/reply',json=body)
    assert created.status_code==201,created.text
    assert created.json()['message']['delivery_status']=='queued'
    assert client.post('/api/conversations/'+conv_id+'/reply',json=body).json()['duplicate'] is True
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert asyncio.run(process_outbox(db.SessionLocal))==0
    assert fake.sent==[('79210010022','Да, сегодня можно')]
    with db.SessionLocal() as session:
        job=session.query(OutgoingJob).first()
        assert job.status=='done' and job.attempts==1
        outgoing=session.query(Message).filter_by(direction='out').one()
        assert outgoing.delivery_status=='accepted'
        assert outgoing.external_id=='wamid.fake-delivery-001'


def test_instagram_webhook_signature_echo_dedup_and_scope(client):
    org=register(client)
    with db.SessionLocal() as session:
        session.add(ChannelConnection(organization_id=org['organization']['id'],provider='instagram',name='IG account',external_account_id='990101',mode='live',status='connected'))
        session.commit()
    event={'object':'instagram','entry':[{'id':'990101','messaging':[{
        'sender':{'id':'77888'},'recipient':{'id':'990101'},'timestamp':int(time.time()*1000),
        'message':{'mid':'ig-message-123','text':'Добрый день'}},
        {'sender':{'id':'990101'},'message':{'mid':'ig-echo-001','text':'Исходящее','is_echo':True}}
    ]}]}
    raw=json.dumps(event).encode()
    sig='sha256='+hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
    invalid=client.post('/api/webhooks/instagram',content=raw,headers={'X-Hub-Signature-256':'sha256=wrong'})
    assert invalid.status_code==403
    good=client.post('/api/webhooks/instagram',content=raw,headers={'X-Hub-Signature-256':sig})
    assert good.status_code==200 and good.json()['accepted']==1
    duplicate=client.post('/api/webhooks/instagram',content=raw,headers={'X-Hub-Signature-256':sig})
    assert duplicate.status_code==200 and duplicate.json()['accepted']==0
    assert len(client.get('/api/conversations').json())==1
    assert client.get('/api/conversations').json()[0]['contact_name'].startswith('Клиент')


def test_retention_and_separated_revenue(client):
    org=start_demo(client)
    stat=client.get('/api/analytics').json()
    assert 'potential_revenue' in stat and 'confirmed_revenue' in stat
    with db.SessionLocal() as session:
        orgrow=session.get(db.Organization,org['organization']['id'])
        orgrow.retention_days=30
        message=session.query(Message).filter_by(organization_id=orgrow.id).first()
        old_id=message.id
        message.created_at=time.time()-31*86400
        session.commit()
        assert purge_expired(session)>=1
        session.expire_all()  # bulk DELETE bypasses SQLAlchemy identity map
        assert session.get(Message,old_id) is None
    assert client.get('/api/analytics').status_code==200


def test_cross_tenant_attachment_cannot_be_fetched(client):
    me=start_demo(client)
    msg=client.get('/api/conversations/'+client.get('/api/conversations').json()[0]['id']).json()['messages'][0]
    assert client.get('/api/media/'+msg['id']).status_code in (404,422)
    assert client.get('/api/media/not-a-valid-id').status_code==404
