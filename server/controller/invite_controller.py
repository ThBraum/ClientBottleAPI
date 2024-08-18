from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Query, status

from server.model.role import UserRole
from server.schema.invite_schema import InviteCreate, UserCreate, UserCreated
from server.service.invite_service import InviteService
from server.utils.dependencies import DepUserAdminPayload

router = APIRouter(tags=["Invite"])


@router.post("/invite/", summary="Invite User - for administrators only.")
async def create_invite(
    invite: InviteCreate,
    background: BackgroundTasks,
    user: DepUserAdminPayload,
    service: InviteService,
    query_role: UserRole,
):
    return await service.create_invite(invite, query_role, background, user)


@router.post(
    "/invite/confirm",
    summary="Confirm User Sign Up",
    response_model=UserCreated,
    status_code=status.HTTP_201_CREATED,
)
async def confirm_user(
    user: UserCreate,
    service: InviteService,
    token: UUID = Query(...),
):
    new_user = await service.confirm_user(user_create=user, token=token)
    return UserCreated(
        full_name=new_user.full_name,
        email=new_user.email,
        role=new_user.role,
        fl_active=new_user.fl_active,
    )


@router.get("/invite/", summary="Get sended invites - for administrators only.")
async def get_sendend_invites(
    user: DepUserAdminPayload,
    service: InviteService,
):
    return await service.get_sended_invites(user)


@router.delete("/invite/", summary="Delete invite - for administrators only.")
async def delete_invite(
    user: DepUserAdminPayload,
    service: InviteService,
    token: Optional[UUID] = Query(None),
    id_invite: Optional[int] = Query(None),
):
    return await service.delete_invite_by_token_or_id_invite(token, id_invite)
