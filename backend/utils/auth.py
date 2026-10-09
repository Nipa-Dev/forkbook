import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

import jwt
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash

from backend.schemas.user import UserInDB, UserRead
from backend.utils.config import settings
from backend.utils.db import GetConnection

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

DUMMY_HASH = password_hash.hash("veryfancyindeed")
FERNET_OBJ = Fernet(settings.FERNET_KEY.get_secret_value().encode("utf-8"))


def verify_password(plain_password, hashed_password) -> tuple[bool, str | None]:
    return password_hash.verify_and_update(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def normalize_username(value: str) -> str:
    return value.strip().casefold()


def normalize_email(value: str) -> str:
    return value.strip().casefold()


def compute_email_blind_index(email: str) -> bytes:
    normalized = normalize_email(email)
    return hmac.new(
        settings.EMAIL_BIDX_SECRET.get_secret_value().encode("utf-8"),
        normalized.encode("utf-8"),
        hashlib.sha256,
    ).digest()


def encrypt_email(email: str) -> bytes:
    """Encrypts normalized email string to raw bytes using Fernet."""
    normalized = normalize_email(email)
    return FERNET_OBJ.encrypt(normalized.encode("utf-8"))


def decrypt_email(email_enc: bytes, key_version: int = 1) -> str:
    """Decrypts bytes back to plaintext string using Fernet."""
    decrypted_bytes = FERNET_OBJ.decrypt(email_enc)
    return decrypted_bytes.decode("utf-8")


async def get_user_by_id(
    conn: GetConnection,
    user_id: UUID,
) -> UserInDB | None:
    async with conn.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (str(user_id),),
    ) as cur:
        row = await cur.fetchone()

    return UserInDB(**row) if row else None


async def get_user_by_username(
    conn: GetConnection, username_normalized: str
) -> UserInDB | None:
    async with conn.execute(
        "SELECT * FROM users WHERE username_normalized = ?",
        (username_normalized,),
    ) as cur:
        row = await cur.fetchone()

    return UserInDB(**row) if row else None


async def get_user_by_email_bidx(
    conn: GetConnection, email_bidx: bytes
) -> UserInDB | None:
    async with conn.execute(
        "SELECT * FROM users WHERE email_bidx = ?",
        (email_bidx,),
    ) as cursor:
        row = await cursor.fetchone()

    return UserInDB(**row) if row else None


async def authenticate_user(
    conn: GetConnection,
    identifier: str,
    password: str,
) -> UserInDB | None:
    identifier = identifier.strip().casefold()
    user = None

    if "@" in identifier:
        email_bidx = compute_email_blind_index(identifier)
        user = await get_user_by_email_bidx(conn, email_bidx)
    else:
        username_normalized = normalize_username(identifier)
        user = await get_user_by_username(conn, username_normalized)

    if not user:
        verify_password(password, DUMMY_HASH)
        return None
    is_valid, _new_hash = verify_password(password, user.hashed_password)
    if not is_valid:
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
        settings.PRIVATE_KEY,
        algorithm=settings.ALGORITHM,
        headers={"kid": settings.JWT_KID},
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
            settings.PUBLIC_KEY,
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


async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> UserRead:
    return UserRead(
        user_id=current_user.user_id,
        username=current_user.username,
        email=decrypt_email(current_user.email_enc, current_user.key_version),
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
