from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import HTTP_401
from app.schemas.auth.bands import TokenData


# Password Hashing
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/u/login', scheme_name="JWT")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)


def create_access_token(subject: Dict[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_min)

    to_encode = {"exp": expires_delta, "id": subject.get("id"), "username": subject.get("username")}

    return jwt.encode(to_encode, settings.jwt_secret_key, settings.algorithm)


def create_refresh_token(subject: Dict[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_min)

    to_encode = {"exp": expires_delta, "id": subject.get("id"), "username": subject.get("username")}

    return jwt.encode(to_encode, settings.jwt_secret_key, settings.algorithm)


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        uid = payload.get("id")
        username = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(id=uid, username=username)
    except JWTError as e:
        raise credentials_exception from e

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTP_401(
        msg="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    return verify_access_token(token=token, credentials_exception=credentials_exception)
