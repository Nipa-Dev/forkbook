from typing import AsyncGenerator, Annotated
from fastapi import Request, Depends
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection


async def _get_conn(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    """Return a connection from database pool."""
    pool: AsyncConnectionPool = request.app.state.pool
    async with pool.connection() as conn:
        yield conn


GetConnection = Annotated[AsyncConnection, Depends(_get_conn)]
