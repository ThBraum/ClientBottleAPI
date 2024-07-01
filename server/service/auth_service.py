from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from server.configuration.database import DepDatabaseSession
from server.lib.auth import (
    create_user_token,
    generate_unique_token,
    get_expiration_time,
    validate_credentials,
)
from server.lib.error import ClientBottleException, CodigoErro
from server.model.user import User
from server.schema.auth_schema import AuthSigninOutput, TokenOutput, UserInfoOutput


class _AuthService:
    def __init__(self, db: DepDatabaseSession):
        self.db = db

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm) -> AuthSigninOutput:
        user = await validate_credentials(self.db, form_data)

        expires_at = get_expiration_time()
        token = await generate_unique_token(self.db, user, expires_at)
        await create_user_token(self.db, user, token.access_token, token.expires_at)

        user_info = UserInfoOutput(
            id_user=user.id_user,
            full_name=user.full_name,
            username=user.username,
            email=user.email,
        )
        return AuthSigninOutput(user=user_info, token=token)


AuthService = Annotated[_AuthService, Depends(_AuthService)]
