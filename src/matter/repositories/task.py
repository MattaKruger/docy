from typing import List, Optional

import logfire
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from ..models.project import Project
from ..models.task import Task
from ..schemas.task import TaskIn, TaskOut, TaskUpdate

from .agent import AgentRepository
from .base import BaseRepository
from .project import ProjectRepository


class TaskRepository(BaseRepository[Task, TaskIn, TaskUpdate]):
    """Repository for handling task model operations"""

    def __init__(self, session: AsyncSession, project_repo: ProjectRepository, agent_repo: AgentRepository):
        super().__init__(Task, session)
        self.project_repo = project_repo
        self.agent_repo = agent_repo

    async def get_all_new(self):
        statement = select(Task, Project).where(Task.project_id == Project.id)
        result = await self.session.execute(statement)
        tasks = list(result.scalars().all())
        print(tasks)

    async def get_all_by_project_id(self, project_id: int) -> List[Task]:
        statement = select(Task).where(Task.project_id == project_id)
        result = await self.session.execute(statement)
        tasks = list(result.scalars().all())
        return tasks

    async def create(self, create_model: TaskIn) -> Task:
        """Creates a new task, ensuring project exists and agent_id is initially None."""
        logfire.info(f"Attempting to create task: {create_model.name} for Project ID: {create_model.project_id}")

        if not create_model.project_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task requires a project id.")

        project = await self.project_repo.get(create_model.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with ID {create_model.project_id} not found"
            )

        task_data = create_model.model_dump()

        task = Task(**task_data)
        task.agent_id = None

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        logfire.info(f"Successfully created Task ID: {task.id} - '{task.name}' for Project ID: {task.project_id}")
        return task

    async def find_unassigned_by_project(self, project_id: int) -> List[Task]:
        """Finds tasks for a project that dont have an agent assigned."""
        statement = select(Task).where(Task.project_id == project_id).where(Task.agent_id == None)
        tasks = await self.session.execute(statement)
        result = list(tasks.scalars().all())

        logfire.info(f"Found {len(result)} unassigned tasks for Project ID: {project_id}")
        return result

    async def assign_agent(self, task_id: int, agent_id: int) -> Optional[Task]:
        """Assigns a specific task to a specific agent, checking existence."""
        logfire.info(f"Attempting to assign Task ID: {task_id} to Agent ID: {agent_id}")
        task = await self.get_or_404(task_id)

        agent = await self.agent_repo.get(agent_id)
        if not agent:
            logfire.error(f"Error: Agent ID {agent_id} not found.")
            return None

        if task.agent_id is not None and task.agent_id != agent_id:
            logfire.warning(
                f"Warning: Task ID {task_id} is already assigned to Agent ID: {task.agent_id}. Reassigning to {agent_id}."
            )
        elif task.agent_id == agent_id:
            logfire.info(f"Info: Task ID {task_id} is already assigned to Agent ID: {agent_id}. No change needed.")
            return task

        task.agent_id = agent_id
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        logfire.info(f"Successfully assigned Task ID: {task.id} to Agent ID: {task.agent_id}")
        return task
