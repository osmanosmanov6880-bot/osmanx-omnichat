"""Authoritative provider-side webhook checks for permitted bot APIs.

No outgoing messages are sent during a check. A configured webhook is not
considered proven until the official provider reports the exact expected URL.
"""
from urllib.parse import quote
from .adapters import call
from .base import AdapterError


async def remote_subscription(provider, credentials, expected_url):
    if provider == 'telegram':
        token=credentials.get('access_token') or ''
        if ':' not in token:
            raise AdapterError('Не задан действительный токен Telegram-бота')
        result=await call('GET',f'https://api.telegram.org/bot{quote(token,safe=":")}/getWebhookInfo')
        if result.get('ok') is not True or not isinstance(result.get('result'),dict):
            raise AdapterError('Telegram не подтвердил состояние webhook')
        remote=result['result']
        url=str(remote.get('url') or '')
        if remote.get('last_error_message'):
            error='Telegram сообщил об ошибке доставки webhook. Проверьте HTTPS, доступность сервера и сертификат.'
        else:
            error=None
        return {'matches':url == expected_url,'registered':bool(url),'pending_updates':int(remote.get('pending_update_count') or 0),
                'error':error,'last_error_at':remote.get('last_error_date')}
    if provider == 'max':
        token=credentials.get('access_token') or ''
        if not token:raise AdapterError('Не задан токен бота MAX')
        result=await call('GET','https://platform-api2.max.ru/subscriptions',headers={'Authorization':token})
        subs=result.get('subscriptions')
        if not isinstance(subs,list):
            raise AdapterError('MAX не вернул список подписок')
        urls=[str(x.get('url') or '') for x in subs if isinstance(x,dict)]
        return {'matches':expected_url in urls,'registered':bool(urls),'pending_updates':None,'error':None,'last_error_at':None}
    raise AdapterError('Для этой площадки нет проверки подписки через доступный API. Проверьте официальные события.')


async def revoke_bot_subscription(provider,credentials,expected_url=None):
    """Remove a tenant bot's provider webhook *before* deleting its local token.

    Do not discard credentials on failure; otherwise the owner loses their only
    means of cleaning up the remote subscription. Telegram/MAX only.
    """
    token=credentials.get('access_token') or ''
    if provider=='telegram':
        result=await call('POST',f'https://api.telegram.org/bot{quote(token,safe=":")}/deleteWebhook',
                          json_data={'drop_pending_updates':False})
        if result.get('ok') is not True or result.get('result') is not True:
            raise AdapterError('Telegram не подтвердил отключение webhook')
        state=await call('GET',f'https://api.telegram.org/bot{quote(token,safe=":")}/getWebhookInfo')
        if not state.get('ok') or (state.get('result') or {}).get('url'):
            raise AdapterError('Telegram по-прежнему сообщает активный webhook')
        return True
    if provider=='max':
        if not expected_url or not expected_url.startswith('https://'):
            raise AdapterError('Для отключения MAX требуется публичный HTTPS URL OSMANX')
        result=await call('DELETE','https://platform-api2.max.ru/subscriptions',
                          headers={'Authorization':token},params={'url':expected_url})
        if result.get('success') is not True:
            raise AdapterError('MAX не подтвердил удаление подписки')
        state=await remote_subscription(provider,credentials,expected_url)
        if state['matches']:
            raise AdapterError('MAX по-прежнему сообщает подписку на этот адрес')
        return True
    raise AdapterError('Автоматическое удаление подписки недоступно для этого канала')
