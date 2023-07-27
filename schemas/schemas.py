from uuid import UUID

from schemas.base_schemas import DocumentBase


class DocumentCreate(DocumentBase):
    ...


class Document(DocumentBase):
    id: UUID

    class Config:
        orm_mode = True