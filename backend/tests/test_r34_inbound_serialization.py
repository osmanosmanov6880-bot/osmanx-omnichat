"""R34: channel-scoped fenced inbound claims, recoverability and reviewed replays."""
import json
from sqlalchemy import update
from cryptography.fernet import Fernet
from app import db
from app.db import Organization, ChannelConnection, InboundJob, Message, AuditLog, now
from app.inbound_jobs import stage, _claim, _release_channel, process_one, process_batch
from conftest import register


def channel(org_id, name='Telegram support'):
    with db.SessionLocal() as s:
        c=ChannelConnection(organization_id=org_id,name=name,provider='telegram',
                            mode='live',status='connected')
        s.add(c);s.commit();return c.id


def event(cid, key, status=None):
    with db.SessionLocal() as s:
        c=s.get(ChannelConnection,cid)
        job=stage(s,channel=c,external_chat_id='chat-'+key,
                  external_message_id='message-'+key,sender_id='sender-'+key,
                  sender_name='Test client',text='SECRET_R34_PAYLOAD')
        if status:
            s.execute(update(InboundJob).where(InboundJob.id==job).values(
                status=status,attempts=5 if status=='failed' else 0,
                last_error='SyntheticFailure' if status=='failed' else None))
        s.commit();return job


def test_one_claim_per_channel_and_parallel_other_channel(client):
    owner=register(client,'r34-claim@example.org')
    cid=channel(owner['organization']['id'])
    other=channel(owner['organization']['id'],'Second account')
    first,second,different=event(cid,'one'),event(cid,'two'),event(other,'third')
    first_token=_claim(db.SessionLocal,first)
    assert first_token
    assert _claim(db.SessionLocal,second) is None
    assert _claim(db.SessionLocal,different) is not None
    with db.SessionLocal() as s:
        assert s.get(InboundJob,first).status=='processing'
        assert s.get(InboundJob,second).status=='queued'
        row=s.get(ChannelConnection,cid)
        assert row.inbound_processing_token==first_token
        assert row.inbound_processing_job_id==first
        assert row.inbound_processing_until>now()
        # Old tokens cannot release a new owner's slot.
        assert _release_channel(s,second,'not-the-owner')==0
        s.rollback()


def test_claim_cas_failure_rolls_back_reserved_channel_slot(client):
    owner=register(client,'r34-claim-rollback@example.org')
    cid=channel(owner['organization']['id'])
    jid=event(cid,'done',status='failed')
    assert _claim(db.SessionLocal,jid) is None
    with db.SessionLocal() as s:
        row=s.get(ChannelConnection,cid)
        assert row.inbound_processing_token is None
        assert row.inbound_last_dispatched_at is None
        assert s.get(InboundJob,jid).status=='failed'


def test_completed_events_release_slot_and_allow_following_event(client):
    owner=register(client,'r34-serial-process@example.org')
    cid=channel(owner['organization']['id'])
    first,second=event(cid,'first'),event(cid,'second')
    assert process_one(db.SessionLocal,first)==1
    assert process_one(db.SessionLocal,second)==1
    with db.SessionLocal() as s:
        row=s.get(ChannelConnection,cid)
        assert row.inbound_processing_token is None
        assert row.inbound_processing_until is None
        assert s.get(InboundJob,first).status=='done'
        assert s.get(InboundJob,second).status=='done'
        assert s.query(Message).count()==2


def test_expired_channel_lease_is_reclaimable_and_old_token_fenced(client):
    owner=register(client,'r34-reclaim@example.org')
    cid=channel(owner['organization']['id'])
    first,second=event(cid,'stale'),event(cid,'fresh')
    old=_claim(db.SessionLocal,first)
    assert old
    with db.SessionLocal() as s:
        # Simulate a crashed worker whose lease and claim both expired.
        s.execute(update(ChannelConnection).where(ChannelConnection.id==cid)
                  .values(inbound_processing_until=now()-10))
        s.execute(update(InboundJob).where(InboundJob.id==first)
                  .values(claim_expires_at=now()-10))
        s.commit()
    replacement=_claim(db.SessionLocal,second)
    assert replacement and replacement!=old
    with db.SessionLocal() as s:
        assert _release_channel(s,first,old)==0
        s.rollback()
    assert process_one(db.SessionLocal,first)==0
    with db.SessionLocal() as s:
        assert s.get(ChannelConnection,cid).inbound_processing_token==replacement


def test_pause_resets_claim_and_releases_slot(client):
    owner=register(client,'r34-pause-claim@example.org')
    cid=channel(owner['organization']['id'])
    job=event(cid,'paused')
    with db.SessionLocal() as s:
        s.execute(update(ChannelConnection).where(ChannelConnection.id==cid)
                  .values(inbound_paused_at=now()))
        s.commit()
    assert process_one(db.SessionLocal,job)==0
    with db.SessionLocal() as s:
        row=s.get(ChannelConnection,cid)
        assert row.inbound_processing_token is None
        assert s.get(InboundJob,job).status=='queued'
        assert s.get(InboundJob,job).attempts==0


def test_unreadable_encrypted_payload_quarantined_immediately_and_recoverable(client,monkeypatch):
    owner=register(client,'r34-crypto@example.org')
    cid=channel(owner['organization']['id'])
    job=event(cid,'rotated')
    original=__import__('os').environ['INTEGRATION_ENCRYPTION_KEY']
    monkeypatch.setenv('INTEGRATION_ENCRYPTION_KEY',Fernet.generate_key().decode())
    assert process_one(db.SessionLocal,job)==0
    with db.SessionLocal() as s:
        r=s.get(InboundJob,job)
        assert r.status=='failed' and r.attempts==1
        assert r.last_error=='encryption_key_unavailable' and r.encrypted_event
        assert s.get(ChannelConnection,cid).inbound_processing_token is None
    # Operator repairs the secret and explicitly retries. No auto-blind retry.
    monkeypatch.setenv('INTEGRATION_ENCRYPTION_KEY',original)
    response=client.post('/api/operations/inbound/'+job+'/retry',json={
        'reason':'Возвращён штатный ключ расшифрования, проверена очередь'})
    assert response.status_code==200,response.text
    assert process_one(db.SessionLocal,job)==1


def test_decrypted_but_malformed_event_immediately_quarantined(client):
    from app.integrations.adapters import seal
    owner=register(client,'r34-corrupt@example.org')
    cid=channel(owner['organization']['id'])
    job=event(cid,'invalid')
    with db.SessionLocal() as s:
        s.execute(update(InboundJob).where(InboundJob.id==job)
                  .values(encrypted_event=seal({'sender_id':'bad'})))
        s.commit()
    assert process_one(db.SessionLocal,job)==0
    with db.SessionLocal() as s:
        r=s.get(InboundJob,job)
        assert r.status=='failed' and r.attempts==1
        assert r.last_error=='invalid_encrypted_event'
        assert s.query(Message).count()==0


def test_signed_replay_preview_confirm_atomic_and_audited(client):
    owner=register(client,'r34-preview@example.org')
    cid=channel(owner['organization']['id'])
    jobs=[event(cid,str(i),status='failed') for i in range(4)]
    preview=client.post('/api/operations/inbound/retry-batch/preview',
                        json={'channel_id':cid,'limit':3})
    assert preview.status_code==200,preview.text
    body=preview.json()
    assert body['count']==3 and len(body['proof'])>40
    assert 'SECRET_R34' not in json.dumps(body)
    confirmed=client.post('/api/operations/inbound/retry-batch-confirm',json={
        'proof':body['proof'],'reason':'Перепроверена причина ошибки и восстановлен ключ'})
    assert confirmed.status_code==200,confirmed.text
    assert confirmed.json()['requeued']==3
    with db.SessionLocal() as s:
        assert s.query(InboundJob).filter_by(channel_id=cid,status='queued').count()==3
        assert s.query(InboundJob).filter_by(channel_id=cid,status='failed').count()==1
        assert s.query(AuditLog).filter_by(
            organization_id=owner['organization']['id'],
            action='inbound.reviewed_batch_retry').count()==1
    assert client.post('/api/operations/inbound/retry-batch-confirm',json={
        'proof':body['proof'],'reason':'Повтор той же команды с тем же планом'}).status_code==409


def test_replay_preview_expires_on_concurrent_change(client):
    owner=register(client,'r34-stale-preview@example.org')
    cid=channel(owner['organization']['id'])
    first=event(cid,'a',status='failed')
    preview=client.post('/api/operations/inbound/retry-batch/preview',json={
        'channel_id':cid,'limit':20}).json()
    event(cid,'b',status='failed')
    result=client.post('/api/operations/inbound/retry-batch-confirm',json={
        'proof':preview['proof'],'reason':'Проверил журнал и все записи в очереди'})
    assert result.status_code==409,result.text
    with db.SessionLocal() as s:
        assert s.get(InboundJob,first).status=='failed'


def test_replay_preview_rejects_tampering_and_foreign_tenant(client):
    owner=register(client,'r34-proof-security@example.org')
    cid=channel(owner['organization']['id'])
    event(cid,'secure',status='failed')
    raw=client.post('/api/operations/inbound/retry-batch/preview',json={
        'channel_id':cid,'limit':20}).json()['proof']
    broken=raw[:-1]+('1' if raw[-1]!='1' else '2')
    assert client.post('/api/operations/inbound/retry-batch-confirm',json={
        'proof':broken,'reason':'Проверил полный журнал обработки события'}).status_code==409
    assert client.post('/api/operations/inbound/retry-batch/preview',json={
        'channel_id':'not-owned','limit':20}).status_code==404
    with db.SessionLocal() as s:
        x=s.get(InboundJob,s.query(InboundJob.id).filter_by(channel_id=cid).scalar())
        assert x.status=='failed'


def test_replay_preview_lead_read_only(client):
    owner=register(client,'r34-lead-preview@example.org')
    cid=channel(owner['organization']['id'])
    with db.SessionLocal() as s:
        s.query(db.Membership).filter_by(organization_id=owner['organization']['id']).update({'role':'lead'})
        s.commit()
    assert client.get('/api/operations/inbound/health').status_code==200
    assert client.post('/api/operations/inbound/retry-batch/preview',json={
        'channel_id':cid,'limit':5}).status_code==403


def test_health_exposes_lease_count_but_never_owner_token(client):
    owner=register(client,'r34-health@example.org')
    cid=channel(owner['organization']['id'])
    jid=event(cid,'health')
    token=_claim(db.SessionLocal,jid)
    overview=client.get('/api/operations/overview').json()
    assert overview['inbound_active_accounts']==1
    info=client.get('/api/operations/inbound/health').json()
    assert info['channels'][0]['actively_processing'] is True
    assert 'SECRET_R34' not in json.dumps(info)
    assert token not in json.dumps(overview)+json.dumps(info)
    with db.SessionLocal() as s:
        s.execute(update(InboundJob).where(InboundJob.id==jid)
                  .values(claim_expires_at=now()-5))
        s.commit()
    assert client.get('/api/operations/overview').json()['inbound_stalled_claims']==1
