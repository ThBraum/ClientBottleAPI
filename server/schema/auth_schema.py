from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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
