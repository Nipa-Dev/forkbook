from contextlib import asynccontextmanager
from pathlib import Path

import psycopg_pool
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import recipe, security
from app.core.config import get_database_url
from app.core.dependencies import State


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with psycopg_pool.AsyncConnectionPool(get_database_url()) as pool:
        yield State(pool=pool)


app = FastAPI(lifespan=lifespan)


# Allow frontend dev server to call backend APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipe.router, prefix="/recipes", tags=["recipes"])
app.include_router(security.router, prefix="/auth")


@app.get("/")
async def root():
    return {"message": "hello world!"}
