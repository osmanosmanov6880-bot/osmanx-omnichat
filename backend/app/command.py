"""Operator command center: deterministic triage, saved views and audited priority.

No customer content is transmitted to an LLM. A saved view is a validated filter
preset, never an executable query. Every row and mutation is tenant scoped.
"""
import json
import math
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import desc, or_, update
from sqlalchemy.orm import Session

from .auth import auth, audit, can_view, require_role
from .db import (get_db, Conversation, Message, Membership, User, Contact,
                 ChannelConnection, SavedInboxView, AuditLog, now)
from .services import as_conversation
from .delivery_truth import confirmed_response

router=APIRouter(prefix='/api',tags=['command-center'])
PRIORITIES={'urgent','high','normal','low'}
FILTER_FIELDS={'channel','status','priority','assigned','archived','sort'}
CHANNELS={'avito','instagram','whatsapp','website',''}
STATUSES={'new','in_progress','waiting','closed',''}
SORTS={'recent','priority','oldest',''}

class PriorityUpdate(BaseModel):
    priority:str
    expected_version:int=Field(ge=0)
    @field_validator('priority')
    @classmethod
    def check_priority(cls,value):
        if value not in PRIORITIES:raise ValueError('Неизвестный приоритет')
        return value

class ViewInput(BaseModel):
    name:str=Field(min_length=2,max_length=64)
    filters:dict[str,str | bool]=Field(default_factory=dict)
    shared:bool=False
    @field_validator('filters')
    @classmethod
    def validate_filters(cls,value):
        if not isinstance(value,dict) or set(value)-FILTER_FIELDS:
            raise ValueError('Разрешены только поддерживаемые фильтры')
        for key,entry in value.items():
            if key=='archived':
                if not isinstance(entry,bool):raise ValueError('Архив: только да или нет')
            elif not isinstance(entry,str) or len(entry)>64:
                raise ValueError('Некорректное значение фильтра')
            elif key=='channel' and entry not in CHANNELS:
                raise ValueError('Неизвестный канал')
            elif key=='status' and entry not in STATUSES:
                raise ValueError('Неизвестный статус')
            elif key=='priority' and entry not in PRIORITIES|{''}:
                raise ValueError('Неизвестный приоритет')
            elif key=='sort' and entry not in SORTS:
                raise ValueError('Неизвестная сортировка')
            elif key=='assigned' and entry and len(entry)!=36:
                raise ValueError('Некорректный идентификатор сотрудника')
        return value


def scoped(db,p,conversation_id):
    conv=db.query(Conversation).filter_by(id=conversation_id,organization_id=p.org.id).first()
    if not conv:raise HTTPException(404,'Диалог не найден')
    if not can_view(p,conv):raise HTTPException(403,'У вас нет доступа к диалогу')
    return conv


def view_payload(row):
    return {'id':row.id,'name':row.name,'filters':json.loads(row.filters_json),
            'shared':row.shared,'is_owner':False,'created_at':row.created_at,
            'creator_user_id':row.creator_user_id}

@router.get('/views')
def list_views(p=Depends(auth),db:Session=Depends(get_db)):
    query=db.query(SavedInboxView).filter_by(organization_id=p.org.id).filter(
        or_(SavedInboxView.creator_user_id==p.user.id,SavedInboxView.shared.is_(True)))
    data=[]
    for item in query.order_by(desc(SavedInboxView.created_at)).limit(100).all():
        result=view_payload(item);result['is_owner']=item.creator_user_id==p.user.id
        data.append(result)
    return data

@router.post('/views',status_code=201)
def create_view(payload:ViewInput,p=Depends(auth),db:Session=Depends(get_db)):
    name=payload.name.strip()
    if len(name)<2:raise HTTPException(422,'Название слишком короткое')
    if payload.shared and p.role not in ('owner','admin','lead'):
        raise HTTPException(403,'Публиковать представления для команды может руководитель')
    count=db.query(SavedInboxView).filter_by(organization_id=p.org.id,creator_user_id=p.user.id).count()
    if count>=20:raise HTTPException(409,'Достигнут лимит 20 представлений')
    if db.query(SavedInboxView).filter_by(organization_id=p.org.id,creator_user_id=p.user.id,name=name).first():
        raise HTTPException(409,'Представление с таким названием уже существует')
    # A filter may reference only a real employee belonging to the same workspace.
    if payload.filters.get('assigned'):
        if p.role in ('manager','operator') and payload.filters['assigned']!=p.user.id:
            raise HTTPException(403,'Нельзя открыть диалоги другого сотрудника')
        member=db.query(Membership).filter_by(organization_id=p.org.id,user_id=payload.filters['assigned'],active=True).first()
        if not member:raise HTTPException(422,'Сотрудник не принадлежит компании')
    row=SavedInboxView(organization_id=p.org.id,creator_user_id=p.user.id,name=name,
                      filters_json=json.dumps(payload.filters,ensure_ascii=False,sort_keys=True),shared=payload.shared)
    db.add(row);db.flush();audit(db,p,'inbox.view_created',row.id,name);db.commit()
    result=view_payload(row);result['is_owner']=True
    return result

@router.delete('/views/{view_id}')
def delete_view(view_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    row=db.query(SavedInboxView).filter_by(organization_id=p.org.id,id=view_id).first()
    if not row:raise HTTPException(404,'Представление не найдено')
    if row.creator_user_id!=p.user.id and p.role not in ('owner','admin'):
        raise HTTPException(403,'Недостаточно прав на удаление')
    audit(db,p,'inbox.view_deleted',row.id,row.name);db.delete(row);db.commit()
    return {'ok':True}

@router.patch('/conversations/{conversation_id}/priority')
def set_priority(conversation_id:str,payload:PriorityUpdate,p=Depends(auth),db:Session=Depends(get_db)):
    scoped(db,p,conversation_id)
    result=db.execute(update(Conversation).where(Conversation.id==conversation_id,
        Conversation.organization_id==p.org.id,Conversation.version==payload.expected_version
        ).values(priority=payload.priority,version=Conversation.version+1))
    if result.rowcount!=1:
        db.rollback();raise HTTPException(409,'Диалог изменён другим сотрудником. Обновите переписку.')
    audit(db,p,'conversation.priority',conversation_id,payload.priority)
    db.commit()
    return as_conversation(db,scoped(db,p,conversation_id))

@router.get('/conversations/{conversation_id}/activity')
def get_activity(conversation_id:str,limit:int=Query(30,ge=1,le=100),p=Depends(auth),db:Session=Depends(get_db)):
    scoped(db,p,conversation_id)
    items=db.query(AuditLog).filter_by(organization_id=p.org.id,entity_id=conversation_id).order_by(desc(AuditLog.created_at)).limit(limit).all()
    # Audit content is for employees only; show human-read events and omit secrets.
    labels={'message.reply':'Отправлен ответ','conversation.status':'Изменён статус',
        'conversation.assign':'Назначен ответственный','conversation.pin':'Закреплён диалог',
        'conversation.priority':'Изменён приоритет','conversation.claimed':'Сотрудник занял диалог',
        'conversation.released':'Сотрудник освободил диалог','note.created':'Добавлена внутренняя заметка',
        'conversation.read':'Прочитаны сообщения','conversation.unread':'Помечено непрочитанным',
        'conversation.archived':'Диалог отправлен в архив'}
    users={u.id:u.name for u in db.query(User).filter(User.id.in_([x.user_id for x in items if x.user_id])).all()}
    return [{'id':x.id,'title':labels.get(x.action,'Действие сотрудника'),
             'actor':users.get(x.user_id,'Система'),'detail':x.detail if x.action in ('conversation.priority','conversation.status') else None,
             'created_at':x.created_at} for x in items]


def _pending_reply(db,org_id,conv):
    if not conv.last_inbound_at:return False
    # The most recent client message must be followed by an outgoing response.
    exists=db.query(Message.id).filter(Message.organization_id==org_id,
        Message.conversation_id==conv.id,Message.direction=='out',
        Message.created_at>=conv.last_inbound_at).first()
    return exists is None


def urgency(conv,unanswered,sla_seconds,current):
    """A deterministic and explainable priority score, not an AI inference."""
    score={'urgent':65,'high':35,'normal':12,'low':0}.get(conv.priority,12)
    reasons=[]
    if conv.priority=='urgent':reasons.append('Помечено как срочное')
    elif conv.priority=='high':reasons.append('Высокий приоритет')
    if unanswered:
        elapsed=max(0,current-(conv.last_inbound_at or current))
        if elapsed>sla_seconds:
            score+=35+min(25,int((elapsed-sla_seconds)/60)//5)
            reasons.append('Срок ответа превышен')
        else:
            score+=12
            reasons.append('Клиент ждёт ответа')
    if conv.unread_count>0:
        score+=min(15,conv.unread_count*5)
        reasons.append('Есть непрочитанные')
    if not conv.assigned_user_id:
        score+=10;reasons.append('Нет ответственного')
    return score,reasons

@router.get('/command-center')
def command_center(p=Depends(auth),db:Session=Depends(get_db)):
    """Attention queue, workload and SLA, scoped to the viewer's allowed conversations.

    Deliberately limit work on a single request to the 500 most recent open
    conversations. Counts carry explicit 'scope' and are not presented as totals.
    """
    query=db.query(Conversation).filter(Conversation.organization_id==p.org.id,
                                          Conversation.archived.is_(False),Conversation.status!='closed')
    if p.role in ('operator','manager'):
        query=query.filter(Conversation.assigned_user_id==p.user.id)
    live=query.order_by(desc(Conversation.last_message_at)).limit(500).all()
    current=now();sla_seconds=p.org.sla_minutes*60
    prioritized=[];by_channel=Counter();workload=Counter();unread=0;overdue=0;waiting=0;unassigned=0
    channel_ids=list({c.channel_id for c in live})
    channel_lookup={c.id:c.provider for c in db.query(ChannelConnection).filter(ChannelConnection.id.in_(channel_ids),ChannelConnection.organization_id==p.org.id).all()} if channel_ids else {}
    # Fetch the last outgoing timestamp per conversation in one query, not one query per conversation.
    from sqlalchemy import func
    out_rows=db.query(Message.conversation_id,func.max(Message.created_at)).filter(
        Message.organization_id==p.org.id,confirmed_response(),Message.conversation_id.in_([c.id for c in live])
    ).group_by(Message.conversation_id).all() if live else []
    replied={cid:ts for cid,ts in out_rows}
    for conv in live:
        has_unanswered=bool(conv.last_inbound_at and replied.get(conv.id,0)<conv.last_inbound_at)
        score,reasons=urgency(conv,has_unanswered,sla_seconds,current)
        waiting+=int(has_unanswered)
        overdue+=int(has_unanswered and current-conv.last_inbound_at>sla_seconds)
        unread+=int(conv.unread_count>0)
        unassigned+=int(conv.assigned_user_id is None)
        workload[conv.assigned_user_id or 'unassigned']+=1
        by_channel[channel_lookup.get(conv.channel_id,'unknown')]+=1
        if has_unanswered or conv.priority in ('urgent','high') or conv.unread_count:
            prioritized.append((score,conv.last_message_at,conv,reasons,
                                int((current-conv.last_inbound_at)/60) if has_unanswered else 0))
    prioritized.sort(key=lambda x:(-x[0],-x[1]))
    top_rows=prioritized[:25]
    # Serialize only the selected candidates, not every conversation in the queue:
    # a busy organization should not trigger hundreds of N+1 read queries.
    prioritized=[]
    for score,_,conv,reasons,minutes in top_rows:
        item=as_conversation(db,conv)
        item.update(score=score,reasons=reasons,minutes_waiting=minutes)
        prioritized.append(item)
    members=db.query(Membership).filter_by(organization_id=p.org.id,active=True).all() if p.role in ('owner','admin','lead') else []
    team=[{'id':m.user_id,'name':db.get(User,m.user_id).name,'active':m.available,
           'open':workload.get(m.user_id,0),'role':m.role} for m in members]
    return {'scope':'latest_500_open_conversations','total_open':len(live),'overdue':overdue,'waiting':waiting,
            'unread':unread,'unassigned':unassigned,'sla_minutes':p.org.sla_minutes,
            'priority_queue':prioritized[:25],'workload':team,
            'channels':dict(by_channel),'is_demo':p.org.is_demo,'refreshed_at':current}
