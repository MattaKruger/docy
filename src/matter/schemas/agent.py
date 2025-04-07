from typing import Optional

from pydantic import BaseModel, Field

from ..models import AgentLLM, AgentState, AgentType, Prompt


class AgentIn(BaseModel):
    name: str = Field()
    system_prompt_id: int = Field()
    agent_type: AgentType = Field(default=AgentType.DEFAULT)
    agent_model: AgentLLM = Field(default=AgentLLM.GROQ_DEFAULT)
    state: AgentState = Field(default=AgentState.INACTIVE)


class AgentOut(BaseModel):
    id: int = Field()
    name: str = Field()
    system_prompt_id: Optional[int] = Field(default=None)
    system_prompt: Optional["Prompt"] = Field(default=None)
    agent_type: AgentType = Field()
    agent_model: AgentLLM = Field()
    state: AgentState = Field()


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    system_prompt_id: Optional[int] = Field(default=None)
    agent_type: Optional[AgentType] = Field(default=None)
    agent_model: Optional[AgentLLM] = Field(default=None)
    state: Optional[AgentState] = Field(default=None)
