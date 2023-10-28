from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import HTTP_500
from db.repositories.auth.auth import AuthRepository
from db.tables.base_class import NotifyEnum
from db.tables.documents.notify import Notify
from schemas.auth.bands import TokenData
from schemas.documents.bands import NotifyPatchStatus


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

    async def get_notifications(self, user: TokenData):
        stmt = (
            select(Notify)
            .where(Notify.receiver_id == user.id)
        )

        notifications = await self.session.execute(stmt)

        return notifications.fetchall()

    async def mark_all_read(self, user: TokenData):
        ...

    async def update_status(self, n_id: UUID, updated_status: NotifyPatchStatus, user: TokenData):
        ...

    async def clear_notification(self, user: TokenData):
        ...
