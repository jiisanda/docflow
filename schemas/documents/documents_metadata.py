from typing import Optional
from uuid import UUID

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
