from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from server.configuration.database import DepDatabaseSession
from server.model.user import User
from server.schema.auth_schema import AuthSigninOutput, UserInfoOutput
from server.utils.auth import generate_token, get_expiration_time, validate_credentials
from server.utils.error import ClientBottleException, CodigoErro


class _AuthService:
    def __init__(self, db: DepDatabaseSession):
        self.db = db

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm) -> AuthSigninOutput:
        user = await validate_credentials(self.db, form_data)

        expires_at = get_expiration_time()
        token = await generate_token(user, expires_at)

        user_info = UserInfoOutput(
            id_user=user.id_user,
            full_name=user.full_name,
            username=user.username,
            email=user.email,
        )
        return AuthSigninOutput(
            user=user_info,
            access_token=token.access_token,
            token_type="bearer",
            expires_at=expires_at,
        )


AuthService = Annotated[_AuthService, Depends(_AuthService)]
