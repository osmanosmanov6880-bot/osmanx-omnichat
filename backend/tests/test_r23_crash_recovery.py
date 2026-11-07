"""R23: pre-send crash recovery vs post-send ambiguous outcome.

All providers are local deterministic mocks. This proves the SQL and API
safety properties, not a live social network, PostgreSQL or deployment.
"""
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from app import db
from app.db import OutgoingJob, Message, AuditLog, Organization, now
from app.outbox_recovery import recover_stale_jobs, mark_send_started, refresh_claim
from app.services import process_outbox
from conftest import register
from test_r22_outbox_control import seed


def make_claim(client, *, started=False, legacy=False):
    org,conv,jid,mid,cid=seed(client)
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,jid)
        job.status='processing'
        job.attempts=1
        job.claim_token=None if legacy else 'new-r23-claim-'+jid[:16]
        job.send_started_at=now()-140 if started else None
        job.claimed_at=now()-150
        session.commit()
        return org,jid,mid,cid,job.claim_token


def test_pre_send_crash_requeues_safely_and_records_own_tenant_audit(client):
    org,jid,mid,cid,token=make_claim(client)
    with db.SessionLocal() as session:
        status=recover_stale_jobs(session)
        assert status=={'before_send':1,'possibly_sent':0}
        job=session.get(OutgoingJob,jid)
        assert job.status=='queued'
        assert job.attempts==0
        assert job.claimed_at is None and job.claim_token is None
        assert job.send_started_at is None
        assert job.next_attempt_at>now()
        assert session.get(Message,mid).delivery_status=='queued'
        audit=session.query(AuditLog).filter_by(organization_id=org,
            action='outbox.recovered_before_send',entity_id=jid).one()
        assert audit.user_id is None
        assert recover_stale_jobs(session)=={'before_send':0,'possibly_sent':0}


def test_legacy_r22_processing_never_assumed_safe_to_requeue(client):
    org,jid,mid,cid,token=make_claim(client,legacy=True)
    with db.SessionLocal() as session:
        assert recover_stale_jobs(session)=={'before_send':0,'possibly_sent':1}
        job=session.get(OutgoingJob,jid)
        assert job.status=='uncertain'
        assert session.get(Message,mid).delivery_status=='uncertain'
        assert session.query(AuditLog).filter_by(organization_id=org,
            action='outbox.uncertain_after_interruption').count()==1
    assert asyncio.run(process_outbox(db.SessionLocal))==0
    assert client.post('/api/operations/outbox/'+jid+'/cancel').status_code==409


def test_started_request_crash_stays_uncertain_no_automatic_replay(client):
    org,jid,mid,cid,token=make_claim(client,started=True)
    with db.SessionLocal() as session:
        assert recover_stale_jobs(session)['possibly_sent']==1
        job=session.get(OutgoingJob,jid)
        assert job.status=='uncertain' and job.send_started_at is not None
        assert session.get(Message,mid).delivery_status=='uncertain'
    assert asyncio.run(process_outbox(db.SessionLocal))==0


def test_old_worker_must_not_mark_send_after_claim_recovery(client):
    org,jid,mid,cid,old_token=make_claim(client)
    with db.SessionLocal() as session:
        recover_stale_jobs(session)
        assert not mark_send_started(session,jid,old_token,org)
        assert not refresh_claim(db.SessionLocal,jid,old_token)
        job=session.get(OutgoingJob,jid)
        assert job.status=='queued' and job.send_started_at is None


def test_checkpoint_is_durable_and_prevents_duplicate_recovery(client):
    org,jid,mid,cid,token=make_claim(client)
    with db.SessionLocal() as session:
        session.get(OutgoingJob,jid).claimed_at=now()
        session.commit()
        assert mark_send_started(session,jid,token,org)
        assert not mark_send_started(session,jid,token,org)
    # The send may have happened, even if the worker disappeared afterward.
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,jid)
        assert job.send_started_at is not None
        job.claimed_at=now()-400
        session.commit()
    with db.SessionLocal() as session:
        assert recover_stale_jobs(session)['possibly_sent']==1
        assert session.get(OutgoingJob,jid).status=='uncertain'


def test_heartbeat_refreshes_processing_claim_while_provider_waits(client,monkeypatch):
    org,conv,jid,mid,cid=seed(client)
    import app.outbox_recovery as recovery
    import app.services as svc
    monkeypatch.setattr(recovery,'CLAIM_HEARTBEAT_INTERVAL',0.025)
    monkeypatch.setattr(svc,'unseal',lambda _: {'access_token':'local-fake'})
    started=asyncio.Event();finish=asyncio.Event()
    calls=[]
    class FakeProvider:
        async def send_message(self,credentials,channel,conversation,body):
            calls.append(body)
            started.set()
            await finish.wait()
            return 'external-test-accepted'
    monkeypatch.setattr(svc,'adapter_for',lambda _:FakeProvider())

    async def scenario():
        task=asyncio.create_task(process_outbox(db.SessionLocal))
        await asyncio.wait_for(started.wait(),timeout=3)
        with db.SessionLocal() as session:
            job=session.get(OutgoingJob,jid)
            assert job.status=='processing' and job.send_started_at is not None
            stamp=job.claimed_at
        await asyncio.sleep(0.12)
        with db.SessionLocal() as session:
            job=session.get(OutgoingJob,jid)
            assert job.claimed_at > stamp, 'Slow provider lost worker heartbeat'
        finish.set()
        return await asyncio.wait_for(task,timeout=4)
    assert asyncio.run(scenario())==1
    assert len(calls)==1
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,jid)
        assert job.status=='done' and job.claim_token is None
        assert session.get(Message,mid).delivery_status=='accepted'


def test_late_provider_success_cannot_override_quarantined_claim(client,monkeypatch):
    org,conv,jid,mid,cid=seed(client)
    import app.services as svc
    monkeypatch.setattr(svc,'unseal',lambda _: {'access_token':'local-fake'})
    started=asyncio.Event();finish=asyncio.Event()
    class FakeProvider:
        async def send_message(self,credentials,channel,conversation,body):
            started.set()
            await finish.wait()
            return 'late-provider-ack'
    monkeypatch.setattr(svc,'adapter_for',lambda _:FakeProvider())

    async def scenario():
        task=asyncio.create_task(process_outbox(db.SessionLocal))
        await asyncio.wait_for(started.wait(),timeout=3)
        with db.SessionLocal() as session:
            job=session.get(OutgoingJob,jid)
            assert job.send_started_at is not None and job.claim_token
            # A different worker observes an expired claim and quarantines it.
            assert recover_stale_jobs(session,stamp=now()+1000)['possibly_sent']==1
            assert session.get(OutgoingJob,jid).status=='uncertain'
        finish.set()
        return await task
    assert asyncio.run(scenario())==0
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,jid).status=='uncertain'
        assert session.get(Message,mid).delivery_status=='uncertain'
        assert session.get(Message,mid).external_id!='late-provider-ack'


def test_two_workers_concurrent_claim_send_at_most_once(client,monkeypatch):
    org,conv,jid,mid,cid=seed(client)
    import app.services as svc
    monkeypatch.setattr(svc,'unseal',lambda _: {'access_token':'local-fake'})
    called=[]
    class Provider:
        async def send_message(self,credentials,channel,conversation,body):
            called.append(body)
            await asyncio.sleep(0.07)
            return 'external-accepted'
    monkeypatch.setattr(svc,'adapter_for',lambda _:Provider())

    async def scenario():
        return await asyncio.gather(process_outbox(db.SessionLocal),process_outbox(db.SessionLocal))
    assert sum(asyncio.run(scenario()))==1
    assert len(called)==1
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,jid).status=='done'


def test_other_company_cannot_see_recovery_events(client):
    org,jid,mid,cid,_=make_claim(client)
    with db.SessionLocal() as session:
        recover_stale_jobs(session)
        assert session.query(AuditLog).filter_by(organization_id=org,
            action='outbox.recovered_before_send').count()==1
        other=Organization(name='Недоступная чужая организация')
        session.add(other);session.commit()
        assert session.query(AuditLog).filter_by(organization_id=other.id).count()==0


def test_legacy_migration_preserves_processing_rows_as_ambiguous(tmp_path):
    import os
    import sqlite3
    import subprocess
    import sys
    from pathlib import Path
    from app.db import engine_for, assert_schema_current
    root=Path(__file__).resolve().parents[2]
    database=tmp_path/'legacy-r22.db'
    env=dict(os.environ,DATABASE_URL='sqlite:///'+str(database),PYTHONPATH='backend')
    cmd=[sys.executable,'-m','alembic','-c','backend/alembic.ini','upgrade']
    subprocess.run(cmd+['f20000a10001'],cwd=root,env=env,check=True,capture_output=True)
    with sqlite3.connect(database) as conn:
        conn.execute("INSERT INTO organizations (id,name,plan,is_demo,retention_days,sla_minutes,currency,timezone,created_at) VALUES ('legacy-org','Предыдущая компания','starter',0,365,5,'RUB','UTC',1)")
        conn.execute("INSERT INTO channel_connections (id,organization_id,name,provider,mode,status,created_at) VALUES ('legacy-channel','legacy-org','Telegram','telegram','live','connected',1)")
        conn.execute("INSERT INTO contacts (id,organization_id,name,tags,stage,deal_confirmed,created_at) VALUES ('legacy-contact','legacy-org','Клиент','[]','new',0,1)")
        conn.execute("INSERT INTO conversations (id,organization_id,channel_id,contact_id,external_chat_id,status,priority,pinned,archived,unread_count,version,last_message_at,created_at) VALUES ('legacy-conv','legacy-org','legacy-channel','legacy-contact','chat','new','normal',0,0,0,1,1,1)")
        conn.execute("INSERT INTO messages (id,organization_id,conversation_id,direction,kind,body,delivery_status,is_demo,created_at) VALUES ('legacy-msg','legacy-org','legacy-conv','out','text','Старый ответ','queued',0,1)")
        conn.execute("INSERT INTO outgoing_jobs (id,organization_id,message_id,channel_id,status,attempts,next_attempt_at,claimed_at,created_at) VALUES ('legacy-job','legacy-org','legacy-msg','legacy-channel','processing',1,1,1,1)")
        conn.commit()
    subprocess.run(cmd+['head'],cwd=root,env=env,check=True,capture_output=True)
    engine=engine_for(env['DATABASE_URL'])
    from sqlalchemy.orm import sessionmaker
    Session=sessionmaker(bind=engine,expire_on_commit=False)
    try:
        assert assert_schema_current(engine)
        with Session() as s:
            assert recover_stale_jobs(s)['possibly_sent']==1
            assert s.get(OutgoingJob,'legacy-job').status=='uncertain'
            assert s.get(Message,'legacy-msg').delivery_status=='uncertain'
            assert s.get(Organization,'legacy-org').name=='Предыдущая компания'
    finally:
        engine.dispose()


def test_operations_exposes_only_tenant_stage_counts_without_claim_ids(client):
    org,jid,mid,cid,token=make_claim(client)
    with db.SessionLocal() as session:
        session.get(OutgoingJob,jid).claimed_at=now()
        session.commit()
    ready=client.get('/api/operations/overview')
    assert ready.status_code==200,ready.text
    data=ready.json()
    assert data['preflight_in_progress']==1
    assert data['provider_requests_in_progress']==0
    assert data['safe_recoveries_last_7_days']==0
    assert 'claim_token' not in str(data)
    rows=client.get('/api/operations/outbox?status=processing').json()
    assert rows[0]['processing_phase']=='Подготовка до отправки'
    assert token not in str(rows)
    with db.SessionLocal() as session:
        assert mark_send_started(session,jid,token,org)
    after=client.get('/api/operations/overview').json()
    assert after['preflight_in_progress']==0
    assert after['provider_requests_in_progress']==1
    jobs=client.get('/api/operations/outbox?status=processing').json()
    assert jobs[0]['processing_phase']=='Запрос передан площадке'


def test_manual_reconcile_refuses_second_manager_decision(client):
    org,jid,mid,cid,token=make_claim(client,started=True)
    with db.SessionLocal() as session:
        recover_stale_jobs(session)
    route='/api/operations/outbox/'+jid+'/resolve'
    first=client.post(route,json={'status':'accepted','evidence':'Проверено вручную в исходной площадке'})
    assert first.status_code==200,first.text
    second=client.post(route,json={'status':'failed','evidence':'Другое мнение после проверенного ответа'})
    assert second.status_code==409
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,jid).status=='done'
        assert session.get(Message,mid).delivery_status=='accepted'
        assert session.query(AuditLog).filter_by(organization_id=org,
            action='outbox.manual_reconcile',entity_id=jid).count()==1


def test_retry_after_definite_refusal_clears_old_checkpoint(client):
    org,jid,mid,cid,token=make_claim(client,started=True)
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,jid)
        job.status='failed'
        job.last_error='API 403: временно отозван доступ'
        session.get(Message,mid).delivery_status='failed'
        session.commit()
    response=client.post('/api/operations/outbox/'+jid+'/retry-verified',json={
        'verified_not_delivered':True,
        'evidence':'В исходной соцсети ответ отсутствует, права восстановлены'})
    assert response.status_code==200,response.text
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,jid)
        assert job.status=='queued' and job.attempts==0
        assert job.claim_token is None and job.send_started_at is None
        assert session.get(Message,mid).delivery_status=='queued'


def test_legacy_processing_with_missing_claim_time_is_quarantined(client):
    org,jid,mid,cid,token=make_claim(client,legacy=True)
    with db.SessionLocal() as session:
        session.get(OutgoingJob,jid).claimed_at=None
        session.commit()
        assert recover_stale_jobs(session)=={'before_send':0,'possibly_sent':1}
        assert session.get(OutgoingJob,jid).status=='uncertain'
        assert session.get(Message,mid).delivery_status=='uncertain'


def test_safe_recovered_preflight_retries_once_after_due(client,monkeypatch):
    org,jid,mid,cid,old_token=make_claim(client)
    import app.services as svc
    monkeypatch.setattr(svc,'unseal',lambda _: {'access_token':'test-only'})
    sent=[]
    class Provider:
        async def send_message(self,credentials,channel,conversation,text):
            sent.append(text)
            return 'provider-accepted-after-r23-safe-recovery'
    monkeypatch.setattr(svc,'adapter_for',lambda _:Provider())
    with db.SessionLocal() as session:
        assert recover_stale_jobs(session)['before_send']==1
        job=session.get(OutgoingJob,jid)
        # Advance the due time in the test without waiting on the real clock.
        job.next_attempt_at=0
        session.commit()
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert asyncio.run(process_outbox(db.SessionLocal))==0
    assert len(sent)==1
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,jid)
        msg=session.get(Message,mid)
        assert job.status=='done' and job.claim_token is None
        assert job.send_started_at is not None
        assert msg.delivery_status=='accepted'
        assert msg.external_id=='provider-accepted-after-r23-safe-recovery'
