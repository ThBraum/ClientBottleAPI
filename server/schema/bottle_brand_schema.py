from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator


class BottleBrandCreate(BaseModel):
    name: str = Field(
        ...,
        title="Nome da marca da garrafa",
        description="Nome da marca da garrafa.",
        min_length=1,
    )


class BottleBrandOutput(BaseModel):
    id_bottle_brand: int
    name: str

    class Config:
        from_attributes = True


class BottleBrandUpdate(BaseModel):
    id_bottle_brand: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    new_name: str = Field(
        ..., title="Novo nome da marca da garrafa", description="Novo nome da marca da garrafa."
    )

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values):
        if not values.get("id_bottle_brand") and not values.get("name"):
            raise HTTPException(
                status_code=400,
                detail="Pelo menos um dos campos 'id_bottle_brand' ou 'name' deve ser fornecido.",
            )
        if values.get("id_bottle_brand") and values.get("name"):
            raise HTTPException(
                status_code=400,
                detail="Apenas um dos campos 'id_bottle_brand' ou 'name' deve ser fornecido, nunca ambos.",
            )
        return values


class BottleBrandInput(BaseModel):
    id_bottle_brand: Optional[int] = Field(None)
    name: Optional[str] = Field(None)

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values):
        if not values.get("id_bottle_brand") and not values.get("name"):
            raise HTTPException(
                status_code=400,
                detail="Pelo menos um dos campos 'id_bottle_brand' ou 'name' deve ser fornecido.",
            )
        if values.get("id_bottle_brand") and values.get("name"):
            raise HTTPException(
                status_code=400,
                detail="Apenas um dos campos 'id_bottle_brand' ou 'name' deve ser fornecido, nunca ambos.",
            )
        return values
