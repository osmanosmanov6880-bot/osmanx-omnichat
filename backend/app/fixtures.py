"""Isolated demo organization per visitor. All records explicitly marked demo."""
import json
import random
from .db import Organization, User, Membership, ChannelConnection, Contact, Conversation, Message, Note, AutomationRule, now, uid
from .auth import make_password

SAMPLES = [
    ('avito', 'Александр Волков', 'Здравствуйте, машина ещё в продаже?', 'Здравствуйте! Да, автомобиль в наличии. Могу прислать подробности.', 'Отлично! А посмотреть сегодня можно?', 'interested', 1850000),
    ('instagram', 'Мария Белова', 'Добрый день! Сколько стоит консультация?', 'Здравствуйте, Мария! Первичная консультация — бесплатно.', 'Хочу записаться на завтра', 'negotiation', 20000),
    ('whatsapp', 'Тимур Ибрагимов', 'Заказ ещё можно оформить на сегодня?', 'Да, Тимур! Напишите удобное время доставки.', 'К 18:00 будет идеально', 'payment', 5200),
    ('avito', 'Елена Смирнова', 'Здравствуйте, есть доставка в другой город?', None, None, 'new', None),
    ('instagram', 'Амина Магомедова', 'Вижу ваше предложение. Хочу узнать детали.', 'Конечно! С удовольствием всё расскажем.', None, 'interested', None),
    ('telegram', 'Руслан Алиев', 'Спасибо большое, всё понравилось!', 'Будем рады видеть вас снова!', None, 'success', 8700),
    ('vk', 'Давид Орлов', 'Есть возможность небольшого торга?', None, None, 'new', None),
    ('messenger', 'Артём Петров', 'Здравствуйте! Можно уточнить условия доставки?', None, None, 'new', None),
    ('max', 'София Ким', 'Здравствуйте! Можно забронировать место?', 'Здравствуйте! На какую дату?', 'В эту субботу на двоих', 'negotiation', 3500),
]

def create_demo(db):
    short = uid()[:8]
    org = Organization(name='OSMANX · Демопространство', plan='professional', is_demo=True)
    owner = User(email=f'demo-{short}@example.invalid', name='Вы · Владелец', password_hash=make_password(uid()))
    teammate = User(email=f'operator-{short}@example.invalid', name='Анна · Оператор', password_hash=make_password(uid()))
    db.add_all([org, owner, teammate]); db.flush()
    db.add_all([Membership(organization_id=org.id, user_id=owner.id, role='owner'), Membership(organization_id=org.id, user_id=teammate.id, role='operator')])
    channels = {}
    for provider, name in [('avito','Авито · Демоканал'),('instagram','Instagram · Демоканал'),('whatsapp','WhatsApp · Демоканал'),('telegram','Telegram · Демобот'),('vk','ВКонтакте · Демосообщество'),('max','MAX · Демобот'),('messenger','Facebook Messenger · Демостраница')]:
        ch = ChannelConnection(organization_id=org.id, provider=provider, name=name, external_account_id=f'demo-{provider}-{short}', mode='demo', status='demo', last_sync_at=now())
        db.add(ch); db.flush(); channels[provider] = ch
    base = now()
    for idx, (provider, name, first, reply, follow, stage, amount) in enumerate(SAMPLES):
        c = Contact(organization_id=org.id, name=name, tags=json.dumps(['VIP'] if idx == 2 else ['Новый'] if idx in (3,6) else [], ensure_ascii=False), stage=stage, deal_amount=amount, deal_confirmed=(stage == 'success'), next_followup_at=base+86400 if idx==1 else None)
        db.add(c); db.flush()
        conv = Conversation(organization_id=org.id, channel_id=channels[provider].id, contact_id=c.id, external_chat_id=f'demo-chat-{short}-{idx}', external_recipient_id=f'demo-user-{idx}', status='waiting' if reply and follow else 'new' if not reply else 'in_progress', priority=('urgent' if idx==3 else 'high' if idx in (0,6) else 'normal'), assigned_user_id=teammate.id if idx==5 else owner.id, pinned=(idx==0), unread_count=1 if idx in (0,3,6) else 0, last_message_at=base-idx*2300, last_inbound_at=base-idx*2300, created_at=base-(idx+1)*7200)
        db.add(conv); db.flush()
        messages = [('in', first, base-idx*2300-1800)]
        if reply: messages.append(('out', reply, base-idx*2300-1600)); conv.first_reply_at=base-idx*2300-1600
        if follow: messages.append(('in', follow, base-idx*2300))
        conv.last_message_at=max(ts for direction,body,ts in messages)
        conv.last_inbound_at=max(ts for direction,body,ts in messages if direction=='in')
        for direction, body, timestamp in messages:
            db.add(Message(organization_id=org.id, conversation_id=conv.id, external_id=f'demo-msg-{short}-{idx}-{timestamp}', direction=direction, body=body, is_demo=True, created_at=timestamp, delivery_status='delivered', response_confirmed_at=(timestamp if direction=='out' else None)))
        if idx == 0: db.add(Note(organization_id=org.id, conversation_id=conv.id, author_user_id=owner.id, body='Клиент заинтересован в осмотре. Уточнить время встречи.'))
    db.add(AutomationRule(organization_id=org.id, name='Важные обращения', event='message_received', condition_type='contains', condition_value='срочно', action_type='tag', action_value='Срочно', enabled=True))
    db.commit()
    return org, owner
