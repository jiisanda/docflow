from typing import List
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import HTTP_500, HTTP_409, HTTP_404
from db.repositories.auth.auth import AuthRepository
from db.tables.base_class import NotifyEnum
from db.tables.documents.notify import Notify
from schemas.auth.bands import TokenData
from schemas.documents.bands import Notification, NotifyPatchStatus


class NotifyRepo:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def notify(self, user: TokenData, receivers: List[str], filename: str, auth_repo: AuthRepository) -> None:
        """
        Notify users about a shared file.

        Args:
            user (TokenData): The authenticated user who shared the file.
            receivers (List[str]): The list of email addresses of the users to be notified.
            filename (str): The name of the shared file.
            auth_repo (AuthRepository): The repository for accessing user authentication data.

        Returns:
            None

        Raises:
            HTTP_500: If an error occurs while adding the notification entry.
        """

        for receiver in receivers:

            receiver_details = (await auth_repo.get_user(field="email", detail=receiver)).__dict__

            notify_entry = Notify(
                receiver_id=receiver_details["id"],
                message=f"{user.username} shared {filename} with you! Access the shared file via mail...",
                status=NotifyEnum.unread
            )

            try:
                self.session.add(notify_entry)
                await self.session.commit()
                await self.session.refresh(notify_entry)
            except Exception as e:
                raise HTTP_500() from e

    async def get_notification_by_id(self, n_id: UUID, user: TokenData) -> Notification:
        """
        Get a notification by its ID for a specific user.

        Args:
            n_id (UUID): The ID of the notification.
            user (TokenData): The authenticated user.

        Returns:
            Notification: The notification object.

        Raises:
            HTTP_404: If no notification with the given ID is found.
        """

        stmt = (
            select(Notify)
            .where(Notify.receiver_id == user.id and Notify.id == n_id)
        )

        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
            return Notification(**result.__dict__)
        except Exception as e:
            raise HTTP_404(
                msg=f"No notification with id: {n_id}"
            ) from e

    async def get_notifications(self, user: TokenData) -> List[Notification]:
        """
        Get all notifications for a specific user.

        Args:
            user (TokenData): The authenticated user.

        Returns:
            List[Notification]: A list of notification objects.
        """

        stmt = (
            select(Notify)
            .where(Notify.receiver_id == user.id)
        )

        notifications = (await self.session.execute(stmt)).fetchall()

        return [
            Notification(**notification.Notify.__dict__)
            for notification in notifications
        ]

    async def mark_all_read(self, user: TokenData) -> List[Notification]:
        """
        Mark all notifications as read for a specific user.

        Args:
            user (TokenData): The authenticated user.

        Returns:
            List[Notification]: A list of notification objects that have been marked as read.

        Raises:
            HTTP_409: If an error occurs while updating the notification status.
        """

        stmt = (
            update(Notify)
            .where(Notify.receiver_id == user.id and Notify.status != NotifyEnum.read)
            .values({Notify.status: NotifyEnum.read})
        )

        try:
            await self.session.execute(stmt)
            return await self.get_notifications(user=user)
        except Exception as e:
            raise HTTP_409(
                msg="Error updating marking notification read..."
            ) from e

    async def update_status(self, n_id: UUID, updated_status: NotifyPatchStatus, user: TokenData):

        """
        Update the status of a notification for a specific user.

        Args:
            n_id (UUID): The ID of the notification to update.
            updated_status (NotifyPatchStatus): The updated status for the notification.
            user (TokenData): The authenticated user.

        Returns:
            Notification: The updated notification object.

        Raises:
            HTTP_409: If an error occurs while updating the notification status.
        """
        stmt = (
            update(Notify)
            .where(Notify.receiver_id == user.id and Notify.id == n_id and Notify.status != updated_status.status)
            .values({Notify.status: updated_status.status})
        )

        try:
            await self.session.execute(stmt)
            return await self.get_notification_by_id(n_id=n_id, user=user)
        except Exception as e:
            raise HTTP_409(
                msg="Error updating notification status..."
            ) from e

    async def clear_notification(self, user: TokenData) -> None:
        """
        Clear all notifications for a specific user.

        Args:
            user (TokenData): The authenticated user.

        Returns:
            None

        Raises:
            Exception: If an error occurs while clearing the notifications.
        """

        stmt = (
            delete(Notify)
            .where(Notify.receiver_id == user.id)
        )

        try:
            await self.session.execute(stmt)
        except Exception as e:
            raise e
