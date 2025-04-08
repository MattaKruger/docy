from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from matter.db import AsyncSession, get_session
from matter.repositories import (
    AgentRepository,
    ProjectRepository,
    PromptRepository,
    TaskRepository,
)
from matter.schemas import AgentOut, TaskIn, TaskOut, TaskUpdate
from matter.services.exceptions import (
    AgentInactiveError,
    AgentNotFoundError,
    NoSuitableAgentFoundError,
    ServiceError,
    TaskAlreadyAssignedError,
    TaskNotAssignedError,
    TaskNotFoundError,
)
from matter.services.task_service import TaskAssignmentService

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
    "/",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project ID not found"
        )
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
    response_model=List[TaskOut],
    summary="Get all unassigned tasks",
)
async def get_unassigned_tasks(
    project_id: Optional[int] = None,
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
    response_model=List[TaskOut],
    summary="Get all tasks with optional filters",
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
    response_model=TaskOut,
    summary="Get a specific task by ID",
    responses={404: {"description": "Task not found"}},
)
async def get_task(
    task_id: int,
    task_repo: TaskRepository = Depends(get_task_repo),
):
    """
    Retrieves details of a specific task by its ID.
    """
    task = await task_repo.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return TaskOut.model_validate(**task.model_dump())


@router.patch(
    "/{task_id}",
    response_model=TaskOut,
    summary="Update a task",
    responses={404: {"description": "Task not found"}},
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
    response_model=TaskOut,
    summary="Assign a task to an agent",
    responses={
        404: {"description": "Task or Agent not found"},
        400: {"description": "Agent is inactive"},
        409: {"description": "Task already assigned to this agent"},
    },
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AgentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AgentInactiveError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except TaskAlreadyAssignedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}"
        )


@router.post(
    "/{task_id}/unassign",
    response_model=TaskOut,
    summary="Unassign an agent from a task",
    responses={
        404: {"description": "Task not found"},
        400: {"description": "Task is not assigned"},
    },
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TaskNotAssignedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/{task_id}/suitable-agents",
    response_model=List[AgentOut],
    summary="Find suitable agents for a task",
    responses={404: {"description": "Task not found"}},
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}"
        )


@router.post(
    "/{task_id}/auto-assign",
    response_model=TaskOut,
    summary="Automatically assign task to a suitable agent",
    responses={
        404: {"description": "Task not found or no suitable agent found"},
        409: {"description": "Task is already assigned"},
    },
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TaskAlreadyAssignedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except NoSuitableAgentFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AgentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Internal consistency error: {e}")
    except AgentInactiveError as e:  # Should not happen if find_suitable filters correctly
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Internal consistency error: {e}")
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}"
        )
