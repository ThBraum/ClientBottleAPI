from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

from server.model.meta import Base, BaseEntity
from server.model.user import User


class UserToken(Base, BaseEntity):
    __tablename__ = "user_token"

    id_user_token: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_user: Mapped[int] = mapped_column(ForeignKey("user.id_user"), index=True)
    api_key: Mapped[str] = mapped_column(String, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship("User", back_populates=None, foreign_keys=[id_user])
