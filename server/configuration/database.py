from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .environment import SETTINGS

async_engine = create_async_engine(
    SETTINGS.async_sqlalchemy_url,
    pool_pre_ping=True,
    echo=SETTINGS.is_local_mode,
    future=True,
)

AsyncSessionLocal: sessionmaker[AsyncSession] = sessionmaker(
    expire_on_commit=False,
    bind=async_engine,
    class_=AsyncSession,
)


async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


DepDatabaseSession = Annotated[AsyncSession, Depends(get_db_async)]
