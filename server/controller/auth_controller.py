from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from server.lib.auth import get_current_active_user
from server.lib.dependencies import DepUser
from server.model.user import User
from server.schema.auth_schema import AuthSigninOutput, UserLoginInput
from server.service.auth_service import AuthService

router = APIRouter(prefix="/server/auth", tags=["Auth"])


@router.post("/login/", summary="Login", response_model=AuthSigninOutput)
async def login(service: AuthService, form_data: OAuth2PasswordRequestForm = Depends()):
    return await service.authenticate_user(form_data)


@router.get("/me/", summary="Get Current User")
async def me(user: DepUser):
    return user
