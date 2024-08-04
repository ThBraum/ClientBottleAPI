import logging
from datetime import datetime, timedelta
from typing import Annotated, Optional
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, Depends, HTTPException
from pytz import timezone

from server.configuration.database import DepDatabaseSession
from server.model.invite import Invite
from server.model.recover_password import RecoverPassword
from server.model.user import User
from server.repository.invite_repository import InviteRepository, _InviteRepository
from server.schema.invite_schema import InviteCreate, RecoverPasswordSchema, UserCreate
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

    async def post_recover_password(
        self, email_or_username: RecoverPasswordSchema, background: BackgroundTasks
    ):
        self.logger.info(f"Recovering password for {email_or_username.email}")
        user = await self.repository.get_user_by_email(email_or_username.email)
        if not user:
            user = await self.repository.get_user_by_username(email_or_username.username)
        if not user:
            return None
        recover_password = RecoverPassword(
            id_user=user.id_user,
            email=user.email,
            token=uuid4(),
        )
        password = await self.repository.create_recover_password(recover_password)
        email_service = get_cliente_email()
        email_service.send_email_recovery_password(
            background, str(password.token), user.email, user.full_name
        )
        return {"message": "Recovery email sent", "email": user.email}

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

    async def confirm_new_hashed_password(self, token: UUID, new_password: str):
        await self.confirm_token_to_recover_password(token)
        user = await self.repository.get_user_by_recover_password_token(str(token))
        if not user:
            raise ClientBottleException(CodigoErro.INVALID_RECOVER_PASSWORD)
        user.password = get_password_hash(new_password)
        await self.repository.update_user_hashed_password(user)
        await self.repository.delete_recover_password_by_token(str(token))
        return {"message": "Password updated"}

    async def confirm_token_to_recover_password(self, token: UUID):
        self.logger.info(f"Confirming token to recover password {token}")
        recover_password = await self.repository.get_recover_password_by_token(str(token))
        if not recover_password:
            raise ClientBottleException(CodigoErro.INVALID_RECOVER_PASSWORD)

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

    async def get_sended_invites(self, user: SessionPayload):
        self.logger.info(f"Getting sended invites by {user.full_name}")
        return await self.repository.get_sended_invites(user.id_user)

    async def delete_invite_by_token_or_id_invite(
        self, token: Optional[UUID] = None, id_invite: Optional[int] = None
    ):
        if not token and not id_invite:
            raise HTTPException(
                status_code=400,
                detail="Informe um token ou id_invite para deletar o convite.",
            )
        if token:
            invite = await self.repository.get_invite_by_token(str(token))
        else:
            invite = await self.repository.get_invite_by_id(id_invite)
        if not invite:
            raise HTTPException(
                status_code=404,
                detail="Convite não encontrado.",
            )
        await self.repository.delete_invite(invite)
        return {"message": "Invite deleted", "invite": invite}


InviteService = Annotated[_AuthService, Depends(_AuthService)]
