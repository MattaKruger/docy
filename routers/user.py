from typing import List
from fastapi import APIRouter, Depends
from database.db import get_session, Session
from models import User, UserIn, UserOut

from repositories import UserRepository


router = APIRouter(prefix="/user", tags=["user"])


def get_user_repo(session: Session = Depends(get_session)) -> UserRepository:
    return UserRepository(User, session)


@router.get("/", response_model=List[UserOut])
async def get_users(user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.get_multi()


@router.post("/", response_model=UserOut)
async def create_user(user: UserIn, user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.create(user)
