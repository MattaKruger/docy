from typing import List, Optional

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio.session import AsyncSession

from docy.db import get_session
from docy.models import Chat
from docy.repositories import ChatRepository, MessageRepository
from docy.schemas.chat import ChatIn, ChatOut
from docy.schemas.message import MessageIn, MessageOut, MessageUpdate

router = APIRouter(prefix="/chats", tags=["chats"])


def get_chat_repo(session: AsyncSession = Depends(get_session)):
    return ChatRepository(session)


def get_message_repo(session: AsyncSession = Depends(get_session)):
    return MessageRepository(session)


@router.get("/", response_model=List[ChatOut])
async def get_chats(chat_repo: ChatRepository = Depends(get_chat_repo)):
    chats = await chat_repo.get_multi()
    return chats


@router.get("/{chat_id}", response_model=Optional[Chat])
async def get_chat_by_id(chat_id: int = Path(...), chat_repo: ChatRepository = Depends(get_chat_repo)):
    chat = await chat_repo.get(chat_id)
    return chat


@router.get("/{chat_id}/messages", response_model=Optional[List[MessageOut]])
async def get_messages_by_chat_id(chat_id: int = Path(...), chat_repo: ChatRepository = Depends(get_chat_repo)):
    messages = await chat_repo.get_messages_by_chat_id(chat_id)
    return messages


@router.get("/{chat_id}/messages/{message_type}", response_model=Optional[List[MessageOut]])
async def get_messages_by_message_type(
    chat_id: int = Path(...), message_type: str = Path(...), chat_repo: ChatRepository = Depends(get_chat_repo)
):
    messages = await chat_repo.get_messages_by_message_type(chat_id, message_type)
    return messages


@router.post(
    "/",
    response_model=ChatOut,
)
async def create_chat(chat_in: ChatIn, chat_repo: ChatRepository = Depends(get_chat_repo)):
    chat_db = await chat_repo.create(chat_in)
    return chat_db


@router.post("/{chat_id}/agent/{agent_id")
async def add_agent_to_chat(
    chat_id: int = Path(...),
    agent_id: int = Path(...),
    chat_repo: ChatRepository = Depends(get_chat_repo),
):
    pass


@router.post("/{chat_id}/message", response_model=MessageOut)
async def add_message_to_chat(
    message_in: MessageIn,
    chat_repo: ChatRepository = Depends(get_chat_repo),
    message_repo: MessageRepository = Depends(get_message_repo),
):
    message_db = await message_repo.create(message_in)
    return message_db


@router.put("/{chat_id}/message/{message_id}", response_model=MessageOut)
async def update_message(
    message_update: MessageUpdate,
    message_id: int = Path(...),
    chat_repo: ChatRepository = Depends(get_chat_repo),
    message_repo: MessageRepository = Depends(get_message_repo),
):
    message_db = await message_repo.get(message_id)
    if not message_db:
        return

    updated_message = await message_repo.update(message_update, message_db)
    return updated_message


@router.delete("/{chat_id}/message/{message_id}", response_model=MessageOut)
async def delete_message(
    message_id: int = Path(...),
    chat_repo: ChatRepository = Depends(get_chat_repo),
    message_repo: MessageRepository = Depends(get_message_repo),
):
    message_db = await message_repo.get(message_id)
    deleted_message = await message_repo.delete(message_db)
    return deleted_message
