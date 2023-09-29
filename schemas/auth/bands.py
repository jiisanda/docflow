from datetime import datetime
from typing import Annotated, Optional
from ulid import ULID

from pydantic import BaseModel, EmailStr, Field


PydanticULID = Annotated[str, ULID]


class UserAuth(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(..., description="Email ID")
    password: str = Field(..., min_length=5, max_length=14, description="Password")


class UserOut(BaseModel):
    id: PydanticULID
    email: EmailStr
    user_since: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
    username: Optional[str] = None

