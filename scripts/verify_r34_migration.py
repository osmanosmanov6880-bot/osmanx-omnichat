"""R33 -> R34 filled SQLite migration preserving all old encrypted events.

Only synthetic values; no production credentials or customer payloads.
"""
import os
import subprocess
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='omnichat-r34-upgrade-') as tmp:
    url='sqlite:///'+str(Path(tmp)/'r33-original.sqlite')
    env=os.environ.copy();env['DATABASE_URL']=url;env['PYTHONPATH']=str(ROOT/'backend')
    def run_alembic(*args):
        proc=subprocess.run(['alembic','-c',str(ROOT/'backend/alembic.ini'),*args],
                   cwd=ROOT,env=env,text=True,capture_output=True)
        assert proc.returncode==0,proc.stdout+'\n'+proc.stderr
    run_alembic('upgrade','f33000a10001')
    engine=create_engine(url)
    with engine.begin() as db:
        db.execute(text("""INSERT INTO organizations(id,name,plan,is_demo,retention_days,
                    sla_minutes,currency,timezone,created_at)
                    VALUES('org-r34','Existing tenant R33','starter',0,365,5,'RUB','UTC',1000000000)"""))
        db.execute(text("""INSERT INTO channel_connections(id,organization_id,provider,name,
                    mode,status,created_at,inbound_last_dispatched_at)
                    VALUES('channel-r34','org-r34','telegram','Existing channel R33',
                    'live','connected',1000000000,1000000002)"""))
        db.execute(text("""INSERT INTO inbound_jobs(id,organization_id,channel_id,provider,
                    fingerprint,encrypted_event,status,attempts,duplicates,
                    next_attempt_at,created_at)
                    VALUES('event-r34','org-r34','channel-r34','telegram','fake-fingerprint',
                    'ENCRYPTED_R33_TEST_MARKER','failed',5,0,1000000000,1000000000)"""))
    engine.dispose()
    run_alembic('upgrade','head')
    run_alembic('check')
    engine=create_engine(url)
    with engine.connect() as db:
        rev=ScriptDirectory.from_config(Config(str(ROOT/'backend/alembic.ini'))).get_current_head()
        assert db.execute(text('SELECT version_num FROM alembic_version')).scalar()==rev
        assert db.execute(text("SELECT name FROM organizations WHERE id='org-r34'")).scalar()=='Existing tenant R33'
        assert db.execute(text("SELECT encrypted_event FROM inbound_jobs WHERE id='event-r34'")).scalar()=='ENCRYPTED_R33_TEST_MARKER'
        assert db.execute(text("SELECT status FROM inbound_jobs WHERE id='event-r34'")).scalar()=='failed'
        assert db.execute(text("SELECT inbound_last_dispatched_at FROM channel_connections WHERE id='channel-r34'")).scalar()==1000000002
        assert db.execute(text("SELECT inbound_processing_token FROM channel_connections WHERE id='channel-r34'")).scalar() is None
        assert db.execute(text("SELECT inbound_processing_job_id FROM channel_connections WHERE id='channel-r34'")).scalar() is None
        assert db.execute(text("SELECT inbound_processing_until FROM channel_connections WHERE id='channel-r34'")).scalar() is None
    engine.dispose()
print('R33_TO_R34_POPULATED_MIGRATION_AND_SCHEMA_CHECK=PASS')
