"""Secure on-demand proxy for WhatsApp media referenced by official webhook media ID."""
from urllib.parse import urlsplit, quote
import httpx
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from .db import get_db, Message, Conversation, ChannelConnection
from .auth import auth, can_view
from .integrations.adapters import unseal, GRAPH_VERSION, AdapterError

router=APIRouter(prefix='/api/media',tags=['media'])

@router.get('/{message_id}')
async def media(message_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    m=db.query(Message).filter_by(id=message_id,organization_id=p.org.id).first()
    if not m or not m.attachment:raise HTTPException(404,'Вложение не найдено')
    c=db.query(Conversation).filter_by(id=m.conversation_id,organization_id=p.org.id).first()
    if not c or not can_view(p,c):raise HTTPException(403,'Доступ запрещён')
    ch=db.query(ChannelConnection).filter_by(id=c.channel_id,organization_id=p.org.id).first()
    import json
    attachment=json.loads(m.attachment)
    if not ch or ch.provider!='whatsapp' or ch.mode!='live' or attachment.get('provider')!='whatsapp':
        raise HTTPException(422,'Это вложение не поддерживает защищённую загрузку')
    mid=attachment.get('media_id','')
    if not mid or not mid.isdigit():raise HTTPException(422,'Некорректный идентификатор медиа')
    try: token=unseal(ch.encrypted_credentials)['access_token']
    except (AdapterError,KeyError):raise HTTPException(503,'Вложение недоступно: подключение истекло')
    headers={'Authorization':f'Bearer {token}'}
    async with httpx.AsyncClient(timeout=15,follow_redirects=False) as client:
        try:
            details=await client.get(f'https://graph.facebook.com/{GRAPH_VERSION}/{quote(mid)}',headers=headers)
            details.raise_for_status()
            media_url=details.json().get('url','')
            parsed=urlsplit(media_url)
            host=(parsed.hostname or '').lower()
            # Whitelist Meta-controlled media hosts, forbid arbitrary URLs and SSRF.
            if parsed.scheme!='https' or host not in ('lookaside.fbsbx.com',) and not host.endswith('.fbcdn.net'):
                raise HTTPException(502,'Провайдер вернул неизвестный домен для вложения')
            async with client.stream('GET',media_url,headers=headers) as item:
                item.raise_for_status()
                mime=item.headers.get('content-type','application/octet-stream').split(';')[0].lower()
                allowed=('image/jpeg','image/png','image/webp','image/gif','application/pdf',
                    'audio/ogg','audio/mpeg','audio/mp4','video/mp4')
                if mime not in allowed:raise HTTPException(415,'Формат вложения не поддерживается')
                if int(item.headers.get('content-length') or 0)>8*1024*1024:
                    raise HTTPException(413,'Файл превышает лимит 8 МБ')
                chunks=[];total=0
                async for chunk in item.aiter_bytes():
                    total+=len(chunk)
                    if total>8*1024*1024:raise HTTPException(413,'Файл превышает лимит 8 МБ')
                    chunks.append(chunk)
                return Response(content=b''.join(chunks),media_type=mime,headers={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'})
        except (httpx.HTTPError,ValueError) as exc:
            raise HTTPException(502,'Ошибка получения вложения у Meta') from exc
