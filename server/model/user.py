import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.base import Mapped

from server.model.meta import Base, BaseEntity
from server.model.role import UserRole


class LoggingId(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[int] = None


class User(Base, BaseEntity):
    __tablename__ = "user"

    id_user: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
