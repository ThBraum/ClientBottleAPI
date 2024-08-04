import os
from pathlib import Path
from typing import Annotated, Optional

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from server.utils.constants import AUTH_ALGORITHM, AUTH_SECRET_KEY, HTTP_SCHEME, OAUTH2_SCHEME
from server.utils.error import ClientBottleException, CodigoErro
from server.utils.types import SessionPayload


def __decode_token(token: Optional[str]):
    if not token:
        raise ClientBottleException(errors=[CodigoErro.AUTENTICACAO_NECESSARIA])
    try:
        payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
        id_usuario = payload.get("id_user")
        if not id_usuario:
            raise ClientBottleException([CodigoErro.AUTENTICACAO_NECESSARIA])

        if not payload.get("fl_active"):
            raise ClientBottleException([CodigoErro.USUARIO_INATIVO])
        return payload
    except jwt.ExpiredSignatureError:
        raise ClientBottleException([CodigoErro.SESSAO_EXPIRADA])
    except jwt.InvalidTokenError:
        raise ClientBottleException([CodigoErro.TOKEN_INVALIDO])
    except jwt.DecodeError:
        raise ClientBottleException([CodigoErro.SESSAO_EXPIRADA_OU_INVALIDA])
    except Exception as e:
        raise ClientBottleException from e


async def auth_dependency(
    token: Annotated[Optional[str], Depends(OAUTH2_SCHEME)] = None,
    http_credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], Depends(HTTP_SCHEME)
    ] = None,
) -> dict:
    if http_credentials:
        token = http_credentials.credentials
    return __decode_token(token)


async def get_user_payload(decoded_token: dict = Depends(auth_dependency)) -> SessionPayload:
    return SessionPayload.model_validate(decoded_token)


async def is_admin(decoded_token: dict = Depends(auth_dependency)) -> SessionPayload:
    if decoded_token.get("role") != "ADMINISTRATOR":
        raise ClientBottleException([CodigoErro.ADMIN_ONLY])
    return SessionPayload.model_validate(decoded_token)


AUTH_DEPENDENCY = Depends(auth_dependency)

UTILS_FOLDER_PATH = Path(__file__).parent
if os.path.exists("/app"):
    ROOT_FOLDER_PATH = Path("/app")
else:
    ROOT_FOLDER_PATH = UTILS_FOLDER_PATH.parent

DepUserPayload = Annotated[SessionPayload, Depends(get_user_payload)]
DepUserAdminPayload = Annotated[SessionPayload, Depends(is_admin)]
