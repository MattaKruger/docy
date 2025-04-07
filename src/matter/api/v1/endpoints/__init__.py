from .agent import router as agent_router
from .artifact import router as artifact_router
from .notes import router as notes_router
from .project import router as project_router
from .task import router as task_router
from .user import router as user_router
from .prompt import router as prompt_router

__all__ = [
    "user_router",
    "project_router",
    "artifact_router",
    "agent_router",
    "notes_router",
    "task_router",
    "prompt_router",
]
