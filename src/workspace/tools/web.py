from typing import Any

import httpx
import logfire
from agents.common import groq_search_agent, ollama_agent, search_agent
from config import settings
from dependencies import http_client
from models import WebsearchResult


async def http_get(url: str) -> str:
    """Performs an HTTP GET request to the specified URL and returns the text content."""
    try:
        response = await http_client.get(url, follow_redirects=True, timeout=15.0)
        response.raise_for_status()
        return response.text
    except httpx.RequestError as e:
        logfire.warning(f"HTTP Request Error for {url}: {e}")
        return f"HTTP Request Error: Could not reach {url}. Details: {e}"
    except httpx.HTTPStatusError as e:
        logfire.warning(f"HTTP Status Error {e.response.status_code} for {e.request.url}")
        return f"HTTP Status Error: Received status {e.response.status_code} from {e.request.url}."
    except Exception as e:
        logfire.error(f"Unexpected error during HTTP GET for {url}: {e}")
        return f"An unexpected error occurred: {e}"


async def get_task_content(task_id: int) -> str:
    """Gets content for a specific task ID from the configured task API."""
    task_url = f"{str(settings.API_TASK_URL).rstrip('/')}/{task_id}"
    logfire.info(f"Fetching task content for ID {task_id} from {task_url}")
    response_text = await http_get(task_url)
    return response_text


async def web_search(query: str) -> str:
    """Performs a web search using the default search agent (Gemini)."""
    logfire.info(f"Performing web search (Gemini) for: {query}")
    try:
        r = await search_agent.run(f"Search DuckDuckGo for the given query: {query}", result_type=WebsearchResult)
        if r and r.data and isinstance(r.data, WebsearchResult):
            return r.data.result
        else:
            logfire.error("Web search (Gemini) returned unexpected data format.", response=r)
            return "Error: Search completed but failed to extract result data."
    except Exception as e:
        logfire.error(f"Web search (Gemini) failed for query '{query}': {e}")
        return f"Error during web search: {e}"


async def ollama_web_search(query: str) -> str:
    """Performs a web search using the Ollama agent."""
    logfire.info(f"Performing web search (Ollama) for: {query}")
    try:
        r = await ollama_agent.run(f"Search DuckDuckGo for the given query: {query}", result_type=WebsearchResult)
        if r and r.data and isinstance(r.data, WebsearchResult):
            return r.data.result
        else:
            logfire.error("Web search (Ollama) returned unexpected data format.", response=r)
            return "Error: Search completed but failed to extract result data."
    except Exception as e:
        logfire.error(f"Web search (Ollama) failed for query '{query}': {e}")
        return f"Error during Ollama web search: {e}"


async def groq_web_search(query: str) -> Any:  # Returns list of messages
    """Performs a web search using the Groq agent and returns all messages."""
    logfire.info(f"Performing web search (Groq) for: {query}")
    try:
        r = await groq_search_agent.run(
            f"Search DuckDuckGo for the given query: {query}",
            result_type=WebsearchResult,  # Still useful for potential parsing/validation within agent
        )
        return r.all_messages() if r else []  # Return empty list on failure
    except Exception as e:
        logfire.error(f"Web search (Groq) failed for query '{query}': {e}")
        return f"Error during Groq web search: {e}"  # Return error message string


async def ask(query: str) -> str:
    """Asks a general question to the default agent (Gemini)."""
    logfire.info(f"Processing 'ask' command with query: {query}")
    try:
        r = await search_agent.run(query)
        return r.data if r and hasattr(r, "data") else "Error: Agent did not return data."
    except Exception as e:
        logfire.error(f"Ask command failed for query '{query}': {e}")
        return f"Error processing question: {e}"


async def sanitize_input(input_str: str) -> str:
    """Sanitizes input string (basic example)."""
    logfire.info("Sanitizing input (placeholder implementation)")
    return input_str.strip()


exported_tools = {
    "http_get": http_get,
    "get_task_content": get_task_content,
    "web_search": web_search,
    "ollama_web_search": ollama_web_search,
    "groq_web_search": groq_web_search,
    "ask": ask,
    "sanitize_input": sanitize_input,
}
