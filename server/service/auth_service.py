import logging
from typing import Annotated, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from server.configuration.database import DepDatabaseSession
from server.model.user import User
from server.repository.auth_repository import AuthRepository, _AuthRepository
from server.schema.auth_schema import (
    AccountDeactivatedByUser,
    AuthSigninOutput,
    UpdateUserFlActiveByAdmin,
    UserInfoForAdminOutput,
    UserInfoOutput,
)
from server.utils.auth import generate_token, get_expiration_time, validate_credentials
from server.utils.dependencies import DepUserPayload
from server.utils.error import ClientBottleException, CodigoErro
from server.utils.types import SessionPayload


class _AuthService:
    def __init__(self, db: DepDatabaseSession):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.repository: _AuthRepository = AuthRepository(db)

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm) -> AuthSigninOutput:
        user = await self.validate_credentials(form_data)
        return await self.create_auth_signin_output(user)

    async def create_auth_signin_output(self, user: User) -> AuthSigninOutput:
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

    async def validate_credentials(self, form_data: OAuth2PasswordRequestForm) -> User:
        user = await validate_credentials(self.db, form_data)
        if not user:
            raise ClientBottleException([CodigoErro.CREDENCIAIS_INVALIDAS])
        elif not user.fl_active:
            await self.reactivate_account_if_needed(user)
        return user

    async def reactivate_account_if_needed(self, user: User):
        if user.update_user_id == user.id_user:
            await self.repository.update_user_fl_active(user, user.id_user, True)
        else:
            raise ClientBottleException([CodigoErro.USUARIO_INATIVO])

    async def delete_current_account(self, user: SessionPayload):
        await self.repository.delete_current_account(user)
        self.logger.info(f"User {user.full_name} deleted account")
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"message": "Conta deletada com sucesso."}
        )

    async def deactivate_user_by_admin(
        self, admin: SessionPayload, data: UpdateUserFlActiveByAdmin
    ) -> UserInfoForAdminOutput:
        self.logger.info(
            f"Initiating request for administrator {admin.username}-{admin.email} to deactivate account {data=}"
        )
        user_to_deactivate = await self.repository.get_user(
            id_user=data.id_user, email=data.email, username=data.username
        )

        if not user_to_deactivate:
            self.logger.error("User not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado",
            )
        elif len(user_to_deactivate) > 1:
            self.logger.error("More than one user found")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Mais de um usuário encontrado. Reveja os dados informados e tente novamente.",
            )
        elif not user_to_deactivate[0].fl_active:
            self.logger.error("User is already deactivated")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário já está desativado",
            )

        updated_user = await self.repository.update_user_fl_active(
            user_to_deactivate[0], admin.id_user, False
        )
        return UserInfoForAdminOutput.model_validate(updated_user)

    async def reactivate_user_by_admin(
        self, admin: SessionPayload, data: UpdateUserFlActiveByAdmin
    ) -> UserInfoForAdminOutput:
        self.logger.info(
            f"Initiating request for administrator {admin.username}-{admin.email} to reactivate account {data=}"
        )
        user_to_reactivate = await self.repository.get_user(
            id_user=data.id_user, email=data.email, username=data.username
        )

        if not user_to_reactivate:
            self.logger.error("User not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado",
            )
        elif len(user_to_reactivate) > 1:
            self.logger.error("More than one user found")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Mais de um usuário encontrado. Reveja os dados informados e tente novamente.",
            )
        elif user_to_reactivate[0].fl_active:
            self.logger.error("User is already active")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário já está ativo",
            )

        updated_user = await self.repository.update_user_fl_active(
            user_to_reactivate[0], admin.id_user, True
        )
        return UserInfoForAdminOutput.model_validate(updated_user)

    async def get_all_users(self, admin: SessionPayload) -> Optional[List[UserInfoForAdminOutput]]:
        self.logger.info(f"Getting all users for admin {admin=}")
        users = await self.repository.get_all_users()
        return [UserInfoForAdminOutput.model_validate(user) for user in users]

    async def deactivate_own_account(self, user: DepUserPayload):
        self.logger.info(f"User {user.username} is deactivating their account")
        user = await self.repository.get_user(id_user=user.id_user)
        updated_user = await self.repository.update_user_fl_active(user[0], user[0].id_user, False)
        user_output = AccountDeactivatedByUser.model_validate(updated_user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Conta desativada com sucesso. Você pode reativá-la a qualquer momento.",
                "user": user_output.model_dump(),
            },
        )


AuthService = Annotated[_AuthService, Depends(_AuthService)]
