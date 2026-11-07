"""R32 -> R33 migration rehearsal with an existing tenant and encrypted backlog.
The payload is a synthetic non-secret marker; no social API is contacted.
"""
import os
import subprocess
import tempfile
from pathlib import Path
from sqlalchemy import create_engine,text
from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='omnichat-r33-migration-') as location:
    target=Path(location)/'existing-r32.sqlite'
    env=os.environ.copy()
    env['DATABASE_URL']='sqlite:///'+str(target)
    env['PYTHONPATH']=str(ROOT/'backend')
    def alembic(*args):
        subprocess.run(['alembic','-c',str(ROOT/'backend/alembic.ini'),*args],
                       cwd=ROOT,env=env,check=True,capture_output=True,text=True)
    alembic('upgrade','f32000a10001')
    engine=create_engine(env['DATABASE_URL'])
    with engine.begin() as c:
        c.execute(text('''INSERT INTO organizations(id,name,plan,is_demo,retention_days,
         sla_minutes,currency,timezone,created_at) VALUES
         ('org-r32','Existing R32 tenant','starter',0,365,5,'RUB','UTC',1000000000)'''))
        c.execute(text('''INSERT INTO channel_connections(id,organization_id,provider,name,
         mode,status,created_at) VALUES ('channel-r32','org-r32','telegram',
         'Active R32 account','live','connected',1000000000)'''))
        c.execute(text('''INSERT INTO inbound_jobs(id,organization_id,channel_id,provider,
         fingerprint,encrypted_event,status,attempts,duplicates,next_attempt_at,created_at)
         VALUES('job-r32','org-r32','channel-r32','telegram','test-fingerprint',
         'synthetic-encrypted-placeholder','failed',5,0,1000000000,1000000000)'''))
    engine.dispose()
    alembic('upgrade','head')
    alembic('check')
    engine=create_engine(env['DATABASE_URL'])
    with engine.connect() as c:
        assert c.execute(text("SELECT name FROM organizations WHERE id='org-r32'")).scalar()=='Existing R32 tenant'
        assert c.execute(text("SELECT name FROM channel_connections WHERE id='channel-r32'")).scalar()=='Active R32 account'
        assert c.execute(text("SELECT encrypted_event FROM inbound_jobs WHERE id='job-r32'")).scalar()=='synthetic-encrypted-placeholder'
        assert c.execute(text("SELECT status FROM inbound_jobs WHERE id='job-r32'")).scalar()=='failed'
        assert c.execute(text("SELECT dismissed_at FROM inbound_jobs WHERE id='job-r32'")).scalar() is None
        assert c.execute(text("SELECT inbound_last_dispatched_at FROM channel_connections WHERE id='channel-r32'")).scalar() is None
        assert c.execute(text('SELECT version_num FROM alembic_version')).scalar()==ScriptDirectory.from_config(Config(str(ROOT/'backend/alembic.ini'))).get_current_head()
    engine.dispose()
    print('R32_TO_R33_POPULATED_SQLITE_MIGRATION=PASS')
