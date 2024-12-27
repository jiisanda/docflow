from datetime import datetime
from uuid import UUID

from app.schemas.documents.bands import CommentBase


class CommentCreate(CommentBase):
    doc_id: UUID


class CommentUpdate(CommentBase): ...


class CommentRead(CommentBase):
    id: UUID
    doc_id: UUID
    author_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attribute = True
