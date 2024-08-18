import logging
from typing import Annotated, List, Optional

from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy import or_, select, text

from server.configuration.database import DepDatabaseSession
from server.model.user import User
from server.utils.types import SessionPayload


class _AuthRepository:
    def __init__(self, db: DepDatabaseSession):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def delete_current_account(self, user: SessionPayload):
        query = text(
            """
            DELETE
            FROM "user"
            WHERE id_user = :id_user
            """
        )
        await self.db.execute(query, {"id_user": user.id_user})
        await self.db.commit()

    async def get_user(
        self,
        id_user: Optional[int] = None,
        email: Optional[EmailStr] = None,
        username: Optional[str] = None,
    ) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(
                or_(
                    User.id_user == id_user,
                    User.email == email,
                    User.username == username,
                )
            )
        )
        return result.scalars().all()

    async def get_all_users(self) -> Optional[List[User]]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def update_user_fl_active(
        self, user: User, update_user_id: int, fl_active: bool
    ) -> User:
        await user.update(update_user_id=update_user_id, fl_active=fl_active)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


AuthRepository = Annotated[_AuthRepository, Depends(_AuthRepository)]
