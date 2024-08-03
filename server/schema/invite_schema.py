import re

from fastapi import HTTPException
from pydantic import BaseModel

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
