"""R21: cross-worker optimistic updates for team operations on a conversation."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy import update
from app import db
from app.auth import make_password
from app.db import Conversation, Organization, User, Membership, now
from conftest import start_demo, register


def test_same_version_conflicts_across_status_pin_and_assignment(client):
    start_demo(client)
    c = client.get('/api/conversations').json()[0]
    url='/api/conversations/'+c['id']
    response=client.patch(url+'/status',json={'status':'in_progress','expected_version':c['version']})
    assert response.status_code==200,response.text
    current=response.json()
    assert current['status']=='in_progress' and current['version']==c['version']+1
    stale=client.patch(url+'/pin',json={'expected_version':c['version']})
    assert stale.status_code==409,stale.text
    assert client.get(url).json()['conversation']['pinned'] is c['pinned']
    good=client.patch(url+'/pin',json={'expected_version':current['version']})
    assert good.status_code==200 and good.json()['pinned'] is (not c['pinned'])
    assert good.json()['version']==current['version']+1
    # No surprise changes after a rejected stale operation.
    stale=client.patch(url+'/status',json={'status':'closed','expected_version':current['version']})
    assert stale.status_code==409
    assert client.get(url).json()['conversation']['status']=='in_progress'
    assert client.get(url).json()['conversation']['archived'] is False


def test_pin_legacy_client_is_sql_atomic_not_in_memory_toggle(client):
    start_demo(client)
    c=client.get('/api/conversations').json()[0]
    url='/api/conversations/'+c['id']+'/pin'
    first=client.patch(url)
    second=client.patch(url)
    assert first.status_code==second.status_code==200
    assert first.json()['pinned'] is (not c['pinned']) and second.json()['pinned'] is c['pinned']
    assert second.json()['version']==c['version']+2


def test_stale_assignment_never_overrides_other_lead(client):
    me=register(client,email='r21-owner@example.org')
    org_id=me['organization']['id']
    with db.SessionLocal() as session:
        from app.db import Contact, ChannelConnection
        ch=ChannelConnection(organization_id=org_id,provider='telegram',name='Test',mode='demo',status='connected')
        contact=Contact(organization_id=org_id,name='Покупатель')
        session.add_all([ch,contact]);session.flush()
        c=Conversation(organization_id=org_id,channel_id=ch.id,contact_id=contact.id,external_chat_id='r21')
        session.add(c)
        members=[]
        for name in ('Первый сотрудник','Второй сотрудник'):
            user=User(email='r21-'+str(len(members))+'@example.org',name=name,
                password_hash=make_password('EmployeeGoodPassword2026'))
            session.add(user);session.flush()
            session.add(Membership(user_id=user.id,organization_id=org_id,role='operator',active=True))
            members.append(user.id)
        session.commit()
        conversation_id=c.id
    url='/api/conversations/'+conversation_id+'/assign'
    v=client.get('/api/conversations/'+conversation_id).json()['conversation']['version']
    first=client.patch(url,json={'user_id':members[0],'expected_version':v})
    assert first.status_code==200,first.text
    second=client.patch(url,json={'user_id':members[1],'expected_version':v})
    assert second.status_code==409
    latest=client.get('/api/conversations/'+conversation_id).json()['conversation']
    assert latest['assigned_user_id']==members[0]
    assert latest['version']==v+1
    wrong=client.patch(url,json={'user_id':'other-organization-user','expected_version':latest['version']})
    assert wrong.status_code==422
    assert client.get('/api/conversations/'+conversation_id).json()['conversation']['assigned_user_id']==members[0]


def test_lease_prevents_takeover_by_reassigning_to_another_operator(client):
    me=register(client,email='r21-lease-owner@example.org')
    org=me['organization']['id']
    from app.db import ChannelConnection,Contact
    with db.SessionLocal() as session:
        channel=ChannelConnection(organization_id=org,provider='telegram',name='Bot',mode='demo',status='connected')
        contact=Contact(organization_id=org,name='Клиент')
        session.add_all([channel,contact]);session.flush()
        conv=Conversation(organization_id=org,channel_id=channel.id,contact_id=contact.id,
            external_chat_id='active-lease')
        session.add(conv)
        operators=[]
        for idx in range(2):
            user=User(name='Оператор '+str(idx),email=f'r21-lease-{idx}@example.org',
                      password_hash=make_password('LongWorkerPassword2026'))
            session.add(user);session.flush()
            session.add(Membership(organization_id=org,user_id=user.id,role='operator',active=True))
            operators.append(user.id)
        conv.assigned_user_id=operators[0]
        conv.reply_lock_owner_id=operators[0]
        conv.reply_lock_expires_at=now()+240
        session.commit();conv_id=conv.id
    url='/api/conversations/'+conv_id+'/assign'
    version=client.get('/api/conversations/'+conv_id).json()['conversation']['version']
    blocked=client.patch(url,json={'user_id':operators[1],'expected_version':version})
    assert blocked.status_code==409
    blocked_unassign=client.patch(url,json={'user_id':None,'expected_version':version})
    assert blocked_unassign.status_code==409
    with db.SessionLocal() as session:
        assert session.get(Conversation,conv_id).assigned_user_id==operators[0]
        session.get(Conversation,conv_id).reply_lock_expires_at=now()-1
        session.commit()
    transferred=client.patch(url,json={'user_id':operators[1],'expected_version':version})
    assert transferred.status_code==200,transferred.text
    assert transferred.json()['assigned_user_id']==operators[1]


def test_atomic_cas_concurrent_db_writers_only_one_wins(client):
    start_demo(client)
    conv=client.get('/api/conversations').json()[0]
    barrier=Barrier(2)
    org_id=client.get('/api/auth/me').json()['organization']['id']

    def update_status_concurrently(desired):
        with db.SessionLocal() as session:
            barrier.wait(timeout=5)
            result=session.execute(update(Conversation).where(
                Conversation.id==conv['id'],
                Conversation.organization_id==org_id,
                Conversation.version==conv['version']
            ).values(status=desired,version=Conversation.version+1))
            session.commit()
            return result.rowcount

    with ThreadPoolExecutor(max_workers=2) as executor:
        results=list(executor.map(update_status_concurrently,['waiting','closed']))
    assert sorted(results)==[0,1]
    data=client.get('/api/conversations/'+conv['id']).json()['conversation']
    assert data['version']==conv['version']+1
    assert data['status'] in ('waiting','closed')


def test_status_and_pin_validate_payloads(client):
    start_demo(client)
    c=client.get('/api/conversations').json()[0]
    url='/api/conversations/'+c['id']
    assert client.patch(url+'/status',json={'status':'not-a-real-state'}).status_code==422
    assert client.patch(url+'/pin',json={'expected_version':-1}).status_code==422
    assert client.patch(url+'/assign',json={'user_id':None,'expected_version':-1}).status_code==422
    assert client.get(url).json()['conversation']['version']==c['version']
