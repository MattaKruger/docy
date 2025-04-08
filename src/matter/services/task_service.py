from typing import List, Optional

from matter.models import Agent, AgentState, AgentType, Task, TaskType
from matter.repositories import AgentRepository, TaskRepository

from .exceptions import (
    AgentInactiveError,
    AgentNotFoundError,
    NoSuitableAgentFoundError,
    ServiceError,
    TaskAlreadyAssignedError,
    TaskNotAssignedError,
    TaskNotFoundError,
)


class TaskAssignmentService:
    """
    Handles the assignment and unassignment of tasks to agents.
    Provides methods for finding tasks and suitable agents.
    """

    def __init__(self, agent_repo: AgentRepository, task_repo: TaskRepository):
        self.agent_repo = agent_repo
        self.task_repo = task_repo

    async def _get_task_or_raise(self, task_id: int) -> Task:
        """Helper to get a task by ID or rais TaskNotFOudnError."""
        task = await self.task_repo.get(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    async def _get_agent_or_raise(self, agent_id: int) -> Agent:
        agent = await self.agent_repo.get(agent_id)
        if not agent:
            raise AgentNotFoundError(agent_id)
        return agent

    async def assign_task(self, task_id: int, agent_id: int) -> Task:
        """
        Assigns a specific task to a specific agent.

        Args:
            task_id: The ID of the task to assign.
            agent_id: The ID of the agent to assign the task to.

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If the task doesn't exist.
            AgentNotFoundError: If the agent doesn't exist.
            AgentInactiveError: If the agent is not in an 'ACTIVE' state.
            TaskAlreadyAssignedError: If the task is already assigned to this agent.
        """
        task_db = await self._get_task_or_raise(task_id)
        agent = await self._get_agent_or_raise(agent_id)

        if agent.state != AgentState.ACTIVE:
            raise AgentInactiveError(agent_id)

        if task_db.agent_id == agent_id:
            raise TaskAlreadyAssignedError(task_id, agent_id)

        task_db.agent_id = agent_id
        updated_task = await self.task_repo.update(
            task_db,
        )
        if updated_task is None:
            raise ServiceError(f"Failed to update task {task_id} assignment.")
        return updated_task

    async def unassign_task(self, task_id: int) -> Task:
        """
        Removes the agent assignment from a task.

        Args:
            task_id: The ID of the task to unassign.

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If the task doesn't exist.
            TaskNotAssignedError: If the task is not currently assigned.
        """
        task = await self._get_task_or_raise(task_id)

        if task.agent_id is None:
            raise TaskNotAssignedError(task_id)

        task.agent_id = None
        updated_task = await self.task_repo.update(task_id, task)
        if updated_task is None:
            raise ServiceError(f"Failed to update task {task_id} unassignment.")
        return updated_task

    async def get_unassigned_tasks(self, project_id: Optional[int] = None) -> List[Task]:
        """
        Retrieves a list of tasks that are not assigned to any agent.

        Args:
            project_id: Optional ID to filter tasks by project.

        Returns:
            A list of unassigned Task objects.
        """
        filters = {"agent_id": None}
        if project_id is not None:
            filters["project_id"] = project_id

        # Assuming repository list method supports filtering
        unassigned_tasks = await self.task_repo.list(**filters)
        return unassigned_tasks

    async def get_tasks_by_agent(self, agent_id: int) -> List[Task]:
        """
        Retrieves all tasks currently assigned to a specific agent.

        Args:
            agent_id: The ID of the agent.

        Returns:
            A list of Task objects assigned to the agent.

        Raises:
            AgentNotFoundError: If the agent doesn't exist.
        """
        # Verify agent exists first
        await self._get_agent_or_raise(agent_id)

        # Assuming repository list method supports filtering by agent_id
        tasks = await self.task_repo.list(agent_id=agent_id)
        return tasks

    def _get_agent_type_for_task_type(self, task_type: TaskType) -> AgentType:
        """Maps a TaskType to a suitable AgentType."""
        if task_type == TaskType.CODING:
            return AgentType.CODE
        elif task_type == TaskType.WRITING:
            # Assuming BRAINSTORM or DEFAULT might be suitable for writing
            return AgentType.BRAINSTORM  # Or AgentType.DEFAULT
        else:
            return AgentType.DEFAULT

    async def find_suitable_agents_for_task(self, task_id: int) -> List[Agent]:
        """
        Finds active agents that are suitable for a given task based on type.

        Args:
            task_id: The ID of the task.

        Returns:
            A list of active Agent objects suitable for the task.

        Raises:
            TaskNotFoundError: If the task doesn't exist.
        """
        task = await self._get_task_or_raise(task_id)
        target_agent_type = self._get_agent_type_for_task_type(task.task_type)

        # Find active agents of the target type
        # Assuming agent_repo.list supports multiple filters
        suitable_agents = await self.agent_repo.list(state=AgentState.ACTIVE, agent_type=target_agent_type)
        return suitable_agents

    async def auto_assign_task(self, task_id: int) -> Task:
        """
        Automatically finds a suitable, active agent and assigns the task.
        Currently uses the first suitable agent found.
        More sophisticated logic (e.g., load balancing) could be added here.

        Args:
            task_id: The ID of the task to auto-assign.

        Returns:
            The updated Task object after assignment.

        Raises:
            TaskNotFoundError: If the task doesn't exist.
            TaskAlreadyAssignedError: If the task is already assigned.
            NoSuitableAgentFoundError: If no active agent of the correct type is found.
            AgentInactiveError: Should not happen with current logic but included for robustness.
            AgentNotFoundError: Should not happen with current logic but included for robustness.
        """
        task = await self._get_task_or_raise(task_id)

        if task.agent_id is not None:
            # Or perhaps unassign first, depending on desired behavior?
            raise TaskAlreadyAssignedError(task_id, task.agent_id)

        suitable_agents = await self.find_suitable_agents_for_task(task_id)

        if not suitable_agents:
            raise NoSuitableAgentFoundError(task_id)

        # Future enhancement: Implement load balancing (e.g., pick agent with fewest tasks).
        chosen_agent = suitable_agents[0]

        return await self.assign_task(task_id, chosen_agent.id)
