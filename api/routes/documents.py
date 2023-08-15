from typing import List, Optional

from fastapi import APIRouter, status, Body, Depends, Query

from api.dependencies.repositories import get_repository
from db.repositories.documents import DocumentRepository
from schemas.documents import DocumentCreate, DocumentRead


router = APIRouter()


@router.post(
    "/upload-document",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    name="upload_documents"
)
async def upload_document(
    document_upload: DocumentCreate = Body(...),
    repository: DocumentRepository = Depends(get_repository(DocumentRepository)),
) -> DocumentRead:
    return await repository.upload(document_upload=document_upload)


@router.get(
    "/documents",
    response_model=List[DocumentRead],
    status_code=status.HTTP_200_OK,
    name="get_documents",
)
async def get_documents(
    limit: int = Query(default=10, lte=100),
    offset: int = Query(default=0),
    repository: DocumentRepository = Depends(get_repository(DocumentRepository)),
) -> List[Optional[DocumentRead]]:
    return await repository.doc_list(limit=limit, offset=offset)
