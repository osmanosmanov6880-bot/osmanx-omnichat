"""CI-only PostgreSQL 16 real two-session delivery receipt verification.

No network provider API, no production DB and no customer data. Requires an
already migrated disposable DATABASE_URL supplied by GitHub Actions.
"""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy.orm import sessionmaker

from app.db import (engine_for,assert_schema_current,Organization,ChannelConnection,
    Contact,Conversation,Message,ProviderDeliveryReceipt,uid)
from app.provider_receipts import record_whatsapp_receipt,reconcile_whatsapp_receipt

url=os.environ.get('DATABASE_URL','')
if not url.startswith(('postgresql://','postgresql+psycopg://')) or os.getenv('APP_ENV')=='production':
    raise SystemExit('R24 test requires a disposable PostgreSQL CI database')
engine=engine_for(url)
assert engine.dialect.name=='postgresql'
assert_schema_current(engine)
Session=sessionmaker(bind=engine,expire_on_commit=False)
try:
    with Session() as session:
        org=Organization(name='R24 PostgreSQL receipt test')
        session.add(org);session.flush()
        ch=ChannelConnection(organization_id=org.id,provider='whatsapp',name='R24 isolated WABA',
            external_account_id='r24-ci-'+uid(),mode='live',status='connected')
        contact=Contact(organization_id=org.id,name='R24 test')
        session.add_all([ch,contact]);session.flush()
        conv=Conversation(organization_id=org.id,channel_id=ch.id,contact_id=contact.id,
            external_chat_id='79000001234',external_recipient_id='79000001234')
        session.add(conv);session.flush()
        msg=Message(organization_id=org.id,conversation_id=conv.id,direction='out',
            body='test receipt, no external API',external_id='wamid.r24-postgres',
            delivery_status='accepted')
        session.add(msg);session.commit()
        channel_id,message_id=ch.id,msg.id

    barrier=Barrier(2)
    def put(status):
        with Session() as session:
            channel=session.get(ChannelConnection,channel_id)
            barrier.wait(timeout=10)
            ok=record_whatsapp_receipt(session,channel,'wamid.r24-postgres',
                                       status,'79000001234')
            session.commit()
            return ok
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(put,state) for state in ('read','sent')]
        assert all(x.result(timeout=25) for x in futures)
    with Session() as session:
        receipt=session.get(ProviderDeliveryReceipt,(channel_id,'wamid.r24-postgres'))
        assert receipt.status=='read'
        assert reconcile_whatsapp_receipt(session,channel_id,'wamid.r24-postgres')
        session.commit()
        assert session.get(Message,message_id).delivery_status=='read'
        channel=session.get(ChannelConnection,channel_id)
        assert not record_whatsapp_receipt(session,channel,'wamid.r24-postgres',
                                           'failed','wrong-recipient')
        assert session.get(ProviderDeliveryReceipt,(channel_id,'wamid.r24-postgres')).status=='read'
    print('R24_POSTGRES_RECEIPTS_PASS: competing upserts, CAS, read > sent, recipient guard')
finally:
    engine.dispose()
