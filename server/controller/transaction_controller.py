from typing import Optional
from fastapi import APIRouter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate

from server.configuration.database import DepDatabaseSession
from server.model.role import UserRole
from server.model.user import User
from server.schema.transaction_schema import (
    TransactionCreateInput,
    TransactionOutput,
    TransactionUpdateInput,
    UserOut,
)

from fastapi import Query, status

from server.service.client_bottle_transaction_service import TransactionService
from server.utils.dependencies import DepUserPayload

from datetime import date


router = APIRouter(tags=["Client Bottle Transaction"])
router_test = APIRouter(tags=["Test - Pagination and AsyncSession"])


@router.get(
    "/transaction/",
    summary="Get all active transactions with filters - paginated",
    response_model=Page[TransactionOutput],
)
async def get_transactions(
    service: TransactionService,
    user: DepUserPayload,
    page: int = Query(1),
    size: int = Query(50),
    term: Optional[str] = Query(None, description="Search term"),
    date_filter: Optional[date] = Query(
        None, description="Filter by transaction date (yyyy-mm-dd)"
    ),
):
    """
    Retrieve all active transactions with pagination.

    - `page`: The page number to retrieve.
    - `size`: The number of records per page.
    - `term`: Optional search term to filter transactions by client name, phone, or recorded_by.
    - `date_filter`: Optional date filter to retrieve transactions by a specific date (yyyy-mm-dd).
    """
    return await service.get_paginated_transactions(page, size, term, date_filter)


@router.post(
    "/transaction/",
    summary="Create a new client bottle transaction",
    response_model=TransactionOutput,
    status_code=status.HTTP_201_CREATED,
)
async def post_transaction(
    transaction_input: TransactionCreateInput,
    service: TransactionService,
    user: DepUserPayload,
):
    """
    Create a new transaction for a client. If the client doesn't exist, they will be created automatically.
    """
    return await service.post_transaction(transaction_input, user)


@router.put(
    "/transaction/{transaction_id}",
    summary="Update an existing client bottle transaction",
    response_model=TransactionOutput,
    status_code=status.HTTP_200_OK,
)
async def update_transaction(
    transaction_id: int,
    transaction_input: TransactionUpdateInput,
    service: TransactionService,
    user: DepUserPayload,
):
    """
    Update an existing transaction for a client.
    """
    return await service.update_transaction(transaction_id, transaction_input, user)


@router.delete(
    "/transaction/{transaction_id}/",
    summary="Deactivate a transaction",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_transaction(
    transaction_id: int,
    service: TransactionService,
    user: DepUserPayload,
):
    """
    Deactivate a transaction without deletion, ensuring data persistence for future reports.
    This endpoint sets the transaction as inactive (`fl_active = False`) to maintain the data,
    allowing the generation of a PDF report at the end of the month that shows the relationship
    between borrowed and returned bottles. The generated report is saved in `AWS S3` for future access.
    """
    await service.deactivate_transaction(transaction_id, user)


@router_test.get("/users/me/default", response_model=Page[UserOut])
async def get_users_sql(db: DepDatabaseSession, user: DepUserPayload):
    query = select(User).where(User.fl_active == True, User.id_user == user.id_user)
    return await paginate(db, query)


@router_test.get("/users/default", response_model=Page[UserOut])
@router_test.get("/users/limit-offset", response_model=LimitOffsetPage[UserOut])
async def get_users(db: DepDatabaseSession):
    return await paginate(db, select(User))


add_pagination(router)
add_pagination(router_test)
