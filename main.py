from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from load_dotenv import load_dotenv
from sqlmodel import SQLModel
from pydantic_ai import Agent
from database.db import engine
from routers import agent_router, artifact_router, chroma_router, notes_router, project_router, user_router, task_router
import logfire

load_dotenv()

logfire.configure()
Agent.instrument_all()

origins = ["http://localhost", "http://localhost:4321", "http://localhost:8000"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables")
    SQLModel.metadata.create_all(engine)
    yield
    print("Application shutdown")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chroma_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(artifact_router)
app.include_router(agent_router)
app.include_router(notes_router)
app.include_router(task_router)
