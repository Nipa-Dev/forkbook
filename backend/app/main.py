import json
import logging
from contextlib import asynccontextmanager

import aiosqlite
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jwt.algorithms import RSAAlgorithm

from app.api.endpoints import rating, recipe, recipe_flags, security
from app.schemas.responses import StatusResponse
from app.utils.config import BASE_DIR, get_database_path, settings

logger = logging.getLogger("uvicorn.error")


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Filter favicon.ico
        return "favicon.ico" not in record.getMessage()


logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await aiosqlite.connect(get_database_path())
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")

    schema_path = BASE_DIR / "db" / "init.sql"
    if schema_path.exists():
        await db.executescript(schema_path.read_text(encoding="utf-8"))
        await db.commit()

    app.state.db = db

    try:
        yield
    finally:
        await db.close()


app = FastAPI(lifespan=lifespan)


# Allow frontend dev server to call backend APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipe_flags.router, prefix="/recipes", tags=["Recipes"])
app.include_router(recipe.router, prefix="/recipes", tags=["Recipes"])
app.include_router(security.router, prefix="/auth", tags=["Authentication"])
app.include_router(rating.router, prefix="/rate", tags=["Ratings"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        f"Validation Error on {request.method} {request.url}\n"
        f"Body: {exc.body}\n"
        f"Errors: {exc.errors()}"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": exc.errors()},
    )


@app.get("/", response_model=StatusResponse)
async def root():
    return {"message": "Hello world!"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/.well-known/jwks.json", tags=["auth"])
async def get_jwks(response: Response):
    """Exposes the public key in JWKS format"""
    response.headers["Cache-Control"] = "public, max-age=86400"

    public_key_obj = serialization.load_pem_public_key(
        settings.PUBLIC_KEY.encode("utf-8"), backend=default_backend()
    )

    if not isinstance(public_key_obj, RSAPublicKey):
        raise ValueError("Configured PUBLIC_KEY is not a valid RSA public key")

    jwk_str = RSAAlgorithm.to_jwk(public_key_obj)
    jwk_dict = json.loads(jwk_str)

    jwk_dict.update({"kid": settings.JWT_KID, "use": "sig", "alg": "RS256"})

    return {"keys": [jwk_dict]}
