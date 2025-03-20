from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from load_dotenv import load_dotenv
from database.db import engine

from routers import chroma_router, user_router, project_router, artifact_router, agent_router


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


@app.get("/")
def read_root():
    return {"message": "Hello World"}
