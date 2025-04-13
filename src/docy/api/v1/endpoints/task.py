from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status

from docy.db import AsyncSession, get_session
from docy.repositories import (
    AgentRepository,
    ProjectRepository,
    PromptRepository,
    TaskRepository,
)
from docy.schemas import AgentOut, MessageIn, MessageOut, TaskIn, TaskOut, TaskUpdate
from docy.services.exceptions import (
    AgentInactiveError,
    AgentNotFoundError,
    NoSuitableAgentFoundError,
    ServiceError,
    TaskAlreadyAssignedError,
    TaskNotAssignedError,
    TaskNotFoundError,
)
from docy.services.task import TaskAssignmentService


router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_prompt_repo(session: AsyncSession = Depends(get_session)) -> PromptRepository:
    return PromptRepository(session)


def get_agent_repo(
    session: AsyncSession = Depends(get_session),
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
) -> AgentRepository:
    return AgentRepository(session=session, prompt_repo=prompt_repo)


def get_project_repo(session: AsyncSession = Depends(get_session)) -> ProjectRepository:
    return ProjectRepository(session)


def get_task_repo(
    session: AsyncSession = Depends(get_session),
    project_repo: ProjectRepository = Depends(get_project_repo),
    agent_repo: AgentRepository = Depends(get_agent_repo),
) -> TaskRepository:
    return TaskRepository(session=session, project_repo=project_repo, agent_repo=agent_repo)


def get_task_assignment_service(
    agent_repo: AgentRepository = Depends(get_agent_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
) -> TaskAssignmentService:
    return TaskAssignmentService(agent_repo=agent_repo, task_repo=task_repo)


@router.post(
    "/{task_id}/message",
    summary="Add message to Task",
    response_model=MessageOut,
)
async def add_message_to_task(
    message_in: MessageIn,
    task_id: int = Path(...),
    task_repo: TaskRepository = Depends(get_task_repo),
):
    await task_repo.get_or_404(task_id)
    return await task_repo.add_task_message(task_id, message_in)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    response_model=int,
)
async def create_task(
    task_in: TaskIn,
    task_repo: TaskRepository = Depends(get_task_repo),
    project_repo: ProjectRepository = Depends(get_project_repo),
):
    """
    Creates a new task associated with a project.
    """
    if not task_in.project_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project ID not found")

    project_db = await project_repo.get(task_in.project_id)
    if not project_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {task_in.project_id} not found",
        )

    task_in.project_id = project_db.id
    task_db = await task_repo.create(task_in)
    if not task_db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task",
        )
    return task_db.id


@router.get(
    "/unassigned",
    summary="Get all unassigned tasks",
    response_model=List[TaskOut],
)
async def get_unassigned_tasks(
    project_id: int | None = None,
    service: TaskAssignmentService = Depends(get_task_assignment_service),
):
    """
    Retrieves a list of tasks that are not currently assigned to any agent.
    Can optionally filter by project ID.
    """
    tasks = await service.get_unassigned_tasks(project_id=project_id)
    return tasks


@router.get(
    "/",
    summary="Get all tasks with optional filters",
    response_model=List[TaskOut],
)
async def get_all_tasks(
    project_id: Optional[int] = None,
    agent_id: Optional[int] = None,
    task_repo: TaskRepository = Depends(get_task_repo),
):
    """
    Retrieves a list of all tasks.
    Can optionally filter by project_id and/or agent_id.
    """
    filters = {}
    if project_id is not None:
        filters["project_id"] = project_id
    if agent_id is not None:
        filters["agent_id"] = agent_id

    tasks = await task_repo.get_multi(**filters)

    return tasks


@router.get(
    "/{task_id}",
    summary="Get a specific task by ID",
    responses={404: {"description": "Task not found"}},
    response_model=TaskOut,
)
async def get_task(
    task_id: int,
    task_repo: TaskRepository = Depends(get_task_repo),
):
    """
    Retrieves details of a specific task by its ID.
    """
    task = await task_repo.get_or_404(task_id)
    return TaskOut.model_validate(**task.model_dump())


@router.patch(
    "/{task_id}",
    summary="Update a task",
    responses={404: {"description": "Task not found"}},
    response_model=TaskOut,
)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    task_repo: TaskRepository = Depends(get_task_repo),
):
    """
    Updates specific fields of an existing task.
    Note: Agent assignment is handled via dedicated endpoints.
    """
    task_db = await task_repo.get(task_id)

    if not task_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    updated_task = await task_repo.update(task_update, task_db)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task",
        )
    return updated_task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    responses={404: {"description": "Task not found"}},
)
async def delete_task(
    task_id: int,
    task_repo: TaskRepository = Depends(get_task_repo),
):
    """
    Deletes a specific task by its ID.
    """
    deleted_count = await task_repo.delete(id=task_id)
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found or already deleted",
        )


@router.post(
    "/{task_id}/assign/{agent_id}",
    summary="Assign a task to an agent",
    responses={
        404: {"description": "Task or Agent not found"},
        400: {"description": "Agent is inactive"},
        409: {"description": "Task already assigned to this agent"},
    },
    response_model=TaskOut,
)
async def assign_task_to_agent(
    task_id: int,
    agent_id: int,
    service: TaskAssignmentService = Depends(get_task_assignment_service),
):
    """
    Assigns a specific task to a specific active agent.
    """
    try:
        updated_task = await service.assign_task(task_id=task_id, agent_id=agent_id)
        return updated_task
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except AgentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except AgentInactiveError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except TaskAlreadyAssignedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}"
        ) from e


@router.post(
    "/{task_id}/unassign",
    summary="Unassign an agent from a task",
    responses={
        404: {"description": "Task not found"},
        400: {"description": "Task is not assigned"},
    },
    response_model=TaskOut,
)
async def unassign_agent_from_task(
    task_id: int,
    service: TaskAssignmentService = Depends(get_task_assignment_service),
):
    """
    Removes the agent assignment from a task.
    """
    try:
        updated_task = await service.unassign_task(task_id=task_id)
        return updated_task
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except TaskNotAssignedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}"
        ) from e


@router.get(
    "/{task_id}/suitable-agents",
    summary="Find suitable agents for a task",
    responses={404: {"description": "Task not found"}},
    response_model=List[AgentOut],
)
async def find_suitable_agents(
    task_id: int,
    service: TaskAssignmentService = Depends(get_task_assignment_service),
):
    """
    Finds active agents whose type matches the requirements of the given task.
    """
    try:
        agents = await service.find_suitable_agents_for_task(task_id=task_id)
        return agents
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}"
        ) from e


@router.post(
    "/{task_id}/auto-assign",
    summary="Automatically assign task to a suitable agent",
    responses={
        404: {"description": "Task not found or no suitable agent found"},
        409: {"description": "Task is already assigned"},
    },
    response_model=TaskOut,
)
async def auto_assign_task_endpoint(
    task_id: int,
    service: TaskAssignmentService = Depends(get_task_assignment_service),
):
    """
    Automatically finds the first available and suitable agent and assigns the task.
    """
    try:
        updated_task = await service.auto_assign_task(task_id=task_id)
        return updated_task
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except TaskAlreadyAssignedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except NoSuitableAgentFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except AgentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Internal consistency error: {e}") from e
    except AgentInactiveError as e:  # Should not happen if find_suitable filters correctly
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Internal consistency error: {e}") from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}"
        ) from e
