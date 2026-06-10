import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.dependencies import GetConnection
from app.schemas.auth import Token
from app.schemas.user import UserInDB, UserRegister
from app.utils import auth
from app.utils.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
    conn: GetConnection,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await authenticate_user(
        conn=conn,
        identifier=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrecr username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        user_id=user.user_id,
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/add-user", status_code=status.HTTP_201_CREATED)
async def create_user(conn: GetConnection, user_in: UserRegister):
    hashed_password = get_password_hash(user_in.password)
    user_email_normalized = auth.normalize_email(user_in.email)
    email_blind_index = auth.compute_email_blind_index(user_email_normalized)
    mock_encrypted_bytes = f"ENC_{user_in.email}".encode()

    user_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    username_normalized = auth.normalize_username(user_in.username)

    query = """
        INSERT INTO users (
            user_id, username, username_normalized,
            email_bidx, email_enc, hashed_password,
            key_version, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING user_id, username;
    """

    async with conn.cursor() as cur:
        await cur.execute(
            query,
            (
                user_id,
                user_in.username,
                username_normalized,
                email_blind_index,
                mock_encrypted_bytes,
                hashed_password,
                1,  # key_version
                now,
                now,
            ),
        )
        new_user = await cur.fetchone()

        return {
            "status": "success",
            "user_id": str(new_user[0]),
            "username": new_user[1],
        }


@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    return current_user
