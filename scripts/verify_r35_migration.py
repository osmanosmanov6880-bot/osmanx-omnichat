"""R34 -> R35 populated SQLite upgrade, preserving encrypted queued events."""
import os
import subprocess
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='omnichat-r35-migration-') as temp:
    url='sqlite:///'+str(Path(temp)/'r34.sqlite')
    env=os.environ.copy()
    env['DATABASE_URL']=url
    env['PYTHONPATH']=str(ROOT/'backend')
    def alembic(*args):
        proc=subprocess.run(['alembic','-c',str(ROOT/'backend/alembic.ini'),*args],
            cwd=ROOT,env=env,capture_output=True,text=True,timeout=90)
        assert proc.returncode==0,proc.stdout+'\n'+proc.stderr
    alembic('upgrade','f34000a10001')
    engine=create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("""INSERT INTO organizations(id,name,plan,is_demo,retention_days,
           sla_minutes,currency,timezone,created_at)
           VALUES('org-r35','Existing R34 workspace','starter',0,365,5,'RUB','UTC',1000000000)"""))
        conn.execute(text("""INSERT INTO channel_connections(id,organization_id,provider,name,
           mode,status,created_at,inbound_last_dispatched_at)
           VALUES('channel-r35','org-r35','telegram','Existing R34 account','live',
           'connected',1000000000,1000000042)"""))
        conn.execute(text("""INSERT INTO inbound_jobs(id,organization_id,channel_id,provider,
           fingerprint,encrypted_event,status,attempts,duplicates,next_attempt_at,created_at)
           VALUES('event-r35','org-r35','channel-r35','telegram',
           'r35-fingerprint','SYNTHETIC_ENCRYPTED_R34_CIPHERTEXT','failed',5,0,1000000000,1000000000)"""))
    engine.dispose()
    alembic('upgrade','head')
    alembic('check')
    engine=create_engine(url)
    expected=ScriptDirectory.from_config(Config(str(ROOT/'backend/alembic.ini'))).get_current_head()
    with engine.connect() as conn:
        assert conn.execute(text('SELECT version_num FROM alembic_version')).scalar()==expected
        assert conn.execute(text("SELECT name FROM organizations WHERE id='org-r35'")).scalar()=='Existing R34 workspace'
        assert conn.execute(text("SELECT encrypted_event FROM inbound_jobs WHERE id='event-r35'")).scalar()=='SYNTHETIC_ENCRYPTED_R34_CIPHERTEXT'
        assert conn.execute(text("SELECT status FROM inbound_jobs WHERE id='event-r35'")).scalar()=='failed'
        assert conn.execute(text("SELECT inbound_last_dispatched_at FROM channel_connections WHERE id='channel-r35'")).scalar()==1000000042
        assert conn.execute(text("SELECT inbound_last_dispatched_at FROM organizations WHERE id='org-r35'")).scalar() is None
    engine.dispose()
print('R34_TO_R35_POPULATED_MIGRATION=PASS')
