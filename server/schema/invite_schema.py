import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, ValidationError, model_validator

from server.model.role import UserRole


class InviteCreate(BaseModel):
    email: EmailStr

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            raise HTTPException(
                status_code=400,
                detail="Formato de email inválido. Siga o padrão 'example@gmail.com'.",
            )


class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str


class UserCreated(BaseModel):
    full_name: str
    email: str
    role: UserRole
    fl_active: bool = True


class RecoverPasswordSchema(BaseModel):
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
        email = values.get("email")
        username = values.get("username")
        if not email and not username:
            raise HTTPException(
                status_code=400,
                detail="Pelo menos um dos campos 'email' ou 'username' deve ser fornecido.",
            )
        return values


class NewHashedPassword(BaseModel):
    new_password: str
