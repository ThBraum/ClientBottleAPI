from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from server.configuration.database import DepDatabaseSession
from server.lib.dependencies import DepUser
from server.schema.auth_schema import UserLoginInput, UserLoginOutput
from server.service.auth_service import AuthService


router = APIRouter(prefix="/api/server", tags=["Auth"])

@router.post("/login/", response_model=UserLoginOutput)
async def exec_db(user: UserLoginInput, db: DepDatabaseSession, service: AuthService):
    try:
        return await service.authenticate(user)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))