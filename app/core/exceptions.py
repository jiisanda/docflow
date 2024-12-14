from typing import Dict

from fastapi.exceptions import HTTPException
from starlette import status


def http_400(msg: str = "Bad Request...") -> HTTPException:
    """Invalid Input"""
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def http_401(msg: str = "Unauthorized", headers: Dict[str, str] = None) -> HTTPException:
    """Unauthorized Access"""
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg, headers=headers)


def http_403(msg: str = "Forbidden") -> HTTPException:
    """Forbidden access"""
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)


def http_404(msg: str = "Entity does not exists...") -> HTTPException:
    """Raised when entity was not found on database."""
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)


def http_409(msg: str = "Entity already exists...") -> HTTPException:
    """Raised when entity already exists on database."""
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)


def http_500(msg: str = "Internal Server Error") -> HTTPException:
    """Raised when error caused due to internal server"""
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)
