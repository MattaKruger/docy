from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

import logfire

logfire.configure()

Agent.instrument_all()
