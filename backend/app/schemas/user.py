from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr
from pydantic.fields import Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=25)
    email: EmailStr
    password: str


class UserRead(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class UserBase(BaseModel):
    user_id: UUID

    username: str = Field(min_length=3, max_length=25)
    username_normalized: str

    email_bidx: str
    email_enc: str

    key_version: int = Field(gt=0)

    created_at: datetime
    updated_at: datetime


class UserInDB(UserBase):
    hashed_password: str
