import logging
from typing import Annotated, Optional

from fastapi import Depends

from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate

from server.configuration.database import DepDatabaseSession
from server.model.client import Client
from server.model.client_bottle_transaction import ClientBottleTransaction
from server.repository.client_bottle_transaction_repository import (
    _TransactionRepository,
    TransactionRepository,
)
from server.schema.transaction_schema import (
    BottleBrandData,
    TransactionCreateInput,
    TransactionOutput,
)
from datetime import date
from sqlalchemy.exc import NoResultFound

from server.utils.types import SessionPayload


class _TransactionService:
    def __init__(self, db: DepDatabaseSession):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.repository: _TransactionRepository = TransactionRepository(db)

    async def get_paginated_transactions(
        self, page: int, size: int, term: Optional[str] = None, date_filter: Optional[date] = None
    ) -> Page[TransactionOutput]:
        if not term and not date_filter:
            self.logger.info("Getting all transactions")
            return await self.repository.get_paginated_transactions(page, size)
        elif term and not date_filter:
            self.logger.info(f"Searching transactions with term: {term}")
            return await self.repository.get_paginated_transactions_by_term(page, size, term)
        else:
            self.logger.info(f"Filtering transactions by date: {date_filter}")
            return await self.repository.get_paginated_transactions_by_date(
                page, size, date_filter
            )

    async def post_transaction(
        self, transaction_input: TransactionCreateInput, user: SessionPayload
    ) -> TransactionOutput:
        client = await self.repository.get_or_post_client(transaction_input, user)

        transaction_data_json = await self.prepare_transaction_data(transaction_input, user)

        new_transaction = await self.repository.create_transaction(
            client_id=client.id_client,
            transaction_data_json=transaction_data_json,
            recorded_by=user.full_name,
            id_user=user.id_user,
        )
        if not new_transaction:
            raise NoResultFound("Transaction not found")
        complete_data = await self.repository.get_transaction_output(
            new_transaction.id_client_bottle_transaction
        )
        self.logger.info(f"new transaction: {complete_data}")

        self.logger.info(f"Creating transaction for client: {transaction_input.client_name}")
        return TransactionOutput.model_validate(complete_data)

    async def prepare_transaction_data(
        self, transaction_input: TransactionCreateInput, user: SessionPayload
    ) -> list:
        transaction_data_json = []
        for item in transaction_input.transaction_data:
            brand = await self.repository.get_or_post_bottle_brand(item, user)
            transaction_data_json.append(
                {"brand_id": brand.id_bottle_brand, "quantity": item.quantity}
            )
        return transaction_data_json


TransactionService = Annotated[_TransactionService, Depends(_TransactionService)]
