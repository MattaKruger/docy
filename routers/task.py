from typing import List

from fastapi import APIRouter, Depends

from database import Session, get_session
from models import TaskIn, TaskOut
from repositories import TaskRepository

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_repo(session: Session = Depends(get_session)) -> TaskRepository:
    return TaskRepository(session)


@router.get("/", response_model=List[TaskOut])
async def get_all_tasks(task_repo: TaskRepository = Depends(get_task_repo)):
    return await task_repo.get_multi()


@router.post("/")
async def create(task: TaskIn, task_repo: TaskRepository = Depends(get_task_repo)):
    return await task_repo.create(task)
