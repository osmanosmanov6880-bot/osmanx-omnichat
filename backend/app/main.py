"""OSMANX OMNICHAT R35: tenant-fair inbound dispatch and guarded integrity maintenance."""
import asyncio
import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

# Local development reads the project .env; actual process environment always wins.
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
from urllib.parse import urlencode, quote
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, Response, Query, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, EmailStr, field_validator
from sqlalchemy import or_, update, desc, text
from sqlalchemy.orm import Session
from . import db as store
from .db import (get_db, Organization, User, Membership, AuthSession, LoginFailure, OAuthState, PendingChannelSelection, ChannelConnection, Contact, Conversation, Message, Note, AutomationRule, Invite, AuditLog, OutgoingJob, now, uid)
from .auth import (auth, session_from_request, grant_session, make_password, verify_password, digest, login_attempt_identity, require_role, can_view, audit, MAX_CHANNELS, MAX_MEMBERS, ROLES, SESSION_COOKIE, CSRF_COOKIE)
from .fixtures import create_demo
from .history import message_history_page
from .services import (as_conversation, as_contact, as_message, analytics, ingest_inbound, process_outbox, VALID_STATUSES, VALID_STAGES)
from .integrations.adapters import (adapter_for, seal, unseal, call, GRAPH_VERSION)
from .integrations.base import AdapterError
from .integrations.readiness import readiness as channel_readiness
from .integrations.subscription_check import remote_subscription, revoke_bot_subscription

BACKEND_DIR = Path(__file__).resolve().parents[1]
ASSET_DIR = BACKEND_DIR.parent / 'frontend' / 'public'
api = APIRouter(prefix='/api')
rate_hits = defaultdict(list)
log = logging.getLogger("omnichat.api")

@asynccontextmanager
async def lifespan(app):
    if os.getenv("APP_ENV", "development")=="production":
        if os.getenv("COOKIE_SECURE", "false").lower()!="true":
            raise RuntimeError("Production mode requires COOKIE_SECURE=true")
        if not os.getenv("PUBLIC_BASE_URL", "").startswith("https://"):
            raise RuntimeError("Production mode requires PUBLIC_BASE_URL=https://...")
        if not os.getenv('DATABASE_URL', '').startswith(('postgresql://', 'postgresql+psycopg://')):
            raise RuntimeError('Production mode requires PostgreSQL DATABASE_URL, not SQLite')
        if not os.getenv('INTEGRATION_ENCRYPTION_KEY'):
            raise RuntimeError('Production mode requires INTEGRATION_ENCRYPTION_KEY')
    store.initialize()
    running=True
    cycle=0
    async def worker():
        nonlocal cycle
        while running:
            try:
                if store.SessionLocal:
                    from .inbound_jobs import process_batch
                    received=await asyncio.to_thread(process_batch,store.SessionLocal,limit=40)
                    processed=await process_outbox(store.SessionLocal)
                    processed+=received
                    from .worker_monitor import finish_cycle
                    finish_cycle(store.SessionLocal,heartbeat_id,processed=processed)
                    cycle+=1
                    if cycle%12==0 and os.getenv('ENABLE_AVITO_POLLING','true').lower()=='true':
                        from .scheduler_lease import run_avito_sync
                        await run_avito_sync(store.SessionLocal)
                    if cycle%20==0:
                        from .scheduler_lease import run_retention_cleanup
                        await run_retention_cleanup(store.SessionLocal)
            except Exception:
                log.exception("Background worker failed; next cycle will retry")
                from .worker_monitor import finish_cycle
                if heartbeat_id:
                    try: finish_cycle(store.SessionLocal,heartbeat_id,succeeded=False)
                    except Exception: log.exception('Failed to update worker-cycle status')
            await asyncio.sleep(3)
    enabled=os.getenv('ENABLE_OUTBOX_WORKER','true').lower()=='true'
    heartbeat_id=None
    heartbeat_task=None
    if enabled:
        from .worker_monitor import start_worker, heartbeat_loop
        heartbeat_id=start_worker(store.SessionLocal,kind='api')
        heartbeat_task=asyncio.create_task(heartbeat_loop(store.SessionLocal,heartbeat_id))
    task = asyncio.create_task(worker()) if enabled else None
    yield
    running=False
    if task:
        task.cancel()
        try: await task
        except asyncio.CancelledError: pass
    if heartbeat_task:
        heartbeat_task.cancel()
        try: await heartbeat_task
        except asyncio.CancelledError: pass

app = FastAPI(title='OSMANX OMNICHAT API',version='3.5.0-recovery',lifespan=lifespan,docs_url='/api/docs' if os.getenv('ENABLE_API_DOCS','true')=='true' else None,openapi_url='/api/openapi.json' if os.getenv('ENABLE_API_DOCS','true')=='true' else None)

@app.middleware('http')
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    if not request.url.path.startswith('/widget/'):
        response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
    response.headers['Cache-Control']=('no-store, private' if request.url.path=='/api/operations/support-bundle' else 'no-store' if request.url.path.startswith(('/api','/widget/')) else 'public, max-age=3600')
    frame_ancestors="'none'"
    if request.url.path.startswith('/widget/') and store.SessionLocal:
        try:
            from .db import WebsiteWidget
            widget_key=request.url.path.rsplit('/',1)[-1]
            with store.SessionLocal() as scoped_db:
                widget=scoped_db.query(WebsiteWidget).filter_by(public_key=widget_key,enabled=True).first()
                if widget:
                    allowed=json.loads(widget.allowed_origins or '[]')
                    frame_ancestors="'self' "+' '.join(allowed)
        except Exception:
            log.exception('Could not evaluate widget frame policy')
    # Meta Embedded Signup is loaded only by the first-party control panel. No
    # inline JS or arbitrary remote scripts are allowed. Widgets remain self-only.
    panel = request.url.path in ('/', '/index.html')
    scripts = "'self' https://connect.facebook.net" if panel else "'self'"
    frames = 'https://www.facebook.com https://web.facebook.com' if panel else "'none'"
    response.headers['Content-Security-Policy']="default-src 'self'; script-src "+scripts+"; style-src 'self'; img-src 'self' data: https:; connect-src 'self'; frame-src "+frames+"; font-src 'self'; object-src 'none'; frame-ancestors "+frame_ancestors+"; base-uri 'none'; form-action 'self'"
    return response

def throttle(request, key, limit, per):
    who = request.client.host if request.client else 'unknown'
    name = (key, who)
    current = now()
    rate_hits[name] = [t for t in rate_hits[name] if current-t<per]
    if len(rate_hits[name])>=limit: raise HTTPException(429,'Слишком много запросов. Повторите позже.')
    rate_hits[name].append(current)

class RegisterPayload(BaseModel):
    company: str = Field(min_length=2,max_length=120)
    name: str = Field(min_length=2,max_length=120)
    email: EmailStr
    password: str = Field(min_length=12,max_length=150)

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

class ReplyPayload(BaseModel):
    body: str = Field(min_length=1,max_length=4000)
    expected_version: int = Field(ge=0)
    client_nonce: str = Field(min_length=8,max_length=100)

class StatusPayload(BaseModel):
    status: str
    # Optional for legacy API clients; official UI always sends a version.
    expected_version: int | None = Field(default=None, ge=0)
    @field_validator('status')
    @classmethod
    def valid_status(cls, v):
        if v not in VALID_STATUSES: raise ValueError('Неизвестный статус')
        return v

class AssignPayload(BaseModel):
    user_id: str | None
    expected_version: int | None = Field(default=None, ge=0)

class PinPayload(BaseModel):
    expected_version: int | None = Field(default=None, ge=0)

class NotePayload(BaseModel):
    body: str = Field(min_length=1,max_length=3000)

class ContactPatch(BaseModel):
    name: str | None = Field(None,min_length=1,max_length=160)
    phone: str | None = Field(None,max_length=80)
    email: str | None = Field(None,max_length=250)
    stage: str | None = None
    deal_amount: float | None = Field(None,ge=0,le=10**12)
    deal_confirmed: bool | None = None
    tags: list[str] | None = None
    next_followup_at: float | None = None

class RulePayload(BaseModel):
    name: str = Field(min_length=2,max_length=120)
    event: str = 'message_received'
    condition_type: str = 'contains'
    condition_value: str = Field(default='',max_length=120)
    action_type: str = 'tag'
    action_value: str = Field(default='',max_length=80)
    enabled: bool = True

class InvitePayload(BaseModel):
    email: EmailStr
    role: str

class AcceptInvitePayload(BaseModel):
    token: str
    name: str | None = None
    password: str | None = None

class ManualConnectionPayload(BaseModel):
    provider: str
    access_token: str = Field(min_length=10,max_length=8000)
    phone_number_id: str | None = None
    waba_id: str | None = Field(None,pattern=r'^\d{4,30}$')

class BotConnectionPayload(BaseModel):
    provider: str
    access_token: str = Field(min_length=10,max_length=3000)
    group_id: str | None = Field(None,max_length=25)
    confirmation_token: str | None = Field(None,max_length=150)

@api.get('/health')
def health():
    return {'status':'ok','app':'OSMANX OMNICHAT','version':'2.5.0-recovery'}

@api.get('/health/ready')
def readiness(db:Session=Depends(get_db)):
    try: db.execute(text('SELECT 1')).scalar_one()
    except Exception as exc: raise HTTPException(503,'База данных недоступна') from exc
    return {'status':'ready','database':'ok'}

@api.post('/auth/register', status_code=201)
def register(payload:RegisterPayload, response:Response, request:Request, db:Session=Depends(get_db)):
    from .public_limits import enforce_public_limit
    enforce_public_limit(db, request, 'register', limit=6, period=3600)
    throttle(request,'register',6,3600)
    email=str(payload.email).lower()
    if db.query(User).filter_by(email=email).first(): raise HTTPException(409,'Эта почта уже используется')
    org=Organization(name=payload.company,plan='starter')
    u=User(email=email,name=payload.name,password_hash=make_password(payload.password))
    db.add_all([org,u]);db.flush()
    db.add(Membership(organization_id=org.id,user_id=u.id,role='owner'))
    db.commit();grant_session(response,u,org,db)
    return {'ok':True,'organization_id':org.id}

# The same fake hash is used for unknown users, reducing account-enumeration
# timing differences without creating an account or revealing its existence.
_DUMMY_PASSWORD_HASH = make_password('omnichat-not-an-account-password')
_LOGIN_FAILURE_WINDOW_SECONDS = 15 * 60
_LOGIN_FAILURE_LIMIT = 10

@api.post('/auth/login')
def login(payload:LoginPayload,request:Request,response:Response,db:Session=Depends(get_db)):
    # Keep office users behind one public NAT from blocking each other.
    # Per-account failures are now also tracked in the shared database.
    throttle(request,'login',60,600)
    email = str(payload.email).strip().lower()
    email_digest = login_attempt_identity(email)
    window = now() - _LOGIN_FAILURE_WINDOW_SECONDS
    failures = db.query(LoginFailure).filter(
        LoginFailure.email_digest == email_digest,
        LoginFailure.attempted_at >= window
    ).count()
    if failures >= _LOGIN_FAILURE_LIMIT:
        raise HTTPException(429,'Слишком много неудачных попыток входа. Попробуйте через 15 минут.')
    u = db.query(User).filter_by(email=email).first()
    password_valid = verify_password(payload.password, u.password_hash if u else _DUMMY_PASSWORD_HASH)
    if not u or not password_valid:
        db.add(LoginFailure(email_digest=email_digest, attempted_at=now()))
        db.commit()
        raise HTTPException(401,'Неверная почта или пароль')
    membership=db.query(Membership).filter_by(user_id=u.id,active=True).first()
    if not membership: raise HTTPException(403,'Нет активной организации')
    # A successful login clears earlier failures for that identity across
    # server instances which share this database.
    db.query(LoginFailure).filter_by(email_digest=email_digest).delete(synchronize_session=False)
    org=db.get(Organization,membership.organization_id)
    grant_session(response,u,org,db)
    return {'ok':True}

@api.post('/demo/start')
def start_demo(request:Request,response:Response,db:Session=Depends(get_db)):
    from .public_limits import enforce_public_limit
    enforce_public_limit(db, request, 'demo', limit=12, period=3600)
    throttle(request,'demo',12,3600)
    org,u=create_demo(db)
    grant_session(response,u,org,db)
    return {'ok':True,'mode':'demo'}

@api.get('/auth/me')
def me(p=Depends(auth),db:Session=Depends(get_db)):
    members=db.query(Membership).filter_by(user_id=p.user.id,active=True).all()
    return {'user':{'id':p.user.id,'name':p.user.name,'email':p.user.email},'organization':{'id':p.org.id,'name':p.org.name,'plan':p.org.plan,'currency':p.org.currency,'timezone':p.org.timezone,'is_demo':p.org.is_demo},'role':p.role,'organizations':[{'id':m.organization_id,'name':db.get(Organization,m.organization_id).name,'role':m.role} for m in members]}

@api.post('/auth/logout')
def logout(response:Response,p=Depends(auth),db:Session=Depends(get_db)):
    db.delete(p.session);db.commit()
    response.delete_cookie(SESSION_COOKIE,path='/');response.delete_cookie(CSRF_COOKIE,path='/')
    return {'ok':True}

@api.get('/auth/sessions')
def list_auth_sessions(p=Depends(auth), db:Session=Depends(get_db)):
    """Show only the current user's session metadata; never return tokens."""
    sessions=db.query(AuthSession).filter_by(user_id=p.user.id).filter(
        AuthSession.expires_at > now()
    ).order_by(AuthSession.created_at.desc()).all()
    return {'count':len(sessions),'sessions':[
        {'created_at':item.created_at, 'is_current':item.id_hash==p.session.id_hash}
        for item in sessions
    ]}

@api.post('/auth/sessions/revoke-others')
def revoke_other_sessions(p=Depends(auth),db:Session=Depends(get_db)):
    revoked=db.query(AuthSession).filter(
        AuthSession.user_id==p.user.id,AuthSession.id_hash!=p.session.id_hash
    ).delete(synchronize_session=False)
    audit(db,p,'security.sessions_revoked',p.user.id,'other_devices')
    db.commit()
    return {'ok':True,'revoked':revoked,'current_session_active':True}

@api.post('/auth/sessions/revoke-all')
def revoke_all_sessions(response:Response,p=Depends(auth),db:Session=Depends(get_db)):
    revoked=db.query(AuthSession).filter_by(user_id=p.user.id).delete(synchronize_session=False)
    audit(db,p,'security.sessions_revoked',p.user.id,'all_devices')
    db.commit()
    response.delete_cookie(SESSION_COOKIE,path='/')
    response.delete_cookie(CSRF_COOKIE,path='/')
    return {'ok':True,'revoked':revoked,'current_session_active':False}

@api.post('/auth/switch/{organization_id}')
def switch_org(organization_id:str,response:Response,p=Depends(auth),db:Session=Depends(get_db)):
    m=db.query(Membership).filter_by(organization_id=organization_id,user_id=p.user.id,active=True).first()
    if not m: raise HTTPException(403,'Нет доступа к организации')
    db.delete(p.session);db.commit()
    grant_session(response,p.user,db.get(Organization,organization_id),db)
    return {'ok':True}

@api.get('/team')
def team(p=Depends(auth),db:Session=Depends(get_db)):
    memberships=db.query(Membership).filter_by(organization_id=p.org.id,active=True).all()
    return [{'id':m.user_id,'name':db.get(User,m.user_id).name,'email':db.get(User,m.user_id).email,'role':m.role,'available':m.available} for m in memberships]

@api.post('/team/invite')
def invite(payload:InvitePayload,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if payload.role not in ('admin','lead','manager','operator'): raise HTTPException(422,'Недопустимая роль')
    count=db.query(Membership).filter_by(organization_id=p.org.id,active=True).count()
    if count>=MAX_MEMBERS[p.org.plan]:raise HTTPException(402,'Лимит сотрудников текущего тарифа')
    token=secrets.token_urlsafe(36)
    item=Invite(organization_id=p.org.id,email=str(payload.email).lower(),role=payload.role,token_hash=digest(token),expires_at=now()+7*86400)
    db.add(item);audit(db,p,'invite.created',item.id);db.commit()
    return {'invite_token':token,'expires_at':item.expires_at,'delivery':'manual_share_only'}

@api.post('/team/accept-invite')
def accept_invite(payload:AcceptInvitePayload,response:Response,db:Session=Depends(get_db)):
    item=db.query(Invite).filter_by(token_hash=digest(payload.token)).first()
    if not item or item.accepted_at or item.expires_at<now():raise HTTPException(404,'Приглашение не найдено или истекло')
    org=db.get(Organization,item.organization_id)
    if db.query(Membership).filter_by(organization_id=org.id,active=True).count()>=MAX_MEMBERS[org.plan]:raise HTTPException(402,'Лимит сотрудников')
    u=db.query(User).filter_by(email=item.email).first()
    if not u:
        if not payload.password or len(payload.password)<12 or not payload.name: raise HTTPException(422,'Для нового сотрудника нужны имя и пароль от 12 символов')
        u=User(email=item.email,name=payload.name,password_hash=make_password(payload.password));db.add(u);db.flush()
    elif not payload.password or not verify_password(payload.password,u.password_hash):
        raise HTTPException(401,'Для существующего сотрудника требуется подтверждение его пароля')
    existing=db.query(Membership).filter_by(user_id=u.id,organization_id=org.id).first()
    if existing: raise HTTPException(409,'Сотрудник уже в организации')
    db.add(Membership(user_id=u.id,organization_id=org.id,role=item.role));item.accepted_at=now();db.commit()
    # Existing user still must log in with own password; possession of token alone isn't authentication.
    return {'ok':True,'email':item.email,'message':'Войдите под своей учётной записью, чтобы выбрать организацию'}

@api.get('/conversations')
def list_conversations(q:str='', channel:str='', status:str='', priority:str='', assigned:str='', pinned:bool=False, archived:bool=False, sort:str='recent', from_date:float|None=None, to_date:float|None=None,limit:int=Query(75,ge=1,le=200),p=Depends(auth),db:Session=Depends(get_db)):
    query=db.query(Conversation).filter_by(organization_id=p.org.id)
    if p.role in ('operator','manager'): query=query.filter_by(assigned_user_id=p.user.id)
    if status: query=query.filter_by(status=status)
    if priority:
        if priority not in ('urgent','high','normal','low'): raise HTTPException(422,'Некорректный приоритет')
        query=query.filter_by(priority=priority)
    if sort not in ('recent','priority','oldest'):raise HTTPException(422,'Неизвестный порядок сортировки')
    query=query.filter_by(archived=archived)
    if from_date is not None:query=query.filter(Conversation.last_message_at>=from_date)
    if to_date is not None:query=query.filter(Conversation.last_message_at<=to_date)
    if assigned and p.role in ('owner','admin','lead'):query=query.filter_by(assigned_user_id=assigned)
    if pinned: query=query.filter_by(pinned=True)
    if channel:
        ids=[c.id for c in db.query(ChannelConnection).filter_by(organization_id=p.org.id,provider=channel).all()]
        query=query.filter(Conversation.channel_id.in_(ids))
    from sqlalchemy import case
    weight=case((Conversation.priority=='urgent',4),(Conversation.priority=='high',3),
                (Conversation.priority=='normal',2),else_=1)
    ordering = [desc(weight),desc(Conversation.last_message_at)] if sort=='priority' else \
               [Conversation.last_message_at.asc()] if sort=='oldest' else \
               [desc(Conversation.pinned),desc(Conversation.last_message_at)]
    if q.strip():
        # Apply filters BEFORE pagination. SQL parameters are bound by SQLAlchemy;
        # escaping wildcard chars preserves users' expectation of literal search.
        from sqlalchemy import select
        needle=q.strip()
        if len(needle)>120:raise HTTPException(422,'Поисковый запрос слишком длинный')
        pattern='%' + needle.replace('!', '!!').replace('%', '!%').replace('_', '!_') + '%'
        contacts_matching=select(Contact.id).where(Contact.organization_id==p.org.id,
            or_(Contact.name.ilike(pattern,escape='!'),Contact.phone.ilike(pattern,escape='!'),Contact.email.ilike(pattern,escape='!')))
        messages_matching=select(Message.conversation_id).where(Message.organization_id==p.org.id,
            Message.body.ilike(pattern,escape='!'))
        query=query.filter(or_(Conversation.contact_id.in_(contacts_matching),Conversation.id.in_(messages_matching)))
    rows=query.order_by(*ordering).limit(limit).all()
    return [as_conversation(db,c) for c in rows]


def get_conv(db,p,conv_id):
    c=db.query(Conversation).filter_by(id=conv_id,organization_id=p.org.id).first()
    if not c: raise HTTPException(404,'Диалог не найден')
    if not can_view(p,c): raise HTTPException(403,'Диалог не назначен вам')
    return c

@api.get('/conversations/{conversation_id}')
def conversation_detail(conversation_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    c=get_conv(db,p,conversation_id)
    contact=db.query(Contact).filter_by(id=c.contact_id,organization_id=p.org.id).first()
    page=message_history_page(db,organization_id=p.org.id,conversation_id=c.id)
    notes=db.query(Note).filter_by(organization_id=p.org.id,conversation_id=c.id).order_by(Note.created_at.asc()).all()
    return {'conversation':as_conversation(db,c),'contact':as_contact(contact),**page,
        'notes':[{'id':n.id,'body':n.body,'author':db.get(User,n.author_user_id).name,'created_at':n.created_at} for n in notes]}

@api.get('/conversations/{conversation_id}/messages')
def conversation_messages(conversation_id:str,
                          before:str|None=None,
                          limit:int=Query(120,ge=1,le=200),
                          p=Depends(auth),db:Session=Depends(get_db)):
    # Reuse assignment/tenant checks of the main conversation endpoint.
    c=get_conv(db,p,conversation_id)
    return message_history_page(db,organization_id=p.org.id,conversation_id=c.id,
                                before=before,limit=limit)

class MarkReadPayload(BaseModel):
    # R29: the UI acknowledges the exact conversation snapshot it displayed.
    # Old clients may omit the body; the backend still uses a read-time CAS.
    expected_version: int | None = Field(default=None,ge=0)

@api.post('/conversations/{conversation_id}/read')
def mark_read(conversation_id:str,payload:MarkReadPayload|None=Body(default=None),
              p=Depends(auth),db:Session=Depends(get_db)):
    c=get_conv(db,p,conversation_id)
    expected=(payload.expected_version if payload and payload.expected_version is not None
              else c.version)
    filters=[Conversation.id==c.id,Conversation.organization_id==p.org.id,
             Conversation.version==expected]
    # Permission must remain true at the SQL write, not only at read time.
    if p.role in ('operator','manager'):
        filters.append(Conversation.assigned_user_id==p.user.id)
    result=db.execute(update(Conversation).where(*filters).values(
        unread_count=0,version=Conversation.version+1))
    if result.rowcount!=1:
        db.rollback()
        raise HTTPException(409,'Пришло новое сообщение или диалог изменился. Обновите переписку.')
    audit(db,p,'conversation.read',c.id)
    db.commit()
    return {'ok':True,'version':expected+1}

def _update_conversation_atomically(db, p, conversation, *, expected_version, changes, assigned_to=None):
    """Atomic SQL update. UI CAS prevents stale two-operator overwrites.

    Legacy clients can omit expected_version, but still receive SQL field-level
    atomicity; new clients always send it. The DB-level owner predicate blocks
    an operator if their assignment was revoked between read and write.
    """
    filters = [Conversation.id == conversation.id,
               Conversation.organization_id == p.org.id]
    if expected_version is not None:
        filters.append(Conversation.version == expected_version)
    if p.role in ('operator', 'manager'):
        filters.append(Conversation.assigned_user_id == p.user.id)
    if assigned_to is not None:
        # Assignment changes may not steal an active reply from another operator.
        # Explicit release/expiry remains the safe path.
        filters.append(or_(Conversation.reply_lock_owner_id.is_(None),
                           Conversation.reply_lock_expires_at.is_(None),
                           Conversation.reply_lock_expires_at <= now(),
                           Conversation.reply_lock_owner_id == assigned_to))
    result = db.execute(update(Conversation).where(*filters).values(
        **changes, version=Conversation.version + 1))
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(409, 'Диалог изменён другим сотрудником или занят. Обновите переписку.')
    db.refresh(conversation)
    return conversation


@api.patch('/conversations/{conversation_id}/status')
def update_status(conversation_id:str,payload:StatusPayload,p=Depends(auth),db:Session=Depends(get_db)):
    c=get_conv(db,p,conversation_id)
    _update_conversation_atomically(db,p,c,expected_version=payload.expected_version,
        changes={'status':payload.status,'archived':payload.status=='closed'})
    audit(db,p,'conversation.status',c.id,payload.status)
    db.commit()
    return as_conversation(db,c)


@api.patch('/conversations/{conversation_id}/pin')
def toggle_pin(conversation_id:str,payload:PinPayload|None=None,p=Depends(auth),db:Session=Depends(get_db)):
    c=get_conv(db,p,conversation_id)
    _update_conversation_atomically(db,p,c,
        expected_version=payload.expected_version if payload else None,
        changes={'pinned':~Conversation.pinned})
    audit(db,p,'conversation.pin',c.id,'pinned' if c.pinned else 'unpinned')
    db.commit()
    return as_conversation(db,c)


@api.patch('/conversations/{conversation_id}/assign')
def assign(conversation_id:str,payload:AssignPayload,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    c=get_conv(db,p,conversation_id)
    if payload.user_id:
        membership=db.query(Membership).filter_by(
            organization_id=p.org.id,user_id=payload.user_id,active=True).first()
        if not membership:
            raise HTTPException(422,'Сотрудника нет в этой компании')
    # Use a sentinel for unassignment so even assigning None checks leases.
    _update_conversation_atomically(db,p,c,expected_version=payload.expected_version,
        changes={'assigned_user_id':payload.user_id},
        assigned_to=payload.user_id if payload.user_id is not None else '')
    audit(db,p,'conversation.assign',c.id,payload.user_id)
    db.commit()
    return as_conversation(db,c)

@api.post('/conversations/{conversation_id}/reply',status_code=201)
def reply(conversation_id:str,payload:ReplyPayload,p=Depends(auth),db:Session=Depends(get_db)):
    c=get_conv(db,p,conversation_id)
    ch=db.query(ChannelConnection).filter_by(id=c.channel_id,organization_id=p.org.id).first()
    body=payload.body.strip()
    if not body: raise HTTPException(422,'Пустой ответ')
    if len(body)>1000 and ch.provider == 'avito': raise HTTPException(422,'Максимум 1000 символов для Авито')
    if ch.provider=='instagram' and len(body.encode('utf-8'))>1000:
        raise HTTPException(422,'Instagram: не более 1000 байт UTF-8, включая кириллицу и эмодзи')
    if ch.mode=='live' and ch.provider in ('instagram','whatsapp','messenger') and (not c.last_inbound_at or now()-c.last_inbound_at>24*3600):
        raise HTTPException(409,'Окно 24 часа закрыто. Для WhatsApp требуется разрешённый шаблон, для Instagram — новое сообщение клиента или отдельное право.')
    if c.reply_lock_owner_id and c.reply_lock_expires_at and c.reply_lock_expires_at>now() and c.reply_lock_owner_id!=p.user.id:
        raise HTTPException(409,'Another teammate is currently replying to this conversation')
    external_key='client-'+payload.client_nonce
    existing=db.query(Message).filter_by(organization_id=p.org.id,conversation_id=c.id,client_nonce=payload.client_nonce).first()
    if existing:return {'message':as_message(existing),'conversation':as_conversation(db,c),'duplicate':True}
    # Optimistic update ensures only the first of simultaneous writers wins.
    result=db.execute(update(Conversation).where(Conversation.id==c.id,Conversation.organization_id==p.org.id,Conversation.version==payload.expected_version,or_(Conversation.reply_lock_owner_id.is_(None),Conversation.reply_lock_owner_id==p.user.id,Conversation.reply_lock_expires_at.is_(None),Conversation.reply_lock_expires_at<=now())).values(version=Conversation.version+1))
    if result.rowcount==0:
        db.rollback();raise HTTPException(409,'Диалог уже изменился. Обновите переписку перед ответом.')
    if ch.mode=='live':
        if ch.status!='connected':raise HTTPException(409,'Канал не подключен')
        if ch.provider in ('whatsapp','instagram','messenger') and (not c.last_inbound_at or now()-c.last_inbound_at > 24*3600):raise HTTPException(422,'24-часовое окно ответа истекло. Нужен новый входящий контакт или одобренный шаблон.')
    timestamp=now()
    m=Message(organization_id=p.org.id,conversation_id=c.id,external_id=external_key,client_nonce=payload.client_nonce,direction='out',body=body,delivery_status='accepted' if ch.provider=='website' else ('delivered' if ch.mode=='demo' else 'queued'),response_confirmed_at=(timestamp if ch.mode=='demo' and ch.provider!='website' else None),is_demo=ch.mode=='demo',author_user_id=p.user.id,created_at=timestamp)
    db.add(m);db.flush()
    if ch.mode=='live' and ch.provider!='website':db.add(OutgoingJob(organization_id=p.org.id,message_id=m.id,channel_id=ch.id))
    c.version=payload.expected_version+1
    c.last_message_at=timestamp
    if not c.first_reply_at:c.first_reply_at=timestamp
    if c.status=='new':c.status='in_progress'
    audit(db,p,'message.reply',c.id,'demo' if ch.mode=='demo' else 'queued')
    db.commit();db.refresh(c)
    return {'message':as_message(m),'conversation':as_conversation(db,c),'duplicate':False}

@api.post('/conversations/{conversation_id}/notes',status_code=201)
def add_note(conversation_id:str,payload:NotePayload,p=Depends(auth),db:Session=Depends(get_db)):
    c=get_conv(db,p,conversation_id)
    note=Note(organization_id=p.org.id,conversation_id=c.id,author_user_id=p.user.id,body=payload.body.strip())
    db.add(note);audit(db,p,'note.created',c.id);db.commit()
    return {'id':note.id,'body':note.body,'author':p.user.name,'created_at':note.created_at}

@api.get('/contacts')
def contacts(q:str='',p=Depends(auth),db:Session=Depends(get_db)):
    visible_ids=None
    if p.role in ('manager','operator'):
        visible_ids={c.contact_id for c in db.query(Conversation).filter_by(organization_id=p.org.id,assigned_user_id=p.user.id).all()}
    all_contacts=db.query(Contact).filter_by(organization_id=p.org.id).all()
    return [as_contact(c) for c in all_contacts if (visible_ids is None or c.id in visible_ids) and q.lower() in (c.name+' '+(c.phone or '')).lower()]

@api.patch('/contacts/{contact_id}')
def patch_contact(contact_id:str,payload:ContactPatch,p=Depends(auth),db:Session=Depends(get_db)):
    c=db.query(Contact).filter_by(id=contact_id,organization_id=p.org.id).first()
    if not c: raise HTTPException(404,'Контакт не найден')
    if p.role in ('operator','manager'):
        if not db.query(Conversation).filter_by(organization_id=p.org.id,contact_id=c.id,assigned_user_id=p.user.id).first():raise HTTPException(403,'Нет доступа к этому контакту')
    patch=payload.model_dump(exclude_unset=True)
    if patch.get('stage') and patch['stage'] not in VALID_STAGES:raise HTTPException(422,'Неизвестный этап сделки')
    if 'tags' in patch:
        if len(patch['tags'] or [])>20 or any(len(t)>40 for t in patch['tags'] or []):raise HTTPException(422,'Слишком много тегов')
        patch['tags']=json.dumps(patch['tags'] or [],ensure_ascii=False)
    if 'deal_confirmed' in patch and patch['deal_confirmed'] and (patch.get('stage',c.stage)!='success'):
        raise HTTPException(422,'Подтверждённая сделка должна быть на этапе «Успешно»')
    for k,v in patch.items():setattr(c,k,v)
    audit(db,p,'contact.updated',c.id,','.join(patch.keys()));db.commit()
    return as_contact(c)

class DemoIncomingPayload(BaseModel):
    conversation_id: str
    body: str = Field(min_length=1,max_length=2000)

@api.post('/demo/incoming',status_code=201)
def demo_incoming(payload:DemoIncomingPayload,p=Depends(auth),db:Session=Depends(get_db)):
    if not p.org.is_demo:raise HTTPException(403,'Только для демонстрации')
    c=get_conv(db,p,payload.conversation_id)
    ch=db.get(ChannelConnection,c.channel_id)
    if ch.mode!='demo':raise HTTPException(403,'Не демонстрационный канал')
    contact=db.get(Contact,c.contact_id)
    msg=ingest_inbound(db,channel=ch,external_chat_id=c.external_chat_id,external_message_id='manual-'+uid(),sender_id=c.external_recipient_id or c.contact_id,sender_name=contact.name,text=payload.body.strip())
    audit(db,p,'demo.incoming',c.id)
    db.commit()
    return {'message':as_message(msg),'conversation':as_conversation(db,c)}

@api.get('/analytics')
def get_analytics(p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    if p.org.plan=='starter':raise HTTPException(402,'Аналитика доступна с тарифа Business')
    return analytics(db,p.org.id)

@api.get('/rules')
def get_rules(p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    return [{'id':r.id,'name':r.name,'event':r.event,'condition_type':r.condition_type,'condition_value':r.condition_value,'action_type':r.action_type,'action_value':r.action_value,'enabled':r.enabled} for r in db.query(AutomationRule).filter_by(organization_id=p.org.id).all()]

@api.post('/rules',status_code=201)
def add_rule(payload:RulePayload,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    if p.org.plan not in ('professional','enterprise'):raise HTTPException(402,'Автоматизация доступна с тарифа Professional')
    if payload.event!='message_received' or payload.condition_type not in ('always','contains') or payload.action_type not in ('tag','priority','status','assign_least_busy'):
        raise HTTPException(422,'Неподдерживаемое правило')
    if payload.action_type=='status' and payload.action_value not in VALID_STATUSES:raise HTTPException(422,'Неизвестный статус')
    if payload.action_type in ('status','tag') and not payload.action_value:raise HTTPException(422,'Укажите значение действия')
    rule=AutomationRule(organization_id=p.org.id,**payload.model_dump());db.add(rule);audit(db,p,'rule.created',rule.id);db.commit();return {'id':rule.id,'ok':True}

@api.patch('/rules/{rule_id}/toggle')
def toggle_rule(rule_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    rule=db.query(AutomationRule).filter_by(id=rule_id,organization_id=p.org.id).first()
    if not rule:raise HTTPException(404,'Правило не найдено')
    rule.enabled=not rule.enabled;audit(db,p,'rule.toggle',rule.id);db.commit();return {'id':rule.id,'enabled':rule.enabled}

@api.get('/integrations')
def list_integrations(p=Depends(auth),db:Session=Depends(get_db)):
    chs=db.query(ChannelConnection).filter_by(organization_id=p.org.id).all()
    public_base=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
    webhook_base=public_base if public_base.startswith('https://') else ''
    return {'connections':[
        {'id':c.id,'provider':c.provider,'name':c.name,'status':c.status,'mode':c.mode,
         'outbound_paused_at':c.outbound_paused_at,'outbound_pause_reason':c.outbound_pause_reason,
         'last_sync_at':c.last_sync_at,'last_verified_at':c.last_verified_at,'webhook_verified_at':c.webhook_verified_at,'webhook_registered_at':c.webhook_registered_at,'token_expires_at':c.token_expires_at,'last_error':c.last_error,'last_probe_at':c.last_probe_at,
         'capabilities':adapter_for(c.provider).get_capabilities().__dict__,
         'readiness':channel_readiness(db,c) if c.mode=='live' else None,
         'webhook_url':f'{webhook_base}/api/webhooks/{c.provider}/{c.id}' if webhook_base and c.provider in ('telegram','vk','max') and c.mode=='live' else None}
        for c in chs],
        'available':{
            'avito':bool(os.getenv('AVITO_CLIENT_ID') and os.getenv('AVITO_CLIENT_SECRET') and webhook_base and os.getenv('INTEGRATION_ENCRYPTION_KEY')),
            'instagram':bool(os.getenv('INSTAGRAM_APP_ID') and os.getenv('INSTAGRAM_APP_SECRET') and webhook_base and os.getenv('INTEGRATION_ENCRYPTION_KEY')),
            'whatsapp':bool(os.getenv('INTEGRATION_ENCRYPTION_KEY')),
            'telegram':bool(os.getenv('INTEGRATION_ENCRYPTION_KEY')),
            'vk':bool(os.getenv('INTEGRATION_ENCRYPTION_KEY')),
            'max':bool(os.getenv('INTEGRATION_ENCRYPTION_KEY')),
            'messenger':bool((os.getenv('FACEBOOK_APP_ID') or os.getenv('META_APP_ID')) and (os.getenv('FACEBOOK_APP_SECRET') or os.getenv('META_APP_SECRET')) and webhook_base and os.getenv('INTEGRATION_ENCRYPTION_KEY'))},
        'requirements':{
            'avito':'Бизнес-аккаунт, Messenger API и разрешения messenger:read/messenger:write',
            'instagram':'Профессиональный Instagram, Instagram Login и instagram_business_manage_messages',
            'whatsapp':'WhatsApp Business Platform: Phone Number ID и официальный токен Meta',
            'telegram':'Только Telegram-бот, созданный через BotFather; HTTPS webhook, не личный профиль',
            'vk':'Сообщество VK с токеном для сообщений, Callback API, секрет и код подтверждения',
            'max':'Проверенный бот MAX, HTTPS webhook с X-Max-Bot-Api-Secret; не личный профиль',
            'messenger':'Facebook Page с Page messaging permission, Meta App Review и подпиской на сообщения страницы'}}

@api.post('/integrations/bots',status_code=201)
async def connect_bot(payload:BotConnectionPayload,p=Depends(auth),db:Session=Depends(get_db)):
    """Verify official bot/community identity; NEVER report connected until webhook is active."""
    require_role(p,'owner','admin')
    if p.org.is_demo:raise HTTPException(403,'Для реального подключения создайте компанию')
    if payload.provider not in ('telegram','vk','max'):raise HTTPException(422,'Поддерживаются боты Telegram, MAX и сообщества VK')
    if db.query(ChannelConnection).filter(ChannelConnection.organization_id==p.org.id,ChannelConnection.mode=='live',ChannelConnection.status!='disconnected').count() >= MAX_CHANNELS[p.org.plan]:
        raise HTTPException(402,'Лимит подключённых каналов текущего тарифа')
    if not os.getenv('INTEGRATION_ENCRYPTION_KEY'):raise HTTPException(503,'Шифрование интеграций не настроено')
    credentials={'access_token':payload.access_token,'webhook_secret':secrets.token_urlsafe(32)}
    if payload.provider=='vk':
        if not payload.group_id or not payload.confirmation_token:raise HTTPException(422,'Нужны ID сообщества и код подтверждения Callback API')
        credentials.update(group_id=payload.group_id,confirmation_token=payload.confirmation_token)
    try:verified=await adapter_for(payload.provider).validate_credentials(credentials)
    except AdapterError as exc:raise HTTPException(422,str(exc))
    duplicate=db.query(ChannelConnection).filter_by(provider=payload.provider,external_account_id=verified['id'],mode='live').filter(ChannelConnection.status!='disconnected').first()
    if duplicate:raise HTTPException(409,'Этот бот или сообщество уже привязаны к другой компании')
    ch=ChannelConnection(organization_id=p.org.id,provider=payload.provider,name=verified['name'],external_account_id=verified['id'],mode='live',status='pending_webhook',encrypted_credentials=seal(credentials),last_verified_at=now())
    db.add(ch);db.flush();audit(db,p,'integration.bot_verified',ch.id,payload.provider);db.commit()
    base=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
    return {'id':ch.id,'status':ch.status,'name':ch.name,
        'webhook_url':f'{base}/api/webhooks/{payload.provider}/{ch.id}' if base.startswith('https://') else None,
        'webhook_secret':credentials['webhook_secret'] if payload.provider=='vk' else None,
        'message':'Личность бота подтверждена. Входящие и отправка требуют настройки и проверки HTTPS webhook.'}

@api.post('/integrations/{channel_id}/activate-webhook')
async def activate_bot_webhook(channel_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    ch=db.query(ChannelConnection).filter_by(id=channel_id,organization_id=p.org.id,mode='live').first()
    if not ch:raise HTTPException(404,'Канал не найден')
    if ch.provider not in ('telegram','max','vk','instagram','whatsapp','messenger'):raise HTTPException(422,'Для этого канала предусмотрена другая настройка')
    base=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
    if not base.startswith('https://'):raise HTTPException(503,'Сначала настройте HTTPS PUBLIC_BASE_URL на сервере')
    url=f'{base}/api/webhooks/{ch.provider}/{ch.id}'
    if ch.provider=='messenger':
        creds=unseal(ch.encrypted_credentials)
        try:
            result=await call('POST',f'https://graph.facebook.com/{GRAPH_VERSION}/{quote(ch.external_account_id)}/subscribed_apps',
                headers={'Authorization':f"Bearer {creds['access_token']}"},params={'subscribed_fields':'messages,messaging_postbacks'})
            if result.get('success') is not True:raise AdapterError('Facebook не подтвердил подписку страницы')
        except AdapterError as exc:raise HTTPException(502,str(exc)) from exc
        ch.webhook_registered_at=now();ch.status='pending_webhook';ch.last_error=None
        audit(db,p,'integration.webhook_registered',ch.id,'messenger');db.commit()
        return {'status':ch.status,'message':'Подписка Facebook-страницы зарегистрирована. Проверьте входящий Messenger.'}
    if ch.provider=='instagram':
        creds=unseal(ch.encrypted_credentials)
        try:
            result=await call('POST',f'https://graph.instagram.com/{GRAPH_VERSION}/me/subscribed_apps',
                headers={'Authorization':f"Bearer {creds['access_token']}"},params={'subscribed_fields':'messages'})
            if result.get('success') is not True:raise AdapterError('Instagram не подтвердил подписку на сообщения')
        except AdapterError as exc:raise HTTPException(502,str(exc)) from exc
        ch.webhook_registered_at=now();ch.status='pending_webhook';ch.last_error=None
        audit(db,p,'integration.webhook_registered',ch.id,'instagram');db.commit()
        return {'status':ch.status,'message':'Подписка Instagram зарегистрирована. Убедитесь, что глобальный webhook Meta настроен, затем проверьте входящий Direct.'}
    if ch.provider=='whatsapp':
        creds=unseal(ch.encrypted_credentials)
        waba_id=creds.get('waba_id')
        if not waba_id:raise HTTPException(422,'Нет WABA ID для подписки. Подключите номер через Meta Embedded Signup или задайте WABA ID при ручном подключении.')
        try:
            result=await call('POST',f'https://graph.facebook.com/{GRAPH_VERSION}/{quote(str(waba_id))}/subscribed_apps',
                headers={'Authorization':f"Bearer {creds['access_token']}"})
            if result.get('success') is not True:raise AdapterError('Meta не подтвердила подписку WABA')
        except AdapterError as exc:raise HTTPException(502,str(exc)) from exc
        ch.webhook_registered_at=now();ch.status='pending_webhook';ch.last_error=None
        audit(db,p,'integration.webhook_registered',ch.id,'whatsapp');db.commit()
        return {'status':ch.status,'message':'Подписка WhatsApp Business зарегистрирована. Проверьте регистрацию номера и входящий webhook.'}
    if ch.provider=='vk':return {'status':ch.status,'webhook_url':url,'message':'Добавьте адрес, секрет и код подтверждения в Callback API сообщества VK. Активируется после проверенного события.'}
    credentials=unseal(ch.encrypted_credentials)
    try:
        if ch.provider=='telegram':
            result=await call('POST',f'https://api.telegram.org/bot{quote(credentials["access_token"],safe=":")}/setWebhook',json_data={'url':url,'secret_token':credentials['webhook_secret'],'allowed_updates':['message']})
            successful=bool(result.get('ok'))
        else:
            result=await call('POST','https://platform-api2.max.ru/subscriptions',headers={'Authorization':credentials['access_token']},json_data={'url':url,'update_types':['message_created','bot_started'],'secret':credentials['webhook_secret']})
            successful=bool(result.get('success'))
        if not successful:raise AdapterError('Провайдер не подтвердил подписку на webhook')
    except AdapterError as exc:raise HTTPException(502,str(exc))
    # The write API accepted registration; verify that provider actually lists our URL.
    # A failed check must NOT become a false success, but can be retried safely.
    ch.status='pending_webhook';ch.webhook_registered_at=now();ch.webhook_provider_verified_at=None
    try:
        remote=await remote_subscription(ch.provider,credentials,url)
        if remote['matches']:
            ch.webhook_provider_verified_at=now()
        else:
            ch.webhook_registered_at=None
            ch.last_error='Подписка не найдена у сервиса. Проверьте адрес HTTPS и повторите настройку.'
    except AdapterError:
        # Registration request succeeded, but read-back could not be established.
        ch.last_error='Сервис принял регистрацию, но повторная проверка подписки недоступна. Нажмите «Проверить подписку».'
    else:
        if ch.webhook_provider_verified_at:ch.last_error=None
    audit(db,p,'integration.webhook_registered',ch.id,ch.provider)
    db.commit()
    return {'status':'pending_webhook','webhook_url':url,'provider_webhook_verified':bool(ch.webhook_provider_verified_at),
            'message':('Webhook подтверждён самим сервисом. Теперь отправьте боту входящее сообщение.'
                       if ch.webhook_provider_verified_at else
                       'Сервис принял запрос регистрации. Подписка ещё не подтверждена: нажмите «Проверить подписку».')}

@api.post('/integrations/manual',status_code=201)
async def connect_manual(payload:ManualConnectionPayload,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if p.org.is_demo:raise HTTPException(403,'В демонстрационной организации реальные подключения отключены')
    if payload.provider!='whatsapp':raise HTTPException(422,'Ручное подключение предусмотрено только для WhatsApp Cloud API')
    if db.query(ChannelConnection).filter(ChannelConnection.organization_id==p.org.id,ChannelConnection.mode=='live',ChannelConnection.status!='disconnected').count()>=MAX_CHANNELS[p.org.plan]:raise HTTPException(402,'Лимит каналов текущего тарифа')
    credentials={'phone_number_id':payload.phone_number_id,'access_token':payload.access_token}
    if payload.waba_id:credentials['waba_id']=payload.waba_id
    try: verified=await adapter_for('whatsapp').validate_credentials(credentials)
    except AdapterError as exc:raise HTTPException(422,str(exc))
    # no duplicate phone ID across different tenants: webhook routing would become ambiguous
    duplicate=db.query(ChannelConnection).filter(ChannelConnection.provider=='whatsapp',ChannelConnection.external_account_id==verified['id'],ChannelConnection.mode=='live',ChannelConnection.status!='disconnected').first()
    if duplicate:raise HTTPException(409,'Этот WhatsApp номер уже подключён к рабочей области')
    ch=ChannelConnection(organization_id=p.org.id,provider='whatsapp',name=verified['name'],external_account_id=verified['id'],mode='live',status='pending_webhook',encrypted_credentials=seal(credentials),last_verified_at=now())
    db.add(ch);audit(db,p,'integration.account_verified',ch.id,'whatsapp');db.commit();return {'id':ch.id,'status':ch.status,'name':ch.name,'message':'Номер подтверждён официальным API, но приём сообщений ещё не проверен'}

@api.post('/integrations/oauth-start/{provider}')
def oauth_start(provider:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    if p.org.is_demo:raise HTTPException(403,'Нельзя подключать реальные аккаунты в деморежиме')
    if provider not in ('avito','instagram','messenger'):raise HTTPException(422,'Для этого канала OAuth недоступен')
    if db.query(ChannelConnection).filter(ChannelConnection.organization_id==p.org.id,ChannelConnection.mode=='live',ChannelConnection.status!='disconnected').count()>=MAX_CHANNELS[p.org.plan]:raise HTTPException(402,'Лимит каналов')
    base=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
    if not base.startswith('https://'):raise HTTPException(503,'Для внешнего OAuth укажите публичный HTTPS PUBLIC_BASE_URL')
    if not os.getenv('INTEGRATION_ENCRYPTION_KEY'):raise HTTPException(503,'Не настроено шифрование интеграций')
    if provider=='avito':
        cid=os.getenv('AVITO_CLIENT_ID');secret=os.getenv('AVITO_CLIENT_SECRET')
        if not cid or not secret or not base:raise HTTPException(503,'Avito OAuth ещё не настроен администратором платформы')
    elif provider=='instagram':
        cid=os.getenv('INSTAGRAM_APP_ID');secret=os.getenv('INSTAGRAM_APP_SECRET')
        if not cid or not secret or not base:raise HTTPException(503,'Instagram Login ещё не настроен администратором платформы')
    else:
        cid=os.getenv('FACEBOOK_APP_ID') or os.getenv('META_APP_ID')
        secret=os.getenv('FACEBOOK_APP_SECRET') or os.getenv('META_APP_SECRET')
        if not cid or not secret or not base:raise HTTPException(503,'Facebook Login for Business ещё не настроен')
    state=secrets.token_urlsafe(40)
    db.add(OAuthState(state_hash=digest(state),user_id=p.user.id,organization_id=p.org.id,provider=provider,expires_at=now()+600))
    db.commit()
    redirect=f'{base}/api/integrations/oauth-callback/{provider}'
    if provider=='avito':
        url='https://avito.ru/oauth?'+urlencode({'response_type':'code','pro_users_flow':'true','client_id':cid,'redirect_uri':redirect,'scope':os.getenv('AVITO_OAUTH_SCOPES','messenger:read,messenger:write'),'state':state})
    elif provider=='instagram':
        url='https://www.instagram.com/oauth/authorize?'+urlencode({'client_id':cid,'redirect_uri':redirect,'scope':'instagram_business_basic,instagram_business_manage_messages','response_type':'code','state':state})
    else:
        url=f'https://www.facebook.com/{GRAPH_VERSION}/dialog/oauth?'+urlencode({'client_id':cid,'redirect_uri':redirect,
           'scope':'pages_show_list,pages_messaging,pages_manage_metadata,pages_read_engagement','response_type':'code','state':state})
    return {'url':url}

@api.get('/integrations/oauth-callback/{provider}')
async def oauth_callback(provider:str,request:Request,code:str='',state:str='',error:str='',db:Session=Depends(get_db)):
    record=db.query(OAuthState).filter_by(state_hash=digest(state),provider=provider).first() if state else None
    if not record or record.expires_at<now():raise HTTPException(403,'OAuth state истёк или недействителен')
    session=session_from_request(request,db)
    if not session or session.user.id!=record.user_id or session.org.id!=record.organization_id:raise HTTPException(403,'OAuth сессия не совпадает с начавшим подключение сотрудником')
    db.delete(record);db.commit()
    if error or not code: return RedirectResponse('/?view=integrations&oauth=denied',303)
    base=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
    try:
        if provider=='avito':
            credentials=await call('POST','https://api.avito.ru/token',data={'grant_type':'authorization_code','client_id':os.getenv('AVITO_CLIENT_ID'),'client_secret':os.getenv('AVITO_CLIENT_SECRET'),'code':code,'redirect_uri':f'{base}/api/integrations/oauth-callback/avito'})
        elif provider=='messenger':
            cid=os.getenv('FACEBOOK_APP_ID') or os.getenv('META_APP_ID')
            secret=os.getenv('FACEBOOK_APP_SECRET') or os.getenv('META_APP_SECRET')
            info=await call('GET',f'https://graph.facebook.com/{GRAPH_VERSION}/oauth/access_token',
                params={'client_id':cid,'client_secret':secret,'redirect_uri':f'{base}/api/integrations/oauth-callback/messenger','code':code})
            user_token=info.get('access_token')
            if not user_token:raise AdapterError('Facebook не подтвердил авторизацию')
            page_data=await call('GET',f'https://graph.facebook.com/{GRAPH_VERSION}/me/accounts',
                headers={'Authorization':f'Bearer {user_token}'},params={'fields':'id,name,access_token,tasks','limit':100})
            pages=[{'id':str(i['id']),'name':str(i['name']),'access_token':str(i['access_token'])}
                 for i in (page_data.get('data') or []) if i.get('id') and i.get('access_token') and bool({'MESSAGING','MODERATE'}.intersection(i.get('tasks') or []))]
            if not pages:raise AdapterError('Facebook не вернул страницы с задачей MESSAGING или MODERATE')
            db.add(PendingChannelSelection(user_id=session.user.id,organization_id=session.org.id,provider='messenger',
                encrypted_payload=seal({'pages':pages}),expires_at=now()+900))
            audit(db,session,'integration.messenger_pages_authorized',None,str(len(pages)));db.commit()
            return RedirectResponse('/?view=integrations&oauth=pages',303)
        elif provider=='instagram':
            raw_token=await call('POST','https://api.instagram.com/oauth/access_token',data={'client_id':os.getenv('INSTAGRAM_APP_ID'),'client_secret':os.getenv('INSTAGRAM_APP_SECRET'),'grant_type':'authorization_code','redirect_uri':f'{base}/api/integrations/oauth-callback/instagram','code':code})
            long_token=await call('GET','https://graph.instagram.com/access_token',params={'grant_type':'ig_exchange_token','client_secret':os.getenv('INSTAGRAM_APP_SECRET'),'access_token':raw_token['access_token']})
            credentials={'access_token':long_token['access_token'],'expires_at':now()+int(long_token.get('expires_in',5184000))}
        else:raise AdapterError('Провайдер неизвестен')
        verified=await adapter_for(provider).validate_credentials(credentials)
        if db.query(ChannelConnection).filter(ChannelConnection.provider==provider,ChannelConnection.external_account_id==verified['id'],ChannelConnection.mode=='live',ChannelConnection.status!='disconnected').first():raise AdapterError('Аккаунт уже подключён к другой рабочей области')
        if provider=='avito':
            credentials['account_id']=verified['id']
            credentials['expires_at']=now()+int(credentials.get('expires_in',86400))
        # Instagram requires a per-account app subscription in addition to app-level
        # webhook configuration. Subscription is not evidence of message delivery.
        status='pending_sync' if provider=='avito' else 'pending_webhook'
        registered_at=None
        if provider=='instagram':
            result=await call('POST',f'https://graph.instagram.com/{GRAPH_VERSION}/me/subscribed_apps',
                headers={'Authorization':f"Bearer {credentials['access_token']}"},params={'subscribed_fields':'messages'})
            if result.get('success') is not True:raise AdapterError('Meta не подтвердила Instagram webhook subscription')
            registered_at=now()
        ch=ChannelConnection(organization_id=session.org.id,provider=provider,name=verified['name'],external_account_id=verified['id'],
            mode='live',status=status,encrypted_credentials=seal(credentials),last_verified_at=now(),
            webhook_registered_at=registered_at,token_expires_at=credentials.get('expires_at'))
        db.add(ch);audit(db,session,'integration.account_verified',ch.id,provider);db.commit()
    except AdapterError as exc:
        return RedirectResponse('/?view=integrations&oauth=failed',303)
    return RedirectResponse('/?view=integrations&oauth=connected',303)

@api.post('/integrations/{channel_id}/sync')
async def manual_sync(channel_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin','lead')
    ch=db.query(ChannelConnection).filter_by(id=channel_id,organization_id=p.org.id).first()
    if not ch:raise HTTPException(404,'Канал не найден')
    if ch.provider!='avito' or ch.mode!='live' or ch.status not in ('connected','pending_sync'):
        raise HTTPException(422,'Ручная синхронизация реализована только для официального API Авито')
    if ch.last_sync_at and now()-ch.last_sync_at<20:raise HTTPException(429,'Подождите перед повторной синхронизацией')
    from .synchronizers import sync_avito
    try:return await sync_avito(db,ch)
    except AdapterError as exc:
        db.rollback()
        ch=db.query(ChannelConnection).filter_by(id=channel_id,organization_id=p.org.id).first()
        ch.last_error=str(exc)[:200];db.commit()
        raise HTTPException(502,str(exc))

@api.post('/integrations/{channel_id}/disconnect')
async def disconnect(channel_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    ch=db.query(ChannelConnection).filter_by(id=channel_id,organization_id=p.org.id).first()
    if not ch:raise HTTPException(404,'Канал не найден')
    if ch.status=='disconnected':return {'ok':True,'message':'Канал уже отключён'}
    if ch.mode=='live' and ch.provider in ('telegram','max') and ch.encrypted_credentials:
        creds=unseal(ch.encrypted_credentials)
        base=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
        url=f'{base}/api/webhooks/{ch.provider}/{ch.id}' if base.startswith('https://') else None
        try:
            await revoke_bot_subscription(ch.provider,creds,url)
        except AdapterError as exc:
            # Do not discard credentials until provider confirms unsubscription.
            raise HTTPException(502,'Удалённая подписка не отключена: '+str(exc)) from exc
    ch.encrypted_credentials=None;ch.status='disconnected';ch.last_error=None
    ch.webhook_verified_at=None;ch.webhook_registered_at=None
    ch.webhook_provider_verified_at=None;ch.outbound_api_accepted_at=None
    audit(db,p,'integration.disconnected',ch.id);db.commit()
    requires_cleanup=ch.mode=='live' and ch.provider not in ('telegram','max')
    return {'ok':True,'remote_cleanup_required':requires_cleanup,
            'message':('Доступ OSMANX отключён локально. Отзовите разрешение приложения и подписки в кабинете площадки.'
                       if requires_cleanup else 'Канал и подписка на события отключены.')}

@api.get('/audit')
def audit_log(p=Depends(auth),db:Session=Depends(get_db)):
    require_role(p,'owner','admin')
    items=db.query(AuditLog).filter_by(organization_id=p.org.id).order_by(desc(AuditLog.created_at)).limit(100).all()
    return [{'action':a.action,'user_id':a.user_id,'entity_id':a.entity_id,'created_at':a.created_at,'detail':a.detail} for a in items]

@api.get('/plans')
def plans(p=Depends(auth)):
    return {'current':p.org.plan,'plans':[{'id':name,'employees':MAX_MEMBERS[name],'channels':MAX_CHANNELS[name],'analytics':name!='starter','automation':name in ('professional','enterprise')} for name in ['starter','business','professional','enterprise']],'billing':'not_connected','message':'Изменение тарифа пока требует ручного оформления. Платёжный провайдер не подключён.'}

@app.websocket('/api/ws')
async def websocket_inbox(ws:WebSocket):
    """Authenticated tenant-scoped near-real-time inbox invalidation (~2s DB checks)."""
    from urllib.parse import urlsplit
    from .auth import session_from_request
    expected=os.getenv('PUBLIC_BASE_URL','')
    origin=ws.headers.get('origin','')
    configured_origin=f'{urlsplit(expected).scheme}://{urlsplit(expected).netloc}' if expected else ''
    # Origin + cookies must both match; prevent cross-site WebSocket hijacking.
    host=ws.headers.get('host','')
    allowed_origins={configured_origin} if configured_origin else {f'http://{host}', f'https://{host}'}
    if not origin or origin not in allowed_origins:
        await ws.close(code=1008)
        return
    if store.SessionLocal is None:store.initialize()
    with store.SessionLocal() as db:
        principal=session_from_request(ws,db)
        if principal is None:
            await ws.close(code=1008)
            return
        org_id=principal.org.id
        user_id=principal.user.id
        role=principal.role
    await ws.accept()
    last_signature=None
    try:
        await ws.send_json({'event':'ready'})
        while True:
            with store.SessionLocal() as db:
                # Recheck live membership and valid session on each tick.
                principal=session_from_request(ws,db)
                if not principal or principal.org.id!=org_id:
                    await ws.close(code=1008)
                    return
                query=db.query(Conversation).filter_by(organization_id=org_id)
                if principal.role in ('operator','manager'):query=query.filter_by(assigned_user_id=user_id)
                rows=query.order_by(desc(Conversation.last_message_at)).limit(250).all()
                signature=hashlib.sha256(json.dumps([(c.id,c.version,c.unread_count,c.status,c.archived,c.assigned_user_id) for c in rows],sort_keys=True).encode()).hexdigest()
            if last_signature is not None and signature!=last_signature:
                await ws.send_json({'event':'inbox.changed'})
            last_signature=signature
            await asyncio.sleep(2)
    except (WebSocketDisconnect,RuntimeError,OSError):
        return

app.include_router(api)
from .extras import router as workspace_router
app.include_router(workspace_router)

# Meta webhooks deliberately placed outside authenticated browser API.
from .webhooks import router as webhooks_router
app.include_router(webhooks_router)
from .media import router as media_router
app.include_router(media_router)
from .website import router as website_router
app.include_router(website_router)
from .claim import router as claim_router
app.include_router(claim_router)
from .operations import router as operations_router
app.include_router(operations_router)
from .company_pause import router as company_pause_router
app.include_router(company_pause_router)
from .outbox_control import router as outbox_control_router
app.include_router(outbox_control_router)
from .dispatch_control import router as dispatch_control_router
app.include_router(dispatch_control_router)
from .command import router as command_router
app.include_router(command_router)
from .onboarding import router as onboarding_router
app.include_router(onboarding_router)
from .quickstart import router as quickstart_router
app.include_router(quickstart_router)
from .whatsapp_templates import router as whatsapp_templates_router
app.include_router(whatsapp_templates_router)

if ASSET_DIR.exists():
    app.mount('/assets',StaticFiles(directory=ASSET_DIR),name='assets')
    @app.get('/',include_in_schema=False)
    def index():
        if os.getenv('FRONTEND_MODE','legacy')=='modern':
            modern=ASSET_DIR/'modern'/'index.html'
            if not modern.is_file():
                # Fail closed: don't claim a React upgrade when dependencies could
                # not be downloaded, built and tested in this deployment.
                raise HTTPException(503,'React 19: сборка не подготовлена. Выполните npm ci и npm run build:modern')
            return FileResponse(modern,headers={'Cache-Control':'no-store'})
        return FileResponse(ASSET_DIR/'index.html')

    @app.get('/widget/{public_key}',include_in_schema=False)
    def widget_iframe(public_key:str, db:Session=Depends(get_db)):
        from .website import get_public_widget
        get_public_widget(db,public_key)
        return FileResponse(ASSET_DIR/'widget.html',media_type='text/html',headers={'Cache-Control':'no-store'})
