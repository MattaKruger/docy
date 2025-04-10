import time
import datetime

from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from load_dotenv import load_dotenv
from pydantic_ai import Agent

from .api import (
    agent_router,
    artifact_router,
    notes_router,
    project_router,
    prompt_router,
    task_router,
    user_router,
    chat_router,
)
from .db import create_db_and_tables, engine

# from .mcp_server import mcp

load_dotenv()

# Configure logfire
logfire.configure()
logfire.instrument_sqlalchemy(engine)
Agent.instrument_all()

origins = ["http://localhost", "http://localhost:4321", "http://localhost:8000"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logfire.info("Creating database tables...")
    await create_db_and_tables()
    yield
    logfire.info("Shutting down...")


templates = Jinja2Templates(directory="templates")

app = FastAPI(lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# TODO learn more about htmx
@app.get("/load-content", response_class=HTMLResponse)
async def load_content_endpoint():
    # Simulate work
    time.sleep(1)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Return ONLY the HTML fragment
    html_fragment = f"""
    <p><strong>Content loaded via HTMX at:</strong> {current_time}</p>
    <p>This is new content replacing the old paragraph.</p>
    """
    return HTMLResponse(content=html_fragment)
    # If using templates for fragments:
    # return templates.TemplateResponse("fragments/content.html", {"request": request, "time": current_time})


logfire.instrument_fastapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/mcp", mcp.sse_app())

app.include_router(user_router)
app.include_router(prompt_router)
app.include_router(project_router)
app.include_router(artifact_router)
app.include_router(agent_router)
app.include_router(notes_router)
app.include_router(task_router)
app.include_router(chat_router)
