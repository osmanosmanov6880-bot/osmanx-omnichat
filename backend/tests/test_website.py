"""Real first-party website messaging and tenant boundary regression tests."""
import hashlib
from app import db
from app.db import WebsiteVisitor, Message, OutgoingJob, ChannelConnection
from conftest import register, start_demo


def site(client, origins=None):
    payload={'name':'Support Chat','allowed_origins':origins or ['https://shop.example.com'],
             'greeting':'A real support conversation','accent':'#4578FD'}
    res=client.post('/api/website-widgets',json=payload)
    assert res.status_code==201,res.text
    return res.json()


def visitor(client,widget,name='Visitor Alice'):
    res=client.post('/api/public/widget/'+widget['key']+'/session',json={'name':name})
    assert res.status_code==201,res.text
    return res.json()['visitor_token']


def send(client,widget,token,body='Need help',nonce='unique_nonce_111'):
    return client.post('/api/public/widget/'+widget['key']+'/messages',
                       headers={'X-Widget-Session':token},json={'body':body,'client_nonce':nonce})


def test_real_website_round_trip_and_idempotency(client):
    register(client)
    widget=site(client)
    key=widget['key']
    frame=client.get('/widget/'+key)
    assert frame.status_code==200
    assert frame.headers['cache-control']=='no-store'
    assert 'https://shop.example.com' in frame.headers['content-security-policy']
    assert 'x-frame-options' not in frame.headers
    bootstrap=client.get('/api/public/widget/'+key+'/bootstrap').json()
    assert bootstrap['company'] == 'Company'.replace('Company','\u041a\u043e\u043c\u043f\u0430\u043d\u0438\u044f')
    token=visitor(client,widget)
    assert not client.get('/api/public/widget/'+key+'/messages').status_code==200
    first=send(client,widget,token).json()
    duplicate=send(client,widget,token).json()
    assert first['message_id']==duplicate['message_id']
    convs=client.get('/api/conversations').json()
    assert len(convs)==1
    conv=convs[0]
    assert conv['channel']=='website'
    assert conv['channel_mode']=='live'
    assert conv['unread_count']==1
    reply=client.post('/api/conversations/'+conv['id']+'/reply',json={
        'body':'Hello Alice!','expected_version':conv['version'],'client_nonce':'outbound_11111'})
    assert reply.status_code==201,reply.text
    assert reply.json()['message']['delivery_status']=='accepted'
    messages=client.get('/api/public/widget/'+key+'/messages',headers={'X-Widget-Session':token}).json()['messages']
    assert [m['body'] for m in messages]==['Need help','Hello Alice!']
    receipt_id=next(m['id'] for m in messages if m['direction']=='out')
    url='/api/public/widget/'+key+'/receipts'
    assert client.post(url,headers={'X-Widget-Session':token},json={'message_ids':[receipt_id]}).json()=={'confirmed':1}
    assert client.post(url,headers={'X-Widget-Session':token},json={'message_ids':[receipt_id]}).json()=={'confirmed':0}
    assert client.get('/api/conversations/'+conv['id']).json()['messages'][-1]['delivery_status']=='delivered' 
    with db.SessionLocal() as session:
        assert session.query(OutgoingJob).count()==0
        visitor_record=session.query(WebsiteVisitor).one()
        assert visitor_record.token_hash==hashlib.sha256(token.encode()).hexdigest()
        assert token not in visitor_record.token_hash
    assert client.get('/assets/embed.js').status_code==200


def test_widget_isolation_and_rotation(client):
    register(client)
    a=site(client,['https://a.example.com'])
    b=site(client,['https://b.example.com'])
    ta=visitor(client,a)
    assert send(client,a,ta).status_code==201
    assert client.get('/api/public/widget/'+b['key']+'/messages',headers={'X-Widget-Session':ta}).status_code==401
    assert client.post('/api/public/widget/'+b['key']+'/messages',headers={'X-Widget-Session':ta},json={'body':'hello','client_nonce':'nonce_good_001'}).status_code==401
    rotated=client.post('/api/website-widgets/'+a['id']+'/rotate-key').json()
    assert rotated['key']!=a['key']
    assert client.get('/widget/'+a['key']).status_code==404
    assert client.get('/api/public/widget/'+rotated['key']+'/messages',headers={'X-Widget-Session':ta}).status_code==200
    disabled=client.patch('/api/website-widgets/'+a['id'],json={
        'name':'Support Chat','allowed_origins':['https://a.example.com'],
        'greeting':'Not available','accent':'#4578FD','enabled':False})
    assert disabled.status_code==200
    assert client.get('/api/public/widget/'+rotated['key']+'/bootstrap').status_code==404


def test_widget_allowed_origins_validation_and_demo_flag(client):
    start_demo(client)
    bad=client.post('/api/website-widgets',json={'name':'Site','allowed_origins':['http://evil.example.com/anything']})
    assert bad.status_code==422
    bad2=client.post('/api/website-widgets',json={'name':'Site','allowed_origins':['https://example.com/evil']})
    assert bad2.status_code==422
    widget=site(client,['http://localhost:3000'])
    token=visitor(client,widget)
    result=send(client,widget,token)
    assert result.json()['is_demo'] is True
    conv=next(c for c in client.get('/api/conversations').json() if c['channel']=='website')
    assert client.get('/api/conversations/'+conv['id']).json()['messages'][0]['is_demo'] is True


def test_widget_session_expiry(client):
    register(client)
    widget=site(client)
    token=visitor(client,widget)
    with db.SessionLocal() as session:
        session.query(WebsiteVisitor).update({'expires_at':0})
        session.commit()
    assert send(client,widget,token).status_code==401


def test_widget_admin_cannot_cross_tenant_boundaries(client):
    register(client,email='org-one@example.com')
    first=site(client)
    assert client.post('/api/auth/logout').status_code==200
    register(client,email='org-two@example.com')
    assert client.get('/api/website-widgets').json()==[]
    assert client.post('/api/website-widgets/'+first['id']+'/rotate-key').status_code==404
    assert client.patch('/api/website-widgets/'+first['id'],json={
        'name':'Hijacked','allowed_origins':['https://attacker.example'],
        'greeting':'No access','accent':'#4578FD','enabled':False}).status_code==404
    assert client.get('/api/operations/overview').json()['channel_total']==0


def test_website_message_rate_limit_is_per_visitor(client):
    from app.main import rate_hits
    from app.db import now
    register(client)
    w=site(client)
    first=visitor(client,w,'First visitor')
    second=visitor(client,w,'Second visitor')
    with db.SessionLocal() as session:
        visitor_id=session.query(WebsiteVisitor).filter_by(token_hash=hashlib.sha256(first.encode()).hexdigest()).one().id
    rate_hits[('widget_send:'+visitor_id,'testclient')]=[now()]*90
    assert send(client,w,first,nonce='nonce_first_123').status_code==429
    assert send(client,w,second,nonce='nonce_second_123').status_code==201
    css=client.get('/assets/embed.css')
    assert css.status_code==200
    assert '.omnichat-embed' in css.text
