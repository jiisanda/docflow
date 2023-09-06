from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query

from db.repositories.document_organization import DocumentOrgRepository
from schemas.documents_metadata import DocumentMetadataRead

router = APIRouter(tags=["Document Search"])


@router.get(
    "/",
    response_model=List[DocumentMetadataRead],
    status_code=status.HTTP_200_OK,
    name="search_document",
)
async def search_document(
    tag: str = None,
    category: str = None,
    file_type: str = None,
    status: str = None,
    limit: int = Query(default=10, lt=100),
    offset: int = Query(default=0),
    repository: DocumentOrgRepository = Depends(DocumentOrgRepository),
) -> List[Optional[DocumentMetadataRead]]:
    ...
