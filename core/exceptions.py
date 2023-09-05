from typing import Any, Dict, Optional

from fastapi.exceptions import HTTPException
from starlette import status


def HTTP_404(msg: str = "Entity does not exists...") -> HTTPException:
    """Raised when entity was not found on database."""
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

def HTTP_409(msg: str = "Entity already exists...") -> HTTPException:
    """Raised when entity already exists on database."""
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
