from uuid import UUID

from schemas.bands import DocumentBase


class DocumentCreate(DocumentBase):
    name: str
    s3_url: str


class Document(DocumentBase):
    id: UUID

    class Config:
        from_attributes = True


class DocumentPatch(DocumentBase):
    ...