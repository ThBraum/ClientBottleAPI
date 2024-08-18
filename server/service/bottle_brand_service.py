import logging
from typing import Annotated, List, Optional

from fastapi import Depends, HTTPException, status

from server.configuration.database import DepDatabaseSession
from server.repository.bottle_brand_repository import BottleBrandRepository, _BottleBrandRepository
from server.schema.bottle_brand_schema import (
    BottleBrandCreate,
    BottleBrandInput,
    BottleBrandOutput,
    BottleBrandUpdate,
)
from server.utils.types import SessionPayload


class _BottleBrandService:
    def __init__(self, db: DepDatabaseSession):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.repository: _BottleBrandRepository = BottleBrandRepository(db)

    async def create_bottle_brand(
        self, user: SessionPayload, data: BottleBrandCreate
    ) -> BottleBrandOutput:
        existing_brand = await self.repository.get_bottle_brand(name=data.name)
        if existing_brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uma marca com esse nome já existe.",
            )
        new_brand = await self.repository.create_bottle_brand(
            creation_user_id=user.id_user, name=data.name
        )
        return BottleBrandOutput.model_validate(new_brand)

    async def update_bottle_brand(
        self, user: SessionPayload, data: BottleBrandUpdate
    ) -> BottleBrandOutput:
        bottle_brand = await self.repository.get_bottle_brand(data.name, data.id_bottle_brand)
        if not bottle_brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Marca não encontrada."
            )

        if data.new_name and await self.repository.get_bottle_brand(name=data.new_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma marca com esse nome.",
            )
        updated_brand = await self.repository.update_bottle_brand(
            bottle_brand, update_user_id=user.id_user, new_name=data.new_name
        )
        return BottleBrandOutput.model_validate(updated_brand)

    async def get_all_bottle_brands(
        self, user: SessionPayload
    ) -> Optional[List[BottleBrandOutput]]:
        self.logger.info("Getting all bottle brands")
        brands = await self.repository.get_all_bottle_brands()
        return [BottleBrandOutput.model_validate(brand) for brand in brands]

    async def get_bottle_brand(
        self, user: SessionPayload, data: BottleBrandInput
    ) -> Optional[BottleBrandOutput]:
        self.logger.info("Getting bottle brand by name or id")
        bottle_brand = await self.repository.get_bottle_brand(data.name, data.id_bottle_brand)
        if not bottle_brand:
            self.logger.error(
                f"Bottle brand id: {data.id_bottle_brand} - name: {data.name} not found"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Marca não encontrada."
            )
        return BottleBrandOutput.model_validate(bottle_brand)

    async def delete_bottle_brand(
        self, user: SessionPayload, data: BottleBrandInput
    ) -> Optional[BottleBrandOutput]:
        self.logger.info("Deleting bottle brand")
        bottle_brand = await self.repository.get_bottle_brand(data.name, data.id_bottle_brand)
        if not bottle_brand:
            self.logger.error(f"Bottle brand {data.id_bottle_brand} - {data.name} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Marca não encontrada.",
            )
        await self.repository.delete_bottle_brand(bottle_brand.id_bottle_brand)
        return BottleBrandOutput.model_validate(bottle_brand)


BottleBrandService = Annotated[_BottleBrandService, Depends(_BottleBrandService)]
