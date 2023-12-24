from typing import Optional, List
from uuid import UUID

from app.schemas.documents.bands import DocumentMetadataBase


class DocumentMetadataCreate(DocumentMetadataBase):
    owner_id: Optional[str] = None
    name: str
    s3_url: str
    access_to: Optional[List[str]] = None


class DocumentMetadataRead(DocumentMetadataBase):
    id: UUID
    name: str

    class Config:
        from_attributes = True
