from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, model_validator

from datetime import date

from server.model.role import UserRole


class BottleBrandData(BaseModel):
    brand_id: Optional[int] = None
    brand: Optional[str] = None
    quantity: Optional[int] = None


class TransactionOutput(BaseModel):
    id_client_bottle_transaction: Optional[int] = None
    client_name: Optional[str] = None
    client_last_name: Optional[str] = None
    client_phone: Optional[str] = None
    transaction_data: Optional[List[BottleBrandData]] = None
    transaction_date: Optional[date] = None
    recorded_by: Optional[str] = None

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id_user: int
    username: str
    email: EmailStr
    full_name: str
    role: UserRole

    class Config:
        from_attributes = True


class BottleBrandInput(BaseModel):
    brand_id: Optional[int] = None
    brand_name: Optional[str] = None
    quantity: int

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values):
        if not values.get("brand_id") and not values.get("brand_name"):
            raise HTTPException(
                status_code=400,
                detail="Pelo menos um dos campos 'brand_id' ou 'brand_name' deve ser fornecido.",
            )
        if values.get("brand_id") and values.get("brand_name"):
            raise HTTPException(
                status_code=400,
                detail="Apenas um dos campos 'brand_id' ou 'brand_name' deve ser fornecido, nunca ambos.",
            )
        return values


class TransactionCreateInput(BaseModel):
    client_name: str
    last_name: str
    client_phone: Optional[str] = None
    transaction_data: List[BottleBrandInput]
