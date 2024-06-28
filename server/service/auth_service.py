from typing import Annotated

from fastapi import Depends
from server.configuration.database import DepDatabaseSession
from server.lib.error import ClientBottleException, CodigoErro
from server.repository.auth_repository import _AuthRepository, AuthRepository
from server.schema.auth_schema import UserLoginInput, UserLoginOutput


class _AuthService:
    def __init__(self, db: DepDatabaseSession):
        self.db = db
        self.repository: _AuthRepository = AuthRepository(db)

    async def update_api_key(self, user):
        new_api_key = await self.repository.generate_api_key()
        await self.repository.update_api_key(user, new_api_key)
        return new_api_key

    async def authenticate(self, user_input: UserLoginInput) -> UserLoginOutput:
        user = await self.repository.get_by_email_or_username(user_input.email_or_username)
        if user:
            if not user.fl_active:
                raise ClientBottleException(errors=[CodigoErro.USUARIO_INATIVO], status_code=401)
            user = await self.repository.verify_password(user, user_input.password)
            if user:
                api_key = await self.update_api_key(user)
                return UserLoginOutput(
                    id_user=user.id_user,
                    full_name=user.full_name,
                    username=user.username,
                    email=user.email,
                    api_key=api_key,
                    created_at=user.created_at,
                )
            else:
                raise ClientBottleException(
                    errors=[CodigoErro.CREDENCIAIS_INVALIDAS], status_code=401
                )
        else:
            raise ClientBottleException(
                errors=[CodigoErro.DS_LOGIN_NAO_ENCONTRADO], status_code=401
            )


AuthService = Annotated[_AuthService, Depends(_AuthService)]
