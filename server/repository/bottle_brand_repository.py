import logging
from typing import Annotated, List, Optional

from fastapi import Depends
from sqlalchemy import delete, select, text

from server.configuration.database import DepDatabaseSession
from server.model.bottle_brand import BottleBrand
from server.schema.bottle_brand_schema import BottleBrandUpdate
from server.utils.types import SessionPayload
from server.utils.utils import get_first_record_as_dict


class _BottleBrandRepository:
    def __init__(self, db: DepDatabaseSession):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def create_bottle_brand(self, creation_user_id: int, name: str) -> Optional[BottleBrand]:
        new_brand = await BottleBrand.create(creation_user_id=creation_user_id, name=name)
        self.db.add(new_brand)
        await self.db.commit()
        await self.db.refresh(new_brand)
        return new_brand

    async def get_all_bottle_brands(self) -> List[BottleBrand]:
        result = await self.db.execute(select(BottleBrand))
        return result.scalars().all()

    async def get_bottle_brand(
        self, name: Optional[str] = None, id_bottle_brand: Optional[int] = None
    ) -> Optional[BottleBrand]:
        name_pattern = f"%{name}%" if name else None
        query = text(
            """
            SELECT *
            FROM bottle_brand
            WHERE public.unaccent(LOWER(name)) ILIKE public.unaccent(LOWER(:name))
            OR id_bottle_brand = :id_bottle_brand
            """
        )
        result = await self.db.execute(
            query, {"name": name_pattern, "id_bottle_brand": id_bottle_brand}
        )
        brand_dict = await get_first_record_as_dict(result)

        if brand_dict and brand_dict != {}:
            return BottleBrand(**brand_dict)
        return None

    async def update_bottle_brand(
        self, bottle_brand: BottleBrand, update_user_id: int, new_name: str
    ) -> BottleBrand:
        query = text(
            """
            UPDATE bottle_brand
            SET update_user_id = :update_user_id,
                name           = :name
            WHERE id_bottle_brand = :id_bottle_brand
            """
        )
        await self.db.execute(
            query,
            {
                "update_user_id": update_user_id,
                "name": new_name,
                "id_bottle_brand": bottle_brand.id_bottle_brand,
            },
        )
        await self.db.commit()
        result = await self.db.execute(
            select(BottleBrand).where(BottleBrand.id_bottle_brand == bottle_brand.id_bottle_brand)
        )
        return result.scalars().one_or_none()

    async def delete_bottle_brand(self, id_bottle_brand: int):
        await self.db.execute(
            delete(BottleBrand).where(BottleBrand.id_bottle_brand == id_bottle_brand)
        )
        await self.db.commit()


BottleBrandRepository = Annotated[_BottleBrandRepository, Depends(_BottleBrandRepository)]
