"""Official bot API contract tests. Network calls are mocked; no fake 'live' integration claims."""
import asyncio
import hashlib
from app import db
from app.integrations.adapters import unseal
from app.services import process_outbox
from conftest import register


def fake_provider_api(monkeypatch):
    import app.integrations.adapters as mod
    observed=[]
    async def transport(method,url,**kw):
        observed.append((method,url,kw))
        if url.endswith('/getMe'):return {'ok':True,'result':{'id':12031,'username':'osmanx_assistant_bot','is_bot':True}}
        if url.endswith('/sendMessage'):return {'ok':True,'result':{'message_id':556677}}
        if url.endswith('/me'):return {'user_id':7702,'name':'OSMANX MAX','is_bot':True}
        if url.endswith('/messages') and 'max.ru' in url:return {'message':{'body':{'mid':'max-sent-123'}}}
        if url.endswith('/groups.getById'):return {'response':{'groups':[{'id':4422,'name':'OSMANX VK'}]}}
        if url.endswith('/messages.send'):return {'response':88883}
        if url.endswith('/setWebhook'):return {'ok':True}
        if url.endswith('/subscriptions'):return {'success':True}
        raise AssertionError(f'Unexpected provider HTTP call: {method} {url}')
    monkeypatch.setattr(mod,'call',transport)
    # main module imported 'call' by value: patch explicit registration paths too
    import app.main as main
    monkeypatch.setattr(main,'call',transport)
    return observed


def verify_sent(client,conv_id):
    data=client.get('/api/conversations/'+conv_id).json()
    payload={'body':'Спасибо за сообщение!','expected_version':data['conversation']['version'],'client_nonce':'new-nonce-0012345'}
    result=client.post('/api/conversations/'+conv_id+'/reply',json=payload)
    assert result.status_code==201,result.text
    assert result.json()['message']['delivery_status']=='queued'
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    messages=client.get('/api/conversations/'+conv_id).json()['messages']
    assert messages[-1]['delivery_status']=='accepted'


def test_telegram_bot_signed_webhook_to_inbox_and_reply(client,monkeypatch):
    register(client)
    observed=fake_provider_api(monkeypatch)
    response=client.post('/api/integrations/bots',json={'provider':'telegram','access_token':'12031:telegram-test-token-12345'})
    assert response.status_code==201,response.text
    info=response.json();assert info['status']=='pending_webhook'
    token = get_secret(info['id'])
    assert 'access_token' not in str(client.get('/api/integrations').json())
    endpoint=f"/api/webhooks/telegram/{info['id']}"
    event={'update_id':123,'message':{'message_id':987,'date':1780000000,'from':{'id':43321,'first_name':'Мария','is_bot':False},'chat':{'id':43321,'type':'private'},'text':'Здравствуйте из Telegram'}}
    assert client.post(endpoint,json=event,headers={'X-Telegram-Bot-Api-Secret-Token':'bad'}).status_code==403
    assert client.get('/api/conversations').json()==[]
    good={'X-Telegram-Bot-Api-Secret-Token':token}
    a=client.post(endpoint,json=event,headers=good)
    assert a.status_code==200,a.text
    assert a.json()['accepted']==1
    assert client.post(endpoint,json=event,headers=good).json()['accepted']==0
    conv=client.get('/api/conversations').json()
    assert len(conv)==1 and conv[0]['channel']=='telegram'
    assert 'Мария' in conv[0]['contact_name']
    assert client.get('/api/integrations').json()['connections'][0]['status']=='connected'
    verify_sent(client,conv[0]['id'])
    assert any(url.endswith('/sendMessage') for _,url,_ in observed)


def get_secret(channel_id):
    from app.db import ChannelConnection
    with db.SessionLocal() as s:
        channel=s.get(ChannelConnection,channel_id)
        return unseal(channel.encrypted_credentials)['webhook_secret']


def test_vk_community_verification_confirmation_inbox_reply(client,monkeypatch):
    register(client)
    calls=fake_provider_api(monkeypatch)
    resp=client.post('/api/integrations/bots',json={'provider':'vk','access_token':'vk-community-token-123456','group_id':'4422','confirmation_token':'confirm-vk-xyz'})
    assert resp.status_code==201,resp.text
    info=resp.json();assert info['status']=='pending_webhook';assert info['webhook_secret']
    hook=f"/api/webhooks/vk/{info['id']}"
    assert client.post(hook,json={'type':'confirmation','secret':'wrong','group_id':4422}).status_code==403
    confirm=client.post(hook,json={'type':'confirmation','secret':info['webhook_secret'],'group_id':4422})
    assert confirm.status_code==200 and confirm.text=='confirm-vk-xyz'
    assert client.get('/api/integrations').json()['connections'][0]['status']=='pending_webhook'
    event={'type':'message_new','group_id':4422,'secret':info['webhook_secret'],'object':{'message':{'id':90001,'peer_id':4567,'from_id':4567,'text':'Вопрос из сообщества','date':1780000000}}}
    assert client.post(hook,json=event).status_code==200
    assert client.post(hook,json=event).status_code==200
    conv=client.get('/api/conversations').json()
    assert len(conv)==1 and conv[0]['channel']=='vk'
    assert len(client.get('/api/conversations/'+conv[0]['id']).json()['messages'])==1
    verify_sent(client,conv[0]['id'])
    sends=[kw['data'] for _,url,kw in calls if url.endswith('/messages.send')]
    assert len(sends)==1 and int(sends[0]['random_id'])>0


def test_max_signed_webhook_inbox_and_reply(client,monkeypatch):
    register(client)
    called=fake_provider_api(monkeypatch)
    resp=client.post('/api/integrations/bots',json={'provider':'max','access_token':'max-bot-token-0012345'})
    assert resp.status_code==201,resp.text
    info=resp.json();secret=get_secret(info['id'])
    hook=f"/api/webhooks/max/{info['id']}"
    event={'update_type':'message_created','timestamp':1780000000000,'message':{'timestamp':1780000000000,'sender':{'user_id':88222,'first_name':'Руслан','is_bot':False},'recipient':{'chat_type':'dialog','user_id':88222},'body':{'mid':'max-in-0001','text':'Вопрос из MAX'}}}
    assert client.post(hook,json=event,headers={'X-Max-Bot-Api-Secret':'wrong'}).status_code==403
    result=client.post(hook,json=event,headers={'X-Max-Bot-Api-Secret':secret})
    assert result.status_code==200,result.text
    assert result.json()['accepted']==1
    assert client.post(hook,json=event,headers={'X-Max-Bot-Api-Secret':secret}).json()['accepted']==0
    conv=client.get('/api/conversations').json()
    assert len(conv)==1 and conv[0]['channel']=='max'
    verify_sent(client,conv[0]['id'])
    assert any(url.endswith('/messages') and kw.get('params')=={'user_id':'88222'} for _,url,kw in called)


def test_demo_has_six_sources_and_live_bot_creation_forbidden(client):
    r=client.post('/api/demo/start');assert r.status_code==200
    sources={c['channel'] for c in client.get('/api/conversations').json()}
    assert sources=={'avito','instagram','whatsapp','telegram','vk','max','messenger'}
    denied=client.post('/api/integrations/bots',json={'provider':'telegram','access_token':'12031:telegram-test-token-12345'})
    assert denied.status_code==403


def test_telegram_webhook_registration_stays_pending_until_real_signed_event(client,monkeypatch):
    register(client)
    observed=fake_provider_api(monkeypatch)
    monkeypatch.setenv('PUBLIC_BASE_URL','https://omnichat.example')
    info=client.post('/api/integrations/bots',json={'provider':'telegram','access_token':'12031:telegram-test-token-12345'}).json()
    subscription=client.post('/api/integrations/'+info['id']+'/activate-webhook')
    assert subscription.status_code==200,subscription.text
    assert subscription.json()['status']=='pending_webhook'
    reg=[kw for method,url,kw in observed if url.endswith('/setWebhook')]
    assert len(reg)==1
    assert reg[0]['json_data']['url']=='https://omnichat.example/api/webhooks/telegram/'+info['id']
    assert reg[0]['json_data']['secret_token']==get_secret(info['id'])
    assert client.get('/api/integrations').json()['connections'][0]['status']=='pending_webhook'
