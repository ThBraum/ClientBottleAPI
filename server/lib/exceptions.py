from urllib.request import Request

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from server.lib.error import ClientBottleException


class ApiBaseException(HTTPException):
    def __init__(self, status_code=500, detail=None) -> None:
        self.status_code = status_code
        self.detail = detail
        if self.detail:
            from server.lib.logger import logger

            logger.exception(self.detail)


class BusinessException(ApiBaseException):
    status_code = 400

    def __init__(self, detail=None) -> None:
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class NotFoundException(ApiBaseException):
    status_code = 404

    def __init__(self, detail=None) -> None:
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class UnprocessableEntityException(ApiBaseException):
    status_code = 422

    def __init__(self, detail=None) -> None:
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class BadRequestException(ApiBaseException):
    status_code = 400

    def __init__(self, detail=None) -> None:
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


def add_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        error_messages = {
            "value_error.missing": "é obrigatório.",
            "type_error.float": "deve ser um float.",
            "type_error.integer": "deve ser um inteiro.",
            "type_error.string": "deve ser uma string.",
            "type_error.list": "deve ser uma lista.",
            "type_error.none": "não pode ser nulo.",
            "type_error.bool": "deve ser um booleano.",
            "type_error.datetime": "deve ser uma data.",
            "type_error.decimal": "deve ser um decimal.",
            "type_error.uuid": "deve ser um UUID.",
            "type_error.list.empty": "não pode ser uma lista vazia.",
            "type_error.dict": "deve ser um dicionário.",
            "type_error.object": "deve ser um objeto.",
            "type_error.enum": "deve ser um dos valores permitidos.",
        }

        errors = []
        for error in exc.errors():
            field_name = error["loc"][-1]
            field_type = error["type"]
            default_message = f"Erro no campo '{field_name}': {error['msg']}"
            message_prefix = f"Falha na validação: o campo '{field_name}' "
            message = message_prefix + error_messages.get(field_type, default_message)
            errors.append(message)

        return JSONResponse(status_code=422, content={"errors": errors})

    app.add_exception_handler(RequestValidationError, validation_exception_handler)


def add_http_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        content = {"errors": [exc.detail]}
        return JSONResponse(status_code=exc.status_code, content=content)

    app.add_exception_handler(HTTPException, http_exception_handler)


def add_bad_request_exception_handler(app: FastAPI):
    @app.exception_handler(ClientBottleException)
    async def marketplace_exception_handler(request: Request, exc: ClientBottleException):
        return exc.to_json_response()

    app.add_exception_handler(ClientBottleException, marketplace_exception_handler)
