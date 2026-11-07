"""R25 operational containment: pause only NEW outbound sends, not inbound.

No live provider traffic. Fail closed for stale worker claims, cross-tenant
access and repeated/outdated administrative actions.
"""
import asyncio
import os
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from app import db
from app.db import (Organization,ChannelConnection,Contact,Conversation,
                    Message,OutgoingJob,AuditLog,Membership,now)
from app.services import process_outbox,ingest_inbound
from app.outbox_recovery import mark_send_started,release_paused_preflight,recover_stale_jobs
from conftest import register
from test_r22_outbox_control import seed


PAUSE='/api/integrations/{}/outbound-pause'
RESUME='/api/integrations/{}/outbound-resume'
BODY={'reason':'security_review','acknowledge_inflight':True}


def test_admin_pause_resume_keeps_channel_and_incoming_live(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    paused=client.post(PAUSE.format(ch_id),json=BODY)
    assert paused.status_code==200,paused.text
    assert paused.json()['outbound_paused'] is True
    assert 'Входящие продолжат' in paused.json()['message']
    with db.SessionLocal() as session:
        ch=session.get(ChannelConnection,ch_id)
        assert ch.status=='connected' and ch.outbound_paused_at
        assert ch.outbound_paused_by
        assert ch.outbound_pause_reason=='security_review'
        result=ingest_inbound(session,channel=ch,external_chat_id='r25-visitor',
            external_message_id='r25-new-inbound',sender_id='r25-visitor',
            sender_name='Посетитель',text='Есть кто-нибудь?')
        assert result and result.body=='Есть кто-нибудь?'
        session.commit()
    connections=client.get('/api/integrations').json()['connections']
    item=next(ch for ch in connections if ch['id']==ch_id)
    assert item['outbound_paused_at']
    assert item['outbound_pause_reason']=='security_review'
    detail=client.get('/api/conversations/'+conv).json()['conversation']
    assert detail['outbound_paused'] is True
    assert 'outbound_paused_by' not in item
    assert 'encrypted_credentials' not in item
    overview=client.get('/api/operations/overview').json()
    assert overview['outbound_paused_channels']==1
    assert any(ch['id']==ch_id and ch['outbound_paused_at'] for ch in overview['channels'])
    assert client.post(PAUSE.format(ch_id),json=BODY).status_code==409
    resumed=client.post(RESUME.format(ch_id))
    assert resumed.status_code==200
    assert resumed.json()['outbound_paused'] is False
    assert client.post(RESUME.format(ch_id)).status_code==409
    with db.SessionLocal() as session:
        ch=session.get(ChannelConnection,ch_id)
        assert ch.outbound_paused_at is None
        assert ch.outbound_pause_reason is None
        logs=session.query(AuditLog).filter_by(organization_id=org,entity_id=ch_id).filter(
            AuditLog.action.in_(['integration.outbound_paused','integration.outbound_resumed'])).all()
        assert {x.action for x in logs}=={'integration.outbound_paused','integration.outbound_resumed'}
        assert all(x.user_id for x in logs)


def test_paused_jobs_not_claimed_and_healthy_other_account_is_served(client,monkeypatch):
    org,conv,job_id,msg_id,ch_id=seed(client)
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=org,provider='telegram',name='Healthy',
            mode='live',status='connected',external_account_id='r25-second')
        contact=Contact(organization_id=org,name='Healthy visitor')
        session.add_all([ch,contact]);session.flush()
        talk=Conversation(organization_id=org,channel_id=ch.id,contact_id=contact.id,
            external_chat_id='healthy-chat',external_recipient_id='healthy')
        session.add(talk);session.flush()
        msg=Message(organization_id=org,conversation_id=talk.id,body='Healthy send',
            direction='out',delivery_status='queued')
        session.add(msg);session.flush()
        session.add(OutgoingJob(organization_id=org,message_id=msg.id,
            channel_id=ch.id,status='queued'))
        session.commit()
        healthy_job=session.query(OutgoingJob).filter_by(message_id=msg.id).one().id
    from app import services
    calls=[]
    class FakeAdapter:
        async def send_message(self, credentials, channel, conversation, text):
            calls.append(channel.id)
            return 'provider-r25-accepted'
    monkeypatch.setattr(services,'unseal',lambda value:{'access_token':'test-token'})
    monkeypatch.setattr(services,'adapter_for',lambda name:FakeAdapter())
    assert client.post(PAUSE.format(ch_id),json=BODY).status_code==200
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert len(calls)==1 and ch_id not in calls
    with db.SessionLocal() as session:
        paused_job=session.get(OutgoingJob,job_id)
        assert paused_job.status=='queued' and paused_job.attempts==0
        assert paused_job.send_started_at is None
        assert session.get(OutgoingJob,healthy_job).status=='done'
    assert client.post(RESUME.format(ch_id)).status_code==200
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert calls[-1]==ch_id


def test_claimed_preflight_does_not_cross_pause_checkpoint(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    token='r25-worker-claim'
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        job.status='processing';job.claim_token=token;job.claimed_at=now();job.attempts=1
        session.commit()
    assert client.post(PAUSE.format(ch_id),json=BODY).status_code==200
    with db.SessionLocal() as session:
        assert not mark_send_started(session,job_id,token,org)
        assert release_paused_preflight(session,job_id,token,org)
        assert not release_paused_preflight(session,job_id,token,org)
        job=session.get(OutgoingJob,job_id)
        assert job.status=='queued' and job.attempts==0
        assert job.claim_token is None and job.send_started_at is None
        assert session.get(Message,msg_id).delivery_status=='queued'


def test_started_http_request_cannot_be_false_cancelled_by_pause(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    token='r25-worker-started'
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        job.status='processing';job.claim_token=token;job.claimed_at=now()-800
        job.send_started_at=now()-800;job.attempts=1
        session.commit()
    assert client.post(PAUSE.format(ch_id),json=BODY).status_code==200
    with db.SessionLocal() as session:
        assert not release_paused_preflight(session,job_id,token,org)
        result=recover_stale_jobs(session)
        assert result['possibly_sent']==1
        assert session.get(OutgoingJob,job_id).status=='uncertain'
        assert session.get(Message,msg_id).delivery_status=='uncertain'
    # Resume must not automatically replay an uncertain external POST.
    assert client.post(RESUME.format(ch_id)).status_code==200
    assert asyncio.run(process_outbox(db.SessionLocal))==0


def test_cross_tenant_cannot_pause_even_with_valid_id(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    with db.SessionLocal() as session:
        foreign=Organization(name='Another company')
        session.add(foreign);session.flush()
        channel=ChannelConnection(organization_id=foreign.id,provider='telegram',
            name='Private other channel',mode='live',status='connected')
        session.add(channel);session.commit()
        foreign_id=channel.id
    assert client.post(PAUSE.format(foreign_id),json=BODY).status_code==404
    assert client.post(RESUME.format(foreign_id)).status_code==404
    with db.SessionLocal() as session:
        assert session.get(ChannelConnection,foreign_id).outbound_paused_at is None
        assert session.query(AuditLog).filter_by(organization_id=org,
             action='integration.outbound_paused',entity_id=foreign_id).count()==0


def test_operators_and_leads_cannot_pause_or_resume(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    with db.SessionLocal() as session:
        mem=session.query(Membership).filter_by(organization_id=org).first()
        mem.role='operator';session.commit()
    assert client.post(PAUSE.format(ch_id),json=BODY).status_code==403
    with db.SessionLocal() as session:
        session.query(Membership).filter_by(organization_id=org).update({'role':'lead'})
        session.commit()
    assert client.post(PAUSE.format(ch_id),json=BODY).status_code==403
    assert client.post(RESUME.format(ch_id)).status_code==403
    with db.SessionLocal() as session:
        assert session.get(ChannelConnection,ch_id).outbound_paused_at is None


def test_requires_explicit_ack_and_bounded_reason_codes(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    for invalid in ({'reason':'security_review'},
                    {'reason':'security_review','acknowledge_inflight':False},
                    {'reason':'password=secret','acknowledge_inflight':True}):
        assert client.post(PAUSE.format(ch_id),json=invalid).status_code==422
    with db.SessionLocal() as session:
        assert session.get(ChannelConnection,ch_id).outbound_paused_at is None


def test_concurrent_pause_is_cas_not_two_successful_requests(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    # Test atomic SQL at the service layer in independent sessions, like two
    # instances of FastAPI handling the same organization's admin action.
    from sqlalchemy import update
    from threading import Barrier
    barrier=Barrier(2)
    # SQL update+commit MUST happen in the same database transaction per
    # worker, or workers could report transient success and roll back.
    def atomic_pause(stamp):
        barrier.wait(timeout=5)
        with db.SessionLocal() as session:
            result=session.execute(update(ChannelConnection).where(
                ChannelConnection.id==ch_id,ChannelConnection.organization_id==org,
                ChannelConnection.outbound_paused_at.is_(None)
            ).values(outbound_paused_at=stamp)).rowcount
            session.commit()
            return result
    with ThreadPoolExecutor(max_workers=2) as pool:
        one=pool.submit(atomic_pause,now())
        two=pool.submit(atomic_pause,now()+1)
        results=[one.result(timeout=10),two.result(timeout=10)]
    assert sorted(results)==[0,1]


def test_r24_to_r25_migration_preserves_connected_channel(tmp_path):
    project=Path(__file__).resolve().parents[2]
    path=tmp_path/'old-r24.db'
    env=dict(os.environ,DATABASE_URL=f'sqlite:///{path}',PYTHONPATH='backend')
    subprocess.run([sys.executable,'-m','alembic','-c','backend/alembic.ini',
        'upgrade','f24000a10001'],cwd=project,env=env,check=True,capture_output=True)
    with sqlite3.connect(path) as sql:
        sql.execute('''INSERT INTO organizations
            (id,name,plan,is_demo,retention_days,sla_minutes,currency,timezone,created_at)
            VALUES (?,?,?,?,?,?,?,?,?)''',('test-r24','Компания R24','starter',0,365,5,'RUB','UTC',1234))
        sql.execute('''INSERT INTO channel_connections
            (id,organization_id,provider,name,mode,status,created_at)
            VALUES (?,?,?,?,?,?,?)''',('r24-live','test-r24','telegram','Ранее подключено','live','connected',1234))
        sql.commit()
    subprocess.run([sys.executable,'-m','alembic','-c','backend/alembic.ini',
        'upgrade','head'],cwd=project,env=env,check=True,capture_output=True)
    with sqlite3.connect(path) as sql:
        # Future releases add migrations; assert the latest revision rather than R25.
        from app.db import engine_for, assert_schema_current
        e=engine_for(env['DATABASE_URL'])
        try: assert assert_schema_current(e)
        finally: e.dispose()
        assert sql.execute('SELECT name FROM organizations WHERE id=?',('test-r24',)).fetchone()==('Компания R24',)
        assert sql.execute('''SELECT name,status,outbound_paused_at FROM channel_connections
            WHERE id=?''',('r24-live',)).fetchone()==('Ранее подключено','connected',None)
