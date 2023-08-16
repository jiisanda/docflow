from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, status, Body, Depends, Query, HTTPException

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


@router.get(
    "/get-a-document/{document_id}",
    response_model=Optional[DocumentRead],
    status_code=status.HTTP_200_OK,
    name="get-document-by-id",
)
async def get_document_by_id(
    document_id: UUID,
    repository: DocumentRepository = Depends(get_repository(DocumentRepository)),
)-> Optional[DocumentRead]:
    try:
        await repository.get(document_id=document_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No Document with the id {document_id}"
        )

    return await repository.get(document_id=document_id)
