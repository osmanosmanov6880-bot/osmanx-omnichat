"""R29: concurrent inbound webhook safety and snapshot-based read receipts.

SQLite local verification; independent PostgreSQL process test is in scripts.
These tests use real FastAPI/SQLAlchemy, not live provider accounts.
"""
import time

from app import db
from app.db import ChannelConnection, Contact, Conversation, Message
from app.services import ingest_inbound
from conftest import register


def _base(client):
    user=register(client)
    org=user['organization']['id']
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=org,name='R29 тестовый Telegram',
            provider='telegram',mode='live',status='connected',external_account_id='r29-local-only')
        contact=Contact(organization_id=org,name='Тестовый покупатель')
        session.add_all([channel,contact]);session.flush()
        clock=time.time()
        conv=Conversation(organization_id=org,channel_id=channel.id,contact_id=contact.id,
            external_chat_id='r29-dialog',external_recipient_id='r29-user',
            unread_count=2,version=4,last_message_at=clock-180,
            last_inbound_at=clock-180,status='waiting')
        session.add(conv);session.commit()
        return org,channel.id,conv.id


def _ingest(session, channel_id, event_id, timestamp=None, history=False):
    return ingest_inbound(session,channel=session.get(ChannelConnection,channel_id),
        external_chat_id='r29-dialog',external_message_id=event_id,
        sender_id='r29-user',sender_name='Клиент',text=f'Событие {event_id}',
        timestamp=timestamp,history=history)


def test_two_stale_sqlalchemy_sessions_do_not_lose_inbound_counts(client):
    org,chid,cid=_base(client)
    now=time.time()
    with db.SessionLocal() as stale:
        stale_row=stale.get(Conversation,cid)
        assert stale_row.unread_count==2
        with db.SessionLocal() as first:
            _ingest(first,chid,'newer',timestamp=now-20)
            first.commit()
        # Strong reference keeps the old ORM snapshot (version=4, unread=2).
        assert stale_row.unread_count==2
        _ingest(stale,chid,'older',timestamp=now-50)
        stale.commit()
    with db.SessionLocal() as check:
        conv=check.get(Conversation,cid)
        assert conv.unread_count==4
        assert conv.version==6
        assert conv.last_inbound_at==now-20
        assert conv.last_message_at==now-20
        assert check.query(Message).filter_by(conversation_id=cid).count()==2


def test_history_backfill_never_adds_unread_and_never_rewinds_last_event(client):
    _,chid,cid=_base(client)
    with db.SessionLocal() as s:
        before=s.get(Conversation,cid)
        last=before.last_inbound_at
        _ingest(s,chid,'historic',timestamp=last-3600,history=True)
        s.commit()
    with db.SessionLocal() as s:
        conv=s.get(Conversation,cid)
        assert conv.unread_count==2
        assert conv.version==5
        assert conv.last_inbound_at==last
        assert conv.last_message_at==last


def test_replayed_inbound_same_external_id_is_idempotent(client):
    _,chid,cid=_base(client)
    with db.SessionLocal() as s:
        _ingest(s,chid,'same')
        s.commit()
    with db.SessionLocal() as s:
        msg=_ingest(s,chid,'same')
        assert msg is not None
        s.commit()
    with db.SessionLocal() as s:
        assert s.get(Conversation,cid).unread_count==3
        assert s.get(Conversation,cid).version==5
        assert s.query(Message).filter_by(conversation_id=cid).count()==1


def test_versioned_read_rejects_stale_snapshot_and_preserves_new_message(client):
    _,chid,cid=_base(client)
    before=client.get(f'/api/conversations/{cid}').json()['conversation']
    with db.SessionLocal() as s:
        _ingest(s,chid,'arrived-after-render')
        s.commit()
    result=client.post(f'/api/conversations/{cid}/read',json={'expected_version':before['version']})
    assert result.status_code==409,result.text
    assert 'новое' in result.json()['detail'].lower()
    with db.SessionLocal() as s:
        assert s.get(Conversation,cid).unread_count==3
    updated=client.get(f'/api/conversations/{cid}').json()['conversation']
    success=client.post(f'/api/conversations/{cid}/read',json={'expected_version':updated['version']})
    assert success.status_code==200 and success.json()['version']==updated['version']+1
    with db.SessionLocal() as s:
        assert s.get(Conversation,cid).unread_count==0


def test_legacy_read_still_supported_but_reads_with_atomic_snapshot(client):
    _,chid,cid=_base(client)
    first=client.post(f'/api/conversations/{cid}/read')
    assert first.status_code==200,first.text
    assert first.json()['version']==5
    with db.SessionLocal() as s:
        _ingest(s,chid,'after-legacy-read')
        s.commit()
        assert s.get(Conversation,cid).unread_count==1
    newer=client.get(f'/api/conversations/{cid}').json()['conversation']['version']
    assert newer==6


def test_unread_endpoint_does_not_overwrite_unread_from_stale_snapshot(client):
    _,chid,cid=_base(client)
    with db.SessionLocal() as stale:
        assert stale.get(Conversation,cid).unread_count==2
        with db.SessionLocal() as other:
            _ingest(other,chid,'concurrent-unread')
            other.commit()
        # The API changes only the field via SQL, preserving all 3 unread.
        response=client.post(f'/api/conversations/{cid}/unread')
        assert response.status_code==200,response.text
        assert response.json()['unread_count']==3
        stale.rollback()
    with db.SessionLocal() as s:
        assert s.get(Conversation,cid).unread_count==3
        assert s.get(Conversation,cid).version==6


def test_tenant_scope_prevents_reading_others_unread(client):
    _,chid,cid=_base(client)
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as foreign:
        assert foreign.post('/api/demo/start').status_code==200
        token=foreign.cookies.get('omnichat_csrf')
        assert foreign.post(f'/api/conversations/{cid}/read',
            json={'expected_version':4},headers={'X-CSRF-Token':token}).status_code==404
        assert foreign.post(f'/api/conversations/{cid}/unread',
            headers={'X-CSRF-Token':token}).status_code==404
    with db.SessionLocal() as s:
        assert s.get(Conversation,cid).unread_count==2


def test_queued_outgoing_does_not_change_inbound_counters(client):
    org,chid,cid=_base(client)
    before=client.get(f'/api/conversations/{cid}').json()['conversation']
    payload={'body':'Ответ из очереди','expected_version':before['version'],'client_nonce':'r29-local-nonce'}
    res=client.post(f'/api/conversations/{cid}/reply',json=payload)
    assert res.status_code==201,res.text
    with db.SessionLocal() as s:
        assert s.get(Conversation,cid).unread_count==2


def test_replayed_webhook_and_new_incoming_only_increment_once_each(client):
    _,chid,cid=_base(client)
    with db.SessionLocal() as s:
        for token in ('a','b','a','c','b'):
            _ingest(s,chid,token)
        s.commit()
    with db.SessionLocal() as s:
        conv=s.get(Conversation,cid)
        assert conv.unread_count==5
        assert conv.version==7
        assert s.query(Message).filter_by(conversation_id=cid).count()==3
