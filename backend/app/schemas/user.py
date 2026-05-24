from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    user_id: UUID

    username: str
    username_normalized: str

    email_bidx: str
    email_enc: str

    key_version: int

    created_at: datetime
    updated_at: datetime


class UserInDB(UserBase):
    hashed_password: str
