from uuid import UUID

from schemas.bands import DocumentMetadataBase


class DocumentMetadataCreate(DocumentMetadataBase):
    name: str
    s3_url: str


class DocumentMetadataRead(DocumentMetadataBase):
    _id: UUID
    name: str

    class Config:
        from_attributes = True


class DocumentMetadataPatch(DocumentMetadataBase):
    ...