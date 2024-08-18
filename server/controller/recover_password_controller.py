from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Body, Query, status
from fastapi.responses import JSONResponse

from server.schema.invite_schema import NewHashedPassword, RecoverPasswordSchema
from server.service.invite_service import InviteService

router = APIRouter(tags=["Recover Password"])


@router.post("/user/recover-password", summary="Send recover password")
async def recover_password(
    service: InviteService,
    background: BackgroundTasks,
    email_or_username: RecoverPasswordSchema = Body(...),
):
    await service.post_recover_password(email_or_username, background)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Se esse usuário foi encontrado, enviamos para o email cadastrado."},
    )


@router.patch("/user/recover-password", summary="Confirm recover password")
async def confirm_recover_password(
    new_password: NewHashedPassword,
    service: InviteService,
    token: UUID = Query(...),
):
    await service.confirm_new_hashed_password(token, new_password.new_password)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Senha atualizada."})
