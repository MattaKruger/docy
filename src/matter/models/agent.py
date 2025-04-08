from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .prompt import Prompt
    from .task import Task


class AgentState(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AgentType(str, Enum):
    DEFAULT = "default"
    CODE = "code"
    BRAINSTORM = "brainstorm"


class AgentLLM(str, Enum):
    GROQ_DEFAULT = "deepseek-r1-distill-qwen-32b"
    GROQ_CODE = "groq_code"
    GROQ_BRAINSTORM = "groq_brainstorm"


class Agent(Base, table=True):
    __tablename__ = "agents"  # type: ignore

    name: str = Field(unique=True, index=True)
    system_prompt_id: Optional[int] = Field(default=None, foreign_key="prompts.id")
    system_prompt: Optional["Prompt"] = Relationship(
        back_populates="agents", sa_relationship_kwargs=dict(lazy="selectin")
    )
    agent_type: AgentType = Field(default=AgentType.DEFAULT, index=True)
    agent_model: AgentLLM = Field(default=AgentLLM.GROQ_DEFAULT)
    state: AgentState = Field(default=AgentState.INACTIVE, index=True)
    tasks: List["Task"] = Relationship(back_populates="agent", sa_relationship_kwargs=dict(lazy="selectin"))
