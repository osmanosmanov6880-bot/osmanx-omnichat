"""V1.3: shared abuse guards, tenant-fair outbox and deployment drift protection."""
import asyncio
import os
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from pathlib import Path
import pytest
from fastapi import HTTPException, Request
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command
from app import db
from app.db import (Organization, ChannelConnection, Contact, Conversation, Message,
                    OutgoingJob, PublicRateBucket, now)
from app.public_limits import enforce_public_limit
from app.services import process_outbox
from conftest import register, start_demo


def fake_request(host='198.51.100.10'):
    return Request({'type':'http','client':(host,4321),'method':'POST',
                    'path':'/api/demo/start','headers':[]})


def test_shared_public_limit_survives_new_session(client):
    request=fake_request()
    with db.SessionLocal() as s:
        assert enforce_public_limit(s,request,'test-scope',limit=2,period=3600)==1
    with db.SessionLocal() as s:
        assert enforce_public_limit(s,request,'test-scope',limit=2,period=3600)==2
    with db.SessionLocal() as s, pytest.raises(HTTPException) as exc:
        enforce_public_limit(s,request,'test-scope',limit=2,period=3600)
    assert exc.value.status_code==429 and int(exc.value.headers['Retry-After'])>0
    with db.SessionLocal() as s:
        rows=s.query(PublicRateBucket).filter_by(scope='test-scope').all()
        assert len(rows)==1 and rows[0].attempts==3
        assert '198.51.100.10' not in rows[0].actor_digest


def test_public_limit_isolated_across_sources_and_purged(client):
    a,b=fake_request('198.51.100.33'),fake_request('203.0.113.35')
    with db.SessionLocal() as s:
        for _ in range(2):
            enforce_public_limit(s,a,'test2',limit=2,period=3600)
        assert enforce_public_limit(s,b,'test2',limit=2,period=3600)==1
        assert enforce_public_limit(s,a,'another',limit=2,period=3600)==1
    with db.SessionLocal() as s:
        for item in s.query(PublicRateBucket).all():item.created_at=now()-4*86400
        s.commit()
        from app.extras import purge_expired
        purge_expired(s)
        assert s.query(PublicRateBucket).count()==0


def test_public_limit_atomic_under_two_database_connections(client):
    gate=Barrier(2)
    def hit():
        with db.SessionLocal() as s:
            gate.wait(timeout=5)
            return enforce_public_limit(s,fake_request(),'parallel',limit=2,period=600)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=[pool.submit(hit) for _ in range(2)]
        assert sorted(p.result(timeout=7) for p in results)==[1,2]
    with db.SessionLocal() as s:
        assert s.query(PublicRateBucket).filter_by(scope='parallel').one().attempts==2


def test_demo_entrypoint_is_limited_in_shared_db_even_after_memory_reset(client):
    from app.main import rate_hits
    # A new test company is created on each allowed call. A different API worker
    # would start with empty memory; the shared DB still prevents the 13th.
    for i in range(12):
        rate_hits.clear()
        response=client.post('/api/demo/start')
        assert response.status_code==200,response.text
    rate_hits.clear()
    response=client.post('/api/demo/start')
    assert response.status_code==429
    assert int(response.headers['Retry-After'])>0


def test_fair_queue_serves_second_tenant_before_all_first_tenant_messages(client,monkeypatch):
    register(client,email='fairness-owner@example.org')
    with db.SessionLocal() as s:
        org_a=Organization(name='Крупный бизнес',plan='enterprise')
        org_b=Organization(name='Малый бизнес',plan='enterprise')
        s.add_all([org_a,org_b]);s.flush()
        for org,volume in [(org_a,8),(org_b,1)]:
            ch=ChannelConnection(organization_id=org.id,name='Test Bot',provider='telegram',
                                 mode='live',status='connected',encrypted_credentials='fake')
            co=Contact(organization_id=org.id,name='Покупатель')
            s.add_all([ch,co]);s.flush()
            cv=Conversation(organization_id=org.id,channel_id=ch.id,contact_id=co.id,
                            external_chat_id=org.id,last_inbound_at=now())
            s.add(cv);s.flush()
            for index in range(volume):
                m=Message(organization_id=org.id,conversation_id=cv.id,direction='out',
                          body=org.name+str(index),delivery_status='queued')
                s.add(m);s.flush()
                s.add(OutgoingJob(organization_id=org.id,message_id=m.id,channel_id=ch.id,
                                  created_at=now()-900+index))
        s.commit()
        small_id=org_b.id
    import app.services as services
    calls=[]
    class FakeAdapter:
        async def send_message(self,credentials,channel,conv,body):
            calls.append((channel.organization_id,body))
            return 'provider-ack-'+str(len(calls))
    monkeypatch.setattr(services,'unseal',lambda _: {'access_token':'test'})
    monkeypatch.setattr(services,'adapter_for',lambda _: FakeAdapter())
    assert asyncio.run(process_outbox(db.SessionLocal,limit=2)) == 2
    assert len(calls)==2
    assert {oid for oid,body in calls} == {small_id, calls[0][0]}
    assert calls[0][0] != calls[1][0]
    with db.SessionLocal() as s:
        assert s.query(OutgoingJob).filter_by(organization_id=small_id,status='done').count()==1
        assert s.query(OutgoingJob).filter_by(status='queued').count()==7


def test_schema_guard_fails_closed_for_unmigrated_and_old_database(tmp_path):
    url='sqlite:///'+str(tmp_path/'schema-test.db')
    engine=create_engine(url)
    with pytest.raises(RuntimeError,match='migrations missing'):
        db.assert_schema_current(engine)
    engine.dispose()
    config=Config(str(Path(__file__).resolve().parents[1]/'alembic.ini'))
    config.set_main_option('sqlalchemy.url',url)
    from unittest.mock import patch
    with patch.dict(os.environ,{'DATABASE_URL':url}):
        command.upgrade(config,'head')
    engine=create_engine(url)
    assert db.assert_schema_current(engine) is True
    with engine.begin() as conn:
        conn.execute(text("UPDATE alembic_version SET version_num='ab111f611001'"))
    with pytest.raises(RuntimeError,match='revision mismatch'):
        db.assert_schema_current(engine)
    engine.dispose()


def test_reverse_proxy_address_is_only_trusted_from_configured_ingress(client,monkeypatch):
    from app.public_limits import verified_client_ip
    def req(remote,forwarded):
        return Request({'type':'http','client':(remote,443),'method':'POST',
                        'path':'/api/demo/start','headers':[(b'x-forwarded-for',forwarded.encode())]})
    forged=req('198.51.100.12','203.0.113.99')
    monkeypatch.delenv('TRUSTED_PROXY_CIDRS',raising=False)
    assert verified_client_ip(forged)=='198.51.100.12'
    monkeypatch.setenv('TRUSTED_PROXY_CIDRS','172.16.0.0/12')
    assert verified_client_ip(forged)=='198.51.100.12'
    behind_proxy=req('172.17.0.8','203.0.113.4, 198.51.100.12, 172.17.0.7')
    # The nearest untrusted hop is authoritative; earlier spoofed values are ignored.
    assert verified_client_ip(behind_proxy)=='198.51.100.12'
    unambiguous=req('172.17.0.8','203.0.113.4')
    assert verified_client_ip(unambiguous)=='203.0.113.4'
    assert verified_client_ip(req('172.17.0.8','bogus'))=='172.17.0.8'


def test_window_rollover_uses_new_bucket(client,monkeypatch):
    import app.public_limits as limits
    start=1710000000.0
    monkeypatch.setattr(limits,'now',lambda: start)
    with db.SessionLocal() as s:
        assert limits.enforce_public_limit(s,fake_request(),'rollover',limit=1,period=60)==1
    monkeypatch.setattr(limits,'now',lambda: start+120)
    with db.SessionLocal() as s:
        assert limits.enforce_public_limit(s,fake_request(),'rollover',limit=1,period=60)==1
        assert s.query(PublicRateBucket).filter_by(scope='rollover').count()==2
