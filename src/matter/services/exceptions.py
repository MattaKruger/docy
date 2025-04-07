class ServiceError(Exception):
    """Base exception for service layer errors."""

    pass


class TaskNotFoundError(ServiceError):
    """Raised when a task with the given ID is not found."""

    def __init__(self, task_id: int):
        super().__init__(f"Task with ID {task_id} not found.")
        self.task_id = task_id


class AgentNotFoundError(ServiceError):
    """Raised when an agent with the given ID is not found."""

    def __init__(self, agent_id: int):
        super().__init__(f"Agent with ID {agent_id} not found.")
        self.agent_id = agent_id


class AgentInactiveError(ServiceError):
    """Raised when trying to assign a task to an inactive agent."""

    def __init__(self, agent_id: int):
        super().__init__(f"Agent with ID {agent_id} is inactive.")
        self.agent_id = agent_id


class TaskAlreadyAssignedError(ServiceError):
    """Raised when trying to assign a task that is already assigned to the *same* agent."""

    def __init__(self, task_id: int, agent_id: int):
        super().__init__(f"Task {task_id} is already assigned to agent {agent_id}.")
        self.task_id = task_id
        self.agent_id = agent_id


class TaskNotAssignedError(ServiceError):
    """Raised when trying to unassign a task that isn't assigned."""

    def __init__(self, task_id: int):
        super().__init__(f"Task {task_id} is not currently assigned to any agent.")
        self.task_id = task_id


class NoSuitableAgentFoundError(ServiceError):
    """Raised when no suitable agent can be found for auto-assignment."""

    def __init__(self, task_id: int, criteria: str = "available and matching type"):
        super().__init__(f"No suitable agent found for task {task_id} based on criteria: {criteria}.")
        self.task_id = task_id
        self.criteria = criteria
