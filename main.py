import os
from typing import Optional, Any, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile, HTTPException
from sqlmodel import SQLModel, Field

from load_dotenv import load_dotenv
from database.db import engine, get_session

from models import *

from routers import chroma_router, user_router, project_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables")
    SQLModel.metadata.create_all(engine)
    yield
    print("Application shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(chroma_router, dependencies=[Depends(get_session)])
app.include_router(user_router)
app.include_router(project_router)


@app.get("/")
def read_root():
    return {"message": "Hello World"}
