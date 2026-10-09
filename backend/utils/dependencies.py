from typing import Annotated

from fastapi import Depends

from backend.schemas.user import UserInDB
from backend.utils.auth import get_current_active_user

CurrentUser = Annotated[UserInDB, Depends(get_current_active_user)]
