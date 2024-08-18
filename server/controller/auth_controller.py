from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from server.schema.auth_schema import (
    AccountDeactivatedByUser,
    AuthSigninOutput,
    UpdateUserFlActiveByAdmin,
    UserInfoForAdminOutput,
)
from server.service.auth_service import AuthService
from server.utils.dependencies import DepUserAdminPayload, DepUserPayload

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login/", summary="Login", response_model=AuthSigninOutput)
async def login(service: AuthService, form_data: OAuth2PasswordRequestForm = Depends()):
    return await service.authenticate_user(form_data)


@router.get("/me/", summary="Get Current User")
async def me(user: DepUserPayload):
    return user


@router.get(
    "/users/",
    summary="Get All Users - for administrators only.",
    response_model=list[UserInfoForAdminOutput],
)
async def get_all_users(admin: DepUserAdminPayload, service: AuthService):
    return await service.get_all_users(admin)


@router.patch(
    "/admin/users/deactivate/",
    summary="Disable a user account - for administrators only",
    response_model=UserInfoForAdminOutput,
)
async def deactivate_user_by_admin(
    admin: DepUserAdminPayload, service: AuthService, data: UpdateUserFlActiveByAdmin
):
    return await service.deactivate_user_by_admin(admin, data)


@router.patch(
    "/admin/users/reactivate/",
    summary="Reactivate a user account - for administrators only.",
)
async def reactivate_user_by_admin(
    admin: DepUserAdminPayload, service: AuthService, data: UpdateUserFlActiveByAdmin
):
    return await service.reactivate_user_by_admin(admin, data)


@router.patch(
    "/deactivate/me/", summary="Deactivate own account", response_model=AccountDeactivatedByUser
)
async def deactivate_own_account(user: DepUserPayload, service: AuthService):
    return await service.deactivate_own_account(user)


@router.delete("/delete/me/", summary="Delete own account")
async def delete_own_account(user: DepUserPayload, service: AuthService):
    return await service.delete_current_account(user)
