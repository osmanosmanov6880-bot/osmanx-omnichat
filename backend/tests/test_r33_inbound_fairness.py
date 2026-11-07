"""R33: fair multi-tenant queue, irreversible encrypted-event disposition, health."""
import json
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import update
from app import db
from app.db import Organization, ChannelConnection, InboundJob, Message, AuditLog, now
from app.inbound_jobs import stage, process_batch, expire_payloads
from conftest import register


def add_channel(owner, name, provider='telegram'):
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=owner['organization']['id'],
             name=name, provider=provider, mode='live', status='connected')
        session.add(channel)
        session.commit()
        return channel.id


def add_job(chid, ident, status='queued', created=None):
    with db.SessionLocal() as session:
        channel=session.get(ChannelConnection,chid)
        jid=stage(session,channel=channel,external_chat_id='c-'+ident,
                  external_message_id='m-'+ident,sender_id='c-'+ident,
                  text='CLIENT_SECRET_R33_NEVER_IN_HEALTH')
        if status=='failed':
            session.execute(update(InboundJob).where(InboundJob.id==jid).values(
                status='failed',attempts=5,last_error='synthetic_error'))
        if created is not None:
            session.execute(update(InboundJob).where(InboundJob.id==jid).values(created_at=created))
        session.commit()
        return jid


def test_fair_claim_prevents_older_flood_starvation_even_at_limit_one(client):
    owner=register(client,'r33-fair-one@example.org')
    older=add_channel(owner,'Long backlog')
    newer=add_channel(owner,'Fresh lead')
    for i in range(12):add_job(older,f'older-{i}',created=now()-3600+i)
    fresh=add_job(newer,'fresh',created=now()-60)
    assert process_batch(db.SessionLocal,limit=1)==1
    assert process_batch(db.SessionLocal,limit=1)==1
    with db.SessionLocal() as session:
        assert session.get(InboundJob,fresh).status=='done'
        assert session.query(InboundJob).filter_by(channel_id=older,status='done').count()==1
        assert session.get(ChannelConnection,older).inbound_last_dispatched_at is not None
        assert session.get(ChannelConnection,newer).inbound_last_dispatched_at is not None
        assert session.query(Message).count()==2


def test_fair_claim_multiple_slots_and_paused_channels(client):
    owner=register(client,'r33-fair-batch@example.org')
    flood=add_channel(owner,'Flood')
    short=add_channel(owner,'Short')
    paused=add_channel(owner,'Paused')
    for i in range(9):add_job(flood,f'flood-{i}',created=now()-3600+i)
    for i in range(3):add_job(short,f'short-{i}',created=now()-120+i)
    pause_id=add_job(paused,'paused-event',created=now()-7200)
    with db.SessionLocal() as session:
        session.execute(update(ChannelConnection).where(ChannelConnection.id==paused)
                        .values(inbound_paused_at=now()))
        session.commit()
    assert process_batch(db.SessionLocal,limit=4)==4
    with db.SessionLocal() as session:
        assert session.query(InboundJob).filter_by(channel_id=flood,status='done').count()==2
        assert session.query(InboundJob).filter_by(channel_id=short,status='done').count()==2
        assert session.get(InboundJob,pause_id).status=='queued'
        assert session.get(ChannelConnection,paused).inbound_last_dispatched_at is None


def test_fairness_tenant_boundaries_and_only_ids(client):
    owner=register(client,'r33-fair-tenant@example.org')
    first=add_channel(owner,'Company channel')
    with db.SessionLocal() as session:
        outsider=Organization(name='Another company')
        session.add(outsider);session.flush()
        channel=ChannelConnection(organization_id=outsider.id,provider='telegram',
                                  name='Private channel',mode='live',status='connected')
        session.add(channel);session.commit();different=channel.id
    a=add_job(first,'mine')
    b=add_job(different,'theirs')
    assert process_batch(db.SessionLocal,limit=2,only_ids=[a,a])==1
    with db.SessionLocal() as session:
        assert session.get(InboundJob,b).status=='queued'
    assert process_batch(db.SessionLocal,limit=2)==1


def test_failed_event_dismiss_erases_ciphertext_and_is_audited(client):
    owner=register(client,'r33-dismiss@example.org')
    chid=add_channel(owner,'Instagram',provider='instagram')
    jid=add_job(chid,'dismiss-event',status='failed')
    body={'reason':'Проверено с площадкой: это безвозвратный тестовый сбой',
          'code':'unrecoverable','confirm_permanent_loss':True}
    out=client.post('/api/operations/inbound/'+jid+'/dismiss',json=body)
    assert out.status_code==200,out.text
    assert out.json()['payload_deleted'] is True
    with db.SessionLocal() as session:
        row=session.get(InboundJob,jid)
        assert row.status=='dismissed' and row.encrypted_event is None
        assert row.dismissed_at is not None and row.dismissed_by==owner['user']['id']
        assert row.dismissal_code=='unrecoverable'
        assert session.query(AuditLog).filter_by(organization_id=owner['organization']['id'],
                     action='inbound.dismiss',entity_id=jid).count()==1
        assert session.query(Message).count()==0
    assert process_batch(db.SessionLocal)==0
    assert client.post('/api/operations/inbound/'+jid+'/retry',json={'reason':'Проверить и повторить позже'}).status_code==409
    assert client.post('/api/operations/inbound/'+jid+'/dismiss',json=body).status_code==409
    # Same authenticated provider callback stays idempotently closed, not re-created.
    with db.SessionLocal() as session:
        channel=session.get(ChannelConnection,chid)
        again=stage(session,channel=channel,external_chat_id='c-dismiss-event',
                    external_message_id='m-dismiss-event',sender_id='c-dismiss-event')
        session.commit()
        assert again==jid
        assert session.query(InboundJob).filter_by(channel_id=chid).count()==1


def test_dismiss_requires_validation_and_explicit_acknowledgement(client):
    owner=register(client,'r33-dismiss-errors@example.org')
    chid=add_channel(owner,'Provider')
    jid=add_job(chid,'bad',status='failed')
    route='/api/operations/inbound/'+jid+'/dismiss'
    base={'reason':'Проверил журнал, событие нельзя импортировать',
          'code':'invalid_event','confirm_permanent_loss':False}
    assert client.post(route,json=base).status_code==422
    assert client.post(route,json={**base,'confirm_permanent_loss':True,'code':'UNKNOWN'}).status_code==422
    assert client.post(route,json={**base,'confirm_permanent_loss':True,'reason':'low'}).status_code==422
    with db.SessionLocal() as session:
        assert session.get(InboundJob,jid).encrypted_event is not None
    live=add_job(chid,'notfailed')
    assert client.post('/api/operations/inbound/'+live+'/dismiss',json={
      **base,'confirm_permanent_loss':True}).status_code==409


def test_dismiss_unauthorized_tenant_cannot_access_event(client):
    owner=register(client,'r33-tenant-owner@example.org')
    with db.SessionLocal() as session:
        other=Organization(name='Private org')
        session.add(other);session.flush()
        private=ChannelConnection(organization_id=other.id,name='Private',provider='telegram',
                                  mode='live',status='connected')
        session.add(private);session.commit();private_id=private.id
    foreign=add_job(private_id,'foreign',status='failed')
    r=client.post('/api/operations/inbound/'+foreign+'/dismiss',json={
        'reason':'Конфиденциальное событие другой компании',
        'code':'other','confirm_permanent_loss':True})
    assert r.status_code==409
    with db.SessionLocal() as session:
        assert session.get(InboundJob,foreign).encrypted_event is not None
    meta=client.get('/api/operations/inbound/triage?status=failed').json()
    assert all(item['id']!=foreign for item in meta['items'])


def test_health_no_payload_and_sorted_by_severity(client,monkeypatch):
    monkeypatch.setenv('INBOUND_MAX_PENDING_PER_CHANNEL','3')
    owner=register(client,'r33-health@example.org')
    urgent=add_channel(owner,'Broken channel')
    ordinary=add_channel(owner,'Fresh channel')
    jid=add_job(urgent,'failed-job',status='failed',created=now()-1800)
    add_job(urgent,'queued-old',created=now()-2400)
    add_job(ordinary,'queued-new',created=now())
    response=client.get('/api/operations/inbound/health?limit=1')
    assert response.status_code==200,response.text
    data=response.json()
    assert data['total_live_channels']==2 and data['truncated'] is True
    assert data['critical_count']==1
    assert len(data['channels'])==1
    item=data['channels'][0]
    assert item['channel_id']==urgent and item['failed']==1 and item['pending']==2
    assert item['capacity_percent']==66.7
    assert item['severity']=='critical'
    assert item['oldest_pending_seconds']>=1700
    assert 'CLIENT_SECRET_R33' not in json.dumps(data)
    assert 'encrypted_event' not in json.dumps(data)
    assert client.get('/api/operations/inbound/health?limit=0').status_code==200
    over=client.get('/api/operations/overview').json()
    assert over['inbound']['dismissed']==0
    triage=client.get('/api/operations/inbound/triage?status=failed').json()
    assert triage['items'][0]['can_dismiss'] is True
    assert client.post('/api/operations/inbound/'+jid+'/dismiss',json={
      'reason':'Проверка завершена, событие исключено из очереди',
      'code':'unrecoverable','confirm_permanent_loss':True}).status_code==200
    final=client.get('/api/operations/overview').json()
    assert final['inbound']['dismissed']==1
    triage2=client.get('/api/operations/inbound/triage?status=dismissed').json()
    assert len(triage2['items'])==1 and triage2['items'][0]['can_retry'] is False
    assert triage2['items'][0]['dismissal_code']=='unrecoverable'


def test_health_scoped_to_one_organization(client):
    owner=register(client,'r33-health-private@example.org')
    own=add_channel(owner,'My public channel')
    add_job(own,'mine')
    with db.SessionLocal() as session:
        other=Organization(name='Foreign restricted org')
        session.add(other);session.flush()
        cid=ChannelConnection(organization_id=other.id,name='SECRET_PRIVATE_ACCOUNT',
               provider='whatsapp',status='connected',mode='live')
        session.add(cid);session.commit();cid=cid.id
    add_job(cid,'secret-tenant',status='failed')
    payload=client.get('/api/operations/inbound/health').json()
    assert payload['total_live_channels']==1
    assert payload['channels'][0]['channel_id']==own
    assert 'SECRET_PRIVATE_ACCOUNT' not in json.dumps(payload)
    assert payload['critical_count']==0


def test_dismissed_payload_is_not_recovered_and_metadata_expires(client):
    owner=register(client,'r33-retention@example.org')
    channel=add_channel(owner,'Retention')
    jid=add_job(channel,'retention',status='failed')
    assert client.post('/api/operations/inbound/'+jid+'/dismiss',json={
        'reason':'Подтверждено, что событие не должно быть импортировано',
        'code':'invalid_event','confirm_permanent_loss':True}).status_code==200
    with db.SessionLocal() as session:
        row=session.get(InboundJob,jid);row.created_at=now()-31*86400;session.commit()
    with db.SessionLocal() as session:
        totals=expire_payloads(session,stamp=now());session.commit()
        assert totals['metadata_deleted']==1
        assert session.get(InboundJob,jid) is None


def test_fair_queue_does_not_consume_a_paused_tenant_slot(client):
    first=register(client,'r33-pause-fair@example.org')
    paused=add_channel(first,'Delayed queue')
    fresh=add_channel(first,'Normal queue')
    add_job(paused,'blocked')
    available=add_job(fresh,'allowed')
    assert client.post('/api/operations/inbound/pause',json={
       'scope':'channel','channel_id':paused,'reason':'Аварийная пауза одного канала'}).status_code==200
    assert process_batch(db.SessionLocal,limit=1)==1
    with db.SessionLocal() as session:
        assert session.get(InboundJob,available).status=='done'
        assert session.get(ChannelConnection,paused).inbound_last_dispatched_at is None



def test_lead_has_read_only_diagnostics_but_no_permanent_delete(client):
    owner=register(client,'r33-lead-diagnostics@example.org')
    channel=add_channel(owner,'Lead test channel')
    jid=add_job(channel,'lead-security',status='failed')
    with db.SessionLocal() as session:
        session.query(db.Membership).filter_by(
            organization_id=owner['organization']['id']).update({'role':'lead'})
        session.commit()
    assert client.get('/api/operations/inbound/health').status_code==200
    assert client.get('/api/operations/inbound/triage?status=failed').status_code==200
    result=client.post('/api/operations/inbound/'+jid+'/dismiss',json={
        'reason':'Подтверждённая проверка закрытия технического события',
        'code':'unrecoverable','confirm_permanent_loss':True})
    assert result.status_code==403
    with db.SessionLocal() as session:
        assert session.get(InboundJob,jid).status=='failed'
        assert session.get(InboundJob,jid).encrypted_event is not None
