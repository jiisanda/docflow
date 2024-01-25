from typing import List, Union
from uuid import UUID

from fastapi import APIRouter, status, Depends

from app.api.dependencies.auth_utils import get_current_user
from app.api.dependencies.repositories import get_repository
from app.core.exceptions import HTTP_404
from app.db.repositories.documents.notify import NotifyRepo
from app.schemas.auth.bands import TokenData
from app.schemas.documents.bands import Notification, NotifyPatchStatus

router = APIRouter(tags=["Notification"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    name="get_notifications"
)
async def get_notifications(
        repository: NotifyRepo = Depends(get_repository(NotifyRepo)),
        user: TokenData = Depends(get_current_user)
) -> List[Notification]:

    """
    Get notifications for a user.

    Args:
        repository (NotifyRepo): The repository for accessing notification data.
        user (TokenData): The authenticated user.

    Returns:
        List[Notification]: A list of notifications for the user.
    """

    return await repository.get_notifications(user=user)


@router.put(
    path="/{notification_id}",
    status_code=status.HTTP_200_OK,
    name="patch_status",
)
async def patch_status(
        updated_status: NotifyPatchStatus = None,
        notification_id: UUID = None,
        repository: NotifyRepo = Depends(get_repository(NotifyRepo)),
        user: TokenData = Depends(get_current_user)
) -> Union[List[Notification], Notification]:
    """
    Patch the status of a notification or mark all notifications as read.

    Args:
        updated_status (NotifyPatchStatus, optional): The updated status for the notification. Defaults to None.
        notification_id (UUID, optional): The ID of the notification to update. Defaults to None.
        repository (NotifyRepo): The repository for accessing notification data.
        user (TokenData): The authenticated user.

    Returns:
        Union[List[Notification], Notification]: If `mark_as_all_read` is True, returns a list of all notifications
            marked as read. If `notification_id` is provided, returns the updated notification.
            Otherwise, raises an HTTP_404 exception.

    Raises:
        HTTP_404: If 'notification_id' is not provided and update_status.mark_all is set to False.
    """

    if updated_status.mark_all:
        return await repository.mark_all_read(user=user)
    elif notification_id:
        return await repository.update_status(n_id=notification_id, updated_status=updated_status, user=user)
    else:
        raise HTTP_404(
            msg="Bad Request: Make sure to either flag mark_all "
                "or enter notification_id along with correct status as payload."
        )


@router.delete(
    path="",
    status_code=status.HTTP_204_NO_CONTENT,
    name="clear_all_notifications",
)
async def clear_all_notifications(
        repository: NotifyRepo = Depends(get_repository(NotifyRepo)),
        user: TokenData = Depends(get_current_user)
) -> None:
    """
    Clear all notifications for a user.

    Args:
        repository (NotifyRepo): The repository for accessing notification data.
        user (TokenData): The authenticated user.

    Returns:
        None
    """

    return await repository.clear_notification(user=user)
