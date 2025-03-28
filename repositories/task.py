from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from .base import BaseRepository
from .project import ProjectRepository
from .agent import AgentRepository

from models import Task, TaskIn, TaskUpdate, Project


class TaskRepository(BaseRepository[Task, TaskIn, TaskUpdate]):
    """Repository for handling task model operations"""

    def __init__(self, session: AsyncSession, project_repo: ProjectRepository, agent_repo: AgentRepository):
        super().__init__(Task, session)
        self.project_repo = project_repo
        self.agent_repo = agent_repo

    async def create(self, task_in: TaskIn) -> Task:
        """Creates a new task, ensuring project exists and agent_id is initially None."""
        print(f"Attempting to create task: {task_in.name} for Project ID: {task_in.project_id}")
        if not task_in.project_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task requires a project id.")
        project = await self.project_repo.get(task_in.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with ID {task_in.project_id} not found"
            )

        task_data = task_in.model_dump()
        task = Task(**task_data)
        task.agent_id = None

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        print(f"Successfully created Task ID: {task.id} - '{task.name}' for Project ID: {task.project_id}")
        return task

    async def find_unassigned_by_project(self, project_id: int) -> List[Task]:
        """Finds tasks for a project that dont have an agent assigned."""
        statement = select(Task).where(Task.project_id == project_id).where(Task.agent_id == None)
        tasks = await self.session.exec(statement)
        result = list(tasks.all())
        print(f"Found {len(result)} unassigned tasks for Project ID: {project_id}")
        return result

    async def assign_agent(self, task_id: int, agent_id: int) -> Optional[Task]:
        """Assigns a specific task to a specific agent, checking existence."""
        print(f"Attempting to assign Task ID: {task_id} to Agent ID: {agent_id}")
        task = await self.get_or_404(task_id)

        # Check if agent exists using injected repository
        agent = await self.agent_repo.get(agent_id)
        if not agent:
            print(f"Error: Agent ID {agent_id} not found.")
            # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent {agent_id} not found")
            return None

        if task.agent_id is not None and task.agent_id != agent_id:
            print(
                f"Warning: Task ID {task_id} is already assigned to Agent ID: {task.agent_id}. Reassigning to {agent_id}."
            )
        elif task.agent_id == agent_id:
            print(f"Info: Task ID {task_id} is already assigned to Agent ID: {agent_id}. No change needed.")
            return task  # No change, return current state

        task.agent_id = agent_id
        self.session.add(task)  # Mark the existing task as modified
        await self.session.commit()
        await self.session.refresh(task)
        print(f"Successfully assigned Task ID: {task.id} to Agent ID: {task.agent_id}")
        return task
