from uuid import UUID

from schemas.base_schemas import DocumentBase


class DocumentCreate(DocumentBase):
    name: str
    s3_url: str


class Document(DocumentBase):
    id: UUID

    class Config:
        from_attributes = True