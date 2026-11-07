"""R28: confirmed outbound response predicate shared by Inbox, SLA and Command Center.

An outgoing draft, queued job, timed-out POST, failed or cancelled delivery
is *not* a response for service-level reporting. A new provider API 2xx sets
response_confirmed_at; a website widget confirms only after browser display.
Legacy 'sent/delivered/read' statuses are usable status evidence, while older
'accepted' without a timestamp is intentionally treated as unverified.
"""
from sqlalchemy import and_, or_
from .db import Message

RESPONSE_STATES = ('accepted', 'sent', 'delivered', 'read')


def confirmed_response():
    return and_(
        Message.direction == 'out',
        or_(
            Message.delivery_status.in_(('sent', 'delivered', 'read')),
            and_(Message.delivery_status == 'accepted',
                 Message.response_confirmed_at.is_not(None)),
        ),
    )
