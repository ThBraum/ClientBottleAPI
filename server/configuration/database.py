from typing import Annotated

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
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
)


async def get_db_async():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


DepDatabaseSession = Annotated[AsyncSession, Depends(get_db_async)]
