"""R30 first-contact concurrency, duplicate delivery, and tenant safety.

No provider secrets or real accounts are used. The SQL race is also exercised
on PostgreSQL by scripts/verify_r30_postgres.py in the CI service job.
"""
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from app import db
from app.db import (ChannelConnection, Contact, ContactIdentity, Conversation,
                    Message, Organization)
from app.services import ingest_inbound
from conftest import register


def _channel(client, *, name='R30 synthetic channel', tenant=None):
    tenant=tenant or register(client)['organization']['id']
    with db.SessionLocal() as s:
        channel=ChannelConnection(organization_id=tenant,provider='telegram',name=name,
                                  mode='live',status='connected')
        s.add(channel)
        s.commit()
        return tenant,channel.id


def _write(session,channel_id, *, chat='first-dialog', event='first-message',
           sender='first-sender', timestamp=None, history=False):
    channel=session.get(ChannelConnection,channel_id)
    return ingest_inbound(session,channel=channel,external_chat_id=chat,
        external_message_id=event,sender_id=sender,
        sender_name=f'Клиент {sender}',text=f'Текст {event}',
        timestamp=timestamp,history=history)


def _counts(tenant, channel_id,chat):
    with db.SessionLocal() as s:
        conversations=s.query(Conversation).filter_by(organization_id=tenant,
            channel_id=channel_id,external_chat_id=chat).all()
        return (conversations,s.query(Contact).filter_by(organization_id=tenant).count(),
                s.query(ContactIdentity).filter_by(organization_id=tenant).count(),
                s.query(Message).filter_by(organization_id=tenant).count())


def test_first_inbound_creates_exactly_one_contact_identity_and_unread(client):
    tenant,channel_id=_channel(client)
    past=time.time()-120
    with db.SessionLocal() as s:
        msg=_write(s,channel_id,timestamp=past)
        assert msg.body=='Текст first-message'
        s.commit()
    conv,contacts,identities,messages=_counts(tenant,channel_id,'first-dialog')
    assert (len(conv),contacts,identities,messages)==(1,1,1,1)
    assert conv[0].unread_count==1 and conv[0].version==1
    # The first message is 2 minutes old; do not claim it just arrived now.
    assert abs(conv[0].last_message_at-past)<.001
    assert abs(conv[0].last_inbound_at-past)<.001


def test_same_external_message_replayed_without_webhook_receipt_does_not_count_twice(client):
    tenant,channel_id=_channel(client)
    with db.SessionLocal() as s:
        first=_write(s,channel_id)
        s.commit()
        first_id=first.id
    with db.SessionLocal() as s:
        replay=_write(s,channel_id)
        s.commit()
        assert replay.id==first_id
    conv,contacts,identities,messages=_counts(tenant,channel_id,'first-dialog')
    assert (len(conv),contacts,identities,messages)==(1,1,1,1)
    assert conv[0].unread_count==1 and conv[0].version==1


def test_two_distinct_chats_from_same_sender_share_one_contact(client):
    tenant,channel_id=_channel(client)
    with db.SessionLocal() as s:
        _write(s,channel_id,chat='first-dialog',event='a')
        _write(s,channel_id,chat='another-dialog',event='b')
        s.commit()
    _,contacts,identities,messages=_counts(tenant,channel_id,'first-dialog')
    with db.SessionLocal() as s:
        assert s.query(Conversation).filter_by(channel_id=channel_id).count()==2
        assert len(set(c.contact_id for c in s.query(Conversation).filter_by(
            channel_id=channel_id).all()))==1
    assert (contacts,identities,messages)==(1,1,2)


def _parallel_inbound(channel_id,requests):
    barrier=Barrier(len(requests))
    def worker(payload):
        with db.SessionLocal() as s:
            # Both sessions have seen the channel before the first write.
            ch=s.get(ChannelConnection,channel_id)
            barrier.wait(timeout=15)
            msg=ingest_inbound(s,channel=ch,external_chat_id=payload['chat'],
                external_message_id=payload['event'],sender_id=payload['sender'],
                sender_name=payload['sender'],text='Без потерь')
            s.commit()
            return msg.id
    with ThreadPoolExecutor(max_workers=len(requests)) as pool:
        return list(pool.map(worker,requests))


def test_parallel_first_messages_one_new_chat_preserve_both(client):
    tenant,channel_id=_channel(client)
    result=_parallel_inbound(channel_id,[
        dict(chat='new-parallel',event='event-a',sender='same-client'),
        dict(chat='new-parallel',event='event-b',sender='same-client')])
    assert len(set(result))==2
    conv,contacts,identities,messages=_counts(tenant,channel_id,'new-parallel')
    assert (len(conv),contacts,identities,messages)==(1,1,1,2)
    assert conv[0].unread_count==2 and conv[0].version==2


def test_parallel_repeated_first_event_returns_one_message(client):
    tenant,channel_id=_channel(client)
    results=_parallel_inbound(channel_id,[
        dict(chat='parallel-duplicate',event='same-id',sender='client'),
        dict(chat='parallel-duplicate',event='same-id',sender='client')])
    assert results[0]==results[1]
    conv,contacts,identities,messages=_counts(tenant,channel_id,'parallel-duplicate')
    assert (len(conv),contacts,identities,messages)==(1,1,1,1)
    assert conv[0].unread_count==1 and conv[0].version==1


def test_parallel_different_senders_for_same_group_chat_do_not_leave_orphans(client):
    tenant,channel_id=_channel(client)
    results=_parallel_inbound(channel_id,[
        dict(chat='shared-group',event='sender-a-event',sender='sender-a'),
        dict(chat='shared-group',event='sender-b-event',sender='sender-b')])
    assert len(set(results))==2
    conv,contacts,identities,messages=_counts(tenant,channel_id,'shared-group')
    assert (len(conv),contacts,identities,messages)==(1,1,1,2)
    assert conv[0].unread_count==2


def test_shared_provider_ids_never_mix_different_organizations(client):
    tenant1,channel1=_channel(client)
    with db.SessionLocal() as s:
        org=Organization(name='Second synthetic organization')
        s.add(org);s.flush()
        other=ChannelConnection(organization_id=org.id,provider='telegram',
            name='Second synthetic channel',mode='live',status='connected')
        s.add(other);s.commit()
        tenant2,channel2=org.id,other.id
    with db.SessionLocal() as s:
        first=_write(s,channel1,chat='same-id',event='same-id',sender='same-id')
        second=_write(s,channel2,chat='same-id',event='same-id',sender='same-id')
        s.commit()
    assert first.id!=second.id
    assert _counts(tenant1,channel1,'same-id')[1:]==(1,1,1)
    assert _counts(tenant2,channel2,'same-id')[1:]==(1,1,1)


@pytest.mark.parametrize('value',[float('nan'),float('inf'),float('-inf'),
    'not-a-time',0,999999999999,{},[]])
def test_bad_provider_time_never_poison_inbox(client,value):
    tenant,channel_id=_channel(client)
    before=time.time()
    with db.SessionLocal() as s:
        _write(s,channel_id,timestamp=value)
        s.commit()
    conv=_counts(tenant,channel_id,'first-dialog')[0][0]
    assert before <= conv.last_inbound_at <= time.time()+1
    assert before <= conv.last_message_at <= time.time()+1


def test_history_backfill_first_chat_has_no_unread_and_correct_time(client):
    tenant,channel_id=_channel(client)
    old=time.time()-86400
    with db.SessionLocal() as s:
        _write(s,channel_id,history=True,timestamp=old)
        s.commit()
    conv=_counts(tenant,channel_id,'first-dialog')[0][0]
    assert conv.unread_count==0
    assert abs(conv.last_message_at-old)<.001
    assert abs(conv.last_inbound_at-old)<.001


def test_overlong_external_id_rejected_without_any_partial_record(client):
    tenant,channel_id=_channel(client)
    with db.SessionLocal() as s:
        with pytest.raises(ValueError,match='250'):
            _write(s,channel_id,chat='x'*251)
        s.rollback()
    assert _counts(tenant,channel_id,'first-dialog')[1:]==(0,0,0)


def _signed_bot(client,provider):
    from app.integrations.adapters import seal
    tenant,channel_id=_channel(client)
    secret='synthetic-r30-bot-webhook-secret'
    with db.SessionLocal() as s:
        channel=s.get(ChannelConnection,channel_id)
        channel.provider=provider
        channel.external_account_id='7654'
        channel.encrypted_credentials=seal({'webhook_secret':secret})
        s.commit()
    return tenant,channel_id,secret


def test_signed_telegram_first_message_and_retransmission_are_idempotent(client):
    tenant,channel,secret=_signed_bot(client,'telegram')
    event={'message':{'message_id':12345,'date':time.time(),
                      'from':{'id':123,'first_name':'Покупатель'},
                      'chat':{'id':123},'text':'Первое обращение'}}
    url=f'/api/webhooks/telegram/{channel}'
    hdr={'X-Telegram-Bot-Api-Secret-Token':secret}
    one=client.post(url,json=event,headers=hdr)
    assert one.status_code==200 and one.json()['accepted']==1,one.text
    two=client.post(url,json=event,headers=hdr)
    assert two.status_code==200 and two.json()['accepted']==0,two.text
    conv,contacts,identities,messages=_counts(tenant,channel,'123')
    assert (len(conv),contacts,identities,messages)==(1,1,1,1)
    assert conv[0].unread_count==1


@pytest.mark.parametrize('provider,broken,expected_header',[
    ('telegram',{'message':['not','an','object']},'X-Telegram-Bot-Api-Secret-Token'),
    ('telegram',{'message':{'message_id':1,'from':'bad','chat':{'id':123}}},'X-Telegram-Bot-Api-Secret-Token'),
    ('vk',{'type':'message_new','group_id':'7654','object':{'message':[]}},None),
    ('vk',{'type':'message_new','group_id':'7654','object':'bad'},None),
    ('max',{'update_type':'message_created','message':{'sender':[]}},'X-Max-Bot-Api-Secret'),
    ('max',{'update_type':'message_created','message':{'sender':{'user_id':123},
       'recipient':{'chat_type':'dialog'},'body':{'mid':'1','attachments':'bad'}}},'X-Max-Bot-Api-Secret'),
])
def test_signed_malformed_bot_payload_returns_422_without_records(client,provider,broken,expected_header):
    tenant,channel,secret=_signed_bot(client,provider)
    if provider=='vk':
        broken['secret']=secret
        headers={}
    else:
        headers={expected_header:secret}
    response=client.post(f'/api/webhooks/{provider}/{channel}',json=broken,headers=headers)
    assert response.status_code==422,response.text
    conv,contacts,identities,messages=_counts(tenant,channel,'unknown')
    assert (len(conv),contacts,identities,messages)==(0,0,0,0)


def test_max_bad_timestamp_becomes_safe_current_timestamp(client):
    tenant,channel,secret=_signed_bot(client,'max')
    event={'update_type':'message_created','timestamp':'corrupt-timestamp',
        'message':{'sender':{'user_id':123,'first_name':'Покупатель'},
                   'recipient':{'chat_type':'dialog'},
                   'body':{'mid':'max-001','text':'Тест неверного времени'}}}
    response=client.post(f'/api/webhooks/max/{channel}',json=event,
        headers={'X-Max-Bot-Api-Secret':secret})
    assert response.status_code==200 and response.json()['accepted']==1,response.text
    conv,contacts,identities,messages=_counts(tenant,channel,'user:123')
    assert (len(conv),contacts,identities,messages)==(1,1,1,1)
    assert conv[0].last_inbound_at>=time.time()-5
