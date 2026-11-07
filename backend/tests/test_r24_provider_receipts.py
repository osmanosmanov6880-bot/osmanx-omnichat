"""R24: WhatsApp status callbacks are durable across outbox races.

Only signed local mock webhooks and fake API transports. No provider account
approval, real network or delivery guarantee is claimed by these tests.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import hashlib
import hmac
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

from app import db
from app.db import (Organization, ChannelConnection, Contact, Conversation,
                    Message, OutgoingJob, ProviderDeliveryReceipt, now)
from app.services import ingest_inbound, process_outbox
from app.provider_receipts import (record_whatsapp_receipt, reconcile_whatsapp_receipt)
from conftest import register


def _signed_status(client,phone_id,external_id,status,recipient=None,secret=b'test-webhook-secret'):
    row={'id':external_id,'status':status}
    if recipient is not None:
        row['recipient_id']=recipient
    payload={'object':'whatsapp_business_account','entry':[{'changes':[{'value':{
        'metadata':{'phone_number_id':phone_id},'statuses':[row]}}]}]}
    raw=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    signature=hmac.new(secret,raw,hashlib.sha256).hexdigest()
    return client.post('/api/webhooks/whatsapp',content=raw,headers={
        'X-Hub-Signature-256':'sha256='+signature,'Content-Type':'application/json'})


def _setup(client,phone_id='7111001',recipient='79001112233'):
    owner=register(client,email='r24-'+phone_id+'@example.org')
    org_id=owner['organization']['id']
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=org_id,provider='whatsapp',
            name='WhatsApp test',external_account_id=phone_id,mode='live',
            status='connected',encrypted_credentials='mocked')
        session.add(channel);session.flush()
        ingest_inbound(session,channel=channel,external_chat_id=recipient,
            external_message_id='inbound-'+phone_id,sender_id=recipient,
            sender_name='Test visitor',text='Здравствуйте')
        session.commit()
        conv=session.query(Conversation).filter_by(channel_id=channel.id).one()
        conv_id,version,channel_id=conv.id,conv.version,channel.id
    result=client.post('/api/conversations/'+conv_id+'/reply',json={
        'body':'Ответ из OSMANX','expected_version':version,
        'client_nonce':'r24-nonce-'+phone_id})
    assert result.status_code==201,result.text
    return org_id,conv_id,channel_id,result.json()['message']['id']


def _accepted_by_api(message_id,provider_id,channel_id):
    with db.SessionLocal() as session:
        item=session.get(Message,message_id)
        item.external_id=provider_id
        item.delivery_status='accepted'
        task=session.query(OutgoingJob).filter_by(message_id=item.id).one()
        task.status='done'
        session.commit()


def test_early_receipt_survives_until_outbox_api_response(client,monkeypatch):
    org,conv,channel_id,message_id=_setup(client)
    assert _signed_status(client,'7111001','wamid.early-r24','delivered','79001112233').status_code==200
    with db.SessionLocal() as session:
        assert session.get(Message,message_id).delivery_status=='queued'
        receipt=session.get(ProviderDeliveryReceipt,(channel_id,'wamid.early-r24'))
        assert receipt.status=='delivered'
        assert receipt.recipient_digest and '79001112233' not in str(receipt.__dict__)

    import app.services as svc
    monkeypatch.setattr(svc,'unseal',lambda _:{'access_token':'local-test'})
    class FakeProvider:
        calls=0
        async def send_message(self,*args):
            self.calls+=1
            return 'wamid.early-r24'
    adapter=FakeProvider()
    monkeypatch.setattr(svc,'adapter_for',lambda _:adapter)
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert adapter.calls==1
    with db.SessionLocal() as session:
        item=session.get(Message,message_id)
        assert item.delivery_status=='delivered'
        assert item.external_id=='wamid.early-r24'
        assert session.query(OutgoingJob).filter_by(message_id=message_id).one().status=='done'


def test_receipt_after_ack_is_applied_immediately(client):
    org,conv,channel_id,message_id=_setup(client)
    _accepted_by_api(message_id,'wamid.late-r24',channel_id)
    response=_signed_status(client,'7111001','wamid.late-r24','read','79001112233')
    assert response.status_code==200,response.text
    with db.SessionLocal() as session:
        assert session.get(Message,message_id).delivery_status=='read'
        assert session.get(ProviderDeliveryReceipt,(channel_id,'wamid.late-r24')).status=='read'


def test_out_of_order_duplicated_receipts_never_downgrade_read(client):
    org,conv,channel_id,message_id=_setup(client)
    _accepted_by_api(message_id,'wamid.reorder-r24',channel_id)
    for status in ['delivered','sent','read','failed','sent','read']:
        assert _signed_status(client,'7111001','wamid.reorder-r24',status,'79001112233').status_code==200
    with db.SessionLocal() as session:
        assert session.query(ProviderDeliveryReceipt).filter_by(channel_id=channel_id).count()==1
        assert session.get(ProviderDeliveryReceipt,(channel_id,'wamid.reorder-r24')).status=='read'
        assert session.get(Message,message_id).delivery_status=='read'


def test_failure_receipt_can_be_replaced_by_later_valid_delivery(client):
    org,conv,channel_id,message_id=_setup(client)
    _accepted_by_api(message_id,'wamid.failed-r24',channel_id)
    assert _signed_status(client,'7111001','wamid.failed-r24','sent').status_code==200
    assert _signed_status(client,'7111001','wamid.failed-r24','failed').status_code==200
    with db.SessionLocal() as session:
        assert session.get(Message,message_id).delivery_status=='failed'
    assert _signed_status(client,'7111001','wamid.failed-r24','delivered').status_code==200
    with db.SessionLocal() as session:
        assert session.get(Message,message_id).delivery_status=='delivered'


def test_wrong_recipient_cannot_bind_even_with_matching_external_id(client):
    org,conv,channel_id,message_id=_setup(client)
    _accepted_by_api(message_id,'wamid.wrong-recipient',channel_id)
    assert _signed_status(client,'7111001','wamid.wrong-recipient','read','wrong-recipient').status_code==200
    with db.SessionLocal() as session:
        assert session.get(Message,message_id).delivery_status=='accepted'
    # Same provider ID but conflicting recipient: never overwrite the original
    # digest, even when the later message otherwise has a stronger status.
    assert _signed_status(client,'7111001','wamid.wrong-recipient','delivered','79001112233').status_code==200
    with db.SessionLocal() as session:
        assert session.get(Message,message_id).delivery_status=='accepted'
        receipt=session.get(ProviderDeliveryReceipt,(channel_id,'wamid.wrong-recipient'))
        assert receipt.status=='read'


def test_receipt_does_not_match_other_tenant_even_same_provider_id(client):
    org,conv,channel_id,message_id=_setup(client)
    _accepted_by_api(message_id,'wamid.identical-r24',channel_id)
    with db.SessionLocal() as session:
        other_org=Organization(name='Другая компания',plan='business')
        session.add(other_org);session.flush()
        other_ch=ChannelConnection(organization_id=other_org.id,provider='whatsapp',
            external_account_id='7111002',name='Other WABA',mode='live',status='connected')
        other_contact=Contact(organization_id=other_org.id,name='Other visitor')
        session.add_all([other_ch,other_contact]);session.flush()
        other_conv=Conversation(organization_id=other_org.id,channel_id=other_ch.id,
            contact_id=other_contact.id,external_chat_id='79005556677',
            external_recipient_id='79005556677')
        session.add(other_conv);session.flush()
        other_msg=Message(organization_id=other_org.id,conversation_id=other_conv.id,
            direction='out',body='Не чужое',external_id='wamid.identical-r24',
            delivery_status='accepted')
        session.add(other_msg);session.commit()
        other_msg_id=other_msg.id
        other_channel_id=other_ch.id
    assert _signed_status(client,'7111002','wamid.identical-r24','delivered','79005556677').status_code==200
    with db.SessionLocal() as session:
        assert session.get(Message,other_msg_id).delivery_status=='delivered'
        assert session.get(Message,message_id).delivery_status=='accepted'
        assert session.query(ProviderDeliveryReceipt).filter_by(channel_id=channel_id).count()==0
        assert session.query(ProviderDeliveryReceipt).filter_by(channel_id=other_channel_id).count()==1


def test_invalid_signature_and_unknown_status_are_not_saved(client):
    org,conv,channel_id,message_id=_setup(client)
    assert _signed_status(client,'7111001','wamid.invalid','read',secret=b'bad-hmac').status_code==403
    assert _signed_status(client,'7111001','wamid.invalid','new-unknown-status').status_code==200
    assert _signed_status(client,'7111001','wamid.invalid','read',recipient='x'*300).status_code==200
    with db.SessionLocal() as session:
        assert session.query(ProviderDeliveryReceipt).count()==0


def test_receipts_are_bounded_and_deleted_by_retention_cleanup(client):
    org,conv,channel_id,message_id=_setup(client)
    assert _signed_status(client,'7111001','wamid.stale-r24','sent','79001112233').status_code==200
    with db.SessionLocal() as session:
        receipt=session.get(ProviderDeliveryReceipt,(channel_id,'wamid.stale-r24'))
        receipt.last_seen_at=now()-35*86400
        session.commit()
    from app.extras import purge_expired
    with db.SessionLocal() as session:
        purge_expired(session)
        assert session.get(ProviderDeliveryReceipt,(channel_id,'wamid.stale-r24')) is None
        assert session.get(Message,message_id) is not None


def test_simultaneous_upserts_keep_strongest_delivery_status(client):
    org,conv,channel_id,message_id=_setup(client)
    with db.SessionLocal() as session:
        _accepted_by_api(message_id,'wamid.concurrent-r24',channel_id)
    barrier=Barrier(2)
    def record(status):
        barrier.wait(timeout=5)
        with db.SessionLocal() as session:
            channel=session.get(ChannelConnection,channel_id)
            result=record_whatsapp_receipt(session,channel,'wamid.concurrent-r24',status,'79001112233')
            session.commit()
        return result
    with ThreadPoolExecutor(max_workers=2) as executor:
        results=list(executor.map(record,['read','sent']))
    assert all(results)
    with db.SessionLocal() as session:
        assert session.get(ProviderDeliveryReceipt,(channel_id,'wamid.concurrent-r24')).status=='read'
        assert reconcile_whatsapp_receipt(session,channel_id,'wamid.concurrent-r24')
        session.commit()
        assert session.get(Message,message_id).delivery_status=='read'


def test_migration_preserves_existing_tenant_and_outbound(tmp_path):
    project=Path(__file__).resolve().parents[2]
    path=tmp_path/'old-r23.db'
    env=dict(os.environ,DATABASE_URL=f'sqlite:///{path}',PYTHONPATH='backend')
    subprocess.run([sys.executable,'-m','alembic','-c','backend/alembic.ini',
        'upgrade','f23000a10001'],cwd=project,env=env,check=True,capture_output=True)
    with sqlite3.connect(path) as conn:
        conn.execute('''INSERT INTO organizations (id,name,plan,is_demo,retention_days,sla_minutes,currency,timezone,created_at)
             VALUES (?,?,?,?,?,?,?,?,?)''',('legacy-r23','Компания R23','starter',0,365,5,'RUB','UTC',1234.0))
        conn.commit()
    subprocess.run([sys.executable,'-m','alembic','-c','backend/alembic.ini',
        'upgrade','head'],cwd=project,env=env,check=True,capture_output=True)
    with sqlite3.connect(path) as conn:
        assert conn.execute('SELECT name FROM organizations WHERE id=?',('legacy-r23',)).fetchone()==('Компания R23',)
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        cfg=Config(str(project/'backend/alembic.ini'))
        cfg.set_main_option('script_location',str(project/'backend/alembic'))
        assert conn.execute('SELECT version_num FROM alembic_version').fetchone()[0] == ScriptDirectory.from_config(cfg).get_current_head()
        assert conn.execute('SELECT count(*) FROM provider_delivery_receipts').fetchone()==(0,)


def test_org_deletion_removes_own_receipts_but_keeps_other_company(client):
    org,conv,channel_id,message_id=_setup(client)
    _signed_status(client,'7111001','wamid.will-delete','sent','79001112233')
    with db.SessionLocal() as session:
        other_org=Organization(name='Другая компания',plan='business')
        session.add(other_org);session.flush()
        other_ch=ChannelConnection(organization_id=other_org.id,provider='whatsapp',
            external_account_id='7111002',name='WABA B',mode='live',status='connected')
        session.add(other_ch);session.flush()
        record_whatsapp_receipt(session,other_ch,'wamid.keep','read','79008887766')
        session.commit()
        other_ch_id=other_ch.id
    response=client.post('/api/organization/delete',json={'confirmation':'Компания'})
    assert response.status_code==200,response.text
    with db.SessionLocal() as session:
        assert session.query(ProviderDeliveryReceipt).filter_by(organization_id=org).count()==0
        assert session.query(ProviderDeliveryReceipt).filter_by(channel_id=other_ch_id).count()==1
        assert session.get(ChannelConnection,channel_id) is None
