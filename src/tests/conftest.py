import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

from docy.core import Settings
from docy.db import get_session as get_app_session
from docy.main import app

settings = Settings()

TEST_DATABASE_URL = DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.TEST_DB_NAME}"
)


test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_setup(event_loop: asyncio.AbstractEventLoop):
    """
    Session-scoped fixture to create and drop database tables.
    `autouse=True` ensures it runs automatically for the session.
    """
    # --- IMPORTANT ---
    # Ensure all your SQLModel models are imported *before* `create_all` is called.
    # This might happen implicitly if your main app or other modules import them.
    # If not, you might need to explicitly import them here, e.g.:
    # from docy.src.docy import models # Assuming models are in __init__.py
    # -----------------

    async with test_engine.begin() as conn:
        # Use run_sync for synchronous metadata operations
        # print("Creating test database tables...")
        await conn.run_sync(SQLModel.metadata.create_all)

    yield  # Run the tests

    async with test_engine.begin() as conn:
        # print("Dropping test database tables...")
        await conn.run_sync(SQLModel.metadata.drop_all)

    await test_engine.dispose()  # Clean up the engine connections


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    """
    Function-scoped fixture to provide a test database session.
    Wraps the test in a transaction and rolls back afterwards.
    """
    async with TestingSessionLocal() as db_session:
        # Begin a nested transaction (if supported, otherwise a regular one)
        await db_session.begin_nested()  # Savepoint

        yield db_session

        # Rollback the transaction to ensure test isolation
        await db_session.rollback()
        # No commit needed as we want to discard changes

        # Optional: Close the session explicitly if needed, though async context manager handles it
        # await db_session.close()


@pytest_asyncio.fixture(scope="function")
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Function-scoped fixture to provide an async test client
    for making API requests, with the database session dependency overridden.
    """
    if not app:
        pytest.skip("FastAPI app not loaded, skipping client fixture.")

    # Define the override function *inside* the fixture
    # so it closes over the correct 'session' instance for this specific test
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    # Apply the dependency override
    app.dependency_overrides[get_app_session] = override_get_session

    # Create the test client
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    # Clean up the override after the test
    del app.dependency_overrides[get_app_session]
