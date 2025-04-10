from config import settings
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

ollama_model = OpenAIModel(
    model_name=settings.OLLAMA_MODEL,
    provider=OpenAIProvider(base_url=str(settings.OLLAMA_BASE_URL)),
)

gemini_model = GeminiModel(
    model_name=settings.GEMINI_MODEL,
)

groq_model = GroqModel(model_name=settings.GROQ_MODEL)

search_agent = Agent(
    gemini_model,
    tools=[duckduckgo_search_tool()],
    system_prompt="Search the DuckDuckGo search tool with provided query. Show sources.",
)

ollama_agent = Agent(
    ollama_model,
    tools=[duckduckgo_search_tool()],
    system_prompt="You are a helpful assistant, help with the task at hand.",
    retries=5,
    model_settings={
        "max_tokens": settings.DEFAULT_MAX_TOKENS,
        "temperature": settings.DEFAULT_TEMPERATURE,
    },
)

groq_search_agent = Agent(
    groq_model,
    tools=[duckduckgo_search_tool()],
    system_prompt="Search the DuckDuckGo search tool with provided query. Show sources.",
    model_settings={
        "max_tokens": 512,
        "temperature": 0.2,
    },
)

groq_code_agent = Agent(
    groq_model,
    system_prompt="You are an expert programmer. Generate clean, efficient, and correct code based on the user's request. Only output raw code blocks unless asked otherwise.",
    model_settings={
        "max_tokens": 2048,
        "temperature": 0.1,
    },
)
