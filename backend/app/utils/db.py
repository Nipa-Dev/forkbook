from typing import Annotated, AsyncGenerator, TypedDict

from fastapi import Depends, Request
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool


class State(TypedDict):
    pool: AsyncConnectionPool


async def _get_conn(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    """Return a connection from database pool."""
    async with request.state["pool"].connection() as conn:
        yield conn


GetConnection = Annotated[AsyncConnection, Depends(_get_conn)]
