from typing import Any, Coroutine

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth_utils import get_hashed_password, verify_password, create_access_token, create_refresh_token
from core.exceptions import HTTP_400, HTTP_403
from db.tables.auth.auth import User
from schemas.auth.bands import UserOut, UserAuth


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _check_user_or_none(self, userdata: UserAuth) -> Coroutine[Any, Any, Any | None]:
        stmt = (
            select(User)
            .where(User.username == userdata.username or User.email == userdata.email)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_user(self, field: str, detail: str):
        stmt = ''
        if field == "username":
            stmt = (
                select(User)
                .where(User.username == detail)
            )
        elif field == "email":
            stmt = (
                select(User)
                .where(User.email == detail)
            )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def signup(self, userdata: UserAuth) -> UserOut:
        # Checking if the user already exists
        if await self._check_user_or_none(userdata) is not None:
            raise HTTP_400(msg="User with details already exists")

        # hashing the password
        hashed_password = get_hashed_password(password=userdata.password)
        userdata.password = hashed_password

        new_user = User(**userdata.model_dump())

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user

    async def login(self, ipdata):
        user = await self._get_user(field="username", detail=ipdata.username)
        if user is None:
            raise HTTP_403(msg="Recheck the credentials")
        user = user.__dict__
        hashed_password = user.get("password")
        if not verify_password(password=ipdata.password, hashed_password=hashed_password):
            raise HTTP_403("Incorrect Password")

        return {
            "token_type": "bearer",
            "access_token": create_access_token(subject={"id": user.get("id"), "username": user.get("username")}),
            "refresh_token": create_refresh_token(subject={"id": user.get("id"), "username": user.get("username")})
        }
