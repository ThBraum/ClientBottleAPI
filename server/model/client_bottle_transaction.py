import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

from server.model.bottle import Bottle
from server.model.bottle_brand import BottleBrand
from server.model.client import Client
from server.model.meta import Base, BaseEntity


class ClientBottleTransaction(Base, BaseEntity):
    __tablename__ = "client_bottle_transaction"
    __table_args__ = (
        Index("ClientBotteTransaction_UNIQUE", "id_client", "id_bottle", "fl_active", unique=True),
    )

    id_client_bottle_transaction: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_client: Mapped[int] = mapped_column(Integer, ForeignKey("client.id_client"))
    id_bottle: Mapped[int] = mapped_column(Integer, ForeignKey("bottle.id_bottle"))
    transaction_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("current_timestamp_brazil()"),
        nullable=False,
    )
    recorded_by: Mapped[Optional[str]] = mapped_column(String)

    rl_client: Mapped[Client] = relationship(foreign_keys=[id_client])
    rl_bottle: Mapped[Bottle] = relationship(foreign_keys=[id_bottle])
