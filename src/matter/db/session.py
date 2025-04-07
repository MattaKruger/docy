from typing import AsyncGenerator

from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from .engine import engine

async_session_local = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_local() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
