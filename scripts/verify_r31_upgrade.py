"""Upgrade a real populated SQLite R30 schema to R31 without losing data."""
import os
import sqlite3
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='r31-upgrade-') as directory:
    database=Path(directory)/'previous.db'
    env={**os.environ,'DATABASE_URL':'sqlite:///'+str(database)}
    command=['alembic','-c','backend/alembic.ini','upgrade']
    subprocess.run(command+['f28000a10001'],cwd=ROOT,env=env,check=True,capture_output=True)
    with sqlite3.connect(database) as db:
        db.execute('INSERT INTO organizations(id,name,plan,is_demo,retention_days,sla_minutes,currency,timezone,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                   ('r30-org','Компания прошлого релиза','starter',0,365,5,'RUB','UTC',1234.0))
        db.execute('INSERT INTO channel_connections(id,organization_id,provider,name,mode,status,created_at) VALUES(?,?,?,?,?,?,?)',
                   ('r30-ch','r30-org','telegram','Старый канал','live','connected',1234.0))
        db.execute('INSERT INTO contacts(id,organization_id,name,tags,stage,deal_confirmed,created_at) VALUES(?,?,?,?,?,?,?)',
                   ('r30-contact','r30-org','Старый клиент','[]','new',0,1234.0))
        db.execute('INSERT INTO conversations(id,organization_id,channel_id,contact_id,external_chat_id,status,priority,pinned,archived,unread_count,version,last_message_at,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                   ('r30-conv','r30-org','r30-ch','r30-contact','old-external','new','normal',0,0,1,1,1234.0,1234.0))
        db.execute('INSERT INTO messages(id,organization_id,conversation_id,external_id,direction,kind,body,delivery_status,is_demo,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)',
                   ('r30-msg','r30-org','r30-conv','old-remote-msg','in','text','Старый клиентский вопрос','delivered',0,1234.0))
        db.commit()
    subprocess.run(command+['head'],cwd=ROOT,env=env,check=True,capture_output=True)
    subprocess.run(['alembic','-c','backend/alembic.ini','check'],cwd=ROOT,env=env,check=True,capture_output=True)
    with sqlite3.connect(database) as db:
        assert db.execute('SELECT name FROM organizations WHERE id="r30-org"').fetchone()==('Компания прошлого релиза',)
        assert db.execute('SELECT name FROM channel_connections WHERE id="r30-ch"').fetchone()==('Старый канал',)
        assert db.execute('SELECT body FROM messages WHERE id="r30-msg"').fetchone()==('Старый клиентский вопрос',)
        assert db.execute('SELECT unread_count FROM conversations WHERE id="r30-conv"').fetchone()==(1,)
        assert db.execute('SELECT version_num FROM alembic_version').fetchone()==('f31000a10001',)
        assert db.execute('SELECT count(*) FROM inbound_jobs').fetchone()==(0,)
print('R31_EXISTING_R30_DATABASE_UPGRADE_AND_PRESERVATION=PASS')
