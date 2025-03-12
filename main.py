import os
from typing import Optional, Any, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, text

from load_dotenv import load_dotenv

# from github_scraper import GithubScraper

from routers import chroma_router

load_dotenv()

engine = create_engine(os.environ.get("DB_URL", ""))


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables")
    SQLModel.metadata.create_all(engine)
    yield
    print("Application shutdown")


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI(lifespan=lifespan)

app.include_router(chroma_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
