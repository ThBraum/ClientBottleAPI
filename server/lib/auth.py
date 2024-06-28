from typing import Annotated
from fastapi import Depends, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select

from server.configuration.database import DepDatabaseSession
from server.lib.context import set_user_id
from server.lib.error import ClientBottleException, CodigoErro
from server.model.user import User

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_user_by_token(db: DepDatabaseSession, api_token: str):
    credential_exception = ClientBottleException(
        errors=[CodigoErro.CREDENCIAIS_INVALIDAS],
        status_code=401,
    )
    if not api_token:
        raise credential_exception
    user = await db.execute(select(User).where(User.api_key == api_token))
    result = user.scalars().first()
    if not result:
        raise credential_exception
    return result


async def validate_user(db: DepDatabaseSession, api_token: str = Security(api_key_header)):
    user = await get_user_by_token(db, api_token)
    set_user_id(user.id_user)
    return user


# DepUser = Annotated[User, Depends(validate_user)]
