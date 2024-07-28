from datetime import datetime

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
    fl_active: bool
    role: UserRole
    creation_user_id: int
    created_at: datetime
    jti: str
    exp: datetime

    @field_validator("created_at", "exp", mode="before")
    def set_timezone(cls, value):
        if isinstance(value, int):
            value = datetime.fromtimestamp(value, tz=timezone_brazil)
        elif isinstance(value, datetime):
            if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
                value = value.replace(tzinfo=timezone("UTC")).astimezone(timezone_brazil)
            else:
                value = value.astimezone(timezone_brazil)
        return value
