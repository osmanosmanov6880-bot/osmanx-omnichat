"""R31 encrypted SQL inbound journal: recovery, access controls and cleanup."""
import hashlib
import hmac
import json
import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import update
from app import db
from app.db import InboundJob, ChannelConnection, Organization, Conversation, Message, AuditLog, now
from app.inbound_jobs import stage, process_one, process_batch, expire_payloads
from app.integrations.adapters import unseal
from conftest import register


def make_channel(owner,provider='telegram',external_id=None):
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=owner['organization']['id'],
            provider=provider,name='R31 local channel',mode='live',status='connected',
            external_account_id=external_id)
        session.add(ch);session.commit()
        return ch.id


def test_signed_meta_stages_and_wipes_ciphertext(client):
    owner=register(client,email='r31meta@example.org')
    channel_id=make_channel(owner,'instagram','r31-page')
    payload={'object':'instagram','entry':[{'id':'r31-page','messaging':[
        {'sender':{'id':'person-1'},'recipient':{'id':'r31-page'},
         'message':{'mid':'mid-r31-1','text':'Персональный вопрос о заказе'},
         'timestamp':int(time.time()*1000)}]}]}
    raw=json.dumps(payload).encode()
    signature='sha256='+hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
    assert client.post('/api/webhooks/instagram',content=raw,
        headers={'X-Hub-Signature-256':'sha256=invalid'}).status_code==403
    assert client.post('/api/webhooks/instagram',content=raw,
        headers={'X-Hub-Signature-256':signature}).json()['accepted']==1
    assert client.post('/api/webhooks/instagram',content=raw,
        headers={'X-Hub-Signature-256':signature}).json()['accepted']==0
    with db.SessionLocal() as session:
        job=session.query(InboundJob).filter_by(channel_id=channel_id).one()
        assert job.status=='done' and job.attempts==1 and job.duplicates==1
        assert job.encrypted_event is None
        assert session.query(Conversation).filter_by(organization_id=owner['organization']['id']).count()==1
        assert session.query(Message).filter_by(organization_id=owner['organization']['id']).count()==1
    overview=client.get('/api/operations/overview').json()
    assert overview['inbound']['done']==1
    assert overview['inbound_duplicates_recorded_24h']==1
    listing=client.get('/api/operations/inbound').json()
    assert len(listing)==1 and listing[0]['status']=='done'
    assert 'Персональный' not in str(listing) and 'person-1' not in str(listing)


def test_failed_inline_processing_is_durable_then_worker_recovers(client,monkeypatch):
    owner=register(client,email='r31restore@example.org')
    channel_id=make_channel(owner,'whatsapp','313131')
    payload={'object':'whatsapp_business_account','entry':[{'changes':[{'value':{
        'metadata':{'phone_number_id':'313131'},
        'messages':[{'id':'r31-msg','from':'70001112233','timestamp':str(int(time.time())),
          'type':'text','text':{'body':'Совершенно приватное сообщение'}}]
    }}]}]}
    raw=json.dumps(payload).encode()
    signature='sha256='+hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
    import app.inbound_jobs as queue
    real=queue.ingest_inbound
    monkeypatch.setattr(queue,'ingest_inbound',lambda *a,**kw: (_ for _ in ()).throw(RuntimeError('private token in error')))
    result=client.post('/api/webhooks/whatsapp',content=raw,
        headers={'X-Hub-Signature-256':signature})
    assert result.status_code==200,result.text
    assert result.json()['accepted']==0
    with db.SessionLocal() as s:
        j=s.query(InboundJob).filter_by(channel_id=channel_id).one()
        assert j.status=='retrying' and j.attempts==1
        assert j.encrypted_event and 'Совершенно приватное' not in j.encrypted_event
        assert unseal(j.encrypted_event)['text']=='Совершенно приватное сообщение'
        assert j.last_error=='RuntimeError' and 'private' not in j.last_error
        assert s.query(Conversation).count()==0
        job_id=j.id
        j.next_attempt_at=0;s.commit()
    monkeypatch.setattr(queue,'ingest_inbound',real)
    assert process_batch(db.SessionLocal)==1
    with db.SessionLocal() as s:
        j=s.get(InboundJob,job_id)
        assert j.status=='done' and j.encrypted_event is None
        assert s.query(Message).one().body=='Совершенно приватное сообщение'
    assert process_batch(db.SessionLocal)==0


def test_dead_letter_manual_retry_and_audit(client,monkeypatch):
    owner=register(client,email='r31manual@example.org')
    channel_id=make_channel(owner)
    with db.SessionLocal() as s:
        job_id=stage(s,channel=s.get(ChannelConnection,channel_id),
            external_chat_id='john',external_message_id='r31-dead-letter',
            sender_id='john',text='Заявка на услугу')
        s.commit()
    import app.inbound_jobs as queue
    normal=queue.ingest_inbound
    monkeypatch.setattr(queue,'ingest_inbound',lambda *a,**kw: (_ for _ in ()).throw(ValueError('sensitive-not-for-client')))
    for k in range(5):
        assert process_one(db.SessionLocal,job_id)==0
        with db.SessionLocal() as s:
            job=s.get(InboundJob,job_id)
            assert job.attempts==k+1
            if k<4:
                assert job.status=='retrying'
                job.next_attempt_at=0;s.commit()
            else:assert job.status=='failed'
    assert process_batch(db.SessionLocal)==0
    listing=client.get('/api/operations/inbound').json()
    assert listing[0]['can_retry'] and listing[0]['last_error']=='ValueError'
    assert 'sensitive' not in str(listing)
    assert client.post(f'/api/operations/inbound/{job_id}/retry',json={'reason':'short'}).status_code==422
    response=client.post(f'/api/operations/inbound/{job_id}/retry',
        json={'reason':'Исправили настройки подключения, разрешаю повтор'})
    assert response.status_code==200,response.text
    assert client.post(f'/api/operations/inbound/{job_id}/retry',
        json={'reason':'Новая попытка другого администратора'}).status_code==409
    with db.SessionLocal() as s:
        entry=s.query(AuditLog).filter_by(action='inbound.manual_retry',entity_id=job_id).one()
        assert entry.organization_id==owner['organization']['id']
        assert s.get(InboundJob,job_id).attempts==0
    monkeypatch.setattr(queue,'ingest_inbound',normal)
    assert process_batch(db.SessionLocal)==1
    assert client.get('/api/operations/inbound').json()[0]['status']=='done'


def test_claim_recovery_is_fenced_and_deduplicates(client):
    owner=register(client,email='r31claim@example.org')
    channel_id=make_channel(owner)
    with db.SessionLocal() as s:
        jid=stage(s,channel=s.get(ChannelConnection,channel_id),
            external_chat_id='abc',external_message_id='first-event',
            sender_id='abc',text='История')
        s.commit()
    with db.SessionLocal() as s:
        s.execute(update(InboundJob).where(InboundJob.id==jid).values(
            status='processing',claim_token='dead-owner',
            claim_expires_at=now()-100, attempts=1))
        s.commit()
    assert process_batch(db.SessionLocal)==1
    assert process_one(db.SessionLocal,jid)==0
    with db.SessionLocal() as s:
        assert s.get(InboundJob,jid).status=='done'
        assert s.query(Message).count()==1


def test_cross_tenant_jobs_and_rights_are_private(client):
    owner=register(client,email='r31tenant@example.org')
    own_ch=make_channel(owner)
    with db.SessionLocal() as s:
        another=Organization(name='Чужая компания')
        s.add(another);s.flush()
        foreign=ChannelConnection(organization_id=another.id,provider='telegram',
            name='foreign',mode='live',status='connected')
        s.add(foreign);s.flush()
        jid=stage(s,channel=foreign,external_chat_id='another-person',
            external_message_id='another-msg',sender_id='another-person',text='Чужое сообщение')
        s.commit()
        assert s.get(InboundJob,jid).organization_id==another.id
    assert client.get('/api/operations/inbound').json()==[]
    assert client.get('/api/operations/overview').json()['inbound']['queued']==0
    assert client.post(f'/api/operations/inbound/{jid}/retry',
        json={'reason':'Попытка взять чужой job'}).status_code==404
    with db.SessionLocal() as s:
        j=s.get(InboundJob,jid)
        assert j.status=='queued' and j.encrypted_event


def test_expired_payload_is_erased_and_not_replayed(client):
    owner=register(client,email='r31expiry@example.org')
    chid=make_channel(owner)
    with db.SessionLocal() as s:
        job=stage(s,channel=s.get(ChannelConnection,chid),
            external_chat_id='obsolete',external_message_id='obsolete-id',
            sender_id='obsolete',text='Удалить по сроку хранения')
        s.execute(update(InboundJob).where(InboundJob.id==job).values(
            created_at=now()-15*86400,status='failed'))
        s.commit()
    with db.SessionLocal() as s:
        result=expire_payloads(s);s.commit()
        assert result['payloads_erased']==1
        item=s.get(InboundJob,job)
        assert item.status=='expired' and item.encrypted_event is None
    assert process_batch(db.SessionLocal)==0
    assert client.post(f'/api/operations/inbound/{job}/retry',
        json={'reason':'Попытка вернуть уничтоженное содержимое'}).status_code==409


def test_legacy_older_message_is_idempotent_after_replay(client):
    owner=register(client,email='r31legacy@example.org')
    chid=make_channel(owner)
    from app.services import ingest_inbound
    with db.SessionLocal() as s:
        ch=s.get(ChannelConnection,chid)
        m=ingest_inbound(s,channel=ch,external_chat_id='same',
            external_message_id='old-event',sender_id='same',sender_name=None,text='Старый текст')
        jid=stage(s,channel=ch,external_chat_id='same',
            external_message_id='old-event',sender_id='same',text='Старый текст')
        s.commit()
    assert process_one(db.SessionLocal,jid)==0
    with db.SessionLocal() as s:
        assert s.query(Message).count()==1
        assert s.get(InboundJob,jid).status=='done'


def test_fifth_crashed_claim_becomes_failed_not_stuck(client):
    owner=register(client,email='r31crash@example.org')
    chid=make_channel(owner)
    with db.SessionLocal() as session:
        jid=stage(session,channel=session.get(ChannelConnection,chid),
            external_chat_id='customer',external_message_id='fifth',sender_id='customer',
            text='Событие перед пятой попыткой')
        session.execute(update(InboundJob).where(InboundJob.id==jid).values(
            status='processing',attempts=5,claim_token='crashed-worker',
            claim_expires_at=now()-60))
        session.commit()
    assert process_batch(db.SessionLocal)==0
    with db.SessionLocal() as session:
        saved=session.get(InboundJob,jid)
        assert saved.status=='failed' and saved.last_error=='worker_claim_expired'
        assert saved.encrypted_event is not None


def test_lead_may_view_but_cannot_requeue_failed_event(client):
    owner=register(client,email='r31roles@example.org')
    chid=make_channel(owner)
    with db.SessionLocal() as session:
        jid=stage(session,channel=session.get(ChannelConnection,chid),
            external_chat_id='guest',external_message_id='role',sender_id='guest',
            text='Клиентский контент скрыт')
        session.execute(update(InboundJob).where(InboundJob.id==jid).values(
            status='failed',attempts=5))
        session.query(db.Membership).filter_by(
            organization_id=owner['organization']['id']).update({'role':'lead'})
        session.commit()
    assert client.get('/api/operations/inbound').status_code==200
    assert client.post(f'/api/operations/inbound/{jid}/retry',
        json={'reason':'Проверил канал перед восстановлением'}).status_code==403
    with db.SessionLocal() as session:
        assert session.get(InboundJob,jid).status=='failed'


def test_workspace_delete_purges_encrypted_inbound_jobs(client):
    owner=register(client,email='r31delete@example.org',name='Компания R31')
    chid=make_channel(owner)
    with db.SessionLocal() as session:
        jid=stage(session,channel=session.get(ChannelConnection,chid),
            external_chat_id='private-id',external_message_id='delete-me',
            sender_id='private-id',text='Только в зашифрованной очереди')
        session.commit()
    response=client.post('/api/organization/delete',json={'confirmation':'Компания R31'})
    assert response.status_code==200,response.text
    with db.SessionLocal() as session:
        assert session.get(InboundJob,jid) is None
        assert session.query(InboundJob).filter_by(organization_id=owner['organization']['id']).count()==0


def test_invalid_signed_event_is_not_stored(client):
    owner=register(client,email='r31invalid@example.org')
    make_channel(owner,'instagram','r31-bad-page')
    payload={'object':'instagram','entry':[{'id':'r31-bad-page','messaging':[
        {'sender':'not-a-dict','message':{'mid':'bad','text':'Should never stage'}}]}]}
    raw=json.dumps(payload).encode()
    signature='sha256='+hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
    r=client.post('/api/webhooks/instagram',content=raw,
        headers={'X-Hub-Signature-256':signature})
    assert r.status_code==422,r.text
    with db.SessionLocal() as session:
        assert session.query(InboundJob).count()==0
