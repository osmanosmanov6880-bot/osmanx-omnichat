"""Atomic short-lived conversation ownership leases for team coordination."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import or_, update
from sqlalchemy.orm import Session
from .db import get_db, Conversation, now
from .auth import auth, can_view, audit
from .services import as_conversation

router = APIRouter(prefix='/api', tags=['collaboration'])

class LeaseRequest(BaseModel):
    seconds: int = Field(default=120, ge=30, le=600)


def scoped_conversation(db, principal, conv_id):
    conv=db.query(Conversation).filter_by(id=conv_id,organization_id=principal.org.id).first()
    if not conv:raise HTTPException(404,'Conversation not found')
    if not can_view(principal,conv):raise HTTPException(403,'Conversation not assigned to you')
    return conv


@router.post('/conversations/{conv_id}/claim')
def claim_conversation(conv_id:str,payload:LeaseRequest,p=Depends(auth),db:Session=Depends(get_db)):
    scoped_conversation(db,p,conv_id)
    expiry=now()+payload.seconds
    result=db.execute(update(Conversation).where(
        Conversation.id==conv_id,Conversation.organization_id==p.org.id,
        or_(Conversation.reply_lock_owner_id.is_(None),
            Conversation.reply_lock_expires_at.is_(None),
            Conversation.reply_lock_expires_at<=now(),
            Conversation.reply_lock_owner_id==p.user.id)
    ).values(reply_lock_owner_id=p.user.id,reply_lock_expires_at=expiry,
             version=Conversation.version+1))
    if not result.rowcount:
        db.rollback();raise HTTPException(409,'Another teammate is responding to this conversation')
    audit(db,p,'conversation.claimed',conv_id)
    db.commit()
    return as_conversation(db,scoped_conversation(db,p,conv_id))


@router.post('/conversations/{conv_id}/release')
def release_conversation(conv_id:str,p=Depends(auth),db:Session=Depends(get_db)):
    scoped_conversation(db,p,conv_id)
    result=db.execute(update(Conversation).where(
        Conversation.id==conv_id,Conversation.organization_id==p.org.id,
        Conversation.reply_lock_owner_id==p.user.id
    ).values(reply_lock_owner_id=None,reply_lock_expires_at=None,version=Conversation.version+1))
    if not result.rowcount:
        db.rollback();raise HTTPException(409,'You do not own this reply lock')
    audit(db,p,'conversation.released',conv_id)
    db.commit()
    return as_conversation(db,scoped_conversation(db,p,conv_id))
