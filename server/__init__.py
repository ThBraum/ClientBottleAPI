from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from server.configuration.environment import SETTINGS
from server.controller.auth_controller import router as auth_router
from server.controller.bottle_brand_controller import router as bottle_brand_router
from server.controller.invite_controller import router as invite_router
from server.controller.recover_password_controller import router as recover_password_router
from server.controller.server_controller import router as server_router
from server.controller.transaction_controller import report_router
from server.controller.transaction_controller import router as transaction_router
from server.controller.transaction_controller import router_test as transaction_router_test
from server.utils.exceptions import add_exception_handlers, add_http_exception_handlers
from server.utils.handler import setup_marketplace_exception_handling
from server.utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")
security = HTTPBearer()


def init_app() -> FastAPI:
    return _init_fast_api_app()


def _init_fast_api_app() -> FastAPI:
    logger.info("Iniciando ClientBottle FastAPI")
    app = FastAPI(**_get_app_args())
    app = _config_app_routes(app)
    app = _config_app_exceptions(app)
    app = _config_app_middlewares(app)
    app.openapi = lambda: _custom_openapi(app)
    setup_marketplace_exception_handling(app)
    return app


def _config_app_routes(app: FastAPI) -> FastAPI:
    routers = [
        # Importar os routers aqui
        auth_router,
        invite_router,
        recover_password_router,
        transaction_router,
        report_router,
        bottle_brand_router,
        server_router,
        transaction_router_test,
    ]
    for route in routers:
        app.include_router(route)
    return app


def _get_app_args() -> dict:
    return dict(
        title="Bottle",
        description="Bottle API",
        # root_path=SETTINGS.root_path,
        version=SETTINGS.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )


def _custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Bottle",
        version="1.0.0",
        description="Bottle API",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login/",
                }
            },
        },
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def _config_app_exceptions(app: FastAPI) -> FastAPI:
    app = _config_validation_exceptions(app)
    app = _config_http_exceptions(app)
    return app


def _config_validation_exceptions(app: FastAPI) -> FastAPI:
    # add_exception_handlers(app)
    return app


def _config_http_exceptions(app: FastAPI) -> FastAPI:
    # add_http_exception_handlers(app)
    return app


def _config_app_middlewares(app: FastAPI) -> FastAPI:
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
