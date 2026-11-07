"""Provider-independent connection readiness in simple Russian.

Proof levels are intentionally separate: token, webhook registration, inbound,
API acceptance of outbound. Provider acceptance does NOT mean delivered/read.
"""
from sqlalchemy.orm import Session
from ..db import ChannelConnection


def outbound_accepted(db:Session,ch:ChannelConnection):
    # Only responses accepted by the provider API since receipt tracking was
    # introduced count. Legacy messages are deliberately not backfilled.
    # Credential check-access must never revoke a valid receipt; token rotation
    # explicitly resets this evidence in onboarding.rotate_token.
    return bool(ch.outbound_api_accepted_at)


def readiness(db:Session,ch:ChannelConnection):
    account=bool(ch.last_verified_at)
    source_is_poll=ch.provider=='avito'
    webhook=bool(ch.last_sync_at if source_is_poll else
                 (ch.webhook_registered_at and (ch.webhook_provider_verified_at if ch.provider in ('telegram','max') else True)))
    incoming=bool(ch.last_sync_at if source_is_poll else ch.webhook_verified_at)
    outgoing=outbound_accepted(db,ch)
    remotely_checked=bool(ch.webhook_provider_verified_at) if ch.provider in ('telegram','max') else None
    stages=[
        {'key':'account','title':'Доступ к аккаунту','done':account,'hint':'Владелец подтвердил доступ через официальный API'},
        {'key':'events','title':'Настройка получения','done':webhook,'hint':'Синхронизация Авито' if source_is_poll else 'Webhook или подписка на события'},
        {'key':'inbound','title':'Получено настоящее сообщение','done':incoming,'hint':'Проверьте входящее из оригинального приложения'},
        {'key':'outbound','title':'API принял ваш ответ','done':outgoing,'hint':'Напишите ответ из Inbox и проверьте его в исходном сервисе'},
    ]
    ready=all(x['done'] for x in stages) and ch.status=='connected'
    if ready:
        next_step='API принял ответ. Проверьте его отображение и доставку в оригинальном приложении.'
    else:
        next_step=next((x['hint'] for x in stages if not x['done']), 'Проверьте статус подключения и права')
    if ch.status in ('needs_attention','expired'):
        ready=False;next_step='Площадка сообщила об ошибке. Проверьте токен, права и подписку.'
    return {'ready_for_api_use':ready,'stages':stages,'next_step':next_step,
            'inbound_verified':incoming,'outbound_api_accepted':outgoing,
            'webhook_provider_verified':remotely_checked,
            'disclaimer':'Подтверждение API не означает доставку на устройство клиента или прочтение.'}
