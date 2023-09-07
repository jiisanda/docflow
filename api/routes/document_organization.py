from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query

from api.dependencies.repositories import get_repository
from db.repositories.documents_metadata import DocumentMetadataRepository
from db.repositories.document_organization import DocumentOrgRepository
from schemas.documents_metadata import DocumentMetadataRead

router = APIRouter(tags=["Document Search"])


@router.get(
    "",
    # response_model=List[DocumentMetadataRead],
    status_code=status.HTTP_200_OK,
    name="search_document",
)
async def search_document(
    limit: int = Query(default=10, lt=100),
    offset: int = Query(default=0),
    tag: str = None,
    category: str = None,
    file_types: str = None,
    status: str = None,
    repository: DocumentOrgRepository = Depends(DocumentOrgRepository),
    repository_metadata: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
):

    doc_list = await repository_metadata.doc_list(limit=limit, offset=offset)
    if tag is None and category is None and file_types is None and status is None:
        return doc_list

    else:
        return await repository.search_doc(docs=doc_list, tags=tag, categories=category, file_types=file_types, status=status)
