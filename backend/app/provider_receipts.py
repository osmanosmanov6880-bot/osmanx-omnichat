"""Durable, tenant-scoped WhatsApp delivery receipts (R24).

WhatsApp may send a signed status callback before the outbound API response is
persisted. Store only the provider message ID, status and a recipient digest;
then reconcile after *both* possible commits. No message body or phone is
stored in this queue and no unverified webhooks can use this code path.
"""
from __future__ import annotations

import hashlib
from sqlalchemy import and_, case, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from .db import ChannelConnection, Conversation, Message, ProviderDeliveryReceipt, now

_STATES = frozenset({'sent','delivered','read','failed'})


def _recipient_digest(channel_id: str, recipient_id: str | None) -> str | None:
    if not recipient_id:
        return None
    return hashlib.sha256(f'{channel_id}:{recipient_id}'.encode('utf-8')).hexdigest()


def _advancing_state(existing, incoming):
    """Atomic SQL transition (same semantics as advance_delivery_state).

    Receipt order cannot be trusted. 'read' is final, 'delivered' may become
    'read' but not 'failed' or 'sent'; 'failed' may be resolved by later success.
    """
    return case(
        (existing == 'read', 'read'),
        (incoming == 'read', 'read'),
        (existing == 'delivered', 'delivered'),
        (incoming == 'delivered', 'delivered'),
        (incoming == 'failed', 'failed'),
        (incoming == 'sent', 'sent'),
        else_=existing,
    )


def record_whatsapp_receipt(db, channel: ChannelConnection, message_id: str,
                            state: str, recipient_id: str | None = None) -> bool:
    """Atomic upsert, rejecting conflicting recipient identities, no commits."""
    if channel.provider != 'whatsapp' or state not in _STATES:
        return False
    if not isinstance(message_id,str) or not 1 <= len(message_id) <= 250:
        return False
    if recipient_id is not None and (not isinstance(recipient_id,str) or len(recipient_id)>250):
        return False
    digest=_recipient_digest(channel.id,recipient_id)
    values=dict(channel_id=channel.id, external_message_id=message_id,
                organization_id=channel.organization_id, status=state,
                recipient_digest=digest, first_seen_at=now(), last_seen_at=now())
    dialect=db.get_bind().dialect.name
    if dialect == 'postgresql':
        stmt=pg_insert(ProviderDeliveryReceipt).values(**values)
    elif dialect == 'sqlite':
        stmt=sqlite_insert(ProviderDeliveryReceipt).values(**values)
    else:
        raise RuntimeError('Provider receipts require SQLite or PostgreSQL')
    current=ProviderDeliveryReceipt
    excluded=stmt.excluded
    stmt=stmt.on_conflict_do_update(
        index_elements=['channel_id','external_message_id'],
        set_={
            'status':_advancing_state(current.status,excluded.status),
            'recipient_digest':func.coalesce(current.recipient_digest,excluded.recipient_digest),
            'last_seen_at':excluded.last_seen_at,
        },
        where=and_(current.organization_id==excluded.organization_id,
            or_(current.recipient_digest.is_(None),
                excluded.recipient_digest.is_(None),
                current.recipient_digest==excluded.recipient_digest)),
    )
    return db.execute(stmt).rowcount == 1


def reconcile_whatsapp_receipt(db, channel_id: str, external_message_id: str) -> bool:
    """Bring one message forward to the strongest recorded receipt.

    Only outbound messages in the *same* channel and organization qualify.
    If the provider ID unexpectedly matches multiple dialogs, fail closed.
    """
    receipt=db.get(ProviderDeliveryReceipt,(channel_id,external_message_id))
    if receipt is None:
        return False
    rows=db.execute(select(Message.id,Conversation.external_recipient_id,
                            Conversation.external_chat_id).join(Conversation,
                            Conversation.id==Message.conversation_id).where(
        Message.external_id==external_message_id,
        Message.direction=='out',
        Message.organization_id==receipt.organization_id,
        Conversation.organization_id==receipt.organization_id,
        Conversation.channel_id==channel_id,
    ).limit(2)).all()
    if len(rows) != 1:
        return False
    message_id,recipient_id,chat_id=rows[0]
    if receipt.recipient_digest:
        candidate=_recipient_digest(channel_id,recipient_id or chat_id)
        if candidate != receipt.recipient_digest:
            return False
    status=Message.delivery_status
    # Updating inside SQL makes overlapping webhook handlers safe even if one
    # read the previous status before the other committed.
    changed=db.execute(update(Message).where(
        Message.id==message_id,
        Message.organization_id==receipt.organization_id,
        Message.external_id==external_message_id,
        Message.direction=='out',
        # A manually cancelled local message is never a provider receipt.
        Message.delivery_status!='cancelled',
    ).values(delivery_status=_advancing_state(status,receipt.status),
              response_confirmed_at=(func.coalesce(Message.response_confirmed_at,now())
                  if receipt.status in ('sent','delivered','read')
                  else Message.response_confirmed_at))).rowcount
    return changed == 1
