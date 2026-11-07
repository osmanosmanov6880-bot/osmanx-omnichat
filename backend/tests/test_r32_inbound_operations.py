"""R32: multi-tenant incident controls, bounded webhook admission, safe triage."""
import hashlib
import hmac
import json
import time
from sqlalchemy import update
from app import db
from app.db import Organization, ChannelConnection, InboundJob, Message, AuditLog, now
from app.inbound_jobs import stage, process_batch, process_one
from conftest import register


def channel_for(owner, provider='telegram', external=None):
    with db.SessionLocal() as session:
        ch=ChannelConnection(organization_id=owner['organization']['id'],
            name='R32 local channel',provider=provider,mode='live',status='connected',
            external_account_id=external)
        session.add(ch);session.commit()
        return ch.id


def make_event(channel_id, suffix, *, state='queued'):
    with db.SessionLocal() as session:
        ch=session.get(ChannelConnection,channel_id)
        job_id=stage(session,channel=ch,external_chat_id='client-'+suffix,
            external_message_id='message-'+suffix,sender_id='client-'+suffix,
            text='Новая заявка: '+suffix)
        if state!='queued':
            session.execute(update(InboundJob).where(InboundJob.id==job_id).values(
                status=state,attempts=5,last_error='ValueError'))
        session.commit()
        return job_id


def test_company_pause_preserves_ingress_and_resumes(client):
    owner=register(client,email='r32-company-pause@example.org')
    chid=channel_for(owner)
    response=client.post('/api/operations/inbound/pause',json={
        'scope':'organization','reason':'Проводится проверка целостности базы'})
    assert response.status_code==200,response.text
    assert client.post('/api/operations/inbound/pause',json={
        'scope':'organization','reason':'Дублировать паузу не надо'}).status_code==409
    queued=make_event(chid,'paused')
    assert process_batch(db.SessionLocal)==0
    with db.SessionLocal() as session:
        job=session.get(InboundJob,queued)
        assert job.status=='queued' and job.attempts==0 and job.encrypted_event
        assert session.query(Message).count()==0
    overview=client.get('/api/operations/overview').json()
    assert overview['organization_inbound_paused_at'] is not None
    assert overview['inbound']['queued']==1
    assert client.post('/api/operations/inbound/resume',json={
        'scope':'organization','reason':'Проверка завершена безопасно'}).status_code==200
    assert process_batch(db.SessionLocal)==1
    with db.SessionLocal() as session:
        job=session.get(InboundJob,queued)
        assert job.status=='done' and job.encrypted_event is None
        actions=[x.action for x in session.query(AuditLog).filter_by(
            organization_id=owner['organization']['id']).all()]
        assert 'inbound.pause.organization' in actions
        assert 'inbound.resume.organization' in actions


def test_per_channel_pause_is_independent_from_company_and_other_channels(client):
    owner=register(client,email='r32-channel-pause@example.org')
    first=channel_for(owner,external='r32-one')
    second=channel_for(owner,external='r32-two')
    assert client.post('/api/operations/inbound/pause',json={
        'scope':'channel','channel_id':first,'reason':'Ошибки канала при проверке'}).status_code==200
    pending=make_event(first,'waiting')
    ready=make_event(second,'active')
    assert process_batch(db.SessionLocal)==1
    with db.SessionLocal() as session:
        assert session.get(InboundJob,pending).status=='queued'
        assert session.get(InboundJob,ready).status=='done'
    assert client.post('/api/operations/inbound/pause',json={
        'scope':'organization','reason':'Аварийное расследование доставки'}).status_code==200
    third=make_event(second,'also-waiting')
    assert process_batch(db.SessionLocal)==0
    assert client.post('/api/operations/inbound/resume',json={
        'scope':'organization','reason':'Восстанавливаем только второй канал'}).status_code==200
    assert process_batch(db.SessionLocal)==1
    with db.SessionLocal() as session:
        assert session.get(InboundJob,pending).status=='queued'
        assert session.get(InboundJob,third).status=='done'
    assert client.post('/api/operations/inbound/resume',json={
        'scope':'channel','channel_id':first,'reason':'Канал проверен и готов'}).status_code==200
    assert process_batch(db.SessionLocal)==1


def test_paused_newly_claimed_event_is_requeued_without_attempt(monkeypatch,client):
    owner=register(client,email='r32-claim-pause@example.org')
    chid=channel_for(owner)
    jid=make_event(chid,'claim-before-pause')
    import app.inbound_jobs as queue
    claim=queue._claim
    def pause_after_claim(factory,identity,**kwargs):
        token=claim(factory,identity,**kwargs)
        with factory() as session:
            session.execute(update(Organization).where(
                Organization.id==owner['organization']['id']).values(
                inbound_paused_at=now(),inbound_pause_reason='Смена оператора'))
            session.commit()
        return token
    monkeypatch.setattr(queue,'_claim',pause_after_claim)
    assert process_one(db.SessionLocal,jid)==0
    with db.SessionLocal() as session:
        item=session.get(InboundJob,jid)
        assert item.status=='queued' and item.attempts==0 and item.claim_token is None


def test_lead_cannot_pause_or_bulk_retry_and_other_tenant_is_private(client):
    owner=register(client,email='r32-lead@example.org')
    own=channel_for(owner)
    with db.SessionLocal() as session:
        foreign=Organization(name='Private company')
        session.add(foreign);session.flush()
        their=ChannelConnection(organization_id=foreign.id,provider='telegram',
            name='Private',status='connected',mode='live')
        session.add(their);session.commit()
        foreign_id=their.id
    assert client.post('/api/operations/inbound/pause',json={
        'scope':'channel','channel_id':foreign_id,
        'reason':'Проверить чужую компанию'}).status_code==404
    assert client.post('/api/operations/inbound/retry-batch',json={
        'channel_id':foreign_id,'reason':'Не разрешённый повтор'}).status_code==404
    with db.SessionLocal() as session:
        session.query(db.Membership).filter_by(
            organization_id=owner['organization']['id']).update({'role':'lead'})
        session.commit()
    assert client.get('/api/operations/inbound/triage').status_code==200
    assert client.post('/api/operations/inbound/pause',json={
        'scope':'organization','reason':'Лиду нельзя останавливать'}).status_code==403
    assert client.post('/api/operations/inbound/retry-batch',json={
        'channel_id':own,'reason':'Лиду нельзя повторять'}).status_code==403


def signed_instagram(client,page,body):
    payload={'object':'instagram','entry':[{'id':page,'messaging':[{'sender':{'id':'person'},
        'recipient':{'id':page},'message':{'mid':body,'text':body},
        'timestamp':int(time.time()*1000)}]}]}
    raw=json.dumps(payload).encode()
    header='sha256='+hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
    return client.post('/api/webhooks/instagram',content=raw,
                       headers={'X-Hub-Signature-256':header})


def test_real_signed_webhook_stores_during_pause(client):
    owner=register(client,email='r32-signed-pause@example.org')
    ch=channel_for(owner,'instagram','r32-ig')
    assert client.post('/api/operations/inbound/pause',json={
        'scope':'organization','reason':'Проверка входящих после обновления'}).status_code==200
    response=signed_instagram(client,'r32-ig','signed-paused')
    assert response.status_code==200,response.text
    assert response.json()['accepted']==0
    with db.SessionLocal() as session:
        job=session.query(InboundJob).filter_by(channel_id=ch).one()
        assert job.status=='queued' and job.encrypted_event
    client.post('/api/operations/inbound/resume',json={
        'scope':'organization','reason':'Успешная проверка входящего'})
    assert process_batch(db.SessionLocal)==1


def test_webhook_capacity_returns_503_and_does_not_ack(monkeypatch,client):
    monkeypatch.setenv('INBOUND_MAX_PENDING_PER_CHANNEL','2')
    owner=register(client,email='r32-capacity@example.org')
    chid=channel_for(owner,'instagram','r32-capacity-page')
    client.post('/api/operations/inbound/pause',json={
        'scope':'organization','reason':'Нагрузочное испытание входящих'})
    assert signed_instagram(client,'r32-capacity-page','first').status_code==200
    assert signed_instagram(client,'r32-capacity-page','second').status_code==200
    # Duplicate remains safely acknowledged; no new job is created.
    d=signed_instagram(client,'r32-capacity-page','first')
    assert d.status_code==200 and d.json()['accepted']==0
    denied=signed_instagram(client,'r32-capacity-page','third')
    assert denied.status_code==503 and denied.headers['retry-after']=='30'
    with db.SessionLocal() as session:
        assert session.query(InboundJob).filter_by(channel_id=chid).count()==2
        assert session.query(InboundJob).filter_by(channel_id=chid).first().encrypted_event
    client.post('/api/operations/inbound/resume',json={
        'scope':'organization','reason':'Нагрузочное испытание окончено'})
    assert process_batch(db.SessionLocal)==2
    assert signed_instagram(client,'r32-capacity-page','third').status_code==200


def test_capacity_is_per_channel_not_per_tenant(monkeypatch,client):
    monkeypatch.setenv('INBOUND_MAX_PENDING_PER_CHANNEL','1')
    owner=register(client,email='r32-capacity-channels@example.org')
    first=channel_for(owner)
    second=channel_for(owner)
    make_event(first,'a')
    make_event(second,'b')
    with db.SessionLocal() as session:
        ch=session.get(ChannelConnection,first)
        from app.inbound_jobs import InboundCapacityExceeded
        try:
            stage(session,channel=ch,external_chat_id='new',external_message_id='new',sender_id='new')
            raise AssertionError('Must be at capacity')
        except InboundCapacityExceeded:
            pass
    assert process_batch(db.SessionLocal)==2


def test_bulk_recovery_bounded_idempotent_audited(client):
    owner=register(client,email='r32-batch@example.org')
    chid=channel_for(owner)
    for index in range(29):make_event(chid,str(index),state='failed')
    payload={'channel_id':chid,'reason':'Проверены настройки, повторить пакет','limit':20}
    reply=client.post('/api/operations/inbound/retry-batch',json=payload)
    assert reply.status_code==200,reply.text
    assert reply.json()['requeued']==20
    with db.SessionLocal() as session:
        assert session.query(InboundJob).filter_by(channel_id=chid,status='queued').count()==20
        assert session.query(InboundJob).filter_by(channel_id=chid,status='failed').count()==9
        assert session.query(AuditLog).filter_by(action='inbound.batch_retry',entity_id=chid).count()==1
    second=client.post('/api/operations/inbound/retry-batch',json=payload)
    assert second.status_code==200 and second.json()['requeued']==9
    assert client.post('/api/operations/inbound/retry-batch',json=payload).status_code==409
    assert process_batch(db.SessionLocal,limit=40)==29


def test_expired_payload_cannot_be_manually_retried(client):
    owner=register(client,email='r32-ttl@example.org')
    chid=channel_for(owner)
    jid=make_event(chid,'too-old',state='failed')
    with db.SessionLocal() as session:
        session.execute(update(InboundJob).where(InboundJob.id==jid).values(
            created_at=now()-15*86400))
        session.commit()
    assert client.post('/api/operations/inbound/retry-batch',json={
        'channel_id':chid,'reason':'Повторить слишком старое событие'}).status_code==409
    assert client.post(f'/api/operations/inbound/{jid}/retry',json={
        'reason':'Повторить слишком старое событие'}).status_code==409


def test_filtered_triage_pages_without_duplicates(client):
    owner=register(client,email='r32-triage@example.org')
    chid=channel_for(owner)
    other=channel_for(owner)
    jobs=[make_event(chid,str(i),state='failed') for i in range(6)]
    make_event(other,'elsewhere',state='failed')
    # identical timestamps are common in batched imports; cursor uses (time,id)
    with db.SessionLocal() as session:
        session.execute(update(InboundJob).where(InboundJob.id.in_(jobs)).values(created_at=1700000000))
        session.commit()
    cursor='';seen=[]
    while True:
        page=client.get('/api/operations/inbound/triage',params={
            'status':'failed','channel_id':chid,'limit':2, 'before':cursor})
        assert page.status_code==200,page.text
        body=page.json()
        seen.extend([item['id'] for item in body['items']])
        assert all('encrypted_event' not in item and 'fingerprint' not in item for item in body['items'])
        cursor=body['next_cursor']
        if not cursor:break
    assert len(seen)==6 and len(set(seen))==6
    assert client.get('/api/operations/inbound/triage',params={'before':'invalid***'}).status_code==422
    assert client.get('/api/operations/inbound/triage',params={'status':'unknown'}).status_code==422
    assert client.get('/api/operations/inbound/triage',params={'channel_id':other}).json()['items'][0]['channel_id']==other


def test_capacity_does_not_erase_or_duplicate_existing_completed_event(monkeypatch,client):
    monkeypatch.setenv('INBOUND_MAX_PENDING_PER_CHANNEL','1')
    owner=register(client,email='r32-idem@example.org')
    chid=channel_for(owner)
    old=make_event(chid,'done')
    assert process_batch(db.SessionLocal)==1
    pending=make_event(chid,'pending')
    with db.SessionLocal() as session:
        ch=session.get(ChannelConnection,chid)
        previous=stage(session,channel=ch,external_chat_id='client-done',
            external_message_id='message-done',sender_id='client-done')
        assert previous==old
        session.commit()
        assert session.get(InboundJob,old).duplicates==1
        assert session.get(InboundJob,pending).encrypted_event
