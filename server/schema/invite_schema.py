import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator

from server.model.role import UserRole

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class InviteCreate(BaseModel):
    email: str

    def __init__(self, **data):
        super().__init__(**data)
        if not EMAIL_REGEX.match(self.email):
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
    email: Optional[str] = Field(None)
    username: Optional[str] = Field(None)

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

    @model_validator(mode="after")
    @classmethod
    def check_email(cls, values):
        email = values.email
        if email and not EMAIL_REGEX.match(email):
            raise HTTPException(
                status_code=400,
                detail="Formato de email inválido. Siga o padrão 'example@gmail.com'.",
            )
        return values


class NewHashedPassword(BaseModel):
    new_password: str
