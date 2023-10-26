from fastapi import APIRouter, status, Depends

from api.dependencies.auth_utils import get_current_user
from api.dependencies.repositories import get_repository
from db.repositories.documents.notify import NotifyRepo
from schemas.auth.bands import TokenData

router = APIRouter(tags=["Notification"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    name="get_notifications"
)
async def get_notifications(
        repository: NotifyRepo = Depends(get_repository(NotifyRepo)),
        user: TokenData = Depends(get_current_user)
):
    return await repository.get_notifications(user=user)
