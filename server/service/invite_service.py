import logging
from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, Depends
from pytz import timezone

from server.configuration.database import DepDatabaseSession
from server.model.invite import Invite
from server.model.user import User
from server.repository.invite_repository import InviteRepository, _InviteRepository
from server.schema.invite_schema import InviteCreate, UserCreate
from server.utils.auth import evaluate_username_availability, get_password_hash
from server.utils.email import get_cliente_email
from server.utils.error import ClientBottleException, CodigoErro
from server.utils.types import SessionPayload


class _AuthService:
    def __init__(self, db: DepDatabaseSession):
        self.db = db
        self.repository: _InviteRepository = InviteRepository(db)
        self.logger = logging.getLogger(__name__)

    async def create_invite(
        self, invite: InviteCreate, query_role, background: BackgroundTasks, user: SessionPayload
    ):
        self.logger.info(f"Creating invite. Sender {user.full_name} - {user.email}")
        sao_paulo_tz = timezone("America/Sao_Paulo")
        new_invite = Invite(
            sender_id=user.id_user,
            token=uuid4(),
            creation_user_id=user.id_user,
            email=invite.email,
            role=query_role,
            expires_at=datetime.now(sao_paulo_tz) + timedelta(hours=24),
        )
        invite = await self.repository.create_invite(new_invite)
        email_service = get_cliente_email()
        email_service.send_email_invitation(background, invite.email, str(new_invite.token))
        return {"message": "Invite sent", "invite": invite}

    async def confirm_user(self, user_create: UserCreate, token: UUID):
        invite = await self.repository.get_invite_by_token(str(token))
        if not invite:
            raise ClientBottleException(CodigoErro.INVALID_INVITE)
        sao_paulo_tz = timezone("America/Sao_Paulo")
        current_time = datetime.now(sao_paulo_tz).astimezone(sao_paulo_tz)
        invite_expiry = invite.expires_at.astimezone(sao_paulo_tz)
        if invite_expiry < current_time:
            raise ClientBottleException(CodigoErro.EXPIRED_INVITE)

        new_user = await self.create_user(user_create, invite)
        if await self.repository.create_user(new_user):
            await self.repository.delete_invite(invite)
        return new_user

    async def create_user(self, user_create: UserCreate, invite: Invite):
        self.logger.info(f"Creating user from invite {invite.email}")
        new_user = User(
            full_name=user_create.full_name,
            username=await evaluate_username_availability(self.db, user_create.username),
            email=invite.email,
            role=invite.role,
            password=get_password_hash(user_create.password),
        )
        return new_user


InviteService = Annotated[_AuthService, Depends(_AuthService)]
