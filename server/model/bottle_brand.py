from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

from server.model.meta import Base, BaseEntity

class BottleBrand(Base, BaseEntity):
    __tablename__ = "bottle_brand"
    
    id_bottle_brand: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

