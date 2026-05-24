import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings
from app.schemas.user import UserInDB

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


async def get_user_by_id(
    conn,
    user_id: UUID,
) -> UserInDB | None: ...


async def get_user_by_username(
    conn,
    username_normalized: str,
) -> UserInDB | None: ...


async def get_user_by_email_bidx(
    conn,
    email_bidx: str,
) -> UserInDB | None: ...


async def authenticate_user(
    conn,
    identifier: str,
    password: str,
) -> UserInDB | None:
    identifier = identifier.strip().casefold()

    user = None

    if "@" in identifier:
        email_bidx = compute_email_blind_index(identifier)

        user = await get_user_by_email_bidx(
            conn,
            email_bidx,
        )

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
        else now + timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
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
    conn,
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
