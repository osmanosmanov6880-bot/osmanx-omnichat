"""R26 tenant-wide kill switch: only queued/preflight outbound is prevented.

No real platform requests are made; a send after a committed durable marker
cannot be cancelled by pretending the provider did not receive it.
"""
import asyncio
import os
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

from sqlalchemy import update
from app import db
from app.db import (Organization, Membership, ChannelConnection, Contact, Message,
                    OutgoingJob, AuditLog, Conversation, now)
from app.services import process_outbox, ingest_inbound
from app.outbox_recovery import mark_send_started, release_paused_preflight, recover_stale_jobs
from conftest import register
from test_r22_outbox_control import seed

PAUSE = '/api/operations/outbound/pause'
RESUME = '/api/operations/outbound/resume'
BODY = {'reason':'security_review','acknowledge_inflight':True}


def pause(client):
    response=client.post(PAUSE,json=BODY)
    assert response.status_code==200,response.text
    return response.json()['outbound_paused_at']


def resume(client,stamp):
    return client.post(RESUME,json={'expected_paused_at':stamp,'acknowledge_inflight':True})


def test_company_pause_holds_all_channels_and_keeps_inbound(client,monkeypatch):
    org,conv,job_id,msg_id,ch_id=seed(client)
    stamp=pause(client)
    import app.services as svc
    calls=[]
    monkeypatch.setattr(svc,'unseal',lambda _: {'access_token':'fake-only'})
    class Provider:
        async def send_message(self,credentials,channel,conv,text):
            calls.append(channel.id)
            return 'local-accepted-id'
    monkeypatch.setattr(svc,'adapter_for',lambda _:Provider())
    assert asyncio.run(process_outbox(db.SessionLocal))==0
    assert not calls
    overview=client.get('/api/operations/overview').json()
    assert overview['organization_outbound_paused_at']==stamp
    assert overview['outbound_paused_channels']==0  # separate per-account control
    detail=client.get('/api/conversations/'+conv).json()['conversation']
    assert detail['outbound_paused'] and detail['organization_outbound_paused']
    with db.SessionLocal() as session:
        channel=session.get(ChannelConnection,ch_id)
        assert channel.status=='connected' and channel.outbound_paused_at is None
        inbound=ingest_inbound(session,channel=channel,external_chat_id='new-customer',
            external_message_id='r26-inbound',sender_id='customer-2',
            sender_name='Клиент',text='Добрый вечер')
        assert inbound is not None
        session.commit()
        assert session.get(OutgoingJob,job_id).status=='queued'
        assert session.get(Message,msg_id).delivery_status=='queued'
        assert session.query(AuditLog).filter_by(organization_id=org,
            action='organization.outbound_paused').count()==1
    result=resume(client,stamp)
    assert result.status_code==200,result.text
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert calls==[ch_id]
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,job_id).status=='done'
        assert session.get(Message,msg_id).delivery_status=='accepted'


def test_global_resume_does_not_clear_an_individually_paused_channel(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    response=client.post(f'/api/integrations/{ch_id}/outbound-pause',json=BODY)
    assert response.status_code==200,response.text
    stamp=pause(client)
    assert resume(client,stamp).status_code==200
    with db.SessionLocal() as session:
        channel=session.get(ChannelConnection,ch_id)
        assert channel.outbound_paused_at is not None
        assert session.get(Organization,org).outbound_paused_at is None
    assert client.get('/api/conversations/'+conv).json()['conversation']['outbound_paused']
    assert asyncio.run(process_outbox(db.SessionLocal))==0


def test_pause_is_idempotence_guarded_and_stale_resume_fails(client):
    org,*_=seed(client)
    stamp=pause(client)
    assert client.post(PAUSE,json=BODY).status_code==409
    assert resume(client,stamp+1).status_code==409
    with db.SessionLocal() as session:
        assert session.get(Organization,org).outbound_paused_at==stamp
    assert resume(client,stamp).status_code==200
    assert resume(client,stamp).status_code==409
    second=pause(client)
    assert second>stamp
    assert resume(client,stamp).status_code==409
    with db.SessionLocal() as session:
        assert session.get(Organization,org).outbound_paused_at==second


def test_explicit_inflight_ack_and_bounded_reason_required(client):
    seed(client)
    invalid=[{}, {'reason':'security_review'},
             {'reason':'security_review','acknowledge_inflight':False},
             {'reason':'secrets_should_never_be_here','acknowledge_inflight':True}]
    for payload in invalid:
        assert client.post(PAUSE,json=payload).status_code==422
    stamp=pause(client)
    for payload in [{}, {'expected_paused_at':stamp},
                    {'expected_paused_at':stamp,'acknowledge_inflight':False},
                    {'expected_paused_at':-1,'acknowledge_inflight':True}]:
        assert client.post(RESUME,json=payload).status_code==422


def test_operator_and_lead_cannot_pause_company(client):
    org,*_=seed(client)
    with db.SessionLocal() as session:
        member=session.query(Membership).filter_by(organization_id=org).one()
        member.role='operator';session.commit()
    assert client.post(PAUSE,json=BODY).status_code==403
    assert client.post(RESUME,json={'expected_paused_at':now(),'acknowledge_inflight':True}).status_code==403
    with db.SessionLocal() as session:
        session.query(Membership).filter_by(organization_id=org).update({'role':'lead'})
        session.commit()
    assert client.post(PAUSE,json=BODY).status_code==403
    with db.SessionLocal() as session:
        assert session.get(Organization,org).outbound_paused_at is None


def test_claimed_but_not_started_is_returned_without_attempt(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    token='worker-checkpoint-r26'
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        job.status='processing';job.claim_token=token;job.claimed_at=now();job.attempts=1
        session.commit()
    stamp=pause(client)
    with db.SessionLocal() as session:
        assert not mark_send_started(session,job_id,token,org)
        assert release_paused_preflight(session,job_id,token,org)
        assert not release_paused_preflight(session,job_id,token,org)
        job=session.get(OutgoingJob,job_id)
        assert job.status=='queued' and job.attempts==0
        assert job.send_started_at is None and job.claim_token is None
    assert resume(client,stamp).status_code==200


def test_started_post_is_not_falsely_cancelled_by_company_pause(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    token='already-sent-checkpoint-r26'
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        job.status='processing';job.claim_token=token
        job.claimed_at=now()-300;job.send_started_at=now()-300;job.attempts=1
        session.commit()
    stamp=pause(client)
    with db.SessionLocal() as session:
        assert not release_paused_preflight(session,job_id,token,org)
        recovery=recover_stale_jobs(session)
        assert recovery['possibly_sent']==1
        assert session.get(OutgoingJob,job_id).status=='uncertain'
        assert session.get(Message,msg_id).delivery_status=='uncertain'
    assert resume(client,stamp).status_code==200
    assert asyncio.run(process_outbox(db.SessionLocal))==0


def test_second_company_is_unaffected_by_foreign_incident(client):
    org,conv,job_id,msg_id,ch_id=seed(client)
    with db.SessionLocal() as session:
        stranger=Organization(name='Другая компания')
        session.add(stranger);session.flush()
        other_channel=ChannelConnection(organization_id=stranger.id,provider='telegram',
            name='Другой бот',mode='live',status='connected')
        session.add(other_channel);session.commit()
        foreign_id=stranger.id
    stamp=pause(client)
    with db.SessionLocal() as session:
        assert session.get(Organization,foreign_id).outbound_paused_at is None
    assert client.get('/api/operations/overview').json()['organization_id']==org
    assert client.get('/api/operations/overview').json()['organization_outbound_paused_at']==stamp
    assert client.post('/api/integrations/'+other_channel.id+'/outbound-resume').status_code==404


def test_two_admin_requests_cannot_both_claim_company_pause(client):
    org,*_=seed(client)
    barrier=Barrier(2)
    def owner(stamp):
        barrier.wait(timeout=5)
        with db.SessionLocal() as session:
            modified=session.execute(update(Organization).where(
                Organization.id==org,Organization.outbound_paused_at.is_(None))
                .values(outbound_paused_at=stamp)).rowcount
            session.commit()
            return modified
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=[f.result(timeout=10) for f in [pool.submit(owner,now()),pool.submit(owner,now()+1)]]
    assert sorted(results)==[0,1]


def test_r25_to_r26_migration_preserves_organization_and_channel(tmp_path):
    project=Path(__file__).resolve().parents[2]
    database=tmp_path/'legacy-r25.db'
    env=dict(os.environ,DATABASE_URL=f'sqlite:///{database}',PYTHONPATH='backend')
    cmd=[sys.executable,'-m','alembic','-c','backend/alembic.ini','upgrade']
    subprocess.run(cmd+['f25000a10001'],cwd=project,env=env,check=True,capture_output=True)
    with sqlite3.connect(database) as conn:
        conn.execute('INSERT INTO organizations(id,name,plan,is_demo,retention_days,sla_minutes,currency,timezone,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
            ('saved-org','Сохранённая компания','starter',0,365,5,'RUB','UTC',123.0))
        conn.execute('INSERT INTO channel_connections(id,organization_id,provider,name,mode,status,created_at) VALUES(?,?,?,?,?,?,?)',
            ('saved-channel','saved-org','telegram','Рабочий бот','live','connected',123.0))
        conn.commit()
    subprocess.run(cmd+['head'],cwd=project,env=env,check=True,capture_output=True)
    with sqlite3.connect(database) as conn:
        assert conn.execute('SELECT name,outbound_paused_at FROM organizations WHERE id=?',('saved-org',)).fetchone()==('Сохранённая компания',None)
        assert conn.execute('SELECT name FROM channel_connections WHERE id=?',('saved-channel',)).fetchone()==('Рабочий бот',)
        from app.db import engine_for, assert_schema_current
        e=engine_for(env['DATABASE_URL'])
        try: assert assert_schema_current(e)
        finally: e.dispose()


def test_paused_tenant_cannot_starve_another_company_outbox(client,monkeypatch):
    org,conv,job_id,msg_id,ch_id=seed(client)
    with db.SessionLocal() as session:
        channel=session.get(ChannelConnection,ch_id)
        # Produce an older flood of queued messages for the stopped tenant.
        for i in range(30):
            msg=Message(organization_id=org,conversation_id=conv,
                direction='out',body=f'Ответ {i}',delivery_status='queued',
                created_at=now()-1800-i)
            session.add(msg);session.flush()
            session.add(OutgoingJob(organization_id=org,message_id=msg.id,
                channel_id=ch_id,status='queued',created_at=msg.created_at))
        stranger=Organization(name='Независимый бизнес')
        session.add(stranger);session.flush()
        ok_channel=ChannelConnection(organization_id=stranger.id,provider='telegram',
            name='Независимый канал',mode='live',status='connected')
        contact=Contact(organization_id=stranger.id,name='Покупатель другой компании')
        session.add_all([ok_channel,contact]);session.flush()
        other_conv=Conversation(organization_id=stranger.id,channel_id=ok_channel.id,
            contact_id=contact.id,external_chat_id='other-chat',external_recipient_id='other-user')
        session.add(other_conv);session.flush()
        msg=Message(organization_id=stranger.id,conversation_id=other_conv.id,
            direction='out',body='Подтверждённый ответ другой компании',delivery_status='queued')
        session.add(msg);session.flush()
        job=OutgoingJob(organization_id=stranger.id,message_id=msg.id,
            channel_id=ok_channel.id,status='queued')
        session.add(job);session.commit()
        ok_job=job.id
    pause(client)
    import app.services as svc
    monkeypatch.setattr(svc,'unseal',lambda _: {'access_token':'fake-for-tests'})
    calls=[]
    class Provider:
        async def send_message(self,credentials,channel,conversation,body):
            calls.append(channel.id)
            return 'provider-test-confirmed'
    monkeypatch.setattr(svc,'adapter_for',lambda name:Provider())
    assert asyncio.run(process_outbox(db.SessionLocal,limit=1))==1
    assert calls==[ok_channel.id]
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,ok_job).status=='done'
        assert session.query(OutgoingJob).filter_by(organization_id=org,status='queued').count()==31
        assert session.get(Organization,org).outbound_paused_at is not None


def test_demo_company_cannot_trigger_outbound_incident_endpoint(client):
    org,*_=seed(client)
    with db.SessionLocal() as session:
        session.get(Organization,org).is_demo=True
        session.commit()
    assert client.post(PAUSE,json=BODY).status_code==403
