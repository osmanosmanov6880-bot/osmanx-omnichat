"""Cookie session and RBAC helpers. All tenant-scoped lookups MUST filter org id."""
import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from .db import User, Membership, Organization, AuthSession, get_db, now

SESSION_COOKIE = 'omnichat_session'
CSRF_COOKIE = 'omnichat_csrf'
SESSION_SECONDS = 7 * 24 * 3600
ROLES = {'owner', 'admin', 'lead', 'manager', 'operator'}
MAX_MEMBERS = {'starter': 1, 'business': 10, 'professional': 100, 'enterprise': 99999}
MAX_CHANNELS = {'starter': 2, 'business': 5, 'professional': 30, 'enterprise': 99999}


def digest(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def login_attempt_identity(email):
    """Keyed, stable pseudonym for login-abuse receipts.

    Production already requires INTEGRATION_ENCRYPTION_KEY, so stolen database
    contents do not expose a plain dictionary hash of common email addresses.
    """
    normalized=email.strip().lower().encode('utf-8')
    secret=os.getenv('AUTH_RATE_LIMIT_SECRET') or os.getenv('INTEGRATION_ENCRYPTION_KEY')
    if secret:
        return hmac.new(secret.encode('utf-8'),normalized,hashlib.sha256).hexdigest()
    # Local-only fallback; production startup rejects a missing encryption key.
    return hashlib.sha256(normalized).hexdigest()

def make_password(password):
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return 'scrypt$' + salt.hex() + '$' + derived.hex()

def verify_password(password, stored):
    try:
        method, salt, hexdigest = stored.split('$')
        if method != 'scrypt': return False
        actual = hashlib.scrypt(password.encode('utf-8'), salt=bytes.fromhex(salt), n=2**14, r=8, p=1, dklen=32)
        return hmac.compare_digest(actual, bytes.fromhex(hexdigest))
    except (ValueError, TypeError):
        return False

@dataclass
class Principal:
    user: User
    org: Organization
    role: str
    session: AuthSession


def session_from_request(req: Request, db: Session):
    token = req.cookies.get(SESSION_COOKIE)
    if not token: return None
    s = db.get(AuthSession, digest(token))
    if not s or s.expires_at < now(): return None
    u = db.get(User, s.user_id)
    o = db.get(Organization, s.organization_id)
    m = db.query(Membership).filter_by(user_id=s.user_id, organization_id=s.organization_id, active=True).first()
    if not all([u, o, m]): return None
    return Principal(u, o, m.role, s)


def auth(req: Request, db: Session = Depends(get_db)):
    p = session_from_request(req, db)
    if not p: raise HTTPException(status_code=401, detail='Необходим вход в систему')
    if req.method not in ('GET', 'HEAD', 'OPTIONS'):
        header = req.headers.get('X-CSRF-Token', '')
        cookie = req.cookies.get(CSRF_COOKIE, '')
        if not header or not cookie or not hmac.compare_digest(header, cookie) or not hmac.compare_digest(digest(header), p.session.csrf_hash):
            raise HTTPException(status_code=403, detail='Проверка CSRF не пройдена')
    return p


def grant_session(response: Response, user: User, org: Organization, db: Session):
    token = secrets.token_urlsafe(48)
    csrf = secrets.token_urlsafe(32)
    s = AuthSession(id_hash=digest(token), csrf_hash=digest(csrf), user_id=user.id, organization_id=org.id, expires_at=now()+SESSION_SECONDS)
    db.add(s)
    db.commit()
    secure = os.getenv('COOKIE_SECURE', 'false').lower() == 'true'
    response.set_cookie(SESSION_COOKIE, token, httponly=True, secure=secure, samesite='lax', max_age=SESSION_SECONDS, path='/')
    response.set_cookie(CSRF_COOKIE, csrf, httponly=False, secure=secure, samesite='lax', max_age=SESSION_SECONDS, path='/')


def require_role(p, *roles):
    if p.role not in roles:
        raise HTTPException(status_code=403, detail='Недостаточно прав')


def can_view(p, conv):
    if conv.organization_id != p.org.id: return False
    if p.role in ('owner','admin','lead'): return True
    return conv.assigned_user_id == p.user.id


def can_manage(p, conv):
    return can_view(p, conv)


def audit(db, p, action, entity_id=None, detail=None):
    from .db import AuditLog
    db.add(AuditLog(organization_id=p.org.id, user_id=p.user.id, action=action, entity_id=entity_id, detail=detail))
