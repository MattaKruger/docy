from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from .base import Base
from .task import Task


class AgentState(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AgentType(str, Enum):
    DEFAULT = "default"
    CODE = "code"
    BRAINSTORM = "brainstorm"


class AgentModel(str, Enum):
    GROQ_DEFAULT = "deepseek-r1-distill-qwen-32b"
    GROQ_CODE = "groq_code"
    GROQ_BRAINSTORM = "groq_brainstorm"


class Prompt(Base, table=True):
    name: str = Field(unique=True, index=True)
    agent_id: int = Field(default=None, foreign_key="agents.id")
    agent: Optional["Agent"] = Relationship(back_populates="system_prompt")

    __tablename__ = "prompts"  # type: ignore


class PromptIn(SQLModel, table=False):
    name: str = Field()
    agent: Optional["Agent"] = Field(default=None)


class PromptOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()
    agent: Optional["Agent"] = Field(default=None)


class Agent(Base, table=True):
    name: str = Field(unique=True, index=True)
    system_prompt: Optional["Prompt"] = Relationship(back_populates="agent")
    agent_type: AgentType = Field(default=AgentType.DEFAULT, index=True)
    agent_model: AgentModel = Field(default=AgentModel.GROQ_DEFAULT)
    state: AgentState = Field(default=AgentState.INACTIVE, index=True)
    tasks: List["Task"] = Relationship(back_populates="agent")

    __tablename__ = "agents"  # type: ignore


class AgentIn(SQLModel, table=False):
    name: str = Field()
    system_prompt_id: int = Field()
    agent_type: AgentType = Field(default=AgentType.DEFAULT)
    agent_model: AgentModel = Field(default=AgentModel.GROQ_DEFAULT)
    state: AgentState = Field(default=AgentState.INACTIVE)


class AgentOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()
    system_prompt: "Prompt" = Field()
    agent_type: AgentType = Field()
    agent_model: AgentModel = Field()
    state: AgentState = Field()


class AgentUpdate(SQLModel, table=False):
    name: Optional[str] = Field()
    system_prompt: Optional[str] = Field()
    agent_type: Optional[AgentType] = Field()
    agent_model: Optional[AgentModel] = Field()
    state: Optional[AgentState] = Field()
