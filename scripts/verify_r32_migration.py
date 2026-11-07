"""Rehearse R31 -> R32 on a populated disposable SQLite database."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='omnichat-r32-upgrade-') as directory:
    target=Path(directory)/'existing-r31.db'
    env=os.environ.copy()
    env['DATABASE_URL']='sqlite:///'+str(target)
    env['PYTHONPATH']=str(ROOT/'backend')
    def alembic(*args):
        subprocess.run(['alembic','-c',str(ROOT/'backend/alembic.ini'),*args],
                       cwd=ROOT,env=env,check=True,capture_output=True,text=True)
    alembic('upgrade','f31000a10001')
    engine=create_engine(env['DATABASE_URL'])
    with engine.begin() as conn:
        conn.execute(text('''INSERT INTO organizations
          (id,name,plan,is_demo,retention_days,sla_minutes,currency,timezone,created_at)
          VALUES ('tenant-r31','Existing company','starter',0,365,5,'RUB','UTC',1700000000)'''))
        conn.execute(text('''INSERT INTO channel_connections
          (id,organization_id,provider,name,mode,status,created_at)
          VALUES ('account-r31','tenant-r31','telegram','Telegram old','live','connected',1700000000)'''))
        conn.execute(text('''INSERT INTO inbound_jobs
          (id,organization_id,channel_id,provider,fingerprint,encrypted_event,status,
           attempts,duplicates,next_attempt_at,created_at)
          VALUES ('event-r31','tenant-r31','account-r31','telegram','fake-sha256-digest',
                  'synthetic-test-ciphertext','queued',0,0,1700000000,1700000000)'''))
    engine.dispose()
    alembic('upgrade','head')
    alembic('check')
    engine=create_engine(env['DATABASE_URL'])
    with engine.connect() as conn:
        assert conn.execute(text("SELECT name FROM organizations WHERE id='tenant-r31'")).scalar()=='Existing company'
        assert conn.execute(text("SELECT name FROM channel_connections WHERE id='account-r31'")).scalar()=='Telegram old'
        assert conn.execute(text("SELECT encrypted_event FROM inbound_jobs WHERE id='event-r31'")).scalar()=='synthetic-test-ciphertext'
        assert conn.execute(text("SELECT inbound_paused_at FROM organizations WHERE id='tenant-r31'")).scalar() is None
        assert conn.execute(text("SELECT inbound_paused_at FROM channel_connections WHERE id='account-r31'")).scalar() is None
        assert conn.execute(text('SELECT version_num FROM alembic_version')).scalar()==ScriptDirectory.from_config(Config(str(ROOT/'backend/alembic.ini'))).get_current_head()
    engine.dispose()
    print('R32_EXISTING_SQLITE_R31_TO_CURRENT_HEAD=PASS')
