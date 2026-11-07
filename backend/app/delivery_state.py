"""One source of truth for message delivery receipts.

'accepted' confirms only the provider API response, never a customer's device.
Webhook receipts may be duplicated or arrive out of order. Do not downgrade a
confirmed delivery/read receipt because a late 'sent' event arrived.
"""

PROGRESS = {'queued': 0, 'processing': 1, 'accepted': 2, 'sent': 3,
            'delivered': 4, 'read': 5}
INBOUND_RECEIPTS = frozenset({'sent', 'delivered', 'read', 'failed'})


def advance_delivery_state(current: str, incoming: str) -> str:
    if incoming not in INBOUND_RECEIPTS:
        return current
    if incoming == 'failed':
        # A late failure must not overwrite an already-proven delivery/read.
        return current if current in ('delivered', 'read') else 'failed'
    if current == 'read':
        return current
    # An explicit newer success receipt may reconcile an earlier failure.
    if current in ('failed', 'uncertain'):
        return incoming
    return incoming if PROGRESS.get(incoming, -1) > PROGRESS.get(current, -1) else current
