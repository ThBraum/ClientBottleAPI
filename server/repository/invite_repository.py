import logging
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import select, text

from server.configuration.database import DepDatabaseSession
from server.model.invite import Invite
from server.model.recover_password import RecoverPassword
from server.model.user import User


class _InviteRepository:
    def __init__(self, db: DepDatabaseSession):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def create_invite(self, invite: Invite):
        if not await self.already_invited(invite.email):
            if not await self.already_registered(invite.email):
                self.logger.info(f"Creating invite for {invite.email}")
                self.db.add(invite)
                await self.db.commit()
                await self.db.refresh(invite)
                self.logger.info(f"Invite created for {invite.email}")
                return invite
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Usuário já registrado com o email {invite.email}",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Convite já enviado para {invite.email}",
        )

    async def create_recover_password(
        self, recover_password: RecoverPassword
    ) -> Optional[RecoverPassword]:
        if await self.already_send_recover_password(recover_password.email):
            return await self.create_new_recover_password(recover_password)
        self.logger.info(f"Creating recover password for {recover_password.email}")
        self.db.add(recover_password)
        await self.db.commit()
        await self.db.refresh(recover_password)
        self.logger.info(f"Recover password created for {recover_password.email}")
        return recover_password

    async def already_send_recover_password(self, email: str) -> bool:
        result = await self.db.execute(
            select(RecoverPassword).where(RecoverPassword.email == email)
        )
        recover_password = result.scalars().one_or_none()
        return recover_password is not None

    async def create_new_recover_password(
        self, recover_password: RecoverPassword
    ) -> Optional[RecoverPassword]:
        await self.delete_already_send_recover_password(recover_password.email)
        self.db.add(recover_password)
        await self.db.commit()
        await self.db.refresh(recover_password)
        return recover_password

    async def delete_already_send_recover_password(self, email: str):
        result = await self.db.execute(
            select(RecoverPassword).where(RecoverPassword.email == email)
        )
        recover_password = result.scalars().one_or_none()
        self.logger.info(f"Deleting recover password for {recover_password.email}")
        await self.db.delete(recover_password)
        await self.db.commit()
        self.logger.info(f"Recover password deleted for {recover_password.email}")

    async def get_user_by_email(self, email: str) -> Optional[User]:
        self.logger.info(f"Getting user by email = {email}")
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalars().one_or_none()
        self.logger.info(f"User found for email {email}")
        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        self.logger.info(f"Getting user by username = {username}")
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalars().one_or_none()
        self.logger.info(f"User found for username {username}")
        return user

    async def get_recover_password_by_token(self, token: str):
        self.logger.info(f"Getting recover password by token = {token}")
        query = text(
            """
            SELECT token
            FROM recover_password
            WHERE token = :token
            """
        )
        result = await self.db.execute(query, {"token": token})
        return result.fetchone()

    async def get_user_by_recover_password_token(self, token: str) -> Optional[User]:
        self.logger.info(f"Getting user by recover password token = {token}")
        query = text(
            """
            SELECT "user".*
            FROM "user"
                    JOIN recover_password ON "user".id_user = recover_password.id_user
            WHERE recover_password.token = :token
            """
        )
        result = await self.db.execute(query, {"token": token})
        row = result.fetchone()
        if row:
            user_dict = dict(row._mapping)
            user = User(**user_dict)
            return user
        else:
            return None

    async def update_user_hashed_password(self, user: User):
        self.logger.info(f"Updating hashed password for user {user.email}")
        await self.db.execute(
            text(
                """
                UPDATE "user"
                SET password = :password,
                    updated_at = current_timestamp_brazil(),
                    update_user_id = id_user
                WHERE id_user = :id_user
                """
            ),
            {"password": user.password, "id_user": user.id_user},
        )
        await self.db.commit()

    async def delete_recover_password_by_token(self, token: str):
        self.logger.info(f"Deleting recover password by token = {token}")
        await self.db.execute(
            text(
                """
                DELETE FROM recover_password
                WHERE token = :token
                """
            ),
            {"token": token},
        )
        await self.db.commit()
        self.logger.info(f"Recover password deleted by token = {token}")

    async def already_registered(self, email: str) -> bool:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalars().one_or_none()
        return user is not None

    async def already_invited(self, email: str) -> bool:
        result = await self.db.execute(select(Invite).where(Invite.email == email))
        invite = result.scalars().one_or_none()
        return invite is not None

    async def get_invite_by_token(self, token: str):
        self.logger.info(f"Getting invite by token = {token}")
        result = await self.db.execute(select(Invite).where(Invite.token == token))
        invite = result.scalars().one_or_none()
        self.logger.info(f"Invite found for token {token}")
        return invite

    async def get_invite_by_id(self, id_invite: int):
        self.logger.info(f"Getting invite by id = {id_invite}")
        result = await self.db.execute(select(Invite).where(Invite.id_invite == id_invite))
        invite = result.scalars().one_or_none()
        self.logger.info(f"Invite found for id {id_invite}")
        return invite

    async def get_all_invites_by_sender(self, sender_id: int):
        self.logger.info(f"Getting all invites by sender id = {sender_id}")
        result = await self.db.execute(select(Invite).where(Invite.sender_id == sender_id))
        invites = result.scalars().all()
        self.logger.info(f"Invites found for sender id = {sender_id}")
        return invites

    async def delete_invite(self, invite: Invite):
        self.logger.info(f"Deleting invite for {invite.email}")
        await self.db.delete(invite)
        await self.db.commit()
        self.logger.info(f"Invite deleted for {invite.email}")

    async def create_user(self, user: User) -> Optional[User]:
        self.logger.info(f"Creating user {user.email}")
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        self.logger.info(f"User created {user.email}")
        return user

    async def get_sended_invites(self, sender_id: int):
        self.logger.info(f"Getting sended invites by sender id = {sender_id}")
        result = await self.db.execute(select(Invite).where(Invite.sender_id == sender_id))
        invites = result.scalars().all()
        self.logger.info(f"Invites found for sender id = {sender_id}")
        return invites


InviteRepository = Annotated[_InviteRepository, Depends(_InviteRepository)]
