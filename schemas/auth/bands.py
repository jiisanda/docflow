from typing import Annotated
from ulid import ULID

from pydantic import BaseModel, EmailStr, Field


PydanticULID = Annotated[str, ULID]


class UserAuth(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(..., description="Email ID")
    password: str = Field(..., min_length=5, max_length=14, description="Password")


class UserOut(BaseModel):
    id: PydanticULID
