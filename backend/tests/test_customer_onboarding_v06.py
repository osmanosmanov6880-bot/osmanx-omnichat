"""Customer-owned official channels: security boundaries and mocked protocol contract checks.

All Graph/Bot HTTP responses in these tests are explicitly mocked. They do not
establish Meta App Review or a real production social account connection.
"""
import asyncio
import hashlib
import hmac
import json
from urllib.parse import urlsplit, parse_qs

from app import db
from app.integrations.adapters import unseal
from app.services import process_outbox
from conftest import register


def fb_fake(monkeypatch):
    calls=[]
    async def transport(method,url,**kw):
        calls.append((method,url,kw))
        if url.endswith('/oauth/access_token'):
            return {'access_token':'FACEBOOK-valid-remote-test-token','expires_in':3600}
        if url.endswith('/me/accounts'):
            return {'data':[{'id':'10101010','name':'Фирменная страница','access_token':'PAGE-secret-123456789','tasks':['MESSAGING','ANALYZE']},
                            {'id':'20202020','name':'Страница без прав на сообщения','access_token':'PAGE-secret-222222222','tasks':['ANALYZE']}]}
        if url.endswith('/10101010'):
            return {'id':'10101010','name':'Фирменная страница'}
        if url.endswith('/10101010/subscribed_apps'):
            return {'success':True}
        if url.endswith('/10101010/messages'):
            return {'message_id':'mid-fb-out-1'}
        if url.endswith('/99887766/phone_numbers'):
            return {'data':[{'id':'88990011','display_phone_number':'+7 901 111-22-33','verified_name':'Бизнес 1'}]}
        if url.endswith('/88990011'):
            return {'id':'88990011','display_phone_number':'+7 901 111-22-33','verified_name':'Бизнес 1'}
        if url.endswith('/99887766/subscribed_apps'):
            return {'success':True}
        if url.endswith('/88990011/register'):
            return {'success':True}
        raise AssertionError('Неожиданный HTTP запрос: '+method+' '+url)
    import app.main as main
    import app.onboarding as onboarding
    import app.integrations.adapters as adapters
    for module in (main,onboarding,adapters):
        monkeypatch.setattr(module,'call',transport)
    return calls


def setup_meta(monkeypatch):
    monkeypatch.setenv('PUBLIC_BASE_URL','https://omnichat.example')
    monkeypatch.setenv('FACEBOOK_APP_ID','123456789')
    monkeypatch.setenv('FACEBOOK_APP_SECRET','fb-secret')
    monkeypatch.setenv('META_APP_ID','987654321')
    monkeypatch.setenv('META_APP_SECRET','fb-secret')
    monkeypatch.setenv('META_WHATSAPP_CONFIG_ID','333333333')
    monkeypatch.setenv('META_WEBHOOK_VERIFY_TOKEN','verify-token-123')


def test_multiple_companies_have_isolated_channels_and_session_switch(client,monkeypatch):
    owner=register(client)
    a=owner['organization']['id']
    added=client.post('/api/organizations',json={'name':'Ресторан Солнце'})
    assert added.status_code==201,added.text
    b=added.json()['id']; assert b!=a
    assert len(client.get('/api/auth/me').json()['organizations'])==2
    assert client.get('/api/integrations').json()['connections']==[]
    response=client.post('/api/auth/switch/'+b)
    assert response.status_code==200,response.text
    assert client.get('/api/auth/me').json()['organization']['id']==b
    assert client.get('/api/integrations').json()['connections']==[]
    assert client.post('/api/auth/switch/'+a).status_code==200
    assert client.get('/api/auth/me').json()['organization']['id']==a
    # A different user/tenant may not switch to either company by guessing the ID.
    client.post('/api/auth/logout')
    register(client,email='second-owner@example.com',name='Чужая компания')
    assert client.post('/api/auth/switch/'+a).status_code==403
    assert client.post('/api/auth/switch/'+b).status_code==403


def test_provider_guide_and_meta_https_prerequisites(client,monkeypatch):
    register(client)
    info=client.get('/api/integrations/guide').json()
    assert info['https_ready'] is False
    assert info['meta_embedded_signup_ready'] is False
    assert 'messenger' in info['providers']
    assert info['providers']['telegram']['account'].startswith('Telegram')
    assert client.post('/api/integrations/whatsapp/embedded/start').status_code==503
    setup_meta(monkeypatch)
    info=client.get('/api/integrations/guide').json()
    assert info['meta_embedded_signup_ready'] is True
    init=client.post('/api/integrations/whatsapp/embedded/start')
    assert init.status_code==200,init.text
    assert 'state' in init.json() and 'app_id' in init.json()
    assert 'fb-secret' not in str(init.json())


def test_page_selection_is_explicit_secure_and_messenger_reply_is_page_scoped(client,monkeypatch):
    me=register(client)
    setup_meta(monkeypatch)
    calls=fb_fake(monkeypatch)
    start=client.post('/api/integrations/oauth-start/messenger')
    assert start.status_code==200,start.text
    redirect=start.json()['url']
    state=parse_qs(urlsplit(redirect).query)['state'][0]
    assert 'pages_messaging' in redirect
    callback=client.get('/api/integrations/oauth-callback/messenger',params={'state':state,'code':'provider-code'},follow_redirects=False)
    assert callback.status_code==303,callback.text
    assert callback.headers['location'].endswith('oauth=pages')
    assert client.get('/api/integrations/oauth-callback/messenger',params={'state':state,'code':'provider-code'},follow_redirects=False).status_code==403
    page_list=client.get('/api/integrations/messenger/pages')
    assert page_list.status_code==200
    assert page_list.json()['pages']==[{'id':'10101010','name':'Фирменная страница'}]
    assert 'PAGE-secret' not in page_list.text
    assert client.post('/api/integrations/messenger/pages/20202020/connect').status_code==404
    link=client.post('/api/integrations/messenger/pages/10101010/connect')
    assert link.status_code==201,link.text
    ch=link.json()['id']; assert link.json()['status']=='pending_webhook'
    assert 'PAGE-secret' not in link.text
    info=client.get('/api/integrations/'+ch+'/diagnostics')
    assert info.status_code==200
    assert info.json()['webhook_registered'] is True
    assert info.json()['webhook_event_seen'] is False
    assert client.get('/api/integrations').json()['connections'][0]['status']=='pending_webhook'

    event={'object':'page','entry':[{'id':'10101010','messaging':[{'sender':{'id':'121212'},'recipient':{'id':'10101010'},
        'timestamp':int(db.now()*1000),'message':{'mid':'mid-fb-in-1','text':'Нужен ответ менеджера'}}]}]}
    raw=json.dumps(event,ensure_ascii=False).encode()
    assert client.post('/api/webhooks/messenger',content=raw,headers={'X-Hub-Signature-256':'sha256='+'0'*64}).status_code==403
    assert client.get('/api/conversations').json()==[]
    signature='sha256='+hmac.new(b'fb-secret',raw,hashlib.sha256).hexdigest()
    received=client.post('/api/webhooks/messenger',content=raw,headers={'X-Hub-Signature-256':signature})
    assert received.status_code==200,received.text
    assert received.json()['accepted']==1
    assert client.post('/api/webhooks/messenger',content=raw,headers={'X-Hub-Signature-256':signature}).json()['accepted']==0
    rows=client.get('/api/conversations').json()
    assert len(rows)==1 and rows[0]['channel']=='messenger'
    assert client.get('/api/integrations/'+ch+'/diagnostics').json()['webhook_event_seen'] is True
    conv=client.get('/api/conversations/'+rows[0]['id']).json()
    reply=client.post('/api/conversations/'+rows[0]['id']+'/reply',json={'body':'Здравствуйте!','expected_version':conv['conversation']['version'],
        'client_nonce':'unique-message-nonce-123'})
    assert reply.status_code==201,reply.text
    assert asyncio.run(process_outbox(db.SessionLocal))==1
    outbound=[x for x in calls if x[1].endswith('/10101010/messages')]
    assert len(outbound)==1
    assert outbound[0][2]['json_data']['recipient']['id']=='121212'
    assert client.post('/api/integrations/messenger/pages/10101010/connect').status_code==409
    # Switching company makes its identity, messages and diagnostic URL inaccessible.
    created=client.post('/api/organizations',json={'name':'Второй бизнес'})
    assert created.status_code==201
    assert client.post('/api/auth/switch/'+created.json()['id']).status_code==200
    assert client.get('/api/conversations').json()==[]
    assert client.get('/api/integrations/messenger/pages').json()['pages']==[]
    assert client.get('/api/integrations/'+ch+'/diagnostics').status_code==404
    assert client.post('/api/integrations/messenger/pages/10101010/connect').status_code==403


def test_whatsapp_embedded_ownership_replay_and_registration(client,monkeypatch):
    register(client)
    setup_meta(monkeypatch)
    observed=fb_fake(monkeypatch)
    begin=client.post('/api/integrations/whatsapp/embedded/start').json()
    data={'state':begin['state'],'code':'fb-business-code','waba_id':'99887766','phone_number_id':'88990011'}
    tampered={**data,'phone_number_id':'99999999'}
    denied=client.post('/api/integrations/whatsapp/embedded/complete',json=tampered)
    assert denied.status_code==422,denied.text
    assert client.post('/api/integrations/whatsapp/embedded/complete',json=data).status_code==403  # one-time state
    begin=client.post('/api/integrations/whatsapp/embedded/start').json()
    data['state']=begin['state']
    complete=client.post('/api/integrations/whatsapp/embedded/complete',json=data)
    assert complete.status_code==201,complete.text
    ch=complete.json()['id']
    assert complete.json()['status']=='pending_webhook'
    assert 'FACEBOOK-valid' not in str(client.get('/api/integrations').json())
    assert client.post('/api/integrations/whatsapp/embedded/complete',json=data).status_code==403
    assert client.post('/api/integrations/'+ch+'/register-phone',json={'pin':'12'}).status_code==422
    phone=client.post('/api/integrations/'+ch+'/register-phone',json={'pin':'123456'})
    assert phone.status_code==200,phone.text
    assert '123456' not in str(client.get('/api/integrations').json())
    assert any(x[1].endswith('/88990011/register') for x in observed)
    assert client.get('/api/integrations/'+ch+'/diagnostics').json()['webhook_registered'] is True
    assert client.get('/api/integrations/'+ch+'/diagnostics').json()['webhook_event_seen'] is False


def test_demo_disallows_real_accounts_and_company_creation(client):
    assert client.post('/api/demo/start').status_code==200
    assert client.post('/api/organizations',json={'name':'Некорректно'}).status_code==403
    assert client.post('/api/integrations/whatsapp/embedded/start').status_code==403
    assert client.get('/api/integrations/messenger/pages').status_code in (200,403)


def test_vk_secrets_only_for_own_company_and_token_rotation(client,monkeypatch):
    me=register(client)
    monkeypatch.setenv('PUBLIC_BASE_URL','https://omnichat.example')
    calls=[]
    async def bot_transport(method,url,**kw):
        calls.append((method,url,kw))
        if url.endswith('/getMe'): return {'ok':True,'result':{'id':777,'is_bot':True,'username':'custom_test_bot'}}
        if url.endswith('/setWebhook'): return {'ok':True}
        if url.endswith('/groups.getById'): return {'response':{'groups':[{'id':4422,'name':'Тестовая группа'}]}}
        raise AssertionError(url)
    import app.integrations.adapters as adapters
    import app.main as main
    monkeypatch.setattr(adapters,'call',bot_transport)
    monkeypatch.setattr(main,'call',bot_transport)
    vk=client.post('/api/integrations/bots',json={'provider':'vk','group_id':'4422','access_token':'vk-test-secret-abcDEF100','confirmation_token':'confirm-key-xyz'})
    assert vk.status_code==201,vk.text
    id=vk.json()['id']
    callback=client.get('/api/integrations/'+id+'/vk-callback-setup')
    assert callback.status_code==200 and callback.json()['confirmation_token']=='confirm-key-xyz'
    assert 'vk-test-secret' not in str(client.get('/api/integrations').json())
    assert client.post('/api/integrations/'+id+'/rotate-token',json={'access_token':'changed-token-for-another-account'}).status_code in (200,409)
    created=client.post('/api/organizations',json={'name':'Чужой проект'})
    assert client.post('/api/auth/switch/'+created.json()['id']).status_code==200
    assert client.get('/api/integrations/'+id+'/vk-callback-setup').status_code==404
    assert client.post('/api/integrations/'+id+'/check-access').status_code==404
    assert client.post('/api/integrations/'+id+'/rotate-token',json={'access_token':'test-test-11223344'}).status_code==404
