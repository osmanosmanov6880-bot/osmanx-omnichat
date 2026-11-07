"""V1.0: truthfulness of delivery states and tenant-scoped provider probes.

All provider replies here are mocked. These tests do not verify any live account.
"""
import hmac
import json
import hashlib
from app import db as store
from app.delivery_state import advance_delivery_state
from app.db import ChannelConnection, Contact, Conversation, Message
from app.integrations import subscription_check
from app.integrations.base import AdapterError
from conftest import register
from test_bot_channels import fake_provider_api


def connect(client, monkeypatch):
    account = register(client, 'probe-owner@example.com', 'Probe Workspace')
    calls = fake_provider_api(monkeypatch)
    response = client.post('/api/integrations/bots', json={
        'provider': 'telegram', 'access_token': '12031:probe-test-token-1234567'})
    assert response.status_code == 201, response.text
    return account, response.json()['id'], calls


def test_delivery_receipts_are_monotonic_and_failed_is_not_success():
    assert advance_delivery_state('accepted', 'delivered') == 'delivered'
    assert advance_delivery_state('delivered', 'sent') == 'delivered'
    assert advance_delivery_state('read', 'delivered') == 'read'
    assert advance_delivery_state('read', 'failed') == 'read'
    assert advance_delivery_state('accepted', 'failed') == 'failed'
    assert advance_delivery_state('failed', 'delivered') == 'delivered'
    assert advance_delivery_state('uncertain', 'sent') == 'sent'
    assert advance_delivery_state('accepted', 'never-heard-of-it') == 'accepted'


def test_provider_probe_is_read_only_and_cooldown_is_persistent(client, monkeypatch):
    _, channel_id, calls = connect(client, monkeypatch)
    monkeypatch.setenv('PUBLIC_BASE_URL', 'https://inbox.example')
    async def subscription(method, url, **kwargs):
        assert method == 'GET' and url.endswith('/getWebhookInfo')
        return {'ok': True, 'result': {
            'url': 'https://inbox.example/api/webhooks/telegram/' + channel_id,
            'pending_update_count': 2}}
    monkeypatch.setattr(subscription_check, 'call', subscription)
    result = client.post('/api/integrations/' + channel_id + '/probe')
    assert result.status_code == 200, result.text
    data = result.json()
    assert data['identity_verified'] is True
    assert data['provider_webhook_matches'] is True
    assert data['incoming_verified'] is False
    assert data['outbound_api_accepted'] is False
    assert data['ready_for_api_use'] is False
    assert data['provider_pending_updates'] == 2
    assert data['last_probe_at']
    assert client.post('/api/integrations/' + channel_id + '/probe').status_code == 429
    assert not any(url.endswith('/sendMessage') for _, url, _ in calls)
    assert 'probe-test-token' not in str(data)


def test_mismatched_provider_webhook_demotes_connected_claim(client, monkeypatch):
    _, channel_id, _ = connect(client, monkeypatch)
    monkeypatch.setenv('PUBLIC_BASE_URL', 'https://inbox.example')
    with store.SessionLocal() as session:
        channel = session.get(ChannelConnection, channel_id)
        channel.status = 'connected'
        channel.webhook_registered_at = store.now()
        channel.webhook_provider_verified_at = store.now()
        channel.webhook_verified_at = store.now()
        session.commit()
    async def mismatch(method, url, **kwargs):
        return {'ok': True, 'result': {'url': 'https://other.example/changed'}}
    monkeypatch.setattr(subscription_check, 'call', mismatch)
    result = client.post('/api/integrations/' + channel_id + '/probe')
    assert result.status_code == 200, result.text
    assert result.json()['provider_webhook_matches'] is False
    assert result.json()['ready_for_api_use'] is False
    with store.SessionLocal() as session:
        channel = session.get(ChannelConnection, channel_id)
        assert channel.status == 'needs_attention'
        assert channel.webhook_provider_verified_at is None


def test_provider_probe_is_tenant_scoped(client, monkeypatch):
    _, channel_id, _ = connect(client, monkeypatch)
    client.post('/api/auth/logout')
    register(client, 'probe-other@example.com', 'Other Tenant')
    assert client.post('/api/integrations/' + channel_id + '/probe').status_code == 404


def test_probe_rejects_wrong_external_identity(client, monkeypatch):
    _, channel_id, _ = connect(client, monkeypatch)
    import app.integrations.adapters as adapters
    async def wrong_account(method, url, **kwargs):
        assert url.endswith('/getMe')
        return {'ok': True, 'result': {
            'id': 99993, 'is_bot': True, 'username': 'wrong_account'}}
    monkeypatch.setattr(adapters, 'call', wrong_account)
    result = client.post('/api/integrations/' + channel_id + '/probe')
    assert result.status_code == 422, result.text
    assert 'probe-test-token' not in result.text
    with store.SessionLocal() as session:
        assert session.get(ChannelConnection, channel_id).status == 'needs_attention'


def test_probe_temporary_provider_outage_does_not_fake_invalid_token(client, monkeypatch):
    _, channel_id, _ = connect(client, monkeypatch)
    import app.integrations.adapters as adapters
    async def outage(method, url, **kwargs):
        raise AdapterError('Temporary provider timeout', retriable=True)
    monkeypatch.setattr(adapters, 'call', outage)
    r = client.post('/api/integrations/' + channel_id + '/probe')
    assert r.status_code == 502
    with store.SessionLocal() as session:
        assert session.get(ChannelConnection, channel_id).status == 'pending_webhook'


def test_whatsapp_out_of_order_receipts_do_not_downgrade_delivery(client, monkeypatch):
    me = register(client, 'wa-probe@example.com', 'Receipt workspace')
    with store.SessionLocal() as session:
        ch = ChannelConnection(organization_id=me['organization']['id'],provider='whatsapp',
                               external_account_id='1111234567',name='WA',mode='live',status='connected')
        contact = Contact(organization_id=me['organization']['id'],name='Customer')
        session.add_all([ch, contact]);session.flush()
        conv = Conversation(organization_id=me['organization']['id'],channel_id=ch.id,
                            contact_id=contact.id, external_chat_id='19992223333')
        session.add(conv);session.flush()
        m = Message(organization_id=me['organization']['id'],conversation_id=conv.id,
                    external_id='wamid.case123',direction='out',body='Hello',delivery_status='accepted')
        session.add(m);session.commit()
        message_id = m.id
    for receipt, expected in [('delivered','delivered'),('sent','delivered'),('read','read'),('failed','read')]:
        event = {'object':'whatsapp_business_account','entry':[{'changes':[{'value':{
            'metadata': {'phone_number_id': '1111234567'},
            'statuses':[{'id':'wamid.case123','status':receipt}]}}]}]}
        raw = json.dumps(event,separators=(',',':')).encode()
        signature = hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
        result = client.post('/api/webhooks/whatsapp',data=raw,
            headers={'X-Hub-Signature-256':'sha256='+signature,'Content-Type':'application/json'})
        assert result.status_code == 200, result.text
        with store.SessionLocal() as session:
            assert session.get(Message, message_id).delivery_status == expected
