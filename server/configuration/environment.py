from enum import Enum
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


class Mode(str, Enum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    PROD = "PROD"


class Environment(BaseSettings):
    version: str
    mode: Mode

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    def render_sqlalchemy_url(self, dialect_and_connector: str):
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        database = quote_plus(self.postgres_db)
        host = self.postgres_host
        port = self.postgres_port
        return f"{dialect_and_connector}://{user}:{password}@{host}:{port}/{database}"

    @property
    def async_sqlalchemy_url(self):
        return self.render_sqlalchemy_url("postgresql+psycopg")

    @property
    def is_local_mode(self):
        return self.mode is Mode.LOCAL

    @property
    def root_path(self):
        return "/api" if self.is_local_mode else "/_api"

    class Config:
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
                cls._convert_env_values_to_upper,
            )

        @staticmethod
        def _convert_env_values_to_upper(settings):
            if "mode" in settings:
                settings["mode"] = settings["mode"].upper()
            return settings


SETTINGS = Environment()
