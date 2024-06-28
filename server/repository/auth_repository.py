from typing import Annotated

from fastapi import Depends
from server.configuration.database import DepDatabaseSession


class _AuthRepository:
    def __init__(self, db: DepDatabaseSession):
        self.db = db


AuthRepository = Annotated[_AuthRepository, Depends(_AuthRepository)]
