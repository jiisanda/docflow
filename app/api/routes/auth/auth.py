from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth_utils import get_current_user
from app.api.dependencies.repositories import get_repository
from app.schemas.auth.bands import UserOut, UserAuth, TokenData
from app.db.repositories.auth.auth import AuthRepository

router = APIRouter(tags=["User Auth"])


@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    name="signup",
    summary="Create new user"
)
async def signup(
    data: UserAuth,
    repository: AuthRepository = Depends(get_repository(AuthRepository))
):

    return await repository.signup(userdata=data)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    name="login",
    summary="Create access and refresh tokens for user"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repository: AuthRepository = Depends(get_repository(AuthRepository))
):

    return await repository.login(ipdata=form_data)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=TokenData,
    name="get_user_data",
    summary="Get details of currently logged in user"
)
async def get_me(user: TokenData = Depends(get_current_user)):

    return user
