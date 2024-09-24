import logging
from typing import Annotated, Optional

from fastapi import Depends, HTTPException

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
    TransactionUpdateInput,
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
            if not brand.id_bottle_brand:
                self.logger.error(f"Brand ID is null for brand: {brand.name}")
                raise ValueError("Brand ID is null")
            transaction_data_json.append(
                {"brand_id": brand.id_bottle_brand, "quantity": item.quantity}
            )
        return transaction_data_json
    
    async def update_transaction(
        self, transaction_id: int, transaction_input: TransactionUpdateInput, user: SessionPayload
    ) -> TransactionOutput:
        existing_transaction = await self.repository.get_transaction_by_id(transaction_id)
        if not existing_transaction:
            raise HTTPException(status_code=404, detail="Transação não encontrada")

        if any([
            transaction_input.client_name is not None,
            transaction_input.last_name is not None,
            transaction_input.client_phone is not None
        ]):
            await self.repository.update_client(
                client_id=existing_transaction.id_client,
                client_name=transaction_input.client_name,
                last_name=transaction_input.last_name,
                client_phone=transaction_input.client_phone,
                user=user,
            )

        if transaction_input.transaction_data is not None:
            transaction_data_json = await self.prepare_transaction_data(transaction_input, user)

            await self.repository.update_transaction(
                transaction_id=transaction_id,
                transaction_data_json=transaction_data_json,
                recorded_by=user.full_name,
                id_user=user.id_user,
            )

        return await self.repository.get_transaction_output(transaction_id)
    
    async def deactivate_transaction(self, transaction_id: int, user: SessionPayload):
        await self.repository.deactivate_transaction(transaction_id, user)


TransactionService = Annotated[_TransactionService, Depends(_TransactionService)]
