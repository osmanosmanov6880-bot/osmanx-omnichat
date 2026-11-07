"""v0.8 proof ladder and provider-side webhook checks.

Provider HTTP transports are mocked deliberately: these tests do NOT claim a
live Telegram, MAX or Meta account was actually connected.
"""
import asyncio
import pytest
from app import db
from app.integrations import subscription_check
from app.integrations.readiness import readiness
from app.services import process_outbox
from conftest import register
from test_bot_channels import fake_provider_api, get_secret


def connect_tg(client,monkeypatch):
    register(client)
    fake_provider_api(monkeypatch)
    response=client.post('/api/integrations/bots',json={'provider':'telegram','access_token':'12031:telegram-test-token-12345'})
    assert response.status_code==201,response.text
    return response.json()['id']


def test_four_stages_do_not_turn_green_from_token_alone(client,monkeypatch):
    channel=connect_tg(client,monkeypatch)
    r=client.get('/api/integrations/'+channel+'/diagnostics')
    assert r.status_code==200,r.text
    d=r.json()
    assert [stage['done'] for stage in d['stages']]==[True,False,False,False]
    assert d['ready_for_api_use'] is False
    assert d['outbound_api_accepted'] is False
    assert d['provider_check_available'] is True
    assert 'telegram-test-token' not in str(d)
    listing=client.get('/api/integrations').json()['connections'][0]
    assert listing['readiness']['ready_for_api_use'] is False
    assert listing['readiness']['stages'][0]['done'] is True


def test_telegram_registration_readback_and_inbound_outbound(client,monkeypatch):
    channel=connect_tg(client,monkeypatch)
    monkeypatch.setenv('PUBLIC_BASE_URL','https://omnichat.example')
    seen=[]
    async def tg_info(method,url,**kwargs):
        seen.append((method,url))
        assert method=='GET' and url.endswith('/getWebhookInfo')
        return {'ok':True,'result':{'url':f'https://omnichat.example/api/webhooks/telegram/{channel}',
                    'pending_update_count':3}}
    monkeypatch.setattr(subscription_check,'call',tg_info)
    act=client.post('/api/integrations/'+channel+'/activate-webhook')
    assert act.status_code==200,act.text
    d=client.get('/api/integrations/'+channel+'/diagnostics').json()
    assert d['webhook_registered'] is True
    assert d['webhook_provider_verified'] is True
    assert d['webhook_event_seen'] is False
    assert d['ready_for_api_use'] is False
    assert len(seen)==1
    assert client.post('/api/integrations/'+channel+'/verify-provider-webhook').json()['pending_updates']==3

    event={'update_id':558,'message':{'message_id':558,'date':int(db.now()),
        'from':{'id':5333,'first_name':'Клиент','is_bot':False},
        'chat':{'id':5333,'type':'private'},'text':'Здравствуйте!'}}
    result=client.post('/api/webhooks/telegram/'+channel,json=event,
        headers={'X-Telegram-Bot-Api-Secret-Token':get_secret(channel)})
    assert result.status_code==200,result.text
    diag=client.get('/api/integrations/'+channel+'/diagnostics').json()
    assert [x['done'] for x in diag['stages']]==[True,True,True,False]
    conv=client.get('/api/conversations').json()[0]
    detail=client.get('/api/conversations/'+conv['id']).json()
    send=client.post('/api/conversations/'+conv['id']+'/reply',json={
        'body':'Ответ через единый Inbox','expected_version':detail['conversation']['version'],'client_nonce':'tg-v8-abcdef'})
    assert send.status_code==201,send.text
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    d=client.get('/api/integrations/'+channel+'/diagnostics').json()
    assert d['ready_for_api_use'] is True
    assert [x['done'] for x in d['stages']]==[True,True,True,True]
    assert d['outbound_api_accepted'] is True
    # Critical wording distinction: API acceptance is NOT delivery or read receipt.
    assert 'не означает доставку' in d['disclaimer']


def test_mismatched_webhook_revokes_ready_status_and_stays_tenant_scoped(client,monkeypatch):
    ch=connect_tg(client,monkeypatch)
    monkeypatch.setenv('PUBLIC_BASE_URL','https://omnichat.example')
    async def fake(method,url,**kw):
        assert method=='GET' and url.endswith('/getWebhookInfo')
        return {'ok':True,'result':{'url':'https://someone-else.invalid/hook','pending_update_count':0}}
    monkeypatch.setattr(subscription_check,'call',fake)
    response=client.post('/api/integrations/'+ch+'/verify-provider-webhook')
    assert response.status_code==200,response.text
    assert response.json()['matches'] is False
    d=client.get('/api/integrations/'+ch+'/diagnostics').json()
    assert d['webhook_provider_verified'] is False
    assert d['webhook_registered'] is False
    assert d['ready_for_api_use'] is False
    # Owner of a different org cannot probe this bot, even knowing its UUID.
    client.post('/api/auth/logout')
    register(client,email='other-company@example.com',name='Чужая фирма')
    assert client.get('/api/integrations/'+ch+'/diagnostics').status_code==404
    assert client.post('/api/integrations/'+ch+'/verify-provider-webhook').status_code==404


def test_max_provider_webhook_readback_requires_exact_url(client,monkeypatch):
    register(client)
    fake_provider_api(monkeypatch)
    resp=client.post('/api/integrations/bots',json={'provider':'max','access_token':'MAX-bot-token-1234567'})
    assert resp.status_code==201,resp.text
    ch=resp.json()['id']
    monkeypatch.setenv('PUBLIC_BASE_URL','https://omnichat.example')
    async def fake(method,url,**kw):
        assert method=='GET' and url.endswith('/subscriptions')
        assert 'Authorization' in kw.get('headers',{})
        return {'subscriptions':[{'url':f'https://omnichat.example/api/webhooks/max/{ch}'}]}
    monkeypatch.setattr(subscription_check,'call',fake)
    r=client.post('/api/integrations/'+ch+'/verify-provider-webhook')
    assert r.status_code==200,r.text
    assert r.json()['matches'] is True
    assert client.get('/api/integrations/'+ch+'/diagnostics').json()['webhook_provider_verified'] is True


def test_provider_check_requires_https_and_supported_provider(client,monkeypatch):
    ch=connect_tg(client,monkeypatch)
    monkeypatch.delenv('PUBLIC_BASE_URL',raising=False)
    assert client.post('/api/integrations/'+ch+'/verify-provider-webhook').status_code==503
    monkeypatch.setenv('PUBLIC_BASE_URL','https://omnichat.example')
    async def bad(method,url,**kwargs):
        return {'ok':False,'description':'bad'}
    monkeypatch.setattr(subscription_check,'call',bad)
    assert client.post('/api/integrations/'+ch+'/verify-provider-webhook').status_code==502


def test_access_recheck_preserves_accepted_outgoing_proof(client,monkeypatch):
    """A routine identity check cannot undo a genuinely accepted response."""
    channel=connect_tg(client,monkeypatch)
    with db.SessionLocal() as s:
        from app.db import ChannelConnection
        ch=s.get(ChannelConnection,channel)
        ch.outbound_api_accepted_at=db.now()
        s.commit()
    before=client.get('/api/integrations/'+channel+'/diagnostics').json()
    assert before['outbound_api_accepted'] is True
    checked=client.post('/api/integrations/'+channel+'/check-access')
    assert checked.status_code==200,checked.text
    after=client.get('/api/integrations/'+channel+'/diagnostics').json()
    assert after['outbound_api_accepted'] is True


def test_token_rotation_invalidates_outbound_proof_even_for_whatsapp(client,monkeypatch):
    """Changing a credential must require a new provider-accepted reply."""
    ch=connect_tg(client,monkeypatch)
    from app.db import ChannelConnection
    with db.SessionLocal() as s:
        channel=s.get(ChannelConnection,ch)
        channel.outbound_api_accepted_at=db.now()
        channel.webhook_provider_verified_at=db.now()
        s.commit()
    before=client.get('/api/integrations/'+ch+'/diagnostics').json()
    assert before['outbound_api_accepted'] is True
    new=client.post('/api/integrations/'+ch+'/rotate-token',json={'access_token':'12031:replacement-token-12345678'})
    assert new.status_code==200,new.text
    after=client.get('/api/integrations/'+ch+'/diagnostics').json()
    assert after['outbound_api_accepted'] is False
    assert after['webhook_provider_verified'] is False
    assert [stage['done'] for stage in after['stages']]==[True,False,False,False]


def test_disconnect_telegram_revokes_provider_webhook_before_dropping_secrets(client,monkeypatch):
    ch=connect_tg(client,monkeypatch)
    seen=[]
    async def fake(method,url,**kw):
        seen.append((method,url))
        if url.endswith('/deleteWebhook'):
            assert method=='POST' and kw['json_data']['drop_pending_updates'] is False
            return {'ok':True,'result':True}
        assert method=='GET' and url.endswith('/getWebhookInfo')
        return {'ok':True,'result':{'url':''}}
    monkeypatch.setattr(subscription_check,'call',fake)
    response=client.post('/api/integrations/'+ch+'/disconnect')
    assert response.status_code==200,response.text
    assert response.json()['ok'] is True
    assert [method for method,_ in seen]==['POST','GET']
    from app.db import ChannelConnection
    with db.SessionLocal() as s:
        channel=s.get(ChannelConnection,ch)
        assert channel.encrypted_credentials is None
        assert channel.status=='disconnected'
        assert channel.webhook_provider_verified_at is None


def test_disconnect_telegram_failure_keeps_encrypted_credential_for_retry(client,monkeypatch):
    ch=connect_tg(client,monkeypatch)
    from app.integrations.base import AdapterError
    async def failure(method,url,**kw):
        raise AdapterError('Тестовая сетевая ошибка')
    monkeypatch.setattr(subscription_check,'call',failure)
    response=client.post('/api/integrations/'+ch+'/disconnect')
    assert response.status_code==502,response.text
    from app.db import ChannelConnection
    with db.SessionLocal() as s:
        channel=s.get(ChannelConnection,ch)
        assert channel.encrypted_credentials is not None
        assert channel.status!='disconnected'


def test_disconnect_max_removes_only_current_channel_webhook(client,monkeypatch):
    register(client)
    fake_provider_api(monkeypatch)
    channel=client.post('/api/integrations/bots',json={'provider':'max','access_token':'MAX-bot-token-1234567'}).json()['id']
    monkeypatch.setenv('PUBLIC_BASE_URL','https://omnichat.example')
    seen=[]
    async def fake(method,url,**kw):
        seen.append((method,url,kw))
        if method=='DELETE':
            assert kw['params']=={'url':f'https://omnichat.example/api/webhooks/max/{channel}'}
            return {'success':True}
        assert method=='GET'
        return {'subscriptions':[]}
    monkeypatch.setattr(subscription_check,'call',fake)
    response=client.post('/api/integrations/'+channel+'/disconnect')
    assert response.status_code==200,response.text
    assert [method for method,_,_ in seen]==['DELETE','GET']
