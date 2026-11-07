"""V1.1: multi-device account protection and bounded WhatsApp receipts."""
import hashlib
import hmac
from conftest import register
from app import db
from app.main import rate_hits
from app.auth import login_attempt_identity
from app.db import (AuthSession, LoginFailure, Organization, ChannelConnection,
                    Contact, Conversation, Message)

EMAIL = 'security-owner@example.com'
PASSWORD = 'CorrectLongPassword!2026'


def test_repeated_login_is_limited_by_shared_database(client):
    register(client, email=EMAIL)
    assert client.post('/api/auth/logout').status_code == 200
    for attempt in range(10):
        res = client.post('/api/auth/login',json={'email':EMAIL,'password':'WrongLongPassword2026!'})
        assert res.status_code == 401, (attempt,res.text)
    with db.SessionLocal() as session:
        recorded = session.query(LoginFailure).all()
        assert len(recorded) == 10
        assert recorded[0].email_digest == login_attempt_identity(EMAIL)
        assert EMAIL not in recorded[0].email_digest
    # Simulate a different server process: the per-process map is empty but
    # the database retains the attempt history.
    rate_hits.clear()
    locked = client.post('/api/auth/login',json={'email':EMAIL,'password':PASSWORD})
    assert locked.status_code == 429, locked.text
    assert '15 минут' in locked.json()['detail']
    # An unrelated identity is not blocked by the email-specific limit.
    other = client.post('/api/auth/login',json={
        'email':'other-person@example.com','password':'WrongLongPassword2026!'})
    assert other.status_code == 401


def test_successful_login_clears_old_failures(client):
    register(client,email=EMAIL)
    client.post('/api/auth/logout')
    assert client.post('/api/auth/login',json={
        'email':EMAIL,'password':'bad-password'}).status_code == 401
    assert client.post('/api/auth/login',json={
        'email':EMAIL,'password':PASSWORD}).status_code == 200
    with db.SessionLocal() as session:
        assert session.query(LoginFailure).filter_by(email_digest=login_attempt_identity(EMAIL)).count() == 0


def test_session_inventory_and_revoke_other_devices(client):
    register(client,email=EMAIL)
    with db.SessionLocal() as session:
        original_hash = session.query(AuthSession).one().id_hash
    assert client.post('/api/auth/login',json={
        'email':EMAIL,'password':PASSWORD}).status_code == 200
    inventory = client.get('/api/auth/sessions')
    assert inventory.status_code == 200
    assert inventory.json()['count'] == 2
    assert sum(bool(s['is_current']) for s in inventory.json()['sessions']) == 1
    assert all(set(s)=={'created_at','is_current'} for s in inventory.json()['sessions'])
    revoked = client.post('/api/auth/sessions/revoke-others')
    assert revoked.status_code == 200
    assert revoked.json()['revoked'] == 1
    assert client.get('/api/auth/me').status_code == 200
    with db.SessionLocal() as session:
        assert session.query(AuthSession).count()==1
        assert session.get(AuthSession,original_hash) is None
    assert client.get('/api/auth/sessions').json()['count'] == 1


def test_revoke_every_device_including_current(client):
    register(client,email=EMAIL)
    assert client.post('/api/auth/login',json={
        'email':EMAIL,'password':PASSWORD}).status_code == 200
    result = client.post('/api/auth/sessions/revoke-all')
    assert result.status_code == 200 and result.json()['revoked'] == 2
    assert result.json()['current_session_active'] is False
    assert client.get('/api/auth/me').status_code == 401
    assert client.get('/api/auth/sessions').status_code == 401
    with db.SessionLocal() as session:
        assert session.query(AuthSession).count()==0


def test_revoking_sessions_requires_csrf(client):
    register(client,email=EMAIL)
    # The fixture injects CSRF headers automatically. Sending an explicit wrong
    # token must still be rejected by the server dependency.
    bad = client.post('/api/auth/sessions/revoke-all',headers={'X-CSRF-Token':'wrong'})
    assert bad.status_code == 403
    assert client.get('/api/auth/me').status_code == 200


def test_whatsapp_receipt_scoped_to_exact_tenant_and_channel(client):
    me=register(client,email=EMAIL)
    org_a=me['organization']['id']
    with db.SessionLocal() as session:
        org_b=Organization(name='Другой арендатор',plan='business')
        session.add(org_b)
        session.flush()
        channels=[]
        msgs=[]
        for oid,pid in [(org_a,'111222333444'),(org_b.id,'999888777666')]:
            ch=ChannelConnection(organization_id=oid,provider='whatsapp',name='WABA',
                                 external_account_id=pid,mode='live',status='connected')
            contact=Contact(organization_id=oid,name='Клиент')
            session.add_all([ch,contact]);session.flush()
            conv=Conversation(organization_id=oid,channel_id=ch.id,contact_id=contact.id,
                              external_chat_id='customer-42')
            session.add(conv);session.flush()
            msg=Message(organization_id=oid,conversation_id=conv.id,direction='out',
                        body='Тестовый ответ',external_id='same-external-message-id',
                        delivery_status='accepted')
            session.add(msg);channels.append(ch);msgs.append(msg)
        session.commit()
        first_id,second_id=msgs[0].id,msgs[1].id
    payload={"object":"whatsapp_business_account","entry":[{"changes":[{"value":{
        "metadata":{"phone_number_id":"111222333444"},
        "statuses":[{"id":"same-external-message-id","status":"delivered"}]}}]}]}
    import json
    raw=json.dumps(payload).encode()
    sig=hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
    result=client.post('/api/webhooks/whatsapp',content=raw,
                       headers={'X-Hub-Signature-256':'sha256='+sig,'Content-Type':'application/json'})
    assert result.status_code==200,result.text
    with db.SessionLocal() as session:
        assert session.get(Message,first_id).delivery_status == 'delivered'
        assert session.get(Message,second_id).delivery_status == 'accepted'


def test_widget_quota_shared_by_workers_and_replays_remain_safe(client):
    from conftest import register
    from app.db import WebsiteVisitor, Message, now
    from app.main import rate_hits
    import hashlib
    register(client,email=EMAIL)
    widget=client.post('/api/website-widgets',json={
        'name':'Чат магазина',
        'allowed_origins':['https://store.example.com'],
        'greeting':'Здравствуйте','accent':'#785AB7'}).json()
    key=widget['key']
    session=client.post('/api/public/widget/'+key+'/session',json={'name':'Али'}).json()
    token=session['visitor_token']
    headers={'X-Widget-Session':token}
    original=client.post('/api/public/widget/'+key+'/messages',headers=headers,
                         json={'body':'Первый вопрос','client_nonce':'unique_first_123'})
    assert original.status_code==201,original.text
    with db.SessionLocal() as session:
        visitor=session.query(WebsiteVisitor).filter_by(token_hash=hashlib.sha256(token.encode()).hexdigest()).one()
        assert visitor.conversation_id
        for idx in range(89):
            session.add(Message(organization_id=visitor.organization_id,
                conversation_id=visitor.conversation_id,external_id='seed-%s'%idx,
                direction='in',body='Seed',created_at=now(),delivery_status='delivered'))
        session.commit()
    rate_hits.clear()  # simulated new worker
    assert client.post('/api/public/widget/'+key+'/messages',headers=headers,
                       json={'body':'Следующий','client_nonce':'unique_next_123'}).status_code==429
    replay=client.post('/api/public/widget/'+key+'/messages',headers=headers,
                       json={'body':'Первый вопрос','client_nonce':'unique_first_123'})
    assert replay.status_code==201
    assert replay.json()['message_id']==original.json()['message_id']
