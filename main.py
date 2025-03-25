from contextlib import asynccontextmanager

from fastapi import FastAPI
from load_dotenv import load_dotenv
from sqlmodel import SQLModel

from database.db import engine
from routers import agent_router, artifact_router, chroma_router, notes_router, project_router, user_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables")
    SQLModel.metadata.create_all(engine)
    yield
    print("Application shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(chroma_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(artifact_router)
app.include_router(agent_router)
app.include_router(notes_router)
