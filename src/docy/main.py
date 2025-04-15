import datetime
from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from load_dotenv import load_dotenv
from pydantic_ai import Agent

from .api.v1 import api_v1_router
from .db import create_db_and_tables, engine

# from .mcp_server import mcp

load_dotenv()

# Configure logfire
logfire.configure()
logfire.instrument_sqlalchemy(engine)
Agent.instrument_all()

origins = ["http://localhost", "http://localhost:4321", "http://localhost:8000", "localhost:5173"]


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
# Not sure if im going to build a webbased frontend for this.
@app.get("/load-content", response_class=HTMLResponse)
async def load_content_endpoint():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_fragment = f"""
    <p><strong>Content loaded via HTMX at:</strong> {current_time} </p>
    <p>This is new content replacing the old paragraph.</p>
    """
    return HTMLResponse(content=html_fragment)


logfire.instrument_fastapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
# Still not sure if mcp is the way to go.
# app.mount("/mcp", mcp.sse_app())
app.include_router(api_v1_router, prefix="/api/v1")
