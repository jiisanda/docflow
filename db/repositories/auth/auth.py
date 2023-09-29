from typing import Any, Coroutine

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth_utils import get_hashed_password
from core.exceptions import HTTP_400
from db.tables.auth.auth import User
from schemas.auth.bands import UserOut, UserAuth


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_user(self, userdata: UserAuth) -> Coroutine[Any, Any, Any | None]:
        stmt = (
            select(User)
            .where(User.username == userdata.username or User.email == userdata.email)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def signup(self, userdata: UserAuth) -> UserOut:
        # Checking if the user already exists
        if await self._get_user(userdata) is not None:
            raise HTTP_400(msg="User with details already exists")

        # hashing the password
        hashed_password = get_hashed_password(password=userdata.password)
        userdata.password = hashed_password

        new_user = User(**userdata.model_dump())

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user

    def login(self, ipdata):
        ...
