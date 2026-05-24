from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated

from app.core.dependencies import GetConnection
from app.utils.auth import authenticate_user

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
