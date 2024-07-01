from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from server.lib.dependencies import DepUser
from server.model.user import User
from server.schema.auth_schema import AuthSigninOutput, UserLoginInput
from server.service.auth_service import AuthService

router = APIRouter(prefix="/server/auth", tags=["User"])


@router.post("/login/", response_model=AuthSigninOutput)
async def login(service: AuthService, form_data: OAuth2PasswordRequestForm = Depends()):
    return await service.authenticate_user(form_data)


@router.get("/me/")
async def me(user: DepUser):
    return user
