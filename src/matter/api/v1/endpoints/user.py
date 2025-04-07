from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from matter.db import get_session
from matter.schemas import UserIn, UserOut
from matter.repositories import UserRepository
from matter.schemas.user import UserProjects


router = APIRouter(prefix="/user", tags=["user"])


def get_user_repo(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)


@router.get("/", response_model=List[UserOut])
async def get_users(user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.get_multi()


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.get(user_id)


@router.post("/", response_model=UserOut)
async def create_user(user: UserIn, user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.create(user)
