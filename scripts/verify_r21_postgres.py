"""CI-only PostgreSQL check: two staff edits based on one version cannot both win.

Use only an isolated PostgreSQL test database. This script refuses to run on
production and creates/removes its own tenant and conversation rows.
"""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy import update, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import make_url
from app.db import Organization, ChannelConnection, Contact, Conversation, engine_for, assert_schema_current, uid

url=os.environ.get('DATABASE_URL','')
parsed=make_url(url)
if parsed.get_backend_name()!='postgresql' or parsed.database!='omnichat_ci' or os.environ.get('APP_ENV')=='production':
    raise SystemExit('PostgreSQL concurrency test requires disposable omnichat_ci DB')
engine=engine_for(url)
assert assert_schema_current(engine)
Session=sessionmaker(bind=engine)
org_id=uid()
with Session() as session:
    org=Organization(id=org_id,name='R21 isolated concurrency test')
    session.add(org);session.flush()
    channel=ChannelConnection(organization_id=org_id,provider='telegram',name='Test channel',mode='demo',status='connected')
    contact=Contact(organization_id=org_id,name='Test visitor')
    session.add_all([channel,contact]);session.flush()
    conv=Conversation(organization_id=org_id,channel_id=channel.id,contact_id=contact.id,external_chat_id='r21-isolation')
    session.add(conv);session.commit()
    conv_id=conv.id;expected=conv.version
barrier=Barrier(2)

def attempt(state):
    with Session() as session:
        barrier.wait(timeout=10)
        changed=session.execute(update(Conversation).where(
            Conversation.organization_id==org_id,
            Conversation.id==conv_id,
            Conversation.version==expected
        ).values(status=state,version=Conversation.version+1)).rowcount
        session.commit()
        return changed
try:
    with ThreadPoolExecutor(max_workers=2) as executor:
        tasks=[executor.submit(attempt,state) for state in ('waiting','closed')]
        results=[t.result(timeout=15) for t in tasks]
    assert sorted(results)==[0,1],results
    with Session() as session:
        saved=session.get(Conversation,conv_id)
        assert saved.version==expected+1 and saved.status in ('waiting','closed')
    print('R21_POSTGRES_ATOMIC_CAS_PASS: exactly one edit committed')
finally:
    with Session() as session:
        session.execute(text('DELETE FROM conversations WHERE id=:id'),{'id':conv_id})
        session.execute(text('DELETE FROM contacts WHERE organization_id=:o'),{'o':org_id})
        session.execute(text('DELETE FROM channel_connections WHERE organization_id=:o'),{'o':org_id})
        session.execute(text('DELETE FROM organizations WHERE id=:o'),{'o':org_id})
        session.commit()
    engine.dispose()
