from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.configuration.environment import SETTINGS
from server.configuration.middleware import ExceptionMiddleware
from server.lib.exceptions import add_exception_handlers, add_http_exception_handlers
from server.lib.logger import logger
from server.controller.server_controller import router as server_router
from server.controller.auth_controller import router as auth_router


def init_app() -> FastAPI:
    return _init_fast_api_app()


def _init_fast_api_app() -> FastAPI:
    logger.info("Iniciando ClientBottle FastAPI")
    app = FastAPI(**_get_app_args())
    app = _config_app_exceptions(app)
    app = _config_app_middlewares(app)
    app = _config_app_routes(app)
    return app


def _config_app_routes(app: FastAPI) -> FastAPI:
    routers = [
        # Importar os routers aqui
        server_router,
        auth_router,
    ]
    for route in routers:
        app.include_router(route)
    return app


def _get_app_args() -> dict:
    return dict(
        title="Bottle",
        description="Bottle API",
        root_path=SETTINGS.root_path,
        version=SETTINGS.version,
        docs_url="/docs",
        redoc_url="/redoc",
        opeanpi_url="/openapi.json",
    )


def _config_app_exceptions(app: FastAPI) -> FastAPI:
    app = _config_validation_exceptions(app)
    app = _config_http_exceptions(app)
    return app


def _config_validation_exceptions(app: FastAPI) -> FastAPI:
    add_exception_handlers(app)
    return app


def _config_http_exceptions(app: FastAPI) -> FastAPI:
    add_http_exception_handlers(app)
    return app


def _config_app_middlewares(app: FastAPI) -> FastAPI:
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ExceptionMiddleware)
    return app
