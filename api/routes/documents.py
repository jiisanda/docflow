from fastapi import APIRouter, status, File, UploadFile, HTTPException, Depends

from schemas.documents_metadata import DocumentMetadataRead

from api.dependencies.repositories import get_repository
from db.repositories.documents import DocumentRepository
from db.repositories.documents_metadata import DocumentMetadataRepository

router = APIRouter(tags=["Document"])


@router.post(
    "/upload",
    response_model=DocumentMetadataRead,
    status_code=status.HTTP_201_CREATED,
    name="upload_document"
)
async def upload(
    file: UploadFile = File(...),
    repository: DocumentRepository = Depends(DocumentRepository),
    metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
):
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No file"
        )

    response = await repository.upload(file=file)
    return await metadata_repository.upload(document_upload=response)
