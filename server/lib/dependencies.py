from typing import Annotated

from fastapi import Depends

from server.lib.auth import validate_user
from server.model.user import User

DepUser = Annotated[User, Depends(validate_user)]
