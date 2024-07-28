from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.model.meta import Base, BaseEntity
from server.model.role import UserRole
from server.model.user import User


class Invite(Base, BaseEntity):
    __tablename__ = "invite"

    id_invite: Mapped[int] = mapped_column(Integer, primary_key=True)

    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id_user"), index=True)
    token: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    expires_at: Mapped[datetime] = mapped_column(DateTime)

    rl_user: Mapped["User"] = relationship(foreign_keys=[sender_id])
