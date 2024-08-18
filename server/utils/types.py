from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator
from pytz import timezone

from server.model.role import UserRole

timezone_brazil = timezone("America/Sao_Paulo")


class SessionPayload(BaseModel):
    id_user: int
    username: str
    full_name: str
    email: str
    creation_user_id: int
    update_user_id: Optional[int] = None
    fl_active: bool
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None
    jti: str
    exp: datetime

    @field_validator("exp", mode="before")
    def set_timezone(cls, value):
        if isinstance(value, int):
            value = datetime.fromtimestamp(value, tz=timezone_brazil)
        elif isinstance(value, datetime):
            value = value.astimezone(timezone_brazil)
        return value
