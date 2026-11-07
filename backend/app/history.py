"""Bounded, tenant-scoped and assignment-safe message history.

The cursor references an actual message in this exact conversation. A secondary
UUID sort key keeps pages stable even when provider messages share timestamps.
The latest 120 messages load first; older history is fetched on demand.
"""
from fastapi import HTTPException
from sqlalchemy import and_, or_
from .db import Message
from .services import as_message

PAGE_SIZE=120


def message_history_page(db, *, organization_id, conversation_id, limit=PAGE_SIZE, before=None):
    if not 1 <= limit <= 200:
        raise HTTPException(422,'Размер страницы: от 1 до 200 сообщений')
    query=db.query(Message).filter(
        Message.organization_id==organization_id,
        Message.conversation_id==conversation_id)
    if before is not None:
        cursor=db.query(Message.id,Message.created_at).filter(
            Message.id==before,
            Message.organization_id==organization_id,
            Message.conversation_id==conversation_id).first()
        if not cursor:
            # An unauthorized conversation or another conversation's message
            # is never exposed through the cursor parameter.
            raise HTTPException(404,'Курсор истории не найден')
        query=query.filter(or_(Message.created_at<cursor.created_at,
            and_(Message.created_at==cursor.created_at,Message.id<cursor.id)))
    rows=query.order_by(Message.created_at.desc(),Message.id.desc()).limit(limit+1).all()
    has_older=len(rows)>limit
    selected=rows[:limit]
    messages=[as_message(m) for m in reversed(selected)]
    return {'messages':messages,'message_paging':{
        'has_older':has_older,
        'next_before':messages[0]['id'] if has_older and messages else None,
        'page_size':limit,
    }}
