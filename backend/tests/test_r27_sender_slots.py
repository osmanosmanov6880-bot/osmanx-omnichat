"""R27 regression: cross-process per-account outbound serialisation.

Uses separate SQLite connections and fake provider calls; no live credentials.
PostgreSQL verification is additionally supplied in GitHub Actions.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy import update

from app import db
from app.channel_dispatch import reserve, release, renew_in_session
from app.db import (ChannelDispatchLease, OutgoingJob, Message,
                    ChannelConnection, Contact, Conversation, Organization, now)
from app.outbox_recovery import mark_send_started, refresh_claim
from app.services import process_outbox
from test_r22_outbox_control import seed


def queued_second(org, conv_id, channel_id):
    with db.SessionLocal() as session:
        message=Message(organization_id=org,conversation_id=conv_id,
                        direction='out',body='Второй ответ',delivery_status='queued')
        session.add(message);session.flush()
        job=OutgoingJob(organization_id=org,message_id=message.id,channel_id=channel_id,
                        status='queued',created_at=now()+0.01)
        session.add(job);session.commit()
        return job.id


def test_sender_slot_ownership_and_expiry_are_fenced(client):
    org,conv,job,mid,channel=seed(client)
    assert reserve(db.SessionLocal,channel,org,'owner-a',stamp=1000,seconds=180)
    assert not reserve(db.SessionLocal,channel,org,'owner-b',stamp=1010,seconds=180)
    with db.SessionLocal() as session:
        assert not renew_in_session(session,channel,'owner-b',stamp=1020)
        session.rollback()
        assert renew_in_session(session,channel,'owner-a',stamp=1050)
        session.commit()
    assert not release(db.SessionLocal,channel,org,'owner-b')
    assert not reserve(db.SessionLocal,channel,org,'owner-c',stamp=1200,seconds=180)
    assert reserve(db.SessionLocal,channel,org,'owner-c',stamp=1231,seconds=180)
    assert not release(db.SessionLocal,channel,org,'owner-a')
    with db.SessionLocal() as session:
        lease=session.get(ChannelDispatchLease,channel)
        assert lease.owner_token=='owner-c' and lease.expires_at==1411
    assert release(db.SessionLocal,channel,org,'owner-c')
    assert reserve(db.SessionLocal,channel,org,'owner-d',stamp=1240,seconds=180)


def test_two_sql_connections_only_one_can_reserve_account(client):
    org,conv,job,mid,channel=seed(client)
    gate=Barrier(2)
    def attempt(worker):
        gate.wait(timeout=5)
        return reserve(db.SessionLocal,channel,org,worker)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(attempt,'writer-a'),pool.submit(attempt,'writer-b')]
        results=[f.result(timeout=8) for f in futures]
    assert results.count(True)==1 and results.count(False)==1
    with db.SessionLocal() as session:
        assert session.query(ChannelDispatchLease).count()==1
        lease=session.get(ChannelDispatchLease,channel)
        assert lease.owner_token in ('writer-a','writer-b')


def test_last_send_checkpoint_requires_live_owned_sender_slot(client):
    org,conv,job_id,mid,channel=seed(client)
    token='claimed-27'
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,job_id)
        job.status='processing';job.claim_token=token;job.claimed_at=now()
        session.commit()
    with db.SessionLocal() as session:
        assert not mark_send_started(session,job_id,token,org,dispatch_token=token)
    assert reserve(db.SessionLocal,channel,org,'other-token')
    with db.SessionLocal() as session:
        assert not mark_send_started(session,job_id,token,org,dispatch_token=token)
    assert release(db.SessionLocal,channel,org,'other-token')
    assert reserve(db.SessionLocal,channel,org,token)
    with db.SessionLocal() as session:
        assert mark_send_started(session,job_id,token,org,dispatch_token=token)
        assert not mark_send_started(session,job_id,token,org,dispatch_token=token)
        assert session.get(OutgoingJob,job_id).send_started_at is not None
    assert release(db.SessionLocal,channel,org,token)


def test_same_account_never_has_two_overlapping_provider_posts(client,monkeypatch):
    org,conv,job1,mid,channel=seed(client)
    job2=queued_second(org,conv,channel)
    import app.services as svc
    monkeypatch.setattr(svc,'unseal',lambda value:{'access_token':'fake'})
    started=asyncio.Event(); finish=asyncio.Event()
    active=0; max_active=0; calls=[]
    class Provider:
        async def send_message(self,credentials,channel,conv,text):
            nonlocal active,max_active
            active+=1; max_active=max(max_active,active);calls.append(text)
            if len(calls)==1:
                started.set()
                await finish.wait()
            await asyncio.sleep(0.001)
            active-=1
            return 'provider-accepted-'+str(len(calls))
    monkeypatch.setattr(svc,'adapter_for',lambda _:Provider())

    async def scenario():
        first=asyncio.create_task(process_outbox(db.SessionLocal,limit=1))
        await asyncio.wait_for(started.wait(),timeout=5)
        # Second API/worker process sees the same shared DB; cannot send via
        # the same sender while its first provider request is unresolved.
        assert await process_outbox(db.SessionLocal,limit=20)==0
        with db.SessionLocal() as session:
            assert session.get(OutgoingJob,job2).status=='queued'
        finish.set()
        assert await asyncio.wait_for(first,timeout=5)==1
        assert await process_outbox(db.SessionLocal,limit=20)==1
    asyncio.run(scenario())
    assert max_active==1 and len(calls)==2
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,job1).status=='done'
        assert session.get(OutgoingJob,job2).status=='done'
        lease=session.get(ChannelDispatchLease,channel)
        assert lease.expires_at==0.0


def test_heartbeat_renews_job_and_slot_during_slow_provider(client,monkeypatch):
    org,conv,job_id,mid,channel=seed(client)
    import app.services as svc
    import app.outbox_recovery as recovery
    monkeypatch.setattr(recovery,'CLAIM_HEARTBEAT_INTERVAL',0.035)
    monkeypatch.setattr(svc,'unseal',lambda _: {'access_token':'test'})
    started=asyncio.Event();done=asyncio.Event()
    class SlowProvider:
        async def send_message(self,*args):
            started.set()
            await done.wait()
            return 'long-send-accepted'
    monkeypatch.setattr(svc,'adapter_for',lambda _:SlowProvider())
    async def run():
        task=asyncio.create_task(process_outbox(db.SessionLocal))
        await asyncio.wait_for(started.wait(),timeout=5)
        with db.SessionLocal() as session:
            original_job=session.get(OutgoingJob,job_id).claimed_at
            original_lease=session.get(ChannelDispatchLease,channel).renewed_at
        await asyncio.sleep(0.16)
        with db.SessionLocal() as session:
            assert session.get(OutgoingJob,job_id).claimed_at>original_job
            assert session.get(ChannelDispatchLease,channel).renewed_at>original_lease
            assert session.get(ChannelDispatchLease,channel).expires_at>now()+140
        done.set()
        assert await asyncio.wait_for(task,timeout=5)==1
    asyncio.run(run())


def test_paused_or_busy_company_does_not_starve_other_tenant(client,monkeypatch):
    org,conv,jid,mid,channel=seed(client)
    busy_token='busy-test-27'
    assert reserve(db.SessionLocal,channel,org,busy_token)
    # The busy account owns many queued messages; another company still wins.
    for _ in range(12):
        queued_second(org,conv,channel)
    with db.SessionLocal() as session:
        company=Organization(name='Другая компания')
        session.add(company);session.flush()
        other_channel=ChannelConnection(organization_id=company.id,provider='telegram',
            name='Другой отправитель',mode='live',status='connected')
        contact=Contact(organization_id=company.id,name='Другой клиент')
        session.add_all([other_channel,contact]);session.flush()
        chat=Conversation(organization_id=company.id,channel_id=other_channel.id,
            contact_id=contact.id,external_chat_id='separate-chat',last_inbound_at=now())
        session.add(chat);session.flush()
        msg=Message(organization_id=company.id,conversation_id=chat.id,
            direction='out',body='Важный ответ другой компании',delivery_status='queued')
        session.add(msg);session.flush()
        other_job=OutgoingJob(organization_id=company.id,message_id=msg.id,
            channel_id=other_channel.id,status='queued')
        session.add(other_job);session.commit();other_id=other_job.id
    import app.services as svc
    monkeypatch.setattr(svc,'unseal',lambda _:{'access_token':'local-test'})
    seen=[]
    class Provider:
        async def send_message(self,creds,ch,conv,text):
            seen.append(ch.id)
            return 'accepted-other'
    monkeypatch.setattr(svc,'adapter_for',lambda _:Provider())
    assert asyncio.run(process_outbox(db.SessionLocal,limit=1))==1
    assert seen==[other_channel.id]
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,jid).status=='queued'
        assert session.get(OutgoingJob,other_id).status=='done'
    assert release(db.SessionLocal,channel,org,busy_token)


def test_old_worker_cannot_refresh_a_replaced_sender_slot(client):
    org,conv,jid,mid,channel=seed(client)
    with db.SessionLocal() as session:
        job=session.get(OutgoingJob,jid)
        job.status='processing';job.claim_token='old';job.claimed_at=now()
        session.commit()
    assert reserve(db.SessionLocal,channel,org,'old',stamp=1000)
    assert reserve(db.SessionLocal,channel,org,'new',stamp=1400)
    assert not refresh_claim(db.SessionLocal,jid,'old',lease_channel_id=channel)
    with db.SessionLocal() as session:
        assert session.get(ChannelDispatchLease,channel).owner_token=='new'
        assert session.get(OutgoingJob,jid).claim_token=='old'


def test_large_queue_drains_sequentially_in_one_worker_cycle(client,monkeypatch):
    org,conv,job1,mid,channel=seed(client)
    jobs=[job1]+[queued_second(org,conv,channel) for _ in range(6)]
    import app.services as svc
    monkeypatch.setattr(svc,'unseal',lambda _:{'access_token':'local-only'})
    calls=[]
    class FastProvider:
        async def send_message(self,credentials,ch,conversation,text):
            calls.append(text)
            return 'ack-'+str(len(calls))
    monkeypatch.setattr(svc,'adapter_for',lambda _:FastProvider())
    assert asyncio.run(process_outbox(db.SessionLocal,limit=5))==5
    with db.SessionLocal() as session:
        assert session.query(OutgoingJob).filter_by(channel_id=channel,status='done').count()==5
        assert session.query(OutgoingJob).filter_by(channel_id=channel,status='queued').count()==2
    assert asyncio.run(process_outbox(db.SessionLocal,limit=5))==2
    assert len(calls)==7


def test_dispatcher_health_summary_never_shows_another_company(client):
    org,conv,job,mid,channel=seed(client)
    with db.SessionLocal() as session:
        other=Organization(name='Чужая компания')
        session.add(other);session.flush()
        outside=ChannelConnection(organization_id=other.id,provider='telegram',
            name='Чужой токен',mode='live',status='connected')
        session.add(outside);session.commit()
        other_org,other_channel=other.id,outside.id
    assert reserve(db.SessionLocal,channel,org,'ours')
    assert reserve(db.SessionLocal,other_channel,other_org,'theirs')
    overview=client.get('/api/operations/overview')
    assert overview.status_code==200
    data=overview.json()
    assert data['active_sender_accounts']==1
    assert str(other_channel) not in str(data)
    assert 'ours' not in str(data) and 'theirs' not in str(data)


def test_r26_to_r27_sqlite_migration_keeps_legacy_records(tmp_path):
    import os, sqlite3, subprocess, sys
    from pathlib import Path
    from app.db import assert_schema_current, engine_for
    project=Path(__file__).resolve().parents[2]
    database=tmp_path/'legacy-r26.db'
    env=dict(os.environ,DATABASE_URL=f'sqlite:///{database}',PYTHONPATH='backend')
    command=[sys.executable,'-m','alembic','-c','backend/alembic.ini','upgrade']
    subprocess.run(command+['f26000a10001'],cwd=project,env=env,check=True,capture_output=True)
    with sqlite3.connect(database) as sql:
        sql.execute('INSERT INTO organizations(id,name,plan,is_demo,retention_days,sla_minutes,currency,timezone,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                    ('old-org','Компания до R27','starter',0,365,5,'RUB','UTC',1234.0))
        sql.execute('INSERT INTO channel_connections(id,organization_id,provider,name,mode,status,created_at) VALUES(?,?,?,?,?,?,?)',
                    ('old-channel','old-org','telegram','Сохранённый канал','live','connected',1234.0))
        sql.execute('INSERT INTO contacts(id,organization_id,name,tags,stage,deal_confirmed,created_at) VALUES(?,?,?,?,?,?,?)',
                    ('old-contact','old-org','Клиент','[]','new',0,1234.0))
        sql.execute('INSERT INTO conversations(id,organization_id,channel_id,contact_id,external_chat_id,status,priority,pinned,archived,unread_count,version,last_message_at,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    ('old-conv','old-org','old-channel','old-contact','legacy-chat','new','normal',0,0,0,0,1234.0,1234.0))
        sql.execute('INSERT INTO messages(id,organization_id,conversation_id,direction,kind,body,delivery_status,is_demo,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                    ('old-msg','old-org','old-conv','out','text','Сохранённый ответ','queued',0,1234.0))
        sql.execute('INSERT INTO outgoing_jobs(id,organization_id,message_id,channel_id,status,attempts,next_attempt_at,created_at) VALUES(?,?,?,?,?,?,?,?)',
                    ('old-job','old-org','old-msg','old-channel','queued',0,1234.0,1234.0))
        sql.commit()
    subprocess.run(command+['head'],cwd=project,env=env,check=True,capture_output=True)
    with sqlite3.connect(database) as sql:
        assert sql.execute('SELECT name FROM organizations WHERE id=?',('old-org',)).fetchone()==('Компания до R27',)
        assert sql.execute('SELECT name FROM channel_connections WHERE id=?',('old-channel',)).fetchone()==('Сохранённый канал',)
        assert sql.execute('SELECT body,delivery_status FROM messages WHERE id=?',('old-msg',)).fetchone()==('Сохранённый ответ','queued')
        assert sql.execute('SELECT status FROM outgoing_jobs WHERE id=?',('old-job',)).fetchone()==('queued',)
        columns={c[1] for c in sql.execute('PRAGMA table_info(channel_dispatch_leases)')}
        assert {'channel_id','organization_id','owner_token','expires_at'} <= columns
    engine=engine_for(env['DATABASE_URL'])
    try:assert assert_schema_current(engine)
    finally:engine.dispose()


def test_workspace_deletion_removes_own_slot_and_preserves_other_tenant(client):
    org,conv,jid,mid,channel=seed(client)
    with db.SessionLocal() as session:
        other=Organization(name='Независимый клиент')
        session.add(other);session.flush()
        other_channel=ChannelConnection(organization_id=other.id,provider='telegram',
            name='Независимый бот',mode='live',status='connected')
        session.add(other_channel);session.commit()
        other_org,other_id=other.id,other_channel.id
    assert reserve(db.SessionLocal,channel,org,'owner-left')
    assert reserve(db.SessionLocal,other_id,other_org,'owner-right')
    response=client.post('/api/organization/delete',json={'confirmation':'Компания'})
    assert response.status_code==200,response.text
    with db.SessionLocal() as session:
        assert session.get(ChannelDispatchLease,channel) is None
        assert session.get(ChannelConnection,channel) is None
        assert session.get(ChannelDispatchLease,other_id).owner_token=='owner-right'
        assert session.get(ChannelConnection,other_id).organization_id==other_org


def test_corrupt_cross_tenant_job_cannot_reserve_foreign_account(client):
    org,conv,jid,mid,channel=seed(client)
    with db.SessionLocal() as session:
        stranger=Organization(name='Иная рабочая область')
        session.add(stranger);session.commit()
        stranger_id=stranger.id
    assert not reserve(db.SessionLocal,channel,stranger_id,'attacker-token')
    with db.SessionLocal() as session:
        assert session.get(ChannelDispatchLease,channel) is None
    assert reserve(db.SessionLocal,channel,org,'actual-owner')
