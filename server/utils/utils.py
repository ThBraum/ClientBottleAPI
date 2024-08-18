import unicodedata
from typing import Any, Dict


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
