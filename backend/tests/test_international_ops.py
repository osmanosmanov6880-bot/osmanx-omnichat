"""Internationalization, operational safeguards and privacy data deletion."""
from app import db
from app.db import WebsiteWidget,WebsiteVisitor
from conftest import register, start_demo
from test_website import site,visitor,send


def test_region_time_zone_currency_and_revenue_guard(client):
    register(client)
    original=client.get('/api/organization/localization')
    assert original.status_code==200
    assert original.json()['currency']=='RUB'
    invalid=client.patch('/api/organization/localization',json={'currency':'ABC','timezone':'Mars/Base'})
    assert invalid.status_code==422
    changed=client.patch('/api/organization/localization',json={'currency':'EUR','timezone':'Europe/Stockholm'})
    assert changed.status_code==200,changed.text
    assert client.get('/api/auth/me').json()['organization']['currency']=='EUR'
    assert client.get('/api/auth/me').json()['organization']['timezone']=='Europe/Stockholm'
    # A real conversation is required to create a deal amount.
    w=site(client);t=visitor(client,w)
    assert send(client,w,t).status_code==201
    c=client.get('/api/conversations').json()[0]
    contact_id=c['contact_id']
    assert client.patch('/api/contacts/'+contact_id,json={'deal_amount':100}).status_code==200
    blocked=client.patch('/api/organization/localization',json={'currency':'USD','timezone':'UTC'})
    assert blocked.status_code==409
    assert client.get('/api/organization/localization').json()['currency']=='EUR'


def test_ops_dashboard_contains_real_not_invented_status(client):
    start_demo(client)
    ops=client.get('/api/operations/overview')
    assert ops.status_code==200
    data=ops.json()
    assert data['channel_total']==7
    assert data['live_connected_count']==0
    assert data['live_external_channels_verified'] is False
    assert data['messages_total']>=8
    assert data['outbox']['uncertain']==0
    assert all(x['mode']=='demo' for x in data['channels'])


def test_deleting_workspace_removes_widget_sessions(client):
    me=register(client)
    w=site(client)
    t=visitor(client,w)
    assert send(client,w,t).status_code==201
    assert client.post('/api/organization/delete',json={'confirmation':'wrong-name'}).status_code==422
    deleted=client.post('/api/organization/delete',json={'confirmation':me['organization']['name']})
    assert deleted.status_code==200,deleted.text
    with db.SessionLocal() as session:
        assert session.query(WebsiteWidget).count()==0
        assert session.query(WebsiteVisitor).count()==0
    assert client.get('/api/public/widget/'+w['key']+'/bootstrap').status_code==404
