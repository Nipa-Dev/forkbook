from typing import AsyncGenerator, Annotated, TypedDict
from fastapi import Request, Depends
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection

class State(TypedDict):
    pool: AsyncConnectionPool

async def _get_conn(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    """Return a connection from database pool."""
    async with request.state["pool"].connection() as conn:
        yield conn

GetConnection = Annotated[AsyncConnection, Depends(_get_conn)]
