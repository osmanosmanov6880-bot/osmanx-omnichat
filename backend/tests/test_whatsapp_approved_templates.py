"""Official Meta approved text-template contract, consent, tenant and outbox tests.

Provider HTTP is mocked; none of these tests claim a live WhatsApp account.
"""
import asyncio
import json
from types import SimpleNamespace
import time
import pytest
from app import db
from app.db import ChannelConnection, Conversation, Message, OutgoingJob, WhatsAppConsent
from app.services import ingest_inbound, process_outbox
from app.integrations.adapters import seal
from app.integrations.base import AdapterError
from app.whatsapp_templates import supported_template, render_template
from conftest import register, start_demo

APPROVED={'name':'appointment_reminder','language':'ru','status':'APPROVED',
    'components':[{'type':'BODY','text':'Здравствуйте, {{1}}! Ваша запись: {{2}}.'}]}
UNAPPROVED={'name':'not_yet_approved','language':'ru','status':'PENDING',
    'components':[{'type':'BODY','text':'Текст'}]}
WITH_BUTTON={'name':'wrong_shape','language':'ru','status':'APPROVED',
    'components':[{'type':'BODY','text':'Текст'}, {'type':'BUTTONS','buttons':[]}]}


def make_channel(client,email='wa-owner@example.org',days_old=3):
    profile=register(client,email=email)
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=profile['organization']['id'],provider='whatsapp',
            name='WA для теста',mode='live',status='connected',external_account_id='123456789001',
            encrypted_credentials=seal({'phone_number_id':'123456789001',
                'waba_id':'99118822','access_token':'TEST_TOKEN_PRIVATE'}))
        session.add(channel);session.flush()
        ingested=ingest_inbound(session,channel=channel,external_chat_id='79001234567',
            external_message_id='incoming-1',sender_id='79001234567',sender_name='Клиент',
            text='Хочу записаться',timestamp=time.time()-days_old*86400)
        session.commit()
        conversation=session.query(Conversation).filter_by(channel_id=channel.id).one()
        return profile,channel.id,conversation.id


def provider_stub(monkeypatch,approved=None):
    from app.integrations import adapters
    seen=[]
    async def fake_call(method,url,*,headers=None,params=None,data=None,json_data=None):
        seen.append((method,url,params,json_data,headers))
        if method=='GET' and '/message_templates' in url:
            assert '99118822' in url
            return {'data': approved if approved is not None else [APPROVED, UNAPPROVED, WITH_BUTTON]}
        if method=='POST' and '/messages' in url:
            assert json_data['messaging_product']=='whatsapp'
            assert json_data['type']=='template'
            return {'messages':[{'id':'wamid.HBgMOCKED_FROM_TEST'}]}
        raise AssertionError('Unexpected provider call '+method+' '+url)
    monkeypatch.setattr(adapters,'call',fake_call)
    return seen


def confirm_consent(client,conv):
    return client.post(f'/api/conversations/{conv}/whatsapp-consent',json={
        'source':'Форма записи от 01.11, получено явное согласие', 'confirmed':True})


def send_template(client,conv,name='appointment_reminder',nonce='test-nonce-001',params=None):
    conversation=client.get('/api/conversations/'+conv).json()['conversation']
    return client.post('/api/conversations/'+conv+'/whatsapp-template',json={
        'name':name,'language':'ru','parameters':params if params is not None else ['Алина','12 ноября в 14:00'],
        'expected_version':conversation['version'],'client_nonce':nonce})


def test_approved_filter_only_simple_text_body():
    assert supported_template(APPROVED)['param_count']==2
    assert supported_template(UNAPPROVED) is None
    assert supported_template(WITH_BUTTON) is None
    assert supported_template({'name':'broken','language':'ru','status':'APPROVED',
        'components':[{'type':'BODY','text':'Hello {{2}}'}]}) is None
    assert render_template(APPROVED['components'][0]['text'],['Ирина','завтра'])=='Здравствуйте, Ирина! Ваша запись: завтра.'


def test_official_listing_and_queue_send_outside_24h(client,monkeypatch):
    _,ch,conv=make_channel(client)
    seen=provider_stub(monkeypatch)
    normal=client.post('/api/conversations/'+conv+'/reply',json={
        'body':'Обычное сообщение','expected_version':1,'client_nonce':'normal-nonce-12'})
    assert normal.status_code in (409,422)
    listed=client.get('/api/conversations/'+conv+'/whatsapp-templates')
    assert listed.status_code==200,listed.text
    assert listed.json()['consent_recorded']==False
    assert [(x['name'],x['param_count']) for x in listed.json()['templates']]==[('appointment_reminder',2)]
    without=send_template(client,conv)
    assert without.status_code==409
    consent=confirm_consent(client,conv)
    assert consent.status_code==200 and not consent.json()['verified_by_provider']
    created=send_template(client,conv)
    assert created.status_code==201,created.text
    assert created.json()['message']['delivery_status']=='queued'
    assert created.json()['message']['kind']=='whatsapp_template'
    assert 'Алина' in created.json()['message']['body']
    replay=send_template(client,conv)
    assert replay.status_code==200 or replay.status_code==201
    assert replay.json()['duplicate'] is True
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    with db.SessionLocal() as session:
        msg=session.query(Message).filter_by(kind='whatsapp_template').one()
        assert msg.delivery_status=='accepted'
        assert msg.external_id=='wamid.HBgMOCKED_FROM_TEST'
        assert session.query(OutgoingJob).one().status=='done'
    posts=[call for call in seen if call[0]=='POST']
    assert len(posts)==1
    body=posts[0][3]
    assert body['type']=='template' and body['template']['name']=='appointment_reminder'
    assert body['template']['components']==[{'type':'body','parameters':[
        {'type':'text','text':'Алина'},{'type':'text','text':'12 ноября в 14:00'}]}]
    assert 'TEST_TOKEN_PRIVATE' not in str(created.json())


def test_non_approved_or_mismatched_parameters_cannot_queue(client,monkeypatch):
    _,_,conv=make_channel(client,'wa-owner2@example.org')
    provider_stub(monkeypatch)
    assert confirm_consent(client,conv).status_code==200
    assert send_template(client,conv,name='not_yet_approved').status_code==409
    assert send_template(client,conv,params=['only one']).status_code==422
    assert client.post('/api/conversations/'+conv+'/whatsapp-template',json={
        'name':'hello world','language':'ru','parameters':[],
        'expected_version':0,'client_nonce':'unique-nonce-500'}).status_code==422
    with db.SessionLocal() as session:
        assert session.query(OutgoingJob).count()==0


def test_consent_revoked_after_queuing_prevents_send(client,monkeypatch):
    _,ch,conv=make_channel(client,'wa-owner3@example.org')
    seen=provider_stub(monkeypatch)
    assert confirm_consent(client,conv).status_code==200
    assert send_template(client,conv).status_code==201
    revoked=client.post('/api/conversations/'+conv+'/whatsapp-consent/revoke')
    assert revoked.status_code==200
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert not any(method=='POST' for method,*_ in seen)
    with db.SessionLocal() as session:
        assert session.query(OutgoingJob).one().status=='failed'
        assert session.query(Message).filter_by(kind='whatsapp_template').one().delivery_status=='failed'


def test_staff_cannot_access_foreign_tenant(client,monkeypatch):
    _,channel_id,conv=make_channel(client,'owner-a@example.org')
    provider_stub(monkeypatch)
    register(client,email='owner-b@example.org')  # session switches company
    for path in [f'/api/conversations/{conv}/whatsapp-templates']:
        assert client.get(path).status_code==404
    assert confirm_consent(client,conv).status_code==404
    assert client.post('/api/conversations/'+conv+'/whatsapp-template',json={
        'name':'appointment_reminder','language':'ru',
        'parameters':['Алина','12 ноября'], 'expected_version':1,
        'client_nonce':'foreign-nonce-001'}).status_code==404
    with db.SessionLocal() as session:
        assert session.query(WhatsAppConsent).count()==0


def test_meta_verification_required_and_demo_never_calls_meta(client,monkeypatch):
    start_demo(client)
    assert client.get('/api/conversations').status_code==200
    conv=client.get('/api/conversations').json()[0]['id']
    assert client.get('/api/conversations/'+conv+'/whatsapp-templates').status_code in (422,403)
    assert client.post('/api/conversations/'+conv+'/whatsapp-consent',json={
        'source':'Согласие от клиента на сайте','confirmed':True}).status_code in (422,403)


def test_backend_revalidates_template_approval_at_delivery(client,monkeypatch):
    _,ch,conv=make_channel(client,'wa-owner4@example.org')
    approved=[APPROVED]
    seen=provider_stub(monkeypatch,approved)
    assert confirm_consent(client,conv).status_code==200
    assert send_template(client,conv).status_code==201
    approved.clear()  # template revoked before worker picks job
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    assert not any(method=='POST' for method,*_ in seen)
    with db.SessionLocal() as session:
        assert session.query(OutgoingJob).one().status=='failed'


def test_idempotency_key_cannot_be_reused_for_different_template(client,monkeypatch):
    _,ch,conv=make_channel(client,'wa-owner5@example.org')
    provider_stub(monkeypatch)
    assert confirm_consent(client,conv).status_code==200
    assert send_template(client,conv,nonce='shared-key-xx').status_code==201
    changed=send_template(client,conv,nonce='shared-key-xx',params=['Ирина','13 ноября'])
    assert changed.status_code==409
    with db.SessionLocal() as session:
        assert session.query(Message).filter_by(kind='whatsapp_template').count()==1


def test_upgrade_from_restored_v15_preserves_data(tmp_path):
    """Upgrade from actual v1.5 Alembic head and keep the old channel."""
    import os
    import sqlite3
    import subprocess
    import sys
    from pathlib import Path
    from app.db import engine_for, assert_schema_current
    project=Path(__file__).resolve().parents[2]
    database=tmp_path/'existing.db'
    env=dict(os.environ,DATABASE_URL='sqlite:///'+str(database),PYTHONPATH='backend')
    command=[sys.executable,'-m','alembic','-c','backend/alembic.ini','upgrade']
    subprocess.run(command+['ee4a14b80001'],cwd=project,env=env,capture_output=True,check=True)
    with sqlite3.connect(database) as sql:
        sql.execute("INSERT INTO organizations (id,name,plan,is_demo,retention_days,sla_minutes,currency,timezone,created_at) VALUES ('old-company','Старая компания','starter',0,365,5,'RUB','UTC',123)")
        sql.execute("INSERT INTO channel_connections (id,organization_id,provider,name,mode,status,created_at) VALUES ('old-channel','old-company','telegram','Старое подключение','demo','connected',123)")
        sql.commit()
    subprocess.run(command+['head'],cwd=project,env=env,capture_output=True,check=True)
    with sqlite3.connect(database) as sql:
        assert sql.execute('SELECT name FROM organizations WHERE id="old-company"').fetchone()==('Старая компания',)
        assert sql.execute('SELECT name FROM channel_connections WHERE id="old-channel"').fetchone()==('Старое подключение',)
        # Latest head is validated against Alembic below; do not pin a stale
        # release revision once later migrations are added.
        assert sql.execute('SELECT count(*) FROM alembic_version').fetchone()==(1,)
    engine=engine_for('sqlite:///'+str(database))
    assert assert_schema_current(engine)
    engine.dispose()
