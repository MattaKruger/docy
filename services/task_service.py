from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from repositories import AgentRepository, TaskRepository, ProjectRepository, PromptRepository
from models import Task, AgentState


class TaskAssignmentService:
    def __init__(self, agent_repo: AgentRepository, task_repo: TaskRepository)
        self.agent_repo = agent_repo
        self.task_repo = task_repo

    async def simulate_agent_pickup(self, agent_id: int, project_id: int) -> List[Task]:
        agent = await self.agent_repo.get_or_404(agent_id)
        if agent.state != AgentState.ACTIVE:
            print(f"Agent '{agent.name}' (ID: {agent_id}) is not active. Cannot pick up tasks.")
            return []

        print(f"Active Agent '{agent.name}' (ID: {agent_id}) looking for tasks in Project ID: {project_id}...")

        # 2. Find Unassigned Tasks using TaskRepository
        unassigned_tasks = await self.task_repo.find_unassigned_by_project(project_id)

        assigned_tasks = []
        if not unassigned_tasks:
            print("No unassigned tasks found for this agent.")
            return []

        # 3. Assign Tasks using TaskRepository
        print(f"Found {len(unassigned_tasks)} tasks. Assigning to agent {agent_id}...")
        for task in unassigned_tasks:
            # Simple pickup: assign all found tasks. Could add limits or logic here.
            updated_task = await self.task_repo.assign_agent(task.id, agent_id)
            if updated_task:
                assigned_tasks.append(updated_task)
            else:
                # Log or handle cases where assignment failed unexpectedly
                print(f"Warning: Failed to assign Task ID {task.id} to Agent ID {agent_id}.")


        return assigned_tasks
