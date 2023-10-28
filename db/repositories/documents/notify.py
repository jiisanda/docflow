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

    async def notify(self, user: TokenData, receivers: List[str], filename: str, auth_repo: AuthRepository):

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
        stmt = (
            select(Notify)
            .where(Notify.receiver_id == user.id)
        )

        notifications = (await self.session.execute(stmt)).fetchall()

        response = []
        for notification in notifications:
            response.append(Notification(**notification.Notify.__dict__))
        return response

    async def mark_all_read(self, user: TokenData) -> List[Notification]:
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
        stmt = (
            update(Notify)
            .where(Notify.receiver_id == user.id and Notify.id == n_id and Notify.status != updated_status.status)
            .values({Notify.status: updated_status.status})
        )

        try:
            await self.session.execute(stmt)
            return await self.get_notification_by_id(n_id=n_id, user=user)
        except Exception as e:
            raise e

    async def clear_notification(self, user: TokenData) -> None:
        stmt = (
            delete(Notify)
            .where(Notify.receiver_id == user.id)
        )

        try:
            await self.session.execute(stmt)
        except Exception as e:
            raise e
