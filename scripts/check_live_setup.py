#!/usr/bin/env python3
"""Safe, offline configuration diagnostics. Never prints secrets or contacts.

A green result means only that local configuration is syntactically ready for
provider authorization; it does NOT establish provider approval or delivery.
"""
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env',override=False)
except ImportError:
    pass


def diagnose(env=None):
    env=env if env is not None else os.environ
    checks=[]
    def check(name,ok,action):
        checks.append({'name':name,'ok':bool(ok),'action':action})
    base=(env.get('PUBLIC_BASE_URL') or '').strip()
    try:
        parsed=urlsplit(base)
        host=(parsed.hostname or '').lower()
        https=(parsed.scheme=='https' and bool(host) and not host.startswith(('127.','192.168.','10.'))
               and host not in ('localhost','0.0.0.0','::1') and parsed.port in (None,443)
               and not any((parsed.username,parsed.password,parsed.query,parsed.fragment,parsed.path.strip('/'))))
    except ValueError:
        https=False
    check('Публичный HTTPS',https,'Задайте PUBLIC_BASE_URL=https://домен без пути и настройте TLS/443')
    key=(env.get('INTEGRATION_ENCRYPTION_KEY') or '').strip()
    try:
        from cryptography.fernet import Fernet
        Fernet(key.encode())
        encrypted=True
    except Exception:
        encrypted=False
    check('Шифрование подключений',encrypted,'Сгенерируйте Fernet-ключ и укажите INTEGRATION_ENCRYPTION_KEY')
    prod=env.get('APP_ENV')=='production'
    if prod:
        check('Безопасные cookie',env.get('COOKIE_SECURE','').lower()=='true','Включите COOKIE_SECURE=true')
        check('PostgreSQL',str(env.get('DATABASE_URL') or '').startswith(('postgresql://','postgresql+psycopg://')),'Используйте PostgreSQL в production')
    providers={
        'telegram':{'ready_to_authorize':encrypted,'requirements':'Нужен токен собственного бота от @BotFather'},
        'vk':{'ready_to_authorize':encrypted,'requirements':'Нужен токен сообщества, ID, Callback API секрет и код'},
        'max':{'ready_to_authorize':encrypted,'requirements':'Нужен токен MAX-бота, HTTPS 443 и доверенный сертификат'},
        'avito':{'ready_to_authorize':encrypted and https and bool(env.get('AVITO_CLIENT_ID') and env.get('AVITO_CLIENT_SECRET')),'requirements':'Нужен согласованный доступ к API Авито и OAuth-приложение'},
        'instagram':{'ready_to_authorize':encrypted and https and bool(env.get('INSTAGRAM_APP_ID') and env.get('INSTAGRAM_APP_SECRET')),'requirements':'Нужно Meta App Review и профессиональный Instagram'},
        'whatsapp':{'ready_to_authorize':encrypted and https and bool(env.get('META_APP_ID') and env.get('META_APP_SECRET') and env.get('META_WHATSAPP_CONFIG_ID')),'requirements':'Нужно Meta Embedded Signup, доступ WABA/номер и подписка'},
        'messenger':{'ready_to_authorize':encrypted and https and bool((env.get('FACEBOOK_APP_ID') or env.get('META_APP_ID')) and (env.get('FACEBOOK_APP_SECRET') or env.get('META_APP_SECRET'))),'requirements':'Нужны Facebook Page и разрешения pages_messaging'},
    }
    return {'checks':checks,'providers':providers,'basic_config_ready':all(c['ok'] for c in checks),
            'note':'Эта проверка не подключается к площадкам и не доказывает одобрение Meta/Авито или доставку сообщений.'}


if __name__=='__main__':
    result=diagnose()
    print('OSMANX OMNICHAT / Проверка подготовки к реальным подключениям')
    for item in result['checks']:
        print(('OK ' if item['ok'] else 'НУЖНО ') + item['name'])
        if not item['ok']: print('  '+item['action'])
    print('\nГотовность конфигурации для авторизации (не статус реального подключения):')
    for name,item in result['providers'].items():
        print(('OK ' if item['ready_to_authorize'] else 'НУЖНО ') + name + ': '+item['requirements'])
    print('\n'+result['note'])
    sys.exit(0 if result['basic_config_ready'] else 1)
