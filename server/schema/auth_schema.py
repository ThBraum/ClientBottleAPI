from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, ValidationError, model_validator

from server.model.role import UserRole


class UserLoginInput(BaseModel):
    email_or_username: str
    password: str


class UserInfoOutput(BaseModel):
    id_user: int
    full_name: str
    username: str
    email: str

    class Config:
        from_attributes = True


class AuthSigninOutput(BaseModel):
    user: Optional[UserInfoOutput] = None
    access_token: str
    token_type: str
    expires_at: datetime

    class Config:
        from_attributes = True


class UserTokenInfoOutput(BaseModel):
    id_user: int
    username: str
    full_name: str
    email: str
    fl_active: bool
    expires_at: datetime
    api_key: str

    class Config:
        from_attributes = True


class TokenLoginOutput(BaseModel):
    token_type: str
    access_token: str

    class Config:
        from_attributes = True


class UpdateUserFlActiveByAdmin(BaseModel):
    id_user: Optional[int] = Field(None)
    email: Optional[EmailStr] = Field(None)
    username: Optional[str] = Field(None)

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            raise HTTPException(
                status_code=400,
                detail="Formato de email inválido. Siga o padrão 'example@gmail.com'.",
            )

    @model_validator(mode="before")
    @classmethod
    def at_least_one(cls, values):
        id_user = values.get("id_user")
        email = values.get("email")
        username = values.get("username")
        if not id_user and not email and not username:
            raise HTTPException(
                status_code=400,
                detail="Pelo menos um dos campos 'id_user', 'email' ou 'username' deve ser fornecido.",
            )
        return values


class UserInfoForAdminOutput(BaseModel):
    id_user: int
    username: str
    full_name: str
    email: str
    creation_user_id: int
    update_user_id: Optional[int] = None
    fl_active: bool
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AccountDeactivatedByUser(BaseModel):
    id_user: int
    full_name: str
    username: str
    email: str
    fl_active: bool

    class Config:
        from_attributes = True
