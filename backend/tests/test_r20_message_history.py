"""R20: large inbox history, stable cursor, and strict tenant/assignment rules."""
import time
from sqlalchemy import func
from app import db
from app.db import Message, Conversation, Organization, User, Membership
from app.auth import make_password
from conftest import start_demo, register


def populate(client, amount=650, *, shared_timestamp=False):
    profile=start_demo(client)
    conv=client.get('/api/conversations').json()[0]
    stamp=time.time()-10000
    with db.SessionLocal() as session:
        rows=[]
        for i in range(amount):
            msg=Message(organization_id=profile['organization']['id'],
                conversation_id=conv['id'],external_id='history-r20-'+str(i),
                direction='in',body=f'История {i:04}',
                delivery_status='delivered',created_at=stamp if shared_timestamp else stamp+i)
            rows.append(msg)
        session.add_all(rows)
        session.commit()
    return profile,conv['id']


def test_latest_120_messages_and_all_older_pages_in_stable_order(client):
    _,cid=populate(client,650)
    latest=client.get('/api/conversations/'+cid)
    assert latest.status_code==200,latest.text
    data=latest.json()
    assert len(data['messages'])==120
    assert any(m['body']=='История 0649' for m in data['messages'])
    assert data['messages'][0]['body'].startswith('История')
    assert data['message_paging']['has_older'] is True
    assert data['message_paging']['next_before']==data['messages'][0]['id']
    all_messages=list(data['messages'])
    pages=1
    while data['message_paging']['has_older']:
        page=client.get('/api/conversations/'+cid+'/messages',params={
            'before':data['message_paging']['next_before']})
        assert page.status_code==200,page.text
        data=page.json()
        assert len(data['messages'])<=120
        all_messages=data['messages']+all_messages
        pages+=1
        assert pages<10
    assert pages==6
    assert all(f'История {i:04}' in {m['body'] for m in all_messages} for i in range(650))
    keys=[(m['created_at'],m['id']) for m in all_messages]
    assert keys==sorted(keys)
    assert len({m['id'] for m in all_messages})==len(all_messages)
    assert any(m['body']=='История 0649' for m in all_messages)


def test_same_timestamp_keeps_every_message_without_overlap(client):
    _,cid=populate(client,300,shared_timestamp=True)
    all_messages=[]
    page=client.get('/api/conversations/'+cid+'/messages',params={'limit':37}).json()
    while True:
        all_messages=page['messages']+all_messages
        if not page['message_paging']['has_older']:break
        page=client.get('/api/conversations/'+cid+'/messages',params={
            'before':page['message_paging']['next_before'],'limit':37}).json()
    assert all(f'История {i:04}' in {m['body'] for m in all_messages} for i in range(300))
    assert len({x['id'] for x in all_messages})==len(all_messages)
    assert [(x['created_at'],x['id']) for x in all_messages]==sorted((x['created_at'],x['id']) for x in all_messages)


def test_new_messages_do_not_shift_older_cursor(client):
    profile,cid=populate(client,150)
    first=client.get('/api/conversations/'+cid+'/messages',params={'limit':25}).json()
    assert first['message_paging']['has_older']
    before=first['message_paging']['next_before']
    with db.SessionLocal() as session:
        session.add(Message(organization_id=profile['organization']['id'],conversation_id=cid,
            external_id='added-r20-new',direction='in',body='Новый ответ',
            delivery_status='delivered',created_at=time.time()))
        session.commit()
    second=client.get('/api/conversations/'+cid+'/messages',params={'before':before,'limit':25}).json()
    assert not any(x['body']=='Новый ответ' for x in second['messages'])
    assert not (set(x['id'] for x in second['messages']) & set(x['id'] for x in first['messages']))
    fresh=client.get('/api/conversations/'+cid).json()
    assert fresh['messages'][-1]['body']=='Новый ответ'


def test_bad_and_foreign_cursor_do_not_leak_data(client):
    profile,cid=populate(client,1)
    other_cid=next(x['id'] for x in client.get('/api/conversations').json() if x['id']!=cid)
    other_msg=client.get('/api/conversations/'+other_cid).json()['messages'][0]['id']
    assert client.get('/api/conversations/'+cid+'/messages',params={'before':other_msg}).status_code==404
    assert client.get('/api/conversations/'+cid+'/messages',params={'before':'nonexistent'}).status_code==404
    assert client.get('/api/conversations/nonexistent/messages').status_code==404
    assert client.get('/api/conversations/'+cid+'/messages',params={'limit':0}).status_code==422
    assert client.get('/api/conversations/'+cid+'/messages',params={'limit':201}).status_code==422
    with db.SessionLocal() as session:
        foreign=Organization(name='Соседняя компания',plan='starter')
        session.add(foreign);session.flush()
        conv=session.get(Conversation,cid)
        foreign_msg=Message(organization_id=foreign.id,conversation_id=cid,
            external_id='foreign-seeded-id',direction='in',body='Чужая финансовая тайна')
        session.add(foreign_msg);session.commit();fid=foreign_msg.id
    # A malicious mixed-tenant data row is excluded despite matching conversation ID.
    assert client.get('/api/conversations/'+cid+'/messages',params={'before':fid}).status_code==404
    assert 'Чужая финансовая тайна' not in client.get('/api/conversations/'+cid).text


def test_operator_may_only_paginate_assigned_conversations(client):
    profile=register(client,email='owner-r20@example.org')
    org=profile['organization']['id']
    from app.services import ingest_inbound
    from app.db import ChannelConnection
    with db.SessionLocal() as session:
        agent=User(email='operator-r20@example.org',name='Оператор тест',
                   password_hash=make_password('operator-testing-long-2026'))
        session.add(agent);session.flush()
        session.add(Membership(organization_id=org,user_id=agent.id,role='operator',active=True))
        channel=ChannelConnection(organization_id=org,provider='telegram',name='Бот',
                                   mode='demo',status='connected')
        session.add(channel);session.flush()
        for i in range(2):
            ingest_inbound(session,channel=channel,external_chat_id=str(5500+i),
                external_message_id='in-operator-'+str(i),sender_id='sender-'+str(i),
                sender_name='Посетитель',text='Тест')
        session.flush()
        conversations=session.query(Conversation).filter_by(organization_id=org).order_by(Conversation.id).all()
        conversations[0].assigned_user_id=agent.id
        session.commit()
        assigned,unassigned=conversations[0].id,conversations[1].id
    client.post('/api/auth/logout')
    logged=client.post('/api/auth/login',json={'email':'operator-r20@example.org','password':'operator-testing-long-2026'})
    assert logged.status_code==200,logged.text
    assert client.get('/api/conversations/'+assigned+'/messages').status_code==200
    assert client.get('/api/conversations/'+unassigned+'/messages').status_code==403
    assert client.get('/api/conversations/'+unassigned).status_code==403
