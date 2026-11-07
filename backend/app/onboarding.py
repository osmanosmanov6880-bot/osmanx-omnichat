"""Tenant-owned channel onboarding, verification, and credential lifecycle.

Every operation is scoped to an authenticated owner/admin. No external credentials are
returned by read endpoints. No provider connection is reported live until a signed
inbound webhook is seen (or an official Avito read-sync succeeds).
"""
import hmac
import os
import re
import secrets
from typing import Literal
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, or_
from sqlalchemy.orm import Session

from .auth import auth, digest, require_role, MAX_CHANNELS, audit
from .db import get_db, Organization, Membership, ChannelConnection, OAuthState, PendingChannelSelection, now
from .integrations.adapters import adapter_for, call, seal, unseal, GRAPH_VERSION
from .integrations.base import AdapterError
from .integrations.readiness import readiness
from .integrations.subscription_check import remote_subscription

router = APIRouter(prefix='/api',tags=['Подключения компаний'])

PROVIDER_GUIDES = {
    'avito': {
        'account':'Профессиональный аккаунт Авито с разрешением Messenger API',
        'onboarding':'oauth',
        'steps':['Получите в Авито доступ к Messenger API для своего тарифа','Разрешите доступ приложению OSMANX через официальный OAuth','Дождитесь первого успешного чтения переписок']},
    'instagram': {
        'account':'Профессиональный аккаунт Instagram Business/Creator',
        'onboarding':'oauth',
        'steps':['Переключите аккаунт в профессиональный и разрешите доступ к сообщениям','Войдите через Instagram Login и предоставьте право на сообщения','Подпишитесь на события, затем проверьте входящий Direct']},
    'whatsapp': {
        'account':'WhatsApp Business Platform / Cloud API',
        'onboarding':'embedded_or_manual',
        'steps':['Пройдите Meta Embedded Signup (при наличии одобренного Meta-приложения)','Создайте или выберите WABA, подтвердите бизнес-номер и права','Зарегистрируйте номер и проверьте входящий webhook']},
    'telegram': {
        'account':'Telegram-бот, принадлежащий компании',
        'onboarding':'token',
        'steps':['Создайте своего бота через @BotFather','Подключите полученный токен в OSMANX','Активируйте HTTPS webhook и отправьте сообщение боту']},
    'vk': {
        'account':'Сообщество ВКонтакте с разрешёнными сообщениями',
        'onboarding':'token',
        'steps':['Включите сообщения сообщества и выдайте ключ доступа','Укажите ID сообщества и код подтверждения Callback API','Зарегистрируйте webhook, секрет и проверьте входящее']},
    'messenger': {
        'account':'Facebook Page с доступом к сообщениям Messenger',
        'onboarding':'oauth_pages',
        'steps':['Авторизуйтесь в Facebook через официальное приложение Meta','Выберите принадлежащую компании Facebook-страницу','Подпишите страницу на события и проверьте входящий Messenger']},
    'max': {
        'account':'Официально созданный бот MAX',
        'onboarding':'token',
        'steps':['Получите токен бота в MAX для бизнеса','Подключите токен в OSMANX','Активируйте защищённую подписку и проверьте входящее']},
}


def https_base():
    base=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
    parsed=urlsplit(base)
    if parsed.scheme!='https' or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise HTTPException(503,'Для реальных webhook и OAuth укажите HTTPS PUBLIC_BASE_URL без паролей и параметров')
    return base


def get_channel(db, principal, channel_id, *, active=True):
    ch=db.query(ChannelConnection).filter_by(id=channel_id,organization_id=principal.org.id,mode='live').first()
    if not ch or (active and ch.status=='disconnected'):
        raise HTTPException(404,'Канал этой компании не найден')
    return ch


def check_capacity(db,principal):
    if principal.org.is_demo: raise HTTPException(403,'Реальные аккаунты нельзя подключать в демонстрационном пространстве')
    if db.query(ChannelConnection).filter(ChannelConnection.organization_id==principal.org.id,
        ChannelConnection.mode=='live',ChannelConnection.status!='disconnected').count()>=MAX_CHANNELS[principal.org.plan]:
        raise HTTPException(402,'Достигнут лимит подключённых каналов тарифа')


def guard_unique(db,provider,account_id):
    existing=db.query(ChannelConnection).filter(ChannelConnection.provider==provider,
        ChannelConnection.external_account_id==str(account_id),ChannelConnection.mode=='live',
        ChannelConnection.status!='disconnected').first()
    if existing:
        raise HTTPException(409,'Этот внешний аккаунт уже привязан к рабочей области. Сначала отключите прежнее подключение.')


def add_channel(db,p,provider,verified,credentials,status='pending_webhook'):
    guard_unique(db,provider,verified['id'])
    ch=ChannelConnection(organization_id=p.org.id,provider=provider,external_account_id=str(verified['id']),
        name=str(verified['name'])[:100],mode='live',status=status,
        encrypted_credentials=seal(credentials),last_verified_at=now(),
        token_expires_at=credentials.get('expires_at'))
    db.add(ch)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409,'Этот внешний аккаунт уже зарегистрирован в другой компании') from exc
    audit(db,p,'integration.account_verified',ch.id,provider)
    db.commit()
    return ch


@router.get('/integrations/guide')
def integration_guide(p=Depends(auth)):
    """Public-safe setup checklist for each tenant, with no tokens or app secrets."""
    base=os.getenv('PUBLIC_BASE_URL','')
    https_ok=base.startswith('https://')
    encrypted=bool(os.getenv('INTEGRATION_ENCRYPTION_KEY'))
    meta_app=bool(os.getenv('META_APP_ID') and os.getenv('META_APP_SECRET') and os.getenv('META_WHATSAPP_CONFIG_ID'))
    return {'organization':p.org.name,'demo':p.org.is_demo,'https_ready':https_ok,
        'encryption_ready':encrypted,'meta_embedded_signup_ready':https_ok and encrypted and meta_app,
        'meta_webhook_ready':bool(os.getenv('META_WEBHOOK_VERIFY_TOKEN')),
        'providers':PROVIDER_GUIDES,
        'warning':'Настроенный OAuth, токен или webhook не доказывают успешную передачу сообщений. Проверяйте тестовый входящий и исходящий на площадке.'}


@router.post('/integrations/{channel_id}/verify-provider-webhook')
async def verify_provider_webhook(channel_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    """Confirm exact callback URL through official Telegram/MAX API, no mock success.

    Owner/admin only; no endpoint lets one company inspect another company's bot.
    """
    require_role(p,'owner','admin')
    ch=get_channel(db,p,channel_id)
    if ch.provider not in ('telegram','max'):
        raise HTTPException(422,'Проверка у провайдера доступна для Telegram и MAX. Для других каналов проверяйте настоящее событие.')
    base=https_base()
    expected=f'{base}/api/webhooks/{ch.provider}/{ch.id}'
    credentials=unseal(ch.encrypted_credentials)
    try:
        report=await remote_subscription(ch.provider,credentials,expected)
    except AdapterError as exc:
        raise HTTPException(502,'Не удалось проверить подписку у сервиса: '+str(exc)) from exc
    if report['matches']:
        ch.webhook_provider_verified_at=now()
        ch.webhook_registered_at=ch.webhook_registered_at or now()
        if ch.status=='needs_attention' and ch.webhook_verified_at:
            ch.status='connected'
        ch.last_error=None
    else:
        ch.webhook_provider_verified_at=None
        ch.webhook_registered_at=None
        ch.webhook_verified_at=None
        ch.last_error='Webhook у сервиса не совпадает с адресом OSMANX. Нажмите «Настроить события».'
        if ch.status=='connected':ch.status='needs_attention'
    audit(db,p,'integration.remote_webhook_checked',ch.id,ch.provider+':'+('match' if report['matches'] else 'mismatch'))
    db.commit()
    return {'matches':report['matches'],'provider':ch.provider,'webhook_registered':bool(ch.webhook_registered_at),
            'pending_updates':report.get('pending_updates'),'provider_error':report.get('error'),
            'message':('Подписка подтверждена официальным API. Осталось проверить входящее и исходящее сообщение.'
                       if report['matches'] else 'Сервис не нашёл нужную подписку. Повторно настройте события.')}


@router.post('/integrations/{channel_id}/probe')
async def probe_connection(channel_id: str, p=Depends(auth), db: Session=Depends(get_db)):
    """One safe click: check provider identity and (when supported) webhook URL.

    Only GET/identity calls are made; no messages are sent, fake events created,
    or delivery claims manufactured. A persisted cooldown protects provider APIs
    across workers and tenants, and tenant ownership is always enforced.
    """
    require_role(p, 'owner', 'admin')
    channel = get_channel(db, p, channel_id)
    if not channel.encrypted_credentials:
        raise HTTPException(409, 'Channel has no active credentials')
    cutoff = now() - 30
    claimed = db.execute(
        update(ChannelConnection).where(
            ChannelConnection.id == channel.id,
            ChannelConnection.organization_id == p.org.id,
            or_(ChannelConnection.last_probe_at.is_(None),
                ChannelConnection.last_probe_at <= cutoff)
        ).values(last_probe_at=now())
    )
    db.commit()
    if claimed.rowcount != 1:
        raise HTTPException(429, 'Please wait 30 seconds before checking again')
    channel = get_channel(db, p, channel_id)
    credentials = unseal(channel.encrypted_credentials)
    try:
        identity = await adapter_for(channel.provider).validate_credentials(credentials)
        if str(identity['id']) != str(channel.external_account_id):
            raise AdapterError('Provider returned a different account identity')
    except AdapterError as exc:
        if not exc.retriable and not exc.uncertain:
            channel.status = 'needs_attention'
            channel.last_error = 'Account access was rejected. Check permissions or reconnect.'
        audit(db, p, 'integration.probe.account_failed', channel.id, channel.provider)
        db.commit()
        raise HTTPException(502 if exc.retriable else 422,
            'Provider identity check failed. Check account access and permissions.') from exc

    channel.name = str(identity['name'])[:100]
    channel.last_verified_at = now()
    remote = None
    base = os.getenv('PUBLIC_BASE_URL', '').rstrip('/')
    if channel.provider in ('telegram', 'max') and base.startswith('https://'):
        expected = f'{base}/api/webhooks/{channel.provider}/{channel.id}'
        try:
            remote = await remote_subscription(channel.provider, credentials, expected)
        except AdapterError as exc:
            # A provider outage does not mean an existing valid webhook vanished.
            channel.last_error = 'Webhook status temporarily unavailable at provider.'
            audit(db, p, 'integration.probe.events_unavailable', channel.id, channel.provider)
            db.commit()
            raise HTTPException(502,
                'Account verified, but provider webhook check could not complete. Retry later.') from exc
        if remote['matches']:
            channel.webhook_provider_verified_at = now()
            channel.webhook_registered_at = channel.webhook_registered_at or now()
            if channel.status == 'needs_attention' and channel.webhook_verified_at:
                channel.status = 'connected'
            channel.last_error = None
        else:
            channel.webhook_provider_verified_at = None
            channel.webhook_registered_at = None
            if channel.status == 'connected':
                channel.status = 'needs_attention'
            channel.last_error = 'Provider webhook URL does not match this OSMANX connection.'
    else:
        if channel.status == 'needs_attention' and channel.webhook_verified_at:
            channel.status = 'connected'
        # For Meta, VK and Avito, GET account checks do not establish delivery.
        channel.last_error = None if channel.status != 'needs_attention' else channel.last_error
    audit(db, p, 'integration.probe.completed', channel.id,
          channel.provider + (':match' if remote and remote['matches'] else ':not_proven'))
    db.commit()
    evidence = readiness(db, channel)
    return {
        'channel_id': channel.id,
        'identity_verified': True,
        'provider_webhook_matches': remote['matches'] if remote else None,
        'provider_pending_updates': remote.get('pending_updates') if remote else None,
        'incoming_verified': evidence['inbound_verified'],
        'outbound_api_accepted': evidence['outbound_api_accepted'],
        'ready_for_api_use': evidence['ready_for_api_use'],
        'status': channel.status,
        'last_probe_at': channel.last_probe_at,
        'next_step': evidence['next_step'],
        'disclaimer': evidence['disclaimer'],
        'message': 'Official account check completed; message delivery is a separate check.'
    }


@router.get('/integrations/{channel_id}/diagnostics')
def channel_diagnostics(channel_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    ch=get_channel(db,p,channel_id)
    base=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
    url=f'{base}/api/webhooks/{ch.provider}/{ch.id}' if base.startswith('https://') and ch.provider in ('telegram','vk','max') else None
    account_ok=bool(ch.last_verified_at or ch.status=='connected')
    evidence=readiness(db,ch)
    return {'id':ch.id,**evidence,'provider':ch.provider,'name':ch.name,'status':ch.status,'account_verified':account_ok,
        'webhook_registered':bool(ch.last_sync_at if ch.provider=='avito' else ch.webhook_registered_at),'webhook_event_seen':bool(ch.last_sync_at if ch.provider=='avito' else ch.webhook_verified_at),
        'provider_check_available':ch.provider in ('telegram','max'),
        'webhook_url':url,'global_meta_webhook_url':(f'{base}/api/webhooks/{ch.provider}' if base.startswith('https://') and ch.provider in ('whatsapp','instagram','messenger') else None),'token_expires_at':ch.token_expires_at,
        'last_verified_at':ch.last_verified_at,'last_sync_at':ch.last_sync_at,
        'last_error':ch.last_error,'last_probe_at':ch.last_probe_at,
        'next_step':evidence['next_step']}


class RotatePayload(BaseModel):
    access_token:str=Field(min_length=10,max_length=8000)


@router.post('/integrations/{channel_id}/rotate-token')
async def rotate_token(channel_id:str,payload:RotatePayload,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    ch=get_channel(db,p,channel_id)
    if ch.provider not in ('telegram','vk','max','whatsapp'):
        raise HTTPException(422,'Для этого сервиса обновите подключение через OAuth')
    credentials=unseal(ch.encrypted_credentials)
    candidate={**credentials,'access_token':payload.access_token}
    try:verified=await adapter_for(ch.provider).validate_credentials(candidate)
    except AdapterError as exc:raise HTTPException(422,str(exc)) from exc
    if str(verified['id'])!=ch.external_account_id:
        raise HTTPException(409,'Новый токен принадлежит другому аккаунту. Подключите его отдельно.')
    ch.encrypted_credentials=seal(candidate)
    ch.last_verified_at=now();ch.last_error=None
    ch.webhook_provider_verified_at=None
    ch.outbound_api_accepted_at=None  # A new token requires a new accepted API response.
    # Bot token rotation can invalidate webhook registration: require fresh signed proof.
    if ch.provider in ('telegram','max'):
        ch.status='pending_webhook';ch.webhook_verified_at=None;ch.webhook_registered_at=None
    audit(db,p,'integration.token_rotated',ch.id,ch.provider);db.commit()
    return {'id':ch.id,'status':ch.status,'message':'Токен проверен, сохранён зашифрованным. Секрет не возвращается.'}


@router.post('/integrations/{channel_id}/check-access')
async def check_access(channel_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    ch=get_channel(db,p,channel_id)
    if not ch.encrypted_credentials:raise HTTPException(409,'Канал без учётных данных')
    credentials=unseal(ch.encrypted_credentials)
    try:
        if credentials.get('expires_at') and credentials['expires_at']<now()+3600 and ch.provider in ('instagram','avito'):
            credentials=await adapter_for(ch.provider).refresh_credentials(credentials)
            if credentials.get('expires_in'):
                credentials['expires_at']=now()+int(credentials['expires_in'])
            ch.encrypted_credentials=seal(credentials)
        info=await adapter_for(ch.provider).validate_credentials(credentials)
        if str(info['id'])!=ch.external_account_id:
            raise AdapterError('Провайдер вернул другой внешний аккаунт')
        ch.name=str(info['name'])[:100]
        ch.last_verified_at=now();ch.token_expires_at=credentials.get('expires_at');ch.last_error=None
        if ch.status in ('needs_attention','expired'):
            ch.status='connected' if ch.webhook_verified_at else ('pending_sync' if ch.provider=='avito' else 'pending_webhook')
        audit(db,p,'integration.access_checked',ch.id,ch.provider)
        db.commit()
        return {'id':ch.id,'name':ch.name,'status':ch.status,'verified_at':ch.last_verified_at,
            'message':'Права на аккаунт подтверждены официальным API; доставка входящих проверяется отдельно'}
    except AdapterError as exc:
        ch.status='needs_attention';ch.last_error=str(exc)[:230]
        db.commit()
        raise HTTPException(422,'Нет доступа к аккаунту: '+str(exc)) from exc


class WhatsAppComplete(BaseModel):
    state:str=Field(min_length=20,max_length=150)
    code:str=Field(min_length=5,max_length=2000)
    waba_id:str=Field(pattern=r'^\d{4,30}$')
    phone_number_id:str=Field(pattern=r'^\d{4,30}$')


@router.post('/integrations/whatsapp/embedded/start')
def whatsapp_embedded_start(p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    check_capacity(db,p)
    base=https_base()
    app_id=os.getenv('META_APP_ID','')
    config_id=os.getenv('META_WHATSAPP_CONFIG_ID','')
    if not all([app_id,os.getenv('META_APP_SECRET'),config_id,os.getenv('INTEGRATION_ENCRYPTION_KEY')]):
        raise HTTPException(503,'Meta Embedded Signup не настроен. Требуются META_APP_ID, META_APP_SECRET, META_WHATSAPP_CONFIG_ID и шифрование.')
    state=secrets.token_urlsafe(40)
    db.add(OAuthState(state_hash=digest(state),user_id=p.user.id,organization_id=p.org.id,provider='whatsapp',expires_at=now()+900))
    db.commit()
    return {'state':state,'app_id':app_id,'config_id':config_id,'graph_version':GRAPH_VERSION,
        'expected_origin':f'{urlsplit(base).scheme}://{urlsplit(base).netloc}',
        'message':'Продолжите официальный Meta Embedded Signup. Запись появится только после серверной проверки WABA и номера.'}


@router.post('/integrations/whatsapp/embedded/complete',status_code=201)
async def whatsapp_embedded_complete(payload:WhatsAppComplete,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    check_capacity(db,p)
    state=db.query(OAuthState).filter_by(state_hash=digest(payload.state),provider='whatsapp',
        user_id=p.user.id,organization_id=p.org.id).first()
    if not state or state.expires_at<now():raise HTTPException(403,'Неверный или истёкший OAuth state')
    # One-time state, including failures; tokens are never accepted from the browser.
    db.delete(state);db.commit()
    app_id=os.getenv('META_APP_ID')
    app_secret=os.getenv('META_APP_SECRET')
    if not app_id or not app_secret:raise HTTPException(503,'Meta-приложение не настроено')
    try:
        token_data=await call('GET',f'https://graph.facebook.com/{GRAPH_VERSION}/oauth/access_token',
            params={'client_id':app_id,'client_secret':app_secret,'code':payload.code})
        token=str(token_data.get('access_token') or '')
        if not token:raise AdapterError('Meta не выдала токен после авторизации')
        headers={'Authorization':f'Bearer {token}'}
        response=await call('GET',f'https://graph.facebook.com/{GRAPH_VERSION}/{payload.waba_id}/phone_numbers',
            headers=headers,params={'fields':'id,display_phone_number,verified_name','limit':100})
        phones=response.get('data') or []
        phone=next((x for x in phones if str(x.get('id'))==payload.phone_number_id),None)
        if not phone:raise AdapterError('Выбранный номер не принадлежит WABA, к которой предоставлен доступ')
        info=await adapter_for('whatsapp').validate_credentials({'access_token':token,'phone_number_id':payload.phone_number_id})
        subscribed=await call('POST',f'https://graph.facebook.com/{GRAPH_VERSION}/{payload.waba_id}/subscribed_apps',headers=headers)
        if subscribed.get('success') is not True:
            raise AdapterError('Meta не подтвердила подписку WABA на webhooks')
        credentials={'access_token':token,'waba_id':payload.waba_id,'phone_number_id':payload.phone_number_id,
                     'expires_at':now()+int(token_data['expires_in']) if token_data.get('expires_in') else None,
                     'auth_method':'embedded_signup'}
        ch=add_channel(db,p,'whatsapp',info,credentials,'pending_webhook')
        ch.webhook_registered_at=now();db.commit()
        return {'id':ch.id,'provider':'whatsapp','name':ch.name,'status':ch.status,
                'requires_phone_registration':True,
                'message':'Доступ к номеру и подписка WABA проверены. Зарегистрируйте номер и подтвердите доставку входящего сообщения.'}
    except AdapterError as exc:
        raise HTTPException(422,'Meta onboarding не завершён: '+str(exc)) from exc


class RegisterPhone(BaseModel):
    pin:str=Field(pattern=r'^\d{6}$')


@router.post('/integrations/{channel_id}/register-phone')
async def register_phone(channel_id:str,payload:RegisterPhone,p=Depends(auth),db:Session=Depends(get_db)):
    """Explicit WhatsApp registration (never store the PIN). Does not prove inbound delivery."""
    require_role(p,'owner','admin')
    ch=get_channel(db,p,channel_id)
    if ch.provider!='whatsapp':raise HTTPException(422,'Действие доступно только для WhatsApp Business')
    creds=unseal(ch.encrypted_credentials)
    if not creds.get('waba_id'):raise HTTPException(422,'Требуется официальный WABA ID: пройдите Meta Embedded Signup')
    try:
        data=await call('POST',f'https://graph.facebook.com/{GRAPH_VERSION}/{ch.external_account_id}/register',
            headers={'Authorization':f"Bearer {creds['access_token']}"},
            json_data={'messaging_product':'whatsapp','pin':payload.pin})
        if str(data.get('success')).lower()!='true':raise AdapterError('Регистрация WhatsApp номера не подтверждена')
    except AdapterError as exc:raise HTTPException(502,str(exc)) from exc
    audit(db,p,'integration.phone_registered',ch.id,'whatsapp');db.commit()
    return {'ok':True,'status':ch.status,'message':'Номер зарегистрирован у Meta. Подтвердите получение входящего сообщения.'}


@router.get('/integrations/{channel_id}/vk-callback-setup')
def vk_callback_setup(channel_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    ch=get_channel(db,p,channel_id)
    if ch.provider!='vk':raise HTTPException(422,'Доступно только для VK')
    base=https_base()
    creds=unseal(ch.encrypted_credentials)
    return {'url':f'{base}/api/webhooks/vk/{ch.id}',
            'confirmation_token':creds.get('confirmation_token'),
            'secret':creds.get('webhook_secret'),
            'warning':'Секрет показывается только владельцу/администратору по явному запросу. Не пересылайте публично.'}


class CreateOrganization(BaseModel):
    name:str=Field(min_length=2,max_length=120)


@router.post('/organizations',status_code=201)
def create_organization(payload:CreateOrganization,p=Depends(auth),db:Session=Depends(get_db)):
    """One login can own multiple isolated businesses; each has its own connections."""
    if p.org.is_demo:raise HTTPException(403,'Для создания рабочей компании зарегистрируйтесь с почтой и паролем')
    owned=db.query(Membership).filter_by(user_id=p.user.id,role='owner',active=True).count()
    if owned>=25:raise HTTPException(422,'Лимит рабочих пространств одного владельца')
    org=Organization(name=payload.name,plan='starter',is_demo=False)
    db.add(org);db.flush()
    db.add(Membership(organization_id=org.id,user_id=p.user.id,role='owner'))
    audit(db,p,'organization.created',org.id,org.name)
    db.commit()
    return {'id':org.id,'name':org.name,'message':'Компания создана. Для работы переключитесь на неё в меню.'}


@router.get('/integrations/messenger/pages')
def list_messenger_pages(p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    pending=db.query(PendingChannelSelection).filter_by(organization_id=p.org.id,user_id=p.user.id,
        provider='messenger').filter(PendingChannelSelection.expires_at>now()).order_by(PendingChannelSelection.created_at.desc()).first()
    if not pending:return {'pages':[], 'message':'Сначала нажмите «Подключить Messenger» и разрешите доступ к страницам Facebook.'}
    items=unseal(pending.encrypted_payload).get('pages') or []
    return {'pages':[{'id':str(i['id']),'name':str(i['name'])} for i in items],
            'expires_at':pending.expires_at,'message':'Выберите страницу своей компании. Страницы других организаций никогда не показываются.'}


@router.post('/integrations/messenger/pages/{page_id}/connect',status_code=201)
async def connect_messenger_page(page_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    check_capacity(db,p)
    if not page_id.isdigit():raise HTTPException(422,'Некорректный ID страницы')
    pending=db.query(PendingChannelSelection).filter_by(organization_id=p.org.id,user_id=p.user.id,
        provider='messenger').filter(PendingChannelSelection.expires_at>now()).order_by(PendingChannelSelection.created_at.desc()).first()
    if not pending:raise HTTPException(403,'Сначала пройдите авторизацию Facebook')
    page=next((x for x in unseal(pending.encrypted_payload).get('pages',[]) if str(x.get('id'))==page_id),None)
    if not page:raise HTTPException(404,'Страница не предоставлена этим входом Facebook')
    credentials={'page_id':page_id,'access_token':str(page['access_token']),'auth_method':'facebook_page_oauth'}
    try:
        verified=await adapter_for('messenger').validate_credentials(credentials)
        # App-level Webhooks Page subscription must also be configured in Meta Dashboard.
        result=await call('POST',f'https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/subscribed_apps',
            headers={'Authorization':f"Bearer {credentials['access_token']}"},
            params={'subscribed_fields':'messages,messaging_postbacks'})
        if result.get('success') is not True:raise AdapterError('Facebook не подтвердил подписку страницы')
        ch=add_channel(db,p,'messenger',verified,credentials,'pending_webhook')
        ch.webhook_registered_at=now();db.commit()
        return {'id':ch.id,'name':ch.name,'status':ch.status,
                'message':'Страница авторизована и подписана. Настройте объект Page в Meta Webhooks и проверьте входящее сообщение.'}
    except AdapterError as exc:raise HTTPException(422,str(exc)) from exc


# R25: emergency containment for an individual company's outbound account.
# This is intentionally not a disconnect: verified inbound events continue.
class ManualOutboundPause(BaseModel):
    reason: Literal['security_review', 'provider_incident', 'configuration_review', 'operator_request']
    acknowledge_inflight: Literal[True]


@router.post('/integrations/{channel_id}/outbound-pause')
def pause_channel_outbound(channel_id: str, payload: ManualOutboundPause,
                           p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p, 'owner', 'admin')
    if p.org.is_demo:
        raise HTTPException(403, 'Аварийная пауза доступна для рабочих подключений')
    ch=get_channel(db,p,channel_id)
    stamp=now()
    changed=db.execute(update(ChannelConnection).where(
        ChannelConnection.id==ch.id,ChannelConnection.organization_id==p.org.id,
        ChannelConnection.mode=='live',ChannelConnection.status!='disconnected',
        ChannelConnection.outbound_paused_at.is_(None)
    ).values(outbound_paused_at=stamp,outbound_paused_by=p.user.id,
             outbound_pause_reason=payload.reason)).rowcount
    if changed!=1:
        db.rollback()
        raise HTTPException(409,'Новые исходящие сообщения этого аккаунта уже приостановлены')
    audit(db,p,'integration.outbound_paused',ch.id,payload.reason)
    db.commit()
    return {'channel_id':ch.id,'outbound_paused':True,'outbound_paused_at':stamp,
            'message':'Новые исходящие приостановлены. Входящие продолжат поступать. Отправки, уже прошедшие контрольную точку, могут завершиться.'}


@router.post('/integrations/{channel_id}/outbound-resume')
def resume_channel_outbound(channel_id: str, p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if p.org.is_demo:
        raise HTTPException(403,'Аварийная пауза доступна для рабочих подключений')
    ch=get_channel(db,p,channel_id)
    changed=db.execute(update(ChannelConnection).where(
        ChannelConnection.id==ch.id,ChannelConnection.organization_id==p.org.id,
        ChannelConnection.mode=='live',ChannelConnection.status!='disconnected',
        ChannelConnection.outbound_paused_at.is_not(None)
    ).values(outbound_paused_at=None,outbound_paused_by=None,
             outbound_pause_reason=None)).rowcount
    if changed!=1:
        db.rollback()
        raise HTTPException(409,'Исходящие сообщения этого аккаунта уже разрешены')
    audit(db,p,'integration.outbound_resumed',ch.id,'manual_review_completed')
    db.commit()
    return {'channel_id':ch.id,'outbound_paused':False,
            'message':'Пауза снята. Новые отправки возобновятся через существующую очередь; отдельные лимиты площадки остаются в силе.'}
