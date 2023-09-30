from datetime import datetime
from typing import List, Optional
from uuid import UUID

from db.tables.base_class import StatusEnum
from schemas.documents.bands import DocumentMetadataBase


class DocumentMetadataCreate(DocumentMetadataBase):
    owner_id: Optional[str] = None
    name: str
    s3_url: str


class DocumentMetadataRead(DocumentMetadataBase):
    _id: UUID
    name: str

    class Config:
        from_attributes = True


class DocumentMetadataPatch(DocumentMetadataBase):
    name: str = None
    s3_url: str = None
    created_at: datetime = None
    size: Optional[int] = None
    file_type: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    status: StatusEnum = None
    file_hash: Optional[str] = None
