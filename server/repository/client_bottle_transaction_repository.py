import logging
from typing import Annotated, List, Optional

from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate


from fastapi import Depends, HTTPException
from sqlalchemy import String, func, or_, select, text
from server.configuration.database import DepDatabaseSession
from server.model.bottle_brand import BottleBrand
from server.model.client import Client
from server.model.client_bottle_transaction import ClientBottleTransaction
from server.repository.bottle_brand_repository import _BottleBrandRepository, BottleBrandRepository

from server.schema.transaction_schema import BottleBrandInput
from server.schema.transaction_schema import TransactionCreateInput, TransactionOutput
from datetime import date

from server.utils.types import SessionPayload
from server.utils.utils import get_first_record_as_dict, process_transaction_data


class _TransactionRepository:
    def __init__(self, db: DepDatabaseSession):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def get_paginated_transactions(self, page: int, size: int) -> Page[TransactionOutput]:
        query = (
            select(
                ClientBottleTransaction.id_client_bottle_transaction,
                Client.name.label("client_name"),
                Client.last_name.label("client_last_name"),
                Client.phone.label("client_phone"),
                ClientBottleTransaction.transaction_data_json.label("transaction_data"),
                ClientBottleTransaction.transaction_date,
                ClientBottleTransaction.recorded_by,
            )
            .join(Client, Client.id_client == ClientBottleTransaction.id_client)
            .where(ClientBottleTransaction.fl_active == True)
            .order_by(ClientBottleTransaction.transaction_date.desc())
            .limit(size)
            .offset((page - 1) * size)
        )
        transactions = await paginate(self.db, query, unique=False)
        return await process_transaction_data(transactions, self.db)

    async def get_paginated_transactions_by_term(
        self, page: int, size: int, term: str
    ) -> Page[TransactionOutput]:
        term_pattern = f"%{term}%"
        query = (
            select(
                ClientBottleTransaction.id_client_bottle_transaction,
                Client.name.label("client_name"),
                Client.last_name.label("client_last_name"),
                Client.phone.label("client_phone"),
                ClientBottleTransaction.transaction_data_json.label("transaction_data"),
                ClientBottleTransaction.transaction_date,
                ClientBottleTransaction.recorded_by,
            )
            .join(Client, Client.id_client == ClientBottleTransaction.id_client)
            .where(
                ClientBottleTransaction.fl_active == True,
                or_(
                    Client.name.ilike(term_pattern),
                    Client.phone.ilike(term_pattern),
                    ClientBottleTransaction.recorded_by.ilike(term_pattern),
                    func.cast(ClientBottleTransaction.transaction_data_json, String).ilike(
                        term_pattern
                    ),
                ),
            )
            .order_by(ClientBottleTransaction.transaction_date.desc())
            .limit(size)
            .offset((page - 1) * size)
        )
        transactions = await paginate(self.db, query, unique=False)
        return await process_transaction_data(transactions, self.db)

    async def get_paginated_transactions_by_date(
        self, page: int, size: int, date_filter: date
    ) -> Page[TransactionOutput]:
        query = (
            select(
                ClientBottleTransaction.id_client_bottle_transaction,
                Client.name.label("client_name"),
                Client.last_name.label("client_last_name"),
                Client.phone.label("client_phone"),
                ClientBottleTransaction.transaction_data_json.label("transaction_data"),
                func.date(ClientBottleTransaction.transaction_date).label("transaction_date"),
                ClientBottleTransaction.recorded_by,
            )
            .join(Client, Client.id_client == ClientBottleTransaction.id_client)
            .where(
                ClientBottleTransaction.fl_active == True,
                func.date(ClientBottleTransaction.transaction_date) == date_filter,
            )
            .order_by(ClientBottleTransaction.transaction_date.desc())
            .limit(size)
            .offset((page - 1) * size)
        )
        transactions = await paginate(self.db, query, unique=False)
        return await process_transaction_data(transactions, self.db)

    async def get_client(self, name: str, last_name: str) -> Optional[Client]:
        name_pattern = f"%{name}%" if name else None
        last_name_pattern = f"%{last_name}%" if last_name else None
        query = text(
            """
            SELECT *
            FROM client
            WHERE public.unaccent(LOWER(name)) LIKE public.unaccent(LOWER(:name)) AND public.unaccent(LOWER(last_name)) LIKE public.unaccent(LOWER(:last_name))
            """
        )
        result = await self.db.execute(
            query, {"name": name_pattern, "last_name": last_name_pattern}
        )
        client_dict = await get_first_record_as_dict(result)
        if client_dict and client_dict != {}:
            return Client(**client_dict)
        return None

    async def post_client(self, data: TransactionCreateInput, user: SessionPayload) -> Client:
        new_client = Client(
            name=data.client_name,
            last_name=data.last_name,
            phone=data.client_phone,
            creation_user_id=user.id_user,
        )
        self.db.add(new_client)
        await self.db.commit()
        await self.db.refresh(new_client)
        return new_client

    async def get_or_post_client(
        self, data: TransactionCreateInput, user: SessionPayload
    ) -> Client:
        client = await self.get_client(data.client_name, data.last_name)
        if not client:
            client = await self.post_client(data, user)
        return client

    async def get_or_post_bottle_brand(
        self, item: BottleBrandInput, user: SessionPayload
    ) -> BottleBrand:
        brand_repository: _BottleBrandRepository = BottleBrandRepository(self.db)
        brand = await brand_repository.get_bottle_brand(item.brand_name, item.brand_id)
        if not brand:
            brand = await brand_repository.create_bottle_brand(
                creation_user_id=user.id_user, name=item.brand_name
            )
        return brand

    async def create_transaction(
        self, client_id: int, transaction_data_json: list, recorded_by: Optional[str], id_user: int
    ) -> ClientBottleTransaction:
        try:
            new_transaction = await ClientBottleTransaction.create(
                creation_user_id=id_user,
                id_client=client_id,
                transaction_data_json=transaction_data_json,
                recorded_by=recorded_by,
            )
            self.db.add(new_transaction)
            await self.db.flush()
            await self.db.refresh(new_transaction)
            await self.db.commit()

            return new_transaction
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Error creating transaction: {e}")
            raise e

    async def get_transaction_output(self, id_client_bottle_transaction: int) -> TransactionOutput:
        query = text(
            """
            SELECT cbt.id_client_bottle_transaction,
                c.name                    AS client_name,
                c.last_name               AS client_last_name,
                c.phone                   AS client_phone,
                cbt.transaction_data_json AS transaction_data,
                cbt.transaction_date,
                cbt.recorded_by
            FROM client_bottle_transaction cbt
                    JOIN client c ON cbt.id_client = c.id_client
            WHERE cbt.id_client_bottle_transaction = :id_client_bottle_transaction
            """
        )
        result = await self.db.execute(
            query, {"id_client_bottle_transaction": id_client_bottle_transaction}
        )
        transaction_dict = await get_first_record_as_dict(result)
        if transaction_dict and transaction_dict != {}:
            transaction_data = transaction_dict["transaction_data"]
            for item in transaction_data:
                brand_name = await self.get_brand_name_by_id(item["brand_id"])
                item["brand_name"] = brand_name
            transaction_dict["transaction_data"] = transaction_data
            return TransactionOutput(**transaction_dict)
        return None

    async def get_brand_name_by_id(self, brand_id: int) -> Optional[str]:
        query = text(
            """
            SELECT name 
            FROM bottle_brand 
            WHERE id_bottle_brand = :brand_id
            """
        )
        result = await self.db.execute(query, {"brand_id": brand_id})
        brand_dict = await get_first_record_as_dict(result)
        return brand_dict.get("name") if brand_dict else None

    async def get_transaction_by_id(
        self, transaction_id: int
    ) -> Optional[ClientBottleTransaction]:
        result = await self.db.execute(
            select(ClientBottleTransaction).where(
                ClientBottleTransaction.id_client_bottle_transaction == transaction_id
            )
        )
        return result.scalars().one_or_none()

    async def get_client_by_id(self, client_id: int) -> Optional[Client]:
        result = await self.db.execute(select(Client).where(Client.id_client == client_id))
        return result.scalars().one_or_none()

    async def update_client(
        self,
        client_id: int,
        client_name: Optional[str],
        last_name: Optional[str],
        client_phone: Optional[str],
        user: SessionPayload,
    ) -> None:
        if client_id is not None:
            client = await self.get_client_by_id(client_id)
        else:
            client = await self.get_client(client_name, last_name)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        if client_name is not None:
            client.name = client_name
        if last_name is not None:
            client.last_name = last_name
        if client_phone is not None:
            client.phone = client_phone
        client.update_user_id = user.id_user

        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)

    async def update_transaction(
        self,
        transaction_id: int,
        transaction_data_json: list,
        recorded_by: Optional[str],
        id_user: int,
    ) -> None:
        transaction = await self.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        transaction.transaction_data_json = transaction_data_json
        transaction.recorded_by = recorded_by
        transaction.update_user_id = id_user

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        
        
    async def deactivate_transaction(self, transaction_id: int, user: SessionPayload):
        transaction = await self.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        transaction.fl_active = False
        transaction.update_user_id = user.id_user
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)


TransactionRepository = Annotated[_TransactionRepository, Depends(_TransactionRepository)]
