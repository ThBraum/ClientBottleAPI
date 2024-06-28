from fastapi import APIRouter
from sqlalchemy import text

from server.configuration.database import DepDatabaseSession
from server.lib.dependencies import DepUser

router = APIRouter(prefix="/api/server", tags=["Server"])


@router.get("/ping/")
async def ping():
    return "pong"


@router.get("/db/")
async def exec_db(db: DepDatabaseSession, user: DepUser):
    result = await db.execute(text("SELECT 'Hello, World!'"))
    return {"result": result.scalars().all(), "User": user.username}
