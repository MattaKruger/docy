from typing import List

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from docy.models.chat import (
    Chat, ChatCreate, ChatRead, ChatReadWithMessages,
    Message, MessageCreate, MessageRead
)
from docy.db.session import get_session

router = APIRouter(prefix="/chat", tags=["chat"])

# == Chat Endpoints ==

@router.post("/chats/", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
async def create_chat(
    *,
    session: AsyncSession = Depends(get_session),
    chat_in: ChatCreate
) -> Chat:
    """
    Create a new chat.
    """
    # Create a Chat instance from the input schema
    db_chat = Chat.from_orm(chat_in)
    session.add(db_chat)
    await session.commit()
    await session.refresh(db_chat)
    return db_chat

@router.get("/chats/", response_model=List[ChatRead])
async def read_chats(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200)
) -> List[Chat]:
    """
    Retrieve a list of chats with pagination.
    """
    statement = select(Chat).offset(skip).limit(limit).order_by(Chat.id)
    result = await session.execute(statement)
    chats = list(result.scalars().all())
    return chats

@router.get("/chats/{chat_id}", response_model=ChatReadWithMessages)
async def read_chat(
    *,
    session: AsyncSession = Depends(get_session),
    chat_id: int
) -> Chat:
    """
    Retrieve a specific chat by ID, including its messages.
    """
    # Use selectinload to efficiently load related messages in the same query
    statement = select(Chat).where(Chat.id == chat_id).options(selectinload(Chat.messages))
    result = await session.execute(statement)
    db_chat = result.scalars().one_or_none() # Use one_or_none() for clarity

    if db_chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return db_chat

# == Message Endpoints ==

@router.post("/chats/{chat_id}/messages/", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def create_message_for_chat(
    *,
    session: AsyncSession = Depends(get_session),
    chat_id: int,
    message_in: MessageCreate # Note: message_in doesn't need chat_id here
) -> Message:
    """
    Create a new message within a specific chat.
    """
    # Optional: Check if chat exists first (good practice)
    chat = await session.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat with id {chat_id} not found")

    db_message = Message.from_orm(message_in, update={'chat_id': chat_id})

    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)
    return db_message

@router.get("/chats/{chat_id}/messages/", response_model=List[MessageRead])
async def read_messages_for_chat(
    *,
    session: AsyncSession = Depends(get_session),
    chat_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500) # Allow fetching more messages
) -> List[Message]:
    """
    Retrieve messages for a specific chat with pagination.
    """
    # Optional: Check if chat exists first
    chat = await session.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat with id {chat_id} not found")

    statement = (
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at) # Order messages chronologically
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(statement)
    messages = list(result.scalars().all())
    return messages
