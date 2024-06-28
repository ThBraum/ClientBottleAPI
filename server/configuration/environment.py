from enum import Enum
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings


class Mode(Enum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    PROD = "PROD"


class Environment(BaseSettings):
    version: str
    mode: Mode

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
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
        if self.is_local_mode:
            return ""
        return "/_api"


SETTINGS = Environment()
