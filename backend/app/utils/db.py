from typing import Annotated, AsyncGenerator, TypedDict

import aiosqlite
from fastapi import Depends, Request


class State(TypedDict):
    db: aiosqlite.Connection


async def _get_conn(request: Request) -> AsyncGenerator[aiosqlite.Connection, None]:
    """Return the SQLite database connection."""

    yield request.app.state.db


GetConnection = Annotated[aiosqlite.Connection, Depends(_get_conn)]
