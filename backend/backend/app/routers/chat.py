from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.core.security import allowed_roles
from app.database import get_db
from app.models.chat import ChatMessage, Conversation
from app.models.friendship import Friendship
from app.models.user import Usuario
from app.schemas.chat import ConversationCreate, MessageCreate

router = APIRouter(prefix="/chat", tags=["User Interaction"])
PRESENCE_TTL = timedelta(seconds=90)
DEFAULT_AVATAR_URL = "/default-avatar.svg"


def _normalized(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _is_online(user: Usuario) -> bool:
    last_seen = _normalized(user.last_seen_at)
    return last_seen is not None and datetime.now(timezone.utc) - last_seen <= PRESENCE_TTL


def _avatar_url(user: Usuario) -> str:
    return DEFAULT_AVATAR_URL if user.avatar_file_id is None else f"/api/users/{user.id}/avatar"


def _pair(first_id: int, second_id: int) -> tuple[int, int]:
    return (first_id, second_id) if first_id < second_id else (second_id, first_id)


def _are_friends(db: Session, first_id: int, second_id: int) -> bool:
    low_id, high_id = _pair(first_id, second_id)
    return (
        db.query(Friendship)
        .filter(Friendship.user_low_id == low_id, Friendship.user_high_id == high_id)
        .first()
        is not None
    )


def _user_payload(db: Session, viewer_id: int, user: Usuario) -> dict[str, object]:
    return {
        "id": user.id,
        "nome": user.nome,
        "sobrenome": user.sobrenome,
        "tipo_usuario": user.tipo_usuario,
        "avatar_url": _avatar_url(user),
        "online": _is_online(user) if _are_friends(db, viewer_id, user.id) else None,
        "active": bool(user.is_active),
    }


def _other_user_id(conversation: Conversation, own_id: int) -> int:
    return conversation.user_high_id if conversation.user_low_id == own_id else conversation.user_low_id


def _participant_conversation(db: Session, conversation_id: int, own_id: int) -> Conversation:
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            or_(Conversation.user_low_id == own_id, Conversation.user_high_id == own_id),
        )
        .first()
    )
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada.")
    return conversation


def _conversation_payload(db: Session, conversation: Conversation, own_id: int) -> dict[str, object]:
    other_id = _other_user_id(conversation, own_id)
    other = db.query(Usuario).filter(Usuario.id == other_id).first()
    if other is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participante não encontrado.")
    last_message = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.id.desc())
        .first()
    )
    return {
        "id": conversation.id,
        "participant": _user_payload(db, own_id, other),
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "last_message": None if last_message is None else {
            "id": last_message.id,
            "sender_id": last_message.sender_id,
            "content": last_message.content,
            "created_at": last_message.created_at,
        },
    }


def _message_payload(message: ChatMessage) -> dict[str, object]:
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "sender_id": message.sender_id,
        "content": message.content,
        "created_at": message.created_at,
        "event": "chat.message.created",
    }


@router.post("/conversations")
def create_or_get_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    identity=Depends(allowed_roles()),
):
    own_id = identity["id"]
    if payload.recipient_id == own_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Você não pode conversar consigo mesmo.")

    recipient = (
        db.query(Usuario)
        .filter(Usuario.id == payload.recipient_id, Usuario.is_active.is_(True))
        .first()
    )
    if recipient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    low_id, high_id = _pair(own_id, payload.recipient_id)
    conversation = (
        db.query(Conversation)
        .filter(Conversation.user_low_id == low_id, Conversation.user_high_id == high_id)
        .first()
    )
    created = False
    if conversation is None:
        conversation = Conversation(user_low_id=low_id, user_high_id=high_id)
        db.add(conversation)
        try:
            db.commit()
            db.refresh(conversation)
            created = True
        except IntegrityError:
            db.rollback()
            conversation = (
                db.query(Conversation)
                .filter(Conversation.user_low_id == low_id, Conversation.user_high_id == high_id)
                .one()
            )

    return success_response(
        data=_conversation_payload(db, conversation, own_id),
        message="Conversa criada com sucesso." if created else "Conversa retornada com sucesso.",
        status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@router.get("/conversations")
def list_conversations(
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    identity=Depends(allowed_roles()),
):
    own_id = identity["id"]
    query = db.query(Conversation).filter(
        or_(Conversation.user_low_id == own_id, Conversation.user_high_id == own_id)
    )
    total = query.count()
    conversations = (
        query.order_by(Conversation.updated_at.desc(), Conversation.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return success_response(
        data={
            "items": [_conversation_payload(db, item, own_id) for item in conversations],
            "total": total,
            "limit": limit,
            "offset": offset,
        },
        message="Conversas retornadas com sucesso.",
    )


@router.get("/conversations/{conversation_id}/messages")
def list_messages(
    conversation_id: int,
    before_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
    identity=Depends(allowed_roles()),
):
    conversation = _participant_conversation(db, conversation_id, identity["id"])
    query = db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation.id)
    if before_id is not None:
        query = query.filter(ChatMessage.id < before_id)

    rows = query.order_by(ChatMessage.id.desc()).limit(limit + 1).all()
    has_more = len(rows) > limit
    selected = rows[:limit]
    selected.reverse()
    next_before_id = selected[0].id if has_more and selected else None
    return success_response(
        data={
            "items": [_message_payload(item) for item in selected],
            "has_more": has_more,
            "next_before_id": next_before_id,
        },
        message="Mensagens retornadas com sucesso.",
    )


@router.post("/conversations/{conversation_id}/messages", status_code=status.HTTP_201_CREATED)
def send_message(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    identity=Depends(allowed_roles()),
):
    own_id = identity["id"]
    conversation = _participant_conversation(db, conversation_id, own_id)
    other_id = _other_user_id(conversation, own_id)
    recipient = db.query(Usuario).filter(Usuario.id == other_id).first()
    if recipient is None or not recipient.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="O outro participante não está disponível.")

    message = ChatMessage(
        conversation_id=conversation.id,
        sender_id=own_id,
        content=payload.content,
    )
    conversation.updated_at = datetime.now(timezone.utc)
    db.add(message)
    db.commit()
    db.refresh(message)
    return success_response(
        data=_message_payload(message),
        message="Mensagem enviada com sucesso.",
        status_code=status.HTTP_201_CREATED,
    )
