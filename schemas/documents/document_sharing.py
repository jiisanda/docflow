from pydantic import BaseModel

from schemas.documents.bands import DocumentSharingBase


class DocumentSharingCreate(DocumentSharingBase):
    ...


class DocumentSharingRead(DocumentSharingBase):
    url_id: str
    visits: int

    class Config:
        from_attributes = True


class SharingRequest(BaseModel):
    visits: int = 1     # default value of visits (1)
