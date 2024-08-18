import os
import uuid
from datetime import datetime, time, timedelta
from typing import Annotated, Optional

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from passlib.context import CryptContext
from pytz import timezone
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from server.configuration.database import DepDatabaseSession
from server.model.user import User
from server.schema.auth_schema import AuthSigninOutput, TokenLoginOutput, UserTokenInfoOutput
from server.utils.error import ClientBottleException, CodigoErro

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

if not SECRET_KEY or not ALGORITHM:
    raise ValueError("SECRET_KEY and ALGORITHM must be set in the environment variables.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="server/auth/login/")
security = HTTPBearer()

timezone_brazil = timezone("America/Sao_Paulo")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_expiration_time() -> datetime:
    now = datetime.now(timezone_brazil)
    return datetime.combine((now + timedelta(days=1)), time(3, 0), tzinfo=timezone_brazil)


async def evaluate_username_availability(db: DepDatabaseSession, username: str) -> str:
    result = await db.execute(select(User).where(User.username == username))
    if result.scalars().first():
        raise ClientBottleException(errors=[CodigoErro.USERNAME_IN_USE])
    return username


async def generate_token(user: User, expires_at: datetime) -> Optional[TokenLoginOutput]:
    payload = {
        "id_user": user.id_user,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "fl_active": user.fl_active,
        "creation_user_id": user.creation_user_id,
        "created_at": int(user.created_at.timestamp()),
        "update_user_id": user.update_user_id if user.update_user_id else None,
        "updated_at": (int(user.updated_at.timestamp()) if user.updated_at else None),
        "jti": str(uuid.uuid4()),
        "exp": int(expires_at.timestamp()),
    }
    token_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return TokenLoginOutput(token_type="bearer", access_token=token_jwt)


async def get_user_by_email_or_username(
    db: DepDatabaseSession, email_or_username: str
) -> Optional[User]:
    result = await db.execute(
        select(User).where(
            (User.email == email_or_username) | (User.username == email_or_username)
        )
    )
    if user := result.scalars().first():
        return user
    else:
        raise ClientBottleException(errors=[CodigoErro.DS_LOGIN_NAO_CADASTRADO])


async def get_user_by_id(
    db: DepDatabaseSession, id_user: int, api_key: str
) -> Optional[UserTokenInfoOutput]:
    query = text(
        """
        select "user".id_user,
            "user".username,
            "user".full_name,
            "user".email,
            "user".fl_active,
            user_token.expires_at,
            user_token.api_key
        from "user"
                join user_token on "user".id_user = user_token.creation_user_id
        where "user".id_user = :id_user
        and user_token.api_key like :api_key
        """
    )

    result = await db.execute(query, {"id_user": id_user, "api_key": api_key})
    if row := result.fetchone():
        return UserTokenInfoOutput(
            id_user=row.id_user,
            username=row.username,
            full_name=row.full_name,
            email=row.email,
            fl_active=row.fl_active,
            expires_at=row.expires_at,
            api_key=row.api_key,
        )
    else:
        raise ClientBottleException(errors=[CodigoErro.SESSAO_EXPIRADA_OU_INVALIDA])


async def validate_credentials(
    db: AsyncSession, form_data: OAuth2PasswordRequestForm
) -> Optional[User]:
    user = await get_user_by_email_or_username(db, form_data.username)
    if not verify_password(form_data.password, user.password):
        raise ClientBottleException(errors=[CodigoErro.CREDENCIAIS_INVALIDAS], status_code=401)
    return user
