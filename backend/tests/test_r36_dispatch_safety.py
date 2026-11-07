"""R36 port candidate: real FastAPI/SQLite flow, cross-tenant boundaries, no live providers."""
import asyncio
import hashlib
import json
from types import SimpleNamespace

from sqlalchemy import text

from app import db
from app.db import (AuditLog, ChannelConnection, Contact, Conversation,
                    DeliveryTransition, DispatchPause, Message, OutgoingJob, now)
from app.services import process_outbox
from conftest import register


def add_job(org_id, key):
    """Create a live-shaped outbox row without touching any external provider."""
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=org_id, provider='telegram',
            name='Test channel ' + key, external_account_id='test-'+key,
            mode='live', status='connected', encrypted_credentials='SECRET_CREDENTIAL_CANARY')
        contact=Contact(organization_id=org_id,name='Private contact ' + key)
        session.add_all([channel,contact]);session.flush()
        conv=Conversation(organization_id=org_id,channel_id=channel.id,
            contact_id=contact.id,external_chat_id='chat-'+key,last_inbound_at=now())
        session.add(conv);session.flush()
        msg=Message(organization_id=org_id,conversation_id=conv.id,
            direction='out',body='PRIVATE MESSAGE BODY '+key,delivery_status='queued')
        session.add(msg);session.flush()
        job=OutgoingJob(organization_id=org_id,message_id=msg.id,
            channel_id=channel.id,status='queued')
        session.add(job);session.commit()
        return channel.id,job.id,msg.id


def fake_provider(monkeypatch, *, fail=None):
    import app.services as services
    calls=[]
    class FakeAdapter:
        async def send_message(self,cred,channel,conversation,text):
            calls.append((channel.organization_id,text))
            if fail is not None:
                raise fail
            return 'external-accepted-test'
    monkeypatch.setattr(services,'adapter_for',lambda provider:FakeAdapter())
    monkeypatch.setattr(services,'unseal',lambda encrypted:{})
    return calls


def test_pause_prevents_claim_without_touching_inbound_or_other_company(client,monkeypatch):
    a=register(client,'r36-a@example.com','Company A')['organization']['id']
    channel_a,job_a,msg_a=add_job(a,'a')
    reply=client.post('/api/operations/dispatch-pauses',json={
        'channel_id':channel_a,'reason_code':'incident','minutes':15})
    assert reply.status_code==200,reply.text
    assert reply.json()['pauses'][0]['channel_id']==channel_a
    # Changing tenant by ending this session does not remove the shared SQL pause.
    assert client.post('/api/auth/logout').status_code==200
    b=register(client,'r36-b@example.com','Company B')['organization']['id']
    channel_b,job_b,msg_b=add_job(b,'b')
    assert client.get('/api/operations/dispatch-pauses').json()['pauses']==[]
    # Foreign tenant must not guess/pause or resume tenant A's connection.
    assert client.post('/api/operations/dispatch-pauses',json={
        'channel_id':channel_a,'reason_code':'maintenance'}).status_code==404
    calls=fake_provider(monkeypatch)
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert len(calls)==1 and calls[0][0]==b
    with db.SessionLocal() as session:
        assert session.get(OutgoingJob,job_a).status=='queued'
        assert session.get(OutgoingJob,job_a).attempts==0
        assert session.get(OutgoingJob,job_b).status=='done'
        assert session.get(Message,msg_a).body=='PRIVATE MESSAGE BODY a'
        assert session.query(DeliveryTransition).filter_by(organization_id=a).count()==0
        assert [e.event_code for e in session.query(DeliveryTransition).filter_by(
            organization_id=b).order_by(DeliveryTransition.created_at).all()]==['claimed','api_accepted']
    # Tenant B cannot inspect job A timeline.
    assert client.get('/api/operations/delivery-events?job_id='+job_a).status_code==404
    assert client.get('/api/operations/delivery-events?job_id='+job_b).status_code==200


def test_global_pause_and_resume_keeps_attempts_unchanged(client,monkeypatch):
    a=register(client,'r36-pause@example.com')['organization']['id']
    channel,job,_=add_job(a,'pause')
    calls=fake_provider(monkeypatch)
    paused=client.post('/api/operations/dispatch-pauses',json={
        'reason_code':'provider_outage','minutes':60})
    assert paused.status_code==200,paused.text
    assert paused.json()['pauses'][0]['channel_id'] is None
    assert asyncio.run(process_outbox(db.SessionLocal))==0
    with db.SessionLocal() as s:
        assert s.get(OutgoingJob,job).status=='queued' and s.get(OutgoingJob,job).attempts==0
    assert not calls
    resumed=client.post('/api/operations/dispatch-pauses/resume',json={})
    assert resumed.status_code==200 and resumed.json()['pauses']==[]
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert calls and len(calls)==1
    with db.SessionLocal() as s:
        events=s.query(DeliveryTransition).filter_by(job_id=job).all()
        assert sorted(e.event_code for e in events)==['api_accepted','claimed']
        assert s.query(AuditLog).filter_by(organization_id=a,action='dispatch.paused').count()==1
        assert s.query(AuditLog).filter_by(organization_id=a,action='dispatch.resumed').count()==1


def test_pauses_are_upserted_expire_and_validate_fields(client,monkeypatch):
    a=register(client,'r36-expire@example.com')['organization']['id']
    c,j,_=add_job(a,'expire')
    for reason in ['incident','maintenance']:
        resp=client.post('/api/operations/dispatch-pauses',json={
            'channel_id':c,'reason_code':reason,'minutes':5})
        assert resp.status_code==200,resp.text
    with db.SessionLocal() as s:
        assert s.query(DispatchPause).filter_by(organization_id=a).count()==1
        gate=s.query(DispatchPause).filter_by(organization_id=a).one()
        assert gate.reason_code=='maintenance'
        gate.expires_at=now()-1;s.commit()
    calls=fake_provider(monkeypatch)
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert len(calls)==1
    assert client.get('/api/operations/dispatch-pauses').json()['pauses']==[]
    assert client.post('/api/operations/dispatch-pauses',json={
        'reason_code':'unknown'}).status_code==422
    assert client.post('/api/operations/dispatch-pauses',json={
        'reason_code':'maintenance','minutes':1441}).status_code==422


def test_operator_cannot_change_or_export_dispatch_safety(client):
    org=register(client,'r36-role@example.com')['organization']['id']
    with db.SessionLocal() as s:
        from app.db import Membership
        membership=s.query(Membership).filter_by(organization_id=org).one()
        membership.role='operator';s.commit()
    assert client.get('/api/operations/dispatch-pauses').status_code==403
    assert client.post('/api/operations/dispatch-pauses',json={
        'reason_code':'incident'}).status_code==403
    assert client.post('/api/operations/dispatch-pauses/resume',json={}).status_code==403
    assert client.get('/api/operations/delivery-telemetry').status_code==403
    assert client.get('/api/operations/support-bundle').status_code==403
    assert client.get('/api/operations/delivery-events?job_id=no').status_code==403


def test_support_bundle_drops_pii_errors_and_has_integrity_digest(client):
    org=register(client,'r36-privacy@example.com')['organization']['id']
    c,j,msg=add_job(org,'sensitive')
    with db.SessionLocal() as s:
        job=s.get(OutgoingJob,j);job.status='uncertain'
        job.last_error='SECRET_ERROR_WITH_ACCESS_TOKEN'
        s.add(DeliveryTransition(organization_id=org,job_id=j,
            status_from='processing',status_to='uncertain',event_code='quarantined',attempts=1))
        s.commit()
    resp=client.get('/api/operations/support-bundle')
    assert resp.status_code==200,resp.text
    assert resp.headers['Cache-Control']=='no-store, private'
    raw=resp.text
    for secret in ('PRIVATE MESSAGE BODY','SECRET_CREDENTIAL_CANARY',
                   'SECRET_ERROR_WITH_ACCESS_TOKEN','Private contact','r36-privacy@example.com',c,j,msg,org):
        assert secret not in raw
    doc=resp.json()
    digest=doc.pop('sha256')
    assert digest==hashlib.sha256(json.dumps(doc,sort_keys=True,
        ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    assert doc['telemetry']['outbox']['uncertain']==1
    assert doc['telemetry']['events_24h']['quarantined']==1
    assert any(x['code']=='uncertain' for x in doc['telemetry']['alerts'])


def test_manual_reconciliation_adds_event_without_reopening_send(client):
    org=register(client,'r36-reconcile@example.com')['organization']['id']
    c,j,m=add_job(org,'reconcile')
    with db.SessionLocal() as s:
        job=s.get(OutgoingJob,j);job.status='uncertain';s.get(Message,m).delivery_status='uncertain';s.commit()
    resp=client.post('/api/operations/outbox/'+j+'/resolve',json={
        'status':'accepted','evidence':'Manually confirmed at provider message log'})
    assert resp.status_code==200,resp.text
    events=client.get('/api/operations/delivery-events?job_id='+j).json()['events']
    assert [x['event_code'] for x in events]==['manual_accepted']
    assert events[0]['from_status']=='uncertain' and events[0]['to_status']=='done'
    assert client.post('/api/operations/outbox/'+j+'/resolve',json={
        'status':'accepted','evidence':'Trying again'}).status_code==409


def test_failing_provider_creates_bounded_transition_without_content(client,monkeypatch):
    from app.integrations.base import AdapterError
    org=register(client,'r36-fail@example.com')['organization']['id']
    c,j,_=add_job(org,'fail')
    fake_provider(monkeypatch,fail=AdapterError('Provider says SECRET_TOKEN',retriable=False))
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    with db.SessionLocal() as s:
        events=s.query(DeliveryTransition).filter_by(job_id=j).all()
        assert sorted(x.event_code for x in events)==['claimed','hard_fail']
        assert not any('SECRET' in str((x.event_code,x.status_from,x.status_to)) for x in events)
        assert s.get(OutgoingJob,j).status=='failed'


def test_sql_conditional_claim_rechecks_active_gate(client,monkeypatch):
    from app.dispatch_control import allowed_to_claim
    from sqlalchemy import update
    org=register(client,'r36-sql@example.com')['organization']['id']
    c,j,_=add_job(org,'sql')
    client.post('/api/operations/dispatch-pauses',json={
        'channel_id':c,'reason_code':'incident'})
    with db.SessionLocal() as s:
        claimed=s.execute(update(OutgoingJob).where(
            OutgoingJob.id==j,OutgoingJob.status=='queued',
            allowed_to_claim(OutgoingJob.organization_id,OutgoingJob.channel_id,now())
        ).values(status='processing'))
        s.commit()
        assert claimed.rowcount==0
        assert s.get(OutgoingJob,j).status=='queued'


def test_operator_cancel_and_verified_retry_add_audit_events_only_after_cas(client):
    from app.db import DeliveryTransition
    from test_r22_outbox_control import seed
    org,conv_id,job_id,message_id,channel_id=seed(client,email='r36-human@example.com')
    cancelled=client.post('/api/operations/outbox/'+job_id+'/cancel')
    assert cancelled.status_code==200,cancelled.text
    with db.SessionLocal() as s:
        events=s.query(DeliveryTransition).filter_by(job_id=job_id).all()
        assert [(e.status_from,e.status_to,e.event_code) for e in events]==[
            ('queued','cancelled','operator_cancelled')]
    assert client.post('/api/operations/outbox/'+job_id+'/cancel').status_code==409
    with db.SessionLocal() as s:
        assert s.query(DeliveryTransition).filter_by(job_id=job_id).count()==1
    # Create a second job within the same organization, with an unambiguous 403.
    channel,another_job,another_msg=add_job(org,'retry-human')
    with db.SessionLocal() as s:
        job=s.get(OutgoingJob,another_job)
        job.status='failed';job.last_error='API 403: explicit provider refusal'
        s.get(Message,another_msg).delivery_status='failed'
        s.commit()
    retried=client.post('/api/operations/outbox/'+another_job+'/retry-verified',json={
        'verified_not_delivered':True,'evidence':'Test provider checked; nothing delivered'})
    assert retried.status_code==200,retried.text
    with db.SessionLocal() as s:
        rows=s.query(DeliveryTransition).filter_by(job_id=another_job).all()
        assert [(e.status_from,e.status_to,e.event_code) for e in rows]==[
            ('failed','queued','operator_verified_retry')]
