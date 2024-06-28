from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

from server.model.bottle_brand import BottleBrand
from server.model.meta import Base, BaseEntity

class Bottle(Base, BaseEntity):
    __tablename__ = "bottle"
    
    id_bottle: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_bottle_brand: Mapped[int] = mapped_column(Integer, ForeignKey("bottle_brand.id_bottle_brand"))

    rl_bottle_brand: Mapped[BottleBrand] = relationship(foreign_keys=[id_bottle_brand])