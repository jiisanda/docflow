from uuid import UUID

from fastapi import APIRouter, status, Depends

from api.dependencies.auth_utils import get_current_user
from api.dependencies.repositories import get_repository
from db.repositories.documents.notify import NotifyRepo
from schemas.auth.bands import TokenData
from schemas.documents.bands import NotifyPatchStatus

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


@router.put(
    path="",
    status_code=status.HTTP_200_OK,
    name="patch_status",
)
async def patch_status(
        updated_status: NotifyPatchStatus,
        mark_as_all_read: bool = False,
        notification_id: UUID = None,
        repository: NotifyRepo = Depends(get_repository(NotifyRepo)),
        user: TokenData = Depends(get_current_user)
):
    if mark_as_all_read:
        return repository.mark_all_read(user=user)
    elif notification_id:
        return repository.update_status(n_id=notification_id, updated_status=updated_status, user=user)


@router.delete(
    path="",
    status_code=status.HTTP_204_NO_CONTENT,
    name="clear_all_notifications",
)
async def clear_all_notifications(
        repository: NotifyRepo = Depends(get_repository(NotifyRepo)),
        user: TokenData = Depends(get_current_user)
):
    return repository.clear_notification(user=user)
