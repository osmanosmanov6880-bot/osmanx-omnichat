"""A company cannot see another company's setup progress or fake delivery."""
from app.db import ChannelConnection, Conversation, Contact, Message, Membership, SessionLocal, now
from conftest import register, start_demo


def test_quickstart_real_company_starts_empty(client):
    register(client)
    r=client.get('/api/quickstart')
    assert r.status_code==200,r.text
    data=r.json()
    assert data['completed']==0
    assert data['connected_accounts']==0
    assert [item['done'] for item in data['tasks']]==[False,False,False]
    assert data['note']


def test_quickstart_is_scoped_to_current_tenant(client):
    first=register(client,'first-quickstart@example.com','Первая компания')
    from app import db as store
    with store.SessionLocal() as session:
        channel=ChannelConnection(organization_id=first['organization']['id'],provider='telegram',name='Telegram компании',mode='live',status='pending_webhook',external_account_id='bot-quickstart-1')
        session.add(channel)
        session.commit()
    one=client.get('/api/quickstart').json()
    assert one['connected_accounts']==1
    assert one['completed']==1
    assert one['provider_verified_routes']==0
    # New account starts a separate organization without receiving old metrics.
    client.post('/api/auth/logout')
    register(client,'second-quickstart@example.com','Вторая компания')
    two=client.get('/api/quickstart').json()
    assert two['organization']=='Вторая компания'
    assert two['connected_accounts']==0
    assert two['completed']==0


def test_quickstart_demo_does_not_treat_demo_messages_as_live(client):
    start_demo(client)
    result=client.get('/api/quickstart')
    assert result.status_code==200
    data=result.json()
    assert data['is_demo'] is True
    assert data['connected_accounts']==0
    assert [step['done'] for step in data['tasks']]==[False,False,False]


def test_quickstart_operator_cannot_inspect_all_company_metrics(client):
    from app import db as store
    me=register(client)
    with store.SessionLocal() as session:
        member=session.query(Membership).filter_by(organization_id=me['organization']['id']).first()
        member.role='operator'
        session.commit()
    assert client.get('/api/quickstart').status_code==403


def test_quickstart_progress_tracks_actual_non_demo_messages(client):
    me=register(client,'progress@example.com','Готовность')
    from app import db as store
    with store.SessionLocal() as session:
        channel=ChannelConnection(organization_id=me['organization']['id'],provider='telegram',
            name='Бот магазина',mode='live',status='pending_webhook',external_account_id='bot-quickstart-progress')
        contact=Contact(organization_id=me['organization']['id'],name='Покупатель')
        session.add_all([channel,contact]);session.flush()
        conversation=Conversation(organization_id=me['organization']['id'],channel_id=channel.id,
            contact_id=contact.id,external_chat_id='progress-chat')
        session.add(conversation);session.flush()
        session.add(Message(organization_id=me['organization']['id'],conversation_id=conversation.id,
            direction='in',body='Здравствуйте',external_id='progress-inbound',is_demo=False))
        session.commit()
        assert client.get('/api/quickstart').json()['completed']==2
        session.add(Message(organization_id=me['organization']['id'],conversation_id=conversation.id,
            direction='out',body='Привет!',external_id='progress-outbound',is_demo=False,delivery_status='queued'))
        session.commit()
    data=client.get('/api/quickstart').json()
    assert data['completed']==2
    assert data['all_done'] is False
    # Merely queued is not evidence that an official platform accepted the reply.
    assert data['provider_verified_routes']==0
    with store.SessionLocal() as session:
        outgoing=session.query(Message).filter_by(organization_id=me['organization']['id'],direction='out').one()
        outgoing.delivery_status='accepted'
        session.commit()
    assert client.get('/api/quickstart').json()['all_done'] is True
