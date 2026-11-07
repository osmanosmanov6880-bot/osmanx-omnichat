"""Small, evidence-based first-run checklist for owners of one company.

No user-controlled completion flags: every step is derived from tenant-scoped
records and distinguishes account setup from a verified incoming message.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .auth import auth, require_role
from .db import get_db, Membership, ChannelConnection, Conversation, Message

router = APIRouter(prefix='/api', tags=['Быстрый старт'])

@router.get('/quickstart')
def quickstart(p=Depends(auth), db: Session=Depends(get_db)):
    require_role(p, 'owner', 'admin')
    org_id = p.org.id
    channels = db.query(ChannelConnection).filter(
        ChannelConnection.organization_id == org_id,
        ChannelConnection.mode == 'live',
        ChannelConnection.status != 'disconnected'
    ).all()
    channel_count = len(channels)
    inbound_exists = db.query(Message.id).filter(
        Message.organization_id == org_id,
        Message.direction == 'in',
        Message.is_demo.is_(False)
    ).first() is not None
    outbound_exists = db.query(Message.id).filter(
        Message.organization_id == org_id,
        Message.direction == 'out',
        Message.is_demo.is_(False),
        Message.delivery_status.in_(('accepted', 'sent', 'delivered', 'read'))
    ).first() is not None
    team_count = db.query(Membership.id).filter(
        Membership.organization_id == org_id, Membership.active.is_(True)
    ).count()
    # Deliberately not count a saved token as a proven delivery path.
    ready_count = sum(1 for c in channels if c.webhook_verified_at is not None and c.outbound_api_accepted_at is not None)
    tasks = [
        {'key': 'channel', 'title': 'Добавьте канал общения',
         'description': 'Подключите разрешённый аккаунт или создайте чат для сайта.',
         'done': channel_count > 0, 'view': 'integrations'},
        {'key': 'incoming', 'title': 'Получите первое сообщение',
         'description': 'Напишите с другого устройства и убедитесь, что обращение появилось во «Входящих».',
         'done': inbound_exists, 'view': 'inbox'},
        {'key': 'reply', 'title': 'Проверьте первый ответ из OSMANX',
         'description': 'Напишите клиенту. Дождитесь принятия ответа площадкой, затем проверьте его у клиента.',
         'done': outbound_exists, 'view': 'inbox'}
    ]
    return {
        'organization': p.org.name,
        'is_demo': p.org.is_demo,
        'connected_accounts': channel_count,
        'provider_verified_routes': ready_count,
        'team_members': team_count,
        'tasks': tasks,
        'completed': sum(1 for task in tasks if task['done']),
        'total': len(tasks),
        'all_done': all(task['done'] for task in tasks),
        'team_is_optional': True,
        'note': 'Подтверждение приёма API не гарантирует прочтение сообщения клиентом. Проверьте ответ в самом сервисе.'
    }
