from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .base import Base


class AgentType(Enum, str):
    DEFAULT = "default"
    CODE = "code"
    BRAINSTORM = "brainstorm"


class AgentModel(Enum, str):
    GROQ_DEFAULT = "deepseek-r1-distill-qwen-32b"
    GROQ_CODE = "groq_code"
    GROQ_BRAINSTORM = "groq_brainstorm"


class Prompt(Base, Table=True):
    name: str = Field()
    agent_id: int = Field(default=None, foreign_key="agent.id")
    agent: "Agent" = Relationship(back_populates="system_prompt")


class PromptIn(SQLModel, table=False):
    name: str = Field()
    agent: Optional["Agent"] = Field(default=None)


class PromptOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()
    agent: Optional["Agent"] = Field(default=None)


class Agent(Base, Table=True):
    name: str = Field()
    system_prompt: Optional["Prompt"] = Relationship(back_populates="agent")
    agent_type: AgentType = Field(default=AgentType.DEFAULT)
    agent_model: AgentModel = Field(default=AgentModel.GROQ_DEFAULT)


class AgentIn(SQLModel, table=False):
    name: str = Field()
    system_prompt_id: int = Field()
    agent_type: AgentType = Field(default=AgentType.DEFAULT)
    agent_model: AgentModel = Field(default=AgentModel.GROQ_DEFAULT)
