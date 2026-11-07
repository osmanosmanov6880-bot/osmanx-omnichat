import os
import pytest
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet
from app import db
from app.main import app, rate_hits

@pytest.fixture
def client(tmp_path,monkeypatch):
    rate_hits.clear()  # isolated request-throttling state between independent tests
    monkeypatch.setenv('DATABASE_URL',f'sqlite:///{tmp_path}/omnichat-test.db')
    monkeypatch.setenv('ENABLE_OUTBOX_WORKER','false')
    monkeypatch.setenv('ENABLE_AVITO_POLLING','false')
    monkeypatch.setenv('COOKIE_SECURE','false')
    monkeypatch.setenv('META_APP_SECRET','test-webhook-secret')
    monkeypatch.setenv('INTEGRATION_ENCRYPTION_KEY',Fernet.generate_key().decode())
    with TestClient(app) as c:
        original=c.request
        def with_csrf(method,url,**kwargs):
            if method.upper() not in ('GET','HEAD','OPTIONS'):
                headers=dict(kwargs.get('headers') or {})
                if 'X-CSRF-Token' not in headers:
                    headers['X-CSRF-Token']=c.cookies.get('omnichat_csrf','')
                kwargs['headers']=headers
            return original(method,url,**kwargs)
        c.request=with_csrf
        yield c
    db._engine.dispose()
    db._engine = None
    db.SessionLocal = None

def start_demo(client):
    resp=client.post('/api/demo/start')
    assert resp.status_code==200,resp.text
    assert resp.json()['mode']=='demo'
    return client.get('/api/auth/me').json()

def register(client,email='owner@example.com',name='Компания'):
    resp=client.post('/api/auth/register',json={'company':name,'name':'Владелец','email':email,'password':'CorrectLongPassword!2026'})
    assert resp.status_code==201,resp.text
    return client.get('/api/auth/me').json()
