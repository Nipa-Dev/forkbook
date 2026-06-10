import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from psycopg.rows import dict_row
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.dependencies import GetConnection
from app.schemas.user import UserInDB, UserRead

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("veryfancyindeed")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def normalize_username(value: str) -> str:
    return value.strip().casefold()


def normalize_email(value: str) -> str:
    return value.strip().casefold()


def compute_email_blind_index(email: str) -> str:
    normalized = normalize_email(email)

    digest = hmac.new(
        settings.EMAIL_BIDX_SECRET.encode(),
        normalized.encode(),
        hashlib.sha256,
    ).hexdigest()

    return digest


def decrypt_email(email_enc: bytes | str, key_version: int) -> str:
    if isinstance(email_enc, bytes):
        email_str = email_enc.decode("utf-8")
    else:
        email_str = email_enc

    original_email = email_str.removeprefix("ENC_")

    return original_email


async def get_user_by_id(
    conn: GetConnection,
    user_id: UUID,
) -> UserInDB | None:
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT * FROM users where user_id = %s", (user_id,))
        row = await cur.fetchone()
        return UserInDB(**row) if row else None


async def get_user_by_username(
    conn: GetConnection, username_normalized: str
) -> UserInDB | None:
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT * FROM users WHERE username_normalized = %s", (username_normalized,)
        )
        row = await cur.fetchone()
        return UserInDB(**row) if row else None


async def get_user_by_email_bidx(
    conn: GetConnection, email_bidx: str
) -> UserInDB | None:
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT * FROM users WHERE email_bidx = %s", (email_bidx,))
        row = await cur.fetchone()
        return UserInDB(**row) if row else None


async def authenticate_user(
    conn: GetConnection,
    identifier: str,
    password: str,
):  # -> UserInDB | None:
    identifier = identifier.strip().casefold()

    user = None

    if "@" in identifier:
        email_bidx = compute_email_blind_index(identifier)
        user = await get_user_by_email_bidx(conn, email_bidx)
    else:
        username_normalized = normalize_username(identifier)

        user = await get_user_by_username(
            conn,
            username_normalized,
        )

    if not user:
        verify_password(password, DUMMY_HASH)
        return None

    if not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    return user


def create_access_token(
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(timezone.utc)

    expire = (
        now + expires_delta
        if expires_delta
        else now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    conn: GetConnection,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "access":
            raise credentials_exception

        sub = payload.get("sub")

        if sub is None:
            raise credentials_exception

        user_id = UUID(sub)

    except (InvalidTokenError, ExpiredSignatureError, ValueError):
        raise credentials_exception

    user = await get_user_by_id(
        conn,
        user_id,
    )

    if user is None:
        raise credentials_exception

    return user


@lru_cache(maxsize=1024)
def _cache_profile(
    user_id: UUID,
    username: str,
    email_enc: bytes,
    key_version: int,
    created_at: datetime,
    updated_at: datetime,
) -> UserRead:
    decrypted_email = decrypt_email(email_enc, key_version)

    return UserRead(
        user_id=user_id,
        username=username,
        email=decrypted_email,
        created_at=created_at,
        updated_at=updated_at,
    )


async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> UserRead:
    return _cache_profile(
        current_user.user_id,
        current_user.username,
        current_user.email_enc,
        current_user.key_version,
        current_user.created_at,
        current_user.updated_at,
    )
    # user_dict = current_user.model_dump()
    # user_dict["email"] = decrypt_email(user_dict["email_enc"], 1)
    # return UserRead(**user_dict)
