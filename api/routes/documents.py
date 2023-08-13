from fastapi import APIRouter, status, Body, Depends

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
