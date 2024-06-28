import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

from server.model.bottle_brand import BottleBrand
from server.model.meta import Base, BaseEntity


class Client(Base, BaseEntity):
    __tablename__ = "client"

    id_client: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
