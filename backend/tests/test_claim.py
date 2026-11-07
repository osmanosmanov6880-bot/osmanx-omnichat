"""Safe team reply leases are versioned and cannot be stolen before expiry."""
from app import db
from app.db import Conversation, now
from conftest import start_demo


def test_claim_renew_release_and_reply_lock(client):
    start_demo(client)
    conv=client.get('/api/conversations').json()[0]
    cid=conv['id']
    first=client.post('/api/conversations/'+cid+'/claim',json={'seconds':120})
    assert first.status_code==200,first.text
    owner=client.get('/api/auth/me').json()['user']['id']
    assert first.json()['reply_lock_owner_id']==owner
    assert first.json()['version']==conv['version']+1
    renewed=client.post('/api/conversations/'+cid+'/claim',json={'seconds':240})
    assert renewed.status_code==200
    assert renewed.json()['reply_lock_expires_at']>first.json()['reply_lock_expires_at']
    with db.SessionLocal() as session:
        conversation=session.get(Conversation,cid)
        conversation.reply_lock_owner_id='other-user'
        conversation.reply_lock_expires_at=now()+300
        conversation.version+=1
        session.commit()
    latest=client.get('/api/conversations/'+cid).json()['conversation']
    assert latest['reply_lock_owner_id']=='other-user'
    assert client.post('/api/conversations/'+cid+'/claim',json={'seconds':120}).status_code==409
    reply=client.post('/api/conversations/'+cid+'/reply',json={
        'body':'This should not be sent','expected_version':latest['version'],
        'client_nonce':'someone_else_replied_12'})
    assert reply.status_code==409
    with db.SessionLocal() as session:
        conversation=session.get(Conversation,cid)
        conversation.reply_lock_expires_at=now()-1
        session.commit()
    expired=client.post('/api/conversations/'+cid+'/claim',json={'seconds':120})
    assert expired.status_code==200
    released=client.post('/api/conversations/'+cid+'/release')
    assert released.status_code==200
    assert released.json()['reply_lock_owner_id'] is None
    assert client.post('/api/conversations/'+cid+'/release').status_code==409


def test_reply_claim_endpoints_require_csrf(client):
    start_demo(client)
    cid=client.get('/api/conversations').json()[0]['id']
    res=client.post('/api/conversations/'+cid+'/claim',json={'seconds':120},headers={'X-CSRF-Token':'incorrect-token'})
    assert res.status_code==403
