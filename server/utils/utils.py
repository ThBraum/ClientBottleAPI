import unicodedata
from typing import Any, Dict, Optional

from fastapi_pagination import Page
from sqlalchemy import select

from server.configuration.database import DepDatabaseSession
from server.model.bottle_brand import BottleBrand
from server.schema.transaction_schema import TransactionOutput


def normalize_string(input_str):
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    only_ascii = nfkd_form.encode("ASCII", "ignore").decode("ASCII")
    return only_ascii.lower()


async def get_first_record_as_dict(result) -> Dict:
    first_record = result.first()
    return dict(first_record._mapping) if first_record else {}


async def get_all_records_as_list(execution) -> list[Dict[str, Any]]:
    rows = await execution.fetchall()
    return [dict(row._mapping) for row in rows]


async def process_transaction_data(
    transactions: Page[TransactionOutput], db: DepDatabaseSession
) -> Page[TransactionOutput]:
    for transaction in transactions.items:
        if transaction.transaction_data:
            for item in transaction.transaction_data:
                brand_id = item.brand_id
                if brand_id:
                    brand_name = await get_bottle_brand_name(db, brand_id)
                    if brand_name:
                        item.brand = brand_name
    return transactions


async def get_bottle_brand_name(db: DepDatabaseSession, brand_id: int) -> Optional[str]:
    query = select(BottleBrand.name).where(BottleBrand.id_bottle_brand == brand_id)
    result = await db.execute(query)
    return result.scalar()
