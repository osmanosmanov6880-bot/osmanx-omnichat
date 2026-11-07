"""Feature and security regression tests for deterministic command center v0.4."""
from fastapi.testclient import TestClient
from app.main import app
from app import db
from conftest import start_demo,register


def test_priority_optimistic_lock_and_realtime_version(client):
    start_demo(client)
    all_rows=client.get('/api/conversations').json()
    selected=next(x for x in all_rows if x['priority']=='normal')
    first=client.patch(f'/api/conversations/{selected["id"]}/priority',json={
        'priority':'urgent','expected_version':selected['version']})
    assert first.status_code==200,first.text
    assert first.json()['priority']=='urgent'
    assert first.json()['version']==selected['version']+1
    repeat=client.patch(f'/api/conversations/{selected["id"]}/priority',json={
        'priority':'low','expected_version':selected['version']})
    assert repeat.status_code==409
    assert client.patch(f'/api/conversations/{selected["id"]}/priority',json={
        'priority':'bogus','expected_version':first.json()['version']}).status_code==422
    assert all(x['priority']=='urgent' for x in client.get('/api/conversations',params={'priority':'urgent'}).json())
    assert client.get('/api/conversations',params={'priority':'bogus'}).status_code==422
    assert client.get('/api/conversations',params={'sort':'not-valid'}).status_code==422
    by_priority=client.get('/api/conversations',params={'sort':'priority'}).json()
    weights={'urgent':4,'high':3,'normal':2,'low':1}
    assert [weights[x['priority']] for x in by_priority]==sorted([weights[x['priority']] for x in by_priority],reverse=True)
    actions=client.get(f'/api/conversations/{selected["id"]}/activity').json()
    assert any(a['title']=='Изменён приоритет' and a['detail']=='urgent' for a in actions)


def test_saved_views_validation_and_tenant_scoping(client):
    me=start_demo(client)
    payload={'name':'Срочные и новые','filters':{'priority':'urgent','status':'new','sort':'priority','archived':False},'shared':True}
    created=client.post('/api/views',json=payload)
    assert created.status_code==201,created.text
    view_id=created.json()['id']
    assert created.json()['is_owner'] is True
    assert created.json()['filters']['priority']=='urgent'
    assert client.post('/api/views',json=payload).status_code==409
    assert client.post('/api/views',json={'name':'Вредный фильтр','filters':{'sql':'DROP TABLE users'}}).status_code==422
    assert client.post('/api/views',json={'name':'Чужая очередь','filters':{'assigned':'00000000-0000-4000-8000-000000000000'}}).status_code==422
    assert client.post('/api/views',json={'name':'Неверный архив','filters':{'archived':'true'}}).status_code==422
    assert any(v['id']==view_id for v in client.get('/api/views').json())
    with TestClient(app) as other:
        assert other.post('/api/demo/start').status_code==200
        assert view_id not in [v['id'] for v in other.get('/api/views').json()]
        other.headers.update({'X-CSRF-Token':other.cookies.get('omnichat_csrf','')})
        assert other.delete('/api/views/'+view_id).status_code==404
        assert other.get('/api/command-center').json()['is_demo']
    assert client.delete('/api/views/'+view_id).status_code==200
    assert client.get('/api/views').json()==[]


def test_triage_is_explicit_deterministic_and_shows_live_state(client):
    me=start_demo(client)
    result=client.get('/api/command-center')
    assert result.status_code==200,result.text
    data=result.json()
    assert data['is_demo'] is True
    assert data['total_open']>0
    assert data['sla_minutes']>=1
    assert data['unread']>=1
    assert data['waiting']>=0
    assert data['scope']=='latest_500_open_conversations'
    assert data['priority_queue']
    assert data['priority_queue']==sorted(data['priority_queue'],key=lambda x:(-x['score'],-x['last_message_at']))
    assert all(x['score']>=0 and isinstance(x['reasons'],list) for x in data['priority_queue'])
    assert all(x['channel'] in ('avito','instagram','whatsapp','website','telegram','vk','max','messenger') for x in data['priority_queue'])
    assert len(data['workload'])>=2
    # A new inbound on a previously closed conversation raises a new unanswered alert.
    with db.SessionLocal() as session:
        from app.db import Conversation,now
        c=session.query(Conversation).filter_by(organization_id=me['organization']['id']).first()
        c.last_inbound_at=now()-1000
        c.unread_count=3
        c.priority='urgent'
        session.commit()
    fresh=client.get('/api/command-center').json()
    assert fresh['overdue']>=1
    assert any('Срок ответа превышен' in x['reasons'] for x in fresh['priority_queue'])


def test_command_center_role_scope_and_cross_workspace_access(client):
    owner=register(client)
    with db.SessionLocal() as session:
        session.get(db.Organization,owner['organization']['id']).plan='business'
        session.commit()
    invite=client.post('/api/team/invite',json={'email':'member@example.com','role':'operator'})
    assert invite.status_code==200,invite.text
    token=invite.json()['invite_token']
    assert client.post('/api/team/accept-invite',json={'token':token,'name':'Марина','password':'safe-long-password-1!'}).status_code==200
    # Owner creates a site conversation.
    from test_website import site,visitor,send
    w=site(client)
    t=visitor(client,w)
    assert send(client,w,t).status_code==201
    conv=client.get('/api/conversations').json()[0]
    before=client.get('/api/command-center').json()
    assert before['total_open']==1
    assert len(before['workload'])>=2
    client.post('/api/auth/logout')
    assert client.post('/api/auth/login',json={'email':'member@example.com','password':'safe-long-password-1!'}).status_code==200
    assert client.get('/api/command-center').json()['total_open']==0
    assert client.get('/api/command-center').json()['workload']==[]
    assert client.patch(f'/api/conversations/{conv["id"]}/priority',json={'priority':'urgent','expected_version':conv['version']}).status_code==403
    assert client.get(f'/api/conversations/{conv["id"]}/activity').status_code==403
    assert client.post('/api/views',json={'name':'Для всех','filters':{},'shared':True}).status_code==403
    mine=client.post('/api/views',json={'name':'Моё представление','filters':{},'shared':False})
    assert mine.status_code==201,mine.text


def test_search_is_literal_and_filtered_before_limit(client):
    """A scoped message search must not treat user-supplied %/_ as SQL wildcard.

    Search is applied to SQL before LIMIT; old matching conversations remain
    discoverable even when the Inbox shows only the latest item.
    """
    start_demo(client)
    rows=client.get('/api/conversations').json()
    target=rows[-1]
    posted=client.post('/api/demo/incoming',json={
        'conversation_id':target['id'],'body':'Артикул тест-100%_X уникальный'})
    assert posted.status_code==201,posted.text
    # Lower the conversation position so it is not on the first page.
    with db.SessionLocal() as session:
        item=session.get(db.Conversation,target['id'])
        item.last_message_at=1
        session.commit()
    found=client.get('/api/conversations',params={'q':'100%_X','limit':1})
    assert found.status_code==200,found.text
    assert [c['id'] for c in found.json()]==[target['id']]
    assert client.get('/api/conversations',params={'q':'100%_Y'}).json()==[]
    assert client.get('/api/conversations',params={'q':'100%%'}).json()==[]
    assert client.get('/api/conversations',params={'q':'a'*121}).status_code==422


def test_search_does_not_return_other_organizations_messages(client):
    """Even the search subquery is scoped to the caller's organization."""
    start_demo(client)
    with TestClient(app) as other:
        assert other.post('/api/demo/start').status_code==200
        other_rows=other.get('/api/conversations').json()
        token=other.cookies.get('omnichat_csrf','')
        send=other.post('/api/demo/incoming',headers={'X-CSRF-Token':token},json={
            'conversation_id':other_rows[0]['id'],'body':'UNIQUE_PRIVATE_WORKSPACE_SIGNAL_2026'})
        assert send.status_code==201,send.text
        assert [x['id'] for x in other.get('/api/conversations',params={'q':'UNIQUE_PRIVATE_WORKSPACE_SIGNAL_2026'}).json()]==[other_rows[0]['id']]
    assert client.get('/api/conversations',params={'q':'UNIQUE_PRIVATE_WORKSPACE_SIGNAL_2026'}).json()==[]
