"""R35 multi-tenant queue fairness, fenced maintenance, zero-PII operators."""
import json
from sqlalchemy import update
from app import db
from app.db import Organization, ChannelConnection, InboundJob, Message, AuditLog, now
from app.inbound_jobs import stage, _claim, process_batch
from app.inbound_maintenance import integrity_report, repair_expired
from conftest import register


def channel(org_id, label):
    with db.SessionLocal() as session:
        ch = ChannelConnection(organization_id=org_id, name=label,
                               provider='telegram', mode='live', status='connected')
        session.add(ch);session.commit();return ch.id


def event(channel_id,key):
    with db.SessionLocal() as session:
        ch=session.get(ChannelConnection,channel_id)
        job=stage(session,channel=ch,external_chat_id='thread-'+key,
                  external_message_id='msg-'+key,sender_id='u-'+key,
                  text='SECRET_R35_QUESTION')
        session.commit()
        return job


def tenant(label):
    with db.SessionLocal() as session:
        org=Organization(name=label)
        session.add(org);session.commit();return org.id


def test_many_channels_one_tenant_cannot_starve_other_tenant_limit_one(client):
    reg=register(client,'r35-fair-one@example.org')
    main=reg['organization']['id']
    other=tenant('Second tenant')
    for idx in range(9):
        cid=channel(main,'Busy-'+str(idx))
        event(cid,'a'+str(idx))
    other_channel=channel(other,'Quiet account')
    other_job=event(other_channel,'other')
    assert process_batch(db.SessionLocal,limit=1)==1
    assert process_batch(db.SessionLocal,limit=1)==1
    with db.SessionLocal() as session:
        assert session.get(InboundJob,other_job).status=='done'
        assert session.query(InboundJob).filter_by(organization_id=main,status='done').count()==1
        assert session.get(Organization,main).inbound_last_dispatched_at is not None
        assert session.get(Organization,other).inbound_last_dispatched_at is not None


def test_organization_fair_batch_distribution(client):
    owner=register(client,'r35-fair-batch@example.org')
    main=owner['organization']['id']
    other=tenant('Small tenant')
    for idx in range(8):
        event(channel(main,'Busy-'+str(idx)),'busy'+str(idx))
    other_job=event(channel(other,'Small'),'quiet')
    assert process_batch(db.SessionLocal,limit=5)>=2
    with db.SessionLocal() as session:
        assert session.get(InboundJob,other_job).status=='done'
        assert session.query(InboundJob).filter_by(organization_id=main,status='done').count()>=1


def test_expired_job_and_channel_slot_repaired_and_audited(client):
    owner=register(client,'r35-expired@example.org')
    org=owner['organization']['id']
    cid=channel(org,'Broken worker')
    jid=event(cid,'recover')
    token=_claim(db.SessionLocal,jid)
    assert token
    with db.SessionLocal() as session:
        session.execute(update(ChannelConnection).where(ChannelConnection.id==cid)
                        .values(inbound_processing_until=now()-5))
        session.execute(update(InboundJob).where(InboundJob.id==jid)
                        .values(claim_expires_at=now()-5))
        session.commit()
    check=client.get('/api/operations/inbound/integrity')
    assert check.status_code==200,check.text
    assert check.json()['expired_claims']==1
    assert check.json()['expired_channel_slots']==1
    assert 'SECRET_R35' not in check.text and token not in check.text
    refused=client.post('/api/operations/inbound/repair-expired',json={
        'reason':'Investigated expired claim after restart', 'confirm_expired_only':False})
    assert refused.status_code==422
    response=client.post('/api/operations/inbound/repair-expired',json={
        'reason':'Investigated expired claim after restart', 'confirm_expired_only':True})
    assert response.status_code==200,response.text
    assert response.json()['retrying']==1
    assert response.json()['expired_slots_released']==1
    with db.SessionLocal() as session:
        row=session.get(InboundJob,jid)
        assert row.status=='retrying' and row.encrypted_event
        assert session.get(ChannelConnection,cid).inbound_processing_token is None
        assert session.query(AuditLog).filter_by(organization_id=org,
            action='inbound.repair_expired').count()==1
    assert process_batch(db.SessionLocal,limit=1)==1
    with db.SessionLocal() as session:
        assert session.get(InboundJob,jid).status=='done'
        assert session.query(Message).count()==1
    assert client.post('/api/operations/inbound/repair-expired',json={
        'reason':'Check same incident is harmless on retry', 'confirm_expired_only':True}).json()['changes']==0


def test_live_claim_must_never_be_released_even_if_slot_clock_is_older(client):
    owner=register(client,'r35-live@example.org')
    cid=channel(owner['organization']['id'],'Active')
    jid=event(cid,'live')
    token=_claim(db.SessionLocal,jid)
    with db.SessionLocal() as session:
        session.execute(update(ChannelConnection).where(ChannelConnection.id==cid)
                        .values(inbound_processing_until=now()-2))
        session.commit()
    overview=client.get('/api/operations/inbound/integrity').json()
    assert overview['expired_claims']==0
    assert overview['expired_channel_slots']==0
    result=client.post('/api/operations/inbound/repair-expired',json={
        'reason':'Checking only leases that actually expired', 'confirm_expired_only':True})
    assert result.status_code==200,result.text
    assert result.json()['changes']==0
    with db.SessionLocal() as session:
        assert session.get(InboundJob,jid).status=='processing'
        assert session.get(ChannelConnection,cid).inbound_processing_token==token


def test_exhausted_attempts_go_to_review_payload_remains(client):
    owner=register(client,'r35-final-attempt@example.org')
    org=owner['organization']['id']
    cid=channel(org,'Last attempt')
    jid=event(cid,'exhausted')
    _claim(db.SessionLocal,jid)
    with db.SessionLocal() as session:
        session.execute(update(InboundJob).where(InboundJob.id==jid)
                        .values(attempts=5,claim_expires_at=now()-10))
        session.execute(update(ChannelConnection).where(ChannelConnection.id==cid)
                        .values(inbound_processing_until=now()-10))
        session.commit()
    with db.SessionLocal() as session:
        result=repair_expired(session,org)
        session.commit()
        assert result['requires_review']==1
        row=session.get(InboundJob,jid)
        assert row.status=='failed'
        assert row.encrypted_event is not None
        assert row.last_error=='worker_claim_expired'


def test_missing_ciphertext_quarantined_without_touching_other_tenant(client):
    owner=register(client,'r35-missing@example.org')
    org=owner['organization']['id']
    foreign=tenant('Other tenant')
    own=event(channel(org,'Own channel'),'blank')
    other=event(channel(foreign,'Other channel'),'private')
    with db.SessionLocal() as session:
        session.execute(update(InboundJob).where(InboundJob.id==own)
                        .values(encrypted_event=None))
        session.commit()
    diagnosis=client.get('/api/operations/inbound/integrity').json()
    assert diagnosis['missing_payload']==1
    response=client.post('/api/operations/inbound/repair-expired',json={
        'reason':'Removing unreachable empty queue metadata only',
        'confirm_expired_only':True})
    assert response.status_code==200
    assert response.json()['missing_payload_quarantined']==1
    with db.SessionLocal() as session:
        assert session.get(InboundJob,own).status=='expired'
        assert session.get(InboundJob,other).status=='queued'
        assert session.get(InboundJob,other).encrypted_event is not None


def test_invalid_channel_binding_detected_but_not_auto_repaired(client):
    owner=register(client,'r35-invalid-binding@example.org')
    main=owner['organization']['id']
    other=tenant('Foreign tenant')
    jid=event(channel(main,'Main'),'mismatch')
    with db.SessionLocal() as session:
        session.execute(update(InboundJob).where(InboundJob.id==jid)
                        .values(organization_id=other))
        session.commit()
    with db.SessionLocal() as session:
        result=integrity_report(session,other)
        assert result['invalid_channel_bindings']==1
        repair=repair_expired(session,other)
        assert repair['changes']==0
        session.rollback()
    assert client.get('/api/operations/inbound/integrity').json()['invalid_channel_bindings']==0


def test_lead_can_inspect_but_not_repair(client):
    owner=register(client,'r35-lead@example.org')
    with db.SessionLocal() as session:
        session.query(db.Membership).filter_by(organization_id=owner['organization']['id']).update({'role':'lead'})
        session.commit()
    assert client.get('/api/operations/inbound/integrity').status_code==200
    response=client.post('/api/operations/inbound/repair-expired',json={
        'reason':'A team lead must not modify system claims', 'confirm_expired_only':True})
    assert response.status_code==403


def test_snapshot_never_includes_sensitive_tokens_or_customer_data(client):
    owner=register(client,'r35-privacy@example.org')
    cid=channel(owner['organization']['id'],'Public name')
    job=event(cid,'secret')
    token=_claim(db.SessionLocal,job)
    payload=json.dumps(client.get('/api/operations/inbound/integrity').json())
    assert token not in payload and 'SECRET_R35' not in payload
    assert 'fingerprint' not in payload and 'encrypted_event' not in payload
