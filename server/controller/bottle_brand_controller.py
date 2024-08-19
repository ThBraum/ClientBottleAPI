from typing import List

from fastapi import APIRouter, Query, status

from server.schema.bottle_brand_schema import (
    BottleBrandCreate,
    BottleBrandInput,
    BottleBrandOutput,
    BottleBrandUpdate,
)
from server.service.bottle_brand_service import BottleBrandService
from server.utils.dependencies import DepUserPayload

router = APIRouter(tags=["Bottle Brand"])


@router.post(
    "/bottle-brand/",
    summary="Create a Bottle Brand",
    response_model=BottleBrandOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_bottle_brand(
    user: DepUserPayload, data: BottleBrandCreate, service: BottleBrandService
):
    return await service.create_bottle_brand(user, data)


@router.get(
    "/bottle-brands/",
    summary="Get All Bottle Brands",
    response_model=List[BottleBrandOutput],
)
async def get_all_bottle_brands(user: DepUserPayload, service: BottleBrandService):
    return await service.get_all_bottle_brands(user)


@router.get(
    "/bottle-brand/",
    summary="Get Bottle Brand by Name or ID",
    response_model=BottleBrandOutput,
)
async def get_bottle_brand(
    user: DepUserPayload,
    service: BottleBrandService,
    id_bottle_brand: int = Query(None),
    name: str = Query(None),
):
    data = BottleBrandInput(id_bottle_brand=id_bottle_brand, name=name)
    return await service.get_bottle_brand(user, data)


@router.patch(
    "/bottle-brand/",
    summary="Update Bottle Brand",
    response_model=BottleBrandOutput,
)
async def update_bottle_brand(
    user: DepUserPayload, data: BottleBrandUpdate, service: BottleBrandService
):
    return await service.update_bottle_brand(user, data)


@router.delete(
    "/bottle-brand/",
    summary="Delete Bottle Brand",
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_bottle_brand(
    user: DepUserPayload, data: BottleBrandInput, service: BottleBrandService
):
    return await service.delete_bottle_brand(user, data)
