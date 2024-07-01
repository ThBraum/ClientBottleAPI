import os
import uuid
from datetime import datetime, time, timedelta
from typing import Annotated, Optional

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pytz import timezone
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from server.configuration.database import DepDatabaseSession
from server.lib.error import ClientBottleException, CodigoErro
from server.model.user import User
from server.model.user_token import UserToken
from server.schema.auth_schema import TokenOutput, UserTokenInfoOutput

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/server/auth/login/", scheme_name="Bearer")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

timezone_brazil = timezone("America/Sao_Paulo")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_expiration_time() -> datetime:
    now = datetime.now(timezone_brazil)
    return datetime.combine((now + timedelta(days=1)), time(3, 0), tzinfo=timezone_brazil)


async def generate_unique_token(
    db: DepDatabaseSession, user: User, expires_at: datetime
) -> TokenOutput:
    while True:
        payload = {"sub": user.id_user, "exp": expires_at, "jti": str(uuid.uuid4())}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        existing_token = await db.execute(select(UserToken).where(UserToken.api_key == token))
        if not existing_token.scalar():
            return TokenOutput(token_type="bearer", access_token=token, expires_at=expires_at)


async def create_user_token(
    db: DepDatabaseSession, user: User, api_key: str, expires_at: datetime
) -> UserToken:
    user_token = UserToken(id_user=user.id_user, api_key=api_key, expires_at=expires_at)
    db.add(user_token)
    await db.commit()
    return user_token


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


async def get_current_user(
    api_key: Annotated[str, Depends(oauth2_scheme)], db: DepDatabaseSession
) -> Optional[UserTokenInfoOutput]:
    try:
        payload = jwt.decode(api_key, SECRET_KEY, algorithms=[ALGORITHM])
        id_user: int = payload.get("sub")
        if id_user is None:
            raise ClientBottleException(errors=[CodigoErro.AUTENTICACAO_NECESSARIA])
        return await get_user_by_id(db, id_user, api_key)
    except jwt.InvalidTokenError as e:
        raise ClientBottleException(
            errors=[CodigoErro.CREDENCIAIS_INVALIDAS], status_code=401
        ) from e
    except ClientBottleException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.errors,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_active_user(
    db: DepDatabaseSession, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    current_user = await get_current_user(token, db)
    if not current_user.fl_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def validate_credentials(
    db: AsyncSession, form_data: OAuth2PasswordRequestForm
) -> Optional[User]:
    user = await get_user_by_email_or_username(db, form_data.username)
    if not verify_password(form_data.password, user.password):
        raise ClientBottleException(errors=[CodigoErro.CREDENCIAIS_INVALIDAS], status_code=401)
    return user


async def remove_expired_tokens(db: DepDatabaseSession):
    now = datetime.now(timezone_brazil)
    await db.execute(delete(UserToken).where(UserToken.expires_at <= now))
    await db.commit()
