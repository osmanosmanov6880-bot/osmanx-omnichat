"""v1.4 durable worker observability and modern frontend feature gate."""
import asyncio
from app import db
from app.db import (WorkerHeartbeat, Organization, ChannelConnection, Contact,
                    Conversation, Message, OutgoingJob, now)
from app.worker_monitor import (start_worker, pulse, finish_cycle, stop_worker,
                                worker_health, heartbeat_loop)
from conftest import register


def test_worker_is_active_only_after_real_completed_cycle(client):
    with db.SessionLocal() as session:
        assert worker_health(session)['code']=='offline'
    worker_id=start_worker(db.SessionLocal,kind='worker')
    with db.SessionLocal() as session:
        status=worker_health(session)
        assert status['code']=='checking' and status['active'] is True
    finish_cycle(db.SessionLocal,worker_id,processed=4)
    with db.SessionLocal() as session:
        item=session.get(WorkerHeartbeat,worker_id)
        assert item.processed_jobs==4 and item.last_cycle_at is not None
        assert worker_health(session)['code']=='working'
    stop_worker(db.SessionLocal,worker_id)
    with db.SessionLocal() as session:
        assert worker_health(session)['code']=='offline'
        assert session.get(WorkerHeartbeat,worker_id).stopped_at is not None


def test_error_does_not_claim_a_completed_cycle(client):
    wid=start_worker(db.SessionLocal,kind='api')
    finish_cycle(db.SessionLocal,wid,succeeded=False)
    with db.SessionLocal() as session:
        item=session.get(WorkerHeartbeat,wid)
        assert item.error_count==1 and item.last_cycle_at is None
        assert worker_health(session)['code']=='checking'
    finish_cycle(db.SessionLocal,wid,succeeded=True,processed=2)
    with db.SessionLocal() as session:
        assert session.get(WorkerHeartbeat,wid).error_count==0
        assert session.get(WorkerHeartbeat,wid).processed_jobs==2
        assert worker_health(session)['code']=='working'


def test_stale_heartbeat_never_looks_healthy(client):
    wid=start_worker(db.SessionLocal)
    finish_cycle(db.SessionLocal,wid)
    with db.SessionLocal() as session:
        item=session.get(WorkerHeartbeat,wid)
        item.last_seen_at=now()-3600
        item.last_cycle_at=now()-3600
        session.commit()
        assert worker_health(session)['code']=='offline'
        assert worker_health(session)['active'] is False


def test_background_heartbeat_stops_on_cancel(client):
    wid=start_worker(db.SessionLocal)
    async def exercise():
        task=asyncio.create_task(heartbeat_loop(db.SessionLocal,wid,interval=0.015))
        await asyncio.sleep(0.05)
        task.cancel()
        try:await task
        except asyncio.CancelledError:pass
    asyncio.run(exercise())
    with db.SessionLocal() as session:
        item=session.get(WorkerHeartbeat,wid)
        assert item.stopped_at is not None


def test_tenant_dashboard_worker_health_is_aggregate_not_secret(client):
    register(client,'health-owner@example.com')
    with db.SessionLocal() as session:
        organization=session.query(Organization).filter_by(name='Компания').first()
        assert organization
        conn=ChannelConnection(organization_id=organization.id,provider='telegram',mode='live',
            status='connected',name='Связь',external_account_id='my-test-account',
            encrypted_credentials='ENCRYPTED_CANARY_SECRET_NEVER_EXPOSE')
        contact=Contact(organization_id=organization.id,name='Тестовый посетитель')
        session.add_all([conn,contact]);session.flush()
        conv=Conversation(organization_id=organization.id,channel_id=conn.id,
                          contact_id=contact.id,external_chat_id='123',last_inbound_at=now())
        session.add(conv);session.flush()
        msg=Message(organization_id=organization.id,conversation_id=conv.id,
                    direction='out',body='Секретный текст клиенту',delivery_status='queued')
        session.add(msg);session.flush()
        session.add(OutgoingJob(organization_id=organization.id,message_id=msg.id,
                    channel_id=conn.id,created_at=now()-380))
        session.commit()
    data=client.get('/api/operations/overview')
    assert data.status_code==200,data.text
    result=data.json()
    assert result['outbox']['queued']==1
    assert result['oldest_queued_seconds'] >= 300
    assert result['worker']['code']=='offline'
    assert 'worker_id' not in str(result)
    assert 'ENCRYPTED_CANARY_SECRET_NEVER_EXPOSE' not in str(result)
    assert 'Секретный текст клиенту' not in str(result)
    wid=start_worker(db.SessionLocal)
    finish_cycle(db.SessionLocal,wid)
    refreshed=client.get('/api/operations/overview').json()
    assert refreshed['worker']['code']=='working'
    assert refreshed['worker']['last_cycle_seconds_ago'] is not None


def test_dashboard_without_external_jobs_has_neutral_empty_state(client):
    register(client,'empty-worker@example.com')
    status=client.get('/api/operations/overview').json()
    assert status['worker']['code']=='not_needed'
    assert status['outbox']['queued']==0
    assert status['oldest_queued_seconds'] is None


def test_modern_frontend_never_falls_back_to_outdated_react_silently(client,monkeypatch):
    monkeypatch.setenv('FRONTEND_MODE','modern')
    result=client.get('/')
    assert result.status_code==503
    assert 'сборка не подготовлена' in result.json()['detail']
    monkeypatch.setenv('FRONTEND_MODE','legacy')
    assert client.get('/').status_code==200
