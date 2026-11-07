"""R36 migration of populated v1.5 data and bounded lifecycle of new receipts."""
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

from app import db
from app.db import DeliveryTransition, DispatchPause, Message, Organization, OutgoingJob, now
from app.extras import purge_expired
from conftest import register
from test_r36_dispatch_safety import add_job


def test_populated_r35_migration_retains_existing_jobs(tmp_path):
    root = Path(__file__).resolve().parents[2]
    target = tmp_path / 'filled-r35.db'
    env = dict(os.environ, DATABASE_URL='sqlite:///' + str(target), PYTHONPATH=str(root / 'backend'))

    def migrate(revision):
        result = subprocess.run([sys.executable, '-m', 'alembic', '-c', 'backend/alembic.ini',
                                 'upgrade', revision], cwd=root, env=env,
                                capture_output=True, text=True, timeout=45)
        assert result.returncode == 0, result.stdout + '\n' + result.stderr

    migrate('f35000a10001')
    with sqlite3.connect(target) as conn:
        org = ('org-v15', 'Original tenant', 'starter', 0, 365, 5, 'RUB', 'UTC', 123.0)
        conn.execute('INSERT INTO organizations (id,name,plan,is_demo,retention_days,sla_minutes,currency,timezone,created_at) VALUES (?,?,?,?,?,?,?,?,?)', org)
        conn.execute('INSERT INTO channel_connections (id,organization_id,provider,name,mode,status,created_at) VALUES (?,?,?,?,?,?,?)',
                     ('channel-v15', 'org-v15', 'telegram', 'Original channel', 'live', 'connected', 123.0))
        conn.execute('INSERT INTO contacts (id,organization_id,name,tags,stage,deal_confirmed,created_at) VALUES (?,?,?,?,?,?,?)',
                     ('contact-v15','org-v15','Original contact','[]','new',0,123.0))
        conn.execute('INSERT INTO conversations (id,organization_id,channel_id,contact_id,external_chat_id,status,priority,pinned,archived,unread_count,version,last_message_at,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                     ('conv-v15','org-v15','channel-v15','contact-v15','external-original','new','normal',0,0,0,0,123.0,123.0))
        conn.execute('INSERT INTO messages (id,organization_id,conversation_id,direction,kind,body,delivery_status,is_demo,created_at) VALUES (?,?,?,?,?,?,?,?,?)',
                     ('message-v15','org-v15','conv-v15','out','text','PLEASE KEEP ORIGINAL MESSAGE','queued',0,123.0))
        conn.execute('INSERT INTO outgoing_jobs (id,organization_id,message_id,channel_id,status,attempts,next_attempt_at,created_at) VALUES (?,?,?,?,?,?,?,?)',
                     ('job-v15','org-v15','message-v15','channel-v15','queued',2,1000.0,123.0))
        conn.commit()
        before = conn.execute('SELECT id,organization_id,status,attempts FROM outgoing_jobs').fetchall()
    migrate('head')
    with sqlite3.connect(target) as conn:
        assert conn.execute('SELECT version_num FROM alembic_version').fetchone()[0] == 'f36000a10001'
        assert conn.execute('SELECT id,organization_id,status,attempts FROM outgoing_jobs').fetchall() == before
        assert conn.execute('SELECT body FROM messages WHERE id=?', ('message-v15',)).fetchone()[0] == 'PLEASE KEEP ORIGINAL MESSAGE'
        assert conn.execute('SELECT name FROM organizations WHERE id=?', ('org-v15',)).fetchone()[0] == 'Original tenant'
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {'dispatch_pauses', 'delivery_transitions'} <= tables
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'


def test_retention_prunes_old_receipts_and_expired_gates(client):
    org_id = register(client, 'r36-retention@example.com')['organization']['id']
    channel_old, job_old, message_old = add_job(org_id, 'retention-old')
    channel_recent, job_recent, _ = add_job(org_id, 'retention-new')
    clock=now()
    with db.SessionLocal() as session:
        session.get(Organization,org_id).retention_days=1
        session.get(Message,message_old).created_at=clock-3*86400
        session.add_all([
            DeliveryTransition(organization_id=org_id,job_id=job_old,status_from='queued',
                status_to='processing',event_code='claimed',attempts=1,created_at=clock),
            DeliveryTransition(organization_id=org_id,job_id=job_recent,status_from='queued',
                status_to='queued',event_code='retry',attempts=1,created_at=clock-3*86400),
            DeliveryTransition(organization_id=org_id,job_id=job_recent,status_from='queued',
                status_to='processing',event_code='claimed',attempts=2,created_at=clock),
            DispatchPause(organization_id=org_id,channel_id=channel_recent,reason_code='incident',
                actor_user_id='owner-test',created_at=clock-100,expires_at=clock-1),
        ])
        session.commit()
        assert purge_expired(session)>=1
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,job_old) is None
        assert session.get(Message,message_old) is None
        assert session.query(DeliveryTransition).filter_by(job_id=job_old).count()==0
        assert session.get(OutgoingJob,job_recent) is not None
        events=session.query(DeliveryTransition).filter_by(job_id=job_recent).all()
        assert [e.event_code for e in events]==['claimed']
        assert session.query(DispatchPause).count()==0


def test_deleting_tenant_removes_new_safety_records(client):
    company = register(client,'r36-delete@example.com','DestroyMe')['organization']
    channel,job,_ = add_job(company['id'],'delete')
    with db.SessionLocal() as session:
        session.add(DeliveryTransition(organization_id=company['id'],job_id=job,
                    status_from='queued',status_to='processing',event_code='claimed',attempts=1))
        session.add(DispatchPause(organization_id=company['id'],channel_id='*',
                    reason_code='maintenance',actor_user_id='owner-test'))
        session.commit()
    response=client.post('/api/organization/delete',json={'confirmation':'DestroyMe'})
    assert response.status_code==200,response.text
    with db.SessionLocal() as session:
        assert session.query(DeliveryTransition).filter_by(organization_id=company['id']).count()==0
        assert session.query(DispatchPause).filter_by(organization_id=company['id']).count()==0
