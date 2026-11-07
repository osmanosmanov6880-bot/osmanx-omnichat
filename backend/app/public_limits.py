"""Cross-worker, database-enforced quota for unauthenticated entrypoints.

Fixed windows are an abuse barrier, not a financial metering service. The
source address is the ASGI client address (not an attacker-controlled header).
If a reverse proxy is deployed, configure its trusted proxy headers correctly.
"""
import hashlib
import hmac
import os
import ipaddress
from fastapi import HTTPException, Request
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from .db import PublicRateBucket, now


def verified_client_ip(request: Request):
    """Reject arbitrary X-Forwarded-For headers unless peer is trusted.

    Walk from the ingress proxy toward the visitor, selecting the nearest
    untrusted hop. This prevents an attacker from supplying a forged first hop
    to skip shared abuse limits. Configure the trusted proxy CIDRs explicitly;
    Uvicorn should run with --no-proxy-headers to preserve the real peer.
    """
    remote = request.client.host if request.client else 'unknown'
    try:
        remote_ip = ipaddress.ip_address(remote)
    except ValueError:
        return remote
    trusted = []
    for cidr in os.getenv('TRUSTED_PROXY_CIDRS', '').split(','):
        if not cidr.strip():continue
        try:trusted.append(ipaddress.ip_network(cidr.strip(), strict=False))
        except ValueError:raise RuntimeError('Invalid TRUSTED_PROXY_CIDRS configuration')
    if not any(remote_ip in cidr for cidr in trusted):
        return str(remote_ip)
    forwarded = request.headers.get('x-forwarded-for','')
    if len(forwarded)>512:return str(remote_ip)
    parts=[p.strip() for p in forwarded.split(',') if p.strip()]
    if not parts or len(parts)>12:return str(remote_ip)
    for part in reversed(parts):
        try:hop=ipaddress.ip_address(part)
        except ValueError:return str(remote_ip)
        if not any(hop in cidr for cidr in trusted):return str(hop)
    # A forged chain containing only trusted proxies is not a useful identity.
    return str(remote_ip)


def enforce_public_limit(db, request: Request, scope: str, *, limit: int, period: int):
    if not scope or len(scope) > 60 or period < 1 or limit < 1:
        raise ValueError('Invalid server-side limit configuration')
    address = verified_client_ip(request)
    key = os.getenv('PUBLIC_RATE_LIMIT_SECRET') or os.getenv('INTEGRATION_ENCRYPTION_KEY')
    # APP_ENV=production already requires the integration key at startup.
    if not key and os.getenv('APP_ENV') == 'production':
        raise RuntimeError('PUBLIC_RATE_LIMIT_SECRET or INTEGRATION_ENCRYPTION_KEY required')
    identity = hmac.new((key or 'local-development-only').encode(),
                        (scope + ':' + address).encode(), hashlib.sha256).hexdigest()
    epoch = int(now() // period) * period
    dialect = db.get_bind().dialect.name
    if dialect == 'sqlite':
        insert = sqlite_insert(PublicRateBucket)
    elif dialect == 'postgresql':
        insert = pg_insert(PublicRateBucket)
    else:
        raise RuntimeError('Public rate buckets require PostgreSQL or SQLite')
    stmt = insert.values(scope=scope, actor_digest=identity, window_start=epoch,
                         attempts=1, created_at=now())
    stmt = stmt.on_conflict_do_update(
        index_elements=['scope','actor_digest','window_start'],
        set_={'attempts':PublicRateBucket.attempts + 1}
    ).returning(PublicRateBucket.attempts)
    # The increment is atomic across connections and server workers.
    count = db.execute(stmt).scalar_one()
    db.commit()
    if count > limit:
        retry_after = max(1, epoch + period - int(now()))
        raise HTTPException(status_code=429, detail='Слишком много запросов. Повторите немного позже.',
                            headers={'Retry-After':str(retry_after)})
    return count
