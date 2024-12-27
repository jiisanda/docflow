from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.tables.documents.documents_metadata import DocumentComment
from app.schemas.documents.comments import CommentCreate, CommentUpdate


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, comment: CommentCreate, author_id: str
    ) -> DocumentComment: ...

    async def get(self, comment_id: UUID) -> Optional[DocumentComment]: ...

    async def get_document_comments(self, doc_id: UUID) -> List[DocumentComment]: ...

    async def update(
        self, comment_id: UUID, comment_update: CommentUpdate
    ) -> Optional[DocumentComment]: ...

    async def delete(self, comment_id: UUID) -> bool: ...

    async def user_can_modify(self, comment_id: UUID, user_id: str) -> bool: ...
