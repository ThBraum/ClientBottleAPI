from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from server.lib.error import ClientBottleException


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
