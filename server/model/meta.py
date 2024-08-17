import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, MetaData, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column, relationship

if TYPE_CHECKING:
    from server.model.user import User


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class BaseMethodEntity:
    __abstract__ = True

    @classmethod
    def create(cls, creation_user_id: Optional[int], **kwargs):
        return cls(creation_user_id=creation_user_id, **kwargs)

    def update(self, update_user_id: Optional[int], **kwargs):
        self.update_user_id = update_user_id
        for key, value in kwargs.items():
            setattr(self, key, value)


CURRENT_TIMESTAMP_BRAZIL = text("current_timestamp_brazil()")


class BaseEntity(BaseMethodEntity):
    __abstract__ = True

    fl_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=CURRENT_TIMESTAMP_BRAZIL, nullable=False
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP_BRAZIL,
        onupdate=CURRENT_TIMESTAMP_BRAZIL,
        nullable=True,
    )
    creation_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id_user"), index=True, server_default="1"
    )
    update_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id_user"), index=True)

    @declared_attr
    def rl_creation_user(cls) -> Mapped["User"]:
        return relationship(foreign_keys=[cls.creation_user_id])

    @declared_attr
    def rl_update_user(cls) -> Mapped[Optional["User"]]:
        return relationship(foreign_keys=[cls.update_user_id])
