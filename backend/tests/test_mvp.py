import hashlib
import hmac
import json
import time
import pytest
from fastapi.testclient import TestClient
from app import db
from app.db import ChannelConnection, Message, Contact, Conversation, Membership, User
from app.services import ingest_inbound, process_outbox
from app.synchronizers import sync_avito
from conftest import start_demo, register


def test_demo_inbox_reply_idempotence_and_notes(client):
    me=start_demo(client)
    assert me['organization']['is_demo'] is True
    rows=client.get('/api/conversations').json()
    assert len(rows)==9
    assert all(c['channel_mode']=='demo' for c in rows)
    c=rows[0]
    detail=client.get('/api/conversations/'+c['id']).json()
    assert all(m['is_demo'] for m in detail['messages'])
    assert client.post('/api/conversations/'+c['id']+'/reply',json={'body':'x','expected_version':0,'client_nonce':'nonce-12345'},headers={'X-CSRF-Token':'invalid'}).status_code==403
    nonce='test-unique-nonce'
    payload={'body':'Тестовый ответ из приложения','expected_version':detail['conversation']['version'],'client_nonce':nonce}
    sent=client.post('/api/conversations/'+c['id']+'/reply',json=payload)
    assert sent.status_code==201,sent.text
    assert sent.json()['message']['is_demo'] is True
    assert sent.json()['message']['delivery_status']=='delivered'
    assert client.post('/api/conversations/'+c['id']+'/reply',json=payload).json()['duplicate'] is True
    other={'body':'Конфликт','expected_version':detail['conversation']['version'],'client_nonce':'other-unique-nonce'}
    assert client.post('/api/conversations/'+c['id']+'/reply',json=other).status_code==409
    note=client.post('/api/conversations/'+c['id']+'/notes',json={'body':'Внутренняя заметка'})
    assert note.status_code==201
    assert 'Внутренняя заметка' in [n['body'] for n in client.get('/api/conversations/'+c['id']).json()['notes']]


def test_demo_incoming_search_filters_and_rules(client):
    start_demo(client)
    rows=client.get('/api/conversations').json()
    chosen=next(c for c in rows if c['channel']=='avito')
    r=client.post('/api/demo/incoming',json={'conversation_id':chosen['id'],'body':'СРОЧНО нужна встреча'})
    assert r.status_code==201,r.text
    c=client.get('/api/conversations/'+chosen['id']).json()
    assert 'Срочно' in c['contact']['tags']
    assert client.get('/api/conversations',params={'q':'СРОЧНО'}).json()
    assert all(c['channel']=='avito' for c in client.get('/api/conversations',params={'channel':'avito'}).json())
    mark=client.post('/api/conversations/'+chosen['id']+'/unread')
    assert mark.status_code==200
    read=client.post('/api/conversations/'+chosen['id']+'/read')
    assert read.status_code==200
    assert read.json()['ok']
    assert client.post('/api/conversations/'+chosen['id']+'/archive').status_code==200
    assert chosen['id'] not in [c['id'] for c in client.get('/api/conversations').json()]
    assert chosen['id'] in [c['id'] for c in client.get('/api/conversations',params={'archived':True}).json()]


def test_tenant_isolation_csrf_and_role_filters(client):
    demo1=start_demo(client)
    org1=demo1['organization']['id']
    id1=client.get('/api/conversations').json()[0]['id']
    from app.main import app
    with TestClient(app) as other:
        demo2=start_demo(other)
        assert demo2['organization']['id']!=org1
        assert other.get('/api/conversations/'+id1).status_code==404
        assert other.post('/api/demo/incoming',json={'conversation_id':id1,'body':'Чужой чат'},headers={'X-CSRF-Token':other.cookies.get('omnichat_csrf','')}).status_code==404
        assert client.get('/api/contacts').status_code==200
        assert other.get('/api/organization/export').status_code==200
        assert id1 not in json.dumps(other.get('/api/organization/export').json())
        assert other.get('/api/auth/me').json()['organization']['id']==demo2['organization']['id']
    assert client.get('/api/auth/me').json()['organization']['id']==org1


def test_saas_plans_and_invites_proof_of_password(client):
    user=register(client)
    assert user['organization']['plan']=='starter'
    assert client.get('/api/analytics').status_code==402
    assert client.post('/api/rules',json={'name':'A Rule','action_type':'tag','action_value':'tag'}).status_code==402
    assert client.post('/api/team/invite',json={'email':'new@example.com','role':'manager'}).status_code==402
    with db.SessionLocal() as session:
        session.get(db.Organization,user['organization']['id']).plan='business';session.commit()
    r=client.post('/api/team/invite',json={'email':'new@example.com','role':'manager'})
    assert r.status_code==200,r.text
    token=r.json()['invite_token']
    assert client.post('/api/team/accept-invite',json={'token':token,'name':'Новый','password':'longpassword123456'}).status_code==200
    assert client.post('/api/team/accept-invite',json={'token':token,'name':'Новый','password':'longpassword123456'}).status_code==404
    client.post('/api/auth/logout')
    resp=client.post('/api/auth/login',json={'email':'new@example.com','password':'longpassword123456'})
    assert resp.status_code==200
    assert client.get('/api/auth/me').json()['role']=='manager'
    assert client.get('/api/analytics').status_code==403
    assert client.get('/api/audit').status_code==403
    assert client.get('/api/organization/export').status_code==403


def test_existing_invitee_requires_password(client):
    owner=register(client)
    with db.SessionLocal() as session:
        session.get(db.Organization,owner['organization']['id']).plan='professional';session.commit()
    create=client.post('/api/team/invite',json={'email':'existing@example.com','role':'operator'})
    token=create.json()['invite_token']
    with db.SessionLocal() as session:
        session.add(db.User(email='existing@example.com',name='Сотрудник',password_hash=db.uid()))
        session.commit()
    assert client.post('/api/team/accept-invite',json={'token':token,'password':'wrong'}).status_code==401


def test_hmac_webhooks_dedup_and_rejects_invalid(client):
    owner=register(client)
    with db.SessionLocal() as session:
        ch=db.ChannelConnection(organization_id=owner['organization']['id'],provider='whatsapp',name='Live for test',external_account_id='101010101',mode='live',status='connected')
        session.add(ch);session.commit()
    event={'object':'whatsapp_business_account','entry':[{'changes':[{'value':{
      'metadata':{'phone_number_id':'101010101'},
      'contacts':[{'wa_id':'79000000001','profile':{'name':'Мария Тест'}}],
      'messages':[{'id':'wamid.test1','from':'79000000001','timestamp':str(int(time.time())),'type':'text','text':{'body':'Здравствуйте!'}}]
    }}]}]}
    raw=json.dumps(event).encode()
    signature='sha256='+hmac.new(b'test-webhook-secret',raw,hashlib.sha256).hexdigest()
    assert client.post('/api/webhooks/whatsapp',data=raw,headers={'X-Hub-Signature-256':'sha256=bad'}).status_code==403
    r=client.post('/api/webhooks/whatsapp',data=raw,headers={'X-Hub-Signature-256':signature})
    assert r.status_code==200,r.text
    assert r.json()['accepted']==1
    r2=client.post('/api/webhooks/whatsapp',data=raw,headers={'X-Hub-Signature-256':signature})
    assert r2.status_code==200
    assert r2.json()['accepted']==0
    conversations=client.get('/api/conversations').json()
    assert len(conversations)==1
    assert conversations[0]['contact_name']=='Мария Тест'
    assert client.get('/api/conversations/'+conversations[0]['id']).json()['messages'][0]['body']=='Здравствуйте!'


def test_automation_auto_assign_and_tenant_aware(client):
    me=start_demo(client)
    r=client.post('/api/rules',json={'name':'Распределение','event':'message_received','condition_type':'always','condition_value':'','action_type':'assign_least_busy','action_value':'','enabled':True})
    assert r.status_code==201,r.text
    with db.SessionLocal() as session:
        ch=session.query(ChannelConnection).filter_by(organization_id=me['organization']['id'],provider='avito').first()
        msg=ingest_inbound(session,channel=ch,external_chat_id='demo-new-chat',external_message_id='test-new',sender_id='fresh-22',sender_name='Свежий',text='Здравствуйте')
        session.commit()
        c=session.query(Conversation).filter_by(external_chat_id='demo-new-chat').first()
        assert c.assigned_user_id is not None
    assert client.get('/api/alerts').status_code==200


def test_quick_replies_merge_privacy_export_delete(client):
    me=start_demo(client)
    template=client.post('/api/quick-replies',json={'title':'Приветствие','body':'Здравствуйте! Чем помочь?'})
    assert template.status_code==201,template.text
    assert any(q['title']=='Приветствие' for q in client.get('/api/quick-replies').json())
    rows=client.get('/api/contacts').json()
    target,source=rows[:2]
    merge=client.post(f'/api/contacts/{target["id"]}/merge/{source["id"]}')
    assert merge.status_code==200,merge.text
    assert source['id'] not in [c['id'] for c in client.get('/api/contacts').json()]
    assert client.patch('/api/organization/privacy',json={'retention_days':120,'sla_minutes':7}).status_code==200
    assert client.get('/api/organization/privacy').json()['sla_minutes']==7
    export=client.get('/api/organization/export')
    assert export.status_code==200 and export.json()['contacts']
    assert client.post('/api/organization/delete',json={'confirmation':'wrong'}).status_code==422
    assert client.post('/api/organization/delete',json={'confirmation':me['organization']['name']}).status_code==200
    assert client.get('/api/auth/me').status_code==401


def test_avito_official_poll_is_idempotent(client,monkeypatch):
    user=register(client)
    from app import synchronizers
    class FakeAvito:
        async def get_conversations(self,credentials):
            return [{'id':'chat-avito-1','users':[{'id':42,'name':'Михаил'},{'id':123,'name':'Осман'}]}]
        async def get_messages(self,credentials,chat_id):
            return [{'id':'m11','author_id':42,'type':'text','created':time.time()-50,'content':{'text':'Цена?'}},
                    {'id':'m12','author_id':123,'direction':'out','type':'text','created':time.time()-40,'content':{'text':'Уточню'}}]
    monkeypatch.setattr(synchronizers,'adapter_for',lambda _: FakeAvito())
    monkeypatch.setattr(synchronizers,'unseal',lambda _: {'account_id':'123','access_token':'mock'})
    with db.SessionLocal() as session:
        ch=db.ChannelConnection(organization_id=user['organization']['id'],provider='avito',name='Проверка',external_account_id='123',mode='live',status='connected',encrypted_credentials='mock')
        session.add(ch);session.commit()
        import asyncio
        assert asyncio.run(sync_avito(session,ch))['new_inbound_messages']==1
        assert asyncio.run(sync_avito(session,ch))['new_inbound_messages']==0
        assert session.query(Message).count()==2
        assert session.query(Contact).count()==1
        assert session.query(Conversation).first().unread_count==0  # historical backfill is not a new notification
