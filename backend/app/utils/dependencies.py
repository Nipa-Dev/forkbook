from typing import AsyncGenerator, Annotated, TypedDict
from fastapi import Request, Depends
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection

from app.schemas.user import UserInDB
from app.utils.auth import get_current_active_user


class State(TypedDict):
    pool: AsyncConnectionPool


async def _get_conn(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    """Return a connection from database pool."""
    async with request.state["pool"].connection() as conn:
        yield conn


GetConnection = Annotated[AsyncConnection, Depends(_get_conn)]
CurrentUser = Annotated[UserInDB, Depends(get_current_active_user)]
