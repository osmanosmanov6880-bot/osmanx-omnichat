import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from cryptography.fernet import Fernet
from check_live_setup import diagnose


def test_default_check_never_claims_provider_ready():
    d=diagnose({'PUBLIC_BASE_URL':'http://127.0.0.1:8000'})
    assert d['basic_config_ready'] is False
    assert d['checks'][0]['ok'] is False
    assert not d['providers']['whatsapp']['ready_to_authorize']
    assert not d['providers']['telegram']['ready_to_authorize']


def test_https_and_encryption_do_not_imply_external_permissions():
    cfg={'PUBLIC_BASE_URL':'https://social.example.com','INTEGRATION_ENCRYPTION_KEY':Fernet.generate_key().decode()}
    d=diagnose(cfg)
    assert d['basic_config_ready'] is True
    assert d['providers']['telegram']['ready_to_authorize'] is True
    assert d['providers']['instagram']['ready_to_authorize'] is False
    assert d['providers']['messenger']['ready_to_authorize'] is False
    assert 'не доказывает' in d['note']


def test_rejects_localhost_wrong_port_and_production_sqlite():
    key=Fernet.generate_key().decode()
    for url in ('https://localhost','https://127.0.0.1','https://a.example.com:8443','https://a.example.com/hidden/path','http://a.example.com'):
        d=diagnose({'PUBLIC_BASE_URL':url,'INTEGRATION_ENCRYPTION_KEY':key})
        assert d['checks'][0]['ok'] is False,url
    d=diagnose({'PUBLIC_BASE_URL':'https://test.example.com','INTEGRATION_ENCRYPTION_KEY':key,
                'APP_ENV':'production','DATABASE_URL':'sqlite:///secret.db','COOKIE_SECURE':'false'})
    assert d['basic_config_ready'] is False
    assert len([x for x in d['checks'] if not x['ok']])==2


def test_preflight_handles_malformed_https_port_without_crashing():
    cfg={'PUBLIC_BASE_URL':'https://example.com:invalid','INTEGRATION_ENCRYPTION_KEY':Fernet.generate_key().decode()}
    result=diagnose(cfg)
    assert result['checks'][0]['ok'] is False
