from typing import List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio.session import AsyncSession

from docy.db import get_session
from docy.repositories import UserRepository
from docy.schemas import ProjectOut, UserIn, UserOut

router = APIRouter(prefix="/users", tags=["user"])


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


@router.get("/{user_id}/projects", response_model=List[ProjectOut])
async def get_user_projects(user_id: int = Path(...), user_repo: UserRepository = Depends(get_user_repo)):
    pass
    # return await user_repo.get_projects(user_id)
