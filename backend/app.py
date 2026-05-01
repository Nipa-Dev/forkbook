from endpoints import recipe
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from utils.constants import get_database_url
from utils.dependencies import State
import psycopg_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with psycopg_pool.AsyncConnectionPool(get_database_url()) as pool:
        yield State(pool=pool)


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="backend/static"), name="static")
# Allow frontend dev server to call backend APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipe.router, prefix="/recipes", tags=["recipes"])


@app.get("/")
async def root():
    return {"message": "hello world!"}
