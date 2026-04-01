from endpoints import recipe
from fastapi import FastAPI

from contextlib import asynccontextmanager
from utils.constants import get_database_url
import psycopg_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with psycopg_pool.AsyncConnectionPool(get_database_url()) as pool:
        app.state.pool = pool
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(recipe.router)


@app.get("/")
async def root():
    return {"message": "hello world!"}
