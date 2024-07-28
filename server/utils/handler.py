from fastapi import FastAPI

from server.utils.error import ClientBottleException


def setup_marketplace_exception_handling(app: FastAPI):
    @app.exception_handler(ClientBottleException)
    async def handle_usuario_exception(request, exc: ClientBottleException):
        return exc.to_json_response()
