from fastapi import APIRouter

from .endpoints import (
    agent_router,
    artifact_router,
    chat_router,
    notes_router,
    project_router,
    prompt_router,
    task_router,
    user_router,
)

api_v1_router = APIRouter()

api_v1_router.include_router(agent_router)
api_v1_router.include_router(artifact_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(notes_router)
api_v1_router.include_router(project_router)
api_v1_router.include_router(prompt_router)
api_v1_router.include_router(task_router)
api_v1_router.include_router(user_router)


__all__ = ["api_v1_router"]
