from typing import Annotated

from fastapi import Depends

from server.lib.auth import get_current_active_user
from server.model.user import User

DepUser = Annotated[User, Depends(get_current_active_user)]
