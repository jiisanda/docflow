from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.repositories import get_db
from api.dependencies.auth_utils import get_hashed_password
from schemas.auth.bands import UserOut, UserAuth
from schemas.auth.auth import SystemUser
from db.tables.auth.auth import User

router = APIRouter(tags=["User Auth"])


@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    name="signup",
    summary="Create new user"
)
async def signup(data: UserAuth, db: AsyncSession = Depends(get_db)):

    # hashing the password
    hashed_password = get_hashed_password(password=data.password)
    data.password = hashed_password

    new_user = User(**data.model_dump())

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    name="login",
    summary="Create access and refresh tokens for user"
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    ...


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
    name="get_user_data",
    summary="Get details of currently logged in user"
)
async def get_me(user: SystemUser = Depends()):
    ...
