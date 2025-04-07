from contextlib import asynccontextmanager

import logfire

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic_ai import Agent

from load_dotenv import load_dotenv

from .api import agent_router, artifact_router, notes_router, project_router, task_router, user_router, prompt_router
from .db import create_db_and_tables, engine
from .mcp_server import mcp


load_dotenv()

logfire.configure()
logfire.instrument_sqlalchemy(engine)

Agent.instrument_all()

origins = ["http://localhost", "http://localhost:4321", "http://localhost:8000"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logfire.info("Creating database tables")
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

logfire.instrument_fastapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/mcp", mcp.sse_app())

app.include_router(user_router)
app.include_router(prompt_router)
app.include_router(project_router)
app.include_router(artifact_router)
app.include_router(agent_router)
app.include_router(notes_router)
app.include_router(task_router)
