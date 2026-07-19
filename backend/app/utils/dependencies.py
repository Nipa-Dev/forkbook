from typing import Annotated

from fastapi import Depends

from app.schemas.user import UserInDB
from app.utils.auth import get_current_active_user

CurrentUser = Annotated[UserInDB, Depends(get_current_active_user)]
