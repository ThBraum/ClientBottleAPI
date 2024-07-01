from datetime import datetime

from pytz import timezone
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from server.configuration.database import AsyncSessionLocal
from server.lib.auth import remove_expired_tokens
from server.lib.error import ClientBottleException
from server.service.auth_service import AuthService


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            response = await call_next(request)
        except ClientBottleException as e:
            return e.to_json_response()
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"errors": [{"code": 500, "message": str(e)}]},
            )
        return response


class RemoveExpiredTokensMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        now = datetime.now(timezone("America/Sao_Paulo"))
        hour = now.hour
        if hour >= 18 or hour < 8:
            async with AsyncSessionLocal() as db_session:
                await remove_expired_tokens(db_session)
        return await call_next(request)
