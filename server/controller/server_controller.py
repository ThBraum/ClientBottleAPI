from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from server.configuration.database import DepDatabaseSession
from server.model.role import UserRole
from server.utils.dependencies import DepUserPayload

router = APIRouter(tags=["Server"])


@router.get("/ping/")
async def ping():
    return "pong"


@router.get("/db/")
async def exec_db(db: DepDatabaseSession, user: DepUserPayload):
    result = await db.execute(text("SELECT 'Hello, World!'"))
    return {"result": result.scalars().all(), "User": user.username}


class RoleCreation(BaseModel):
    role: UserRole


@router.post("/role")
async def pydantic_role(db: DepDatabaseSession, query_role: UserRole, body_role: RoleCreation):
    return {
        "query_role": query_role,
        "body_role": body_role,
    }
