from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.model.meta import Base, BaseEntity
from server.model.user import User


class RecoverPassword(Base, BaseEntity):
    __tablename__ = "recover_password"

    id_recover_password: Mapped[int] = mapped_column(Integer, primary_key=True)

    id_user: Mapped[int] = mapped_column(ForeignKey("user.id_user"), index=True)
    token: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True)

    rl_user: Mapped["User"] = relationship(foreign_keys=[id_user])
