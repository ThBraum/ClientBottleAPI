from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

from server.model.client import Client
from server.model.meta import Base, BaseEntity


class ClientBottleTransaction(Base, BaseEntity):
    __tablename__ = "client_bottle_transaction"
    __table_args__ = (
        Index("idx_transaction_data_json", "transaction_data_json", postgresql_using="gin"),
        Index("idx_transaction_date", "transaction_date"),
    )

    id_client_bottle_transaction: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_client: Mapped[int] = mapped_column(Integer, ForeignKey("client.id_client"))
    transaction_data_json: Mapped[dict] = mapped_column(JSONB)
    transaction_date: Mapped[date] = mapped_column(
        Date, server_default=text("current_timestamp_brazil()::date")
    )
    recorded_by: Mapped[Optional[str]] = mapped_column(String)

    rl_client: Mapped[Client] = relationship(foreign_keys=[id_client])
