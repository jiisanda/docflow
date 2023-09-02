from typing import Dict

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
) -> DocumentMetadataRead:
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No file"
        )

    response = await repository.upload(file=file)
    return await metadata_repository.upload(document_upload=response)


@router.get(
    "/download",
    status_code=status.HTTP_200_OK,
    name="download_document"
)
async def download(
    file_name: str,
    repository: DocumentRepository = Depends(DocumentRepository),
    metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> Dict[str, str]:
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No file name"
        )

    get_document_metadata = dict(await metadata_repository.get(document=file_name))
    s3_url = str(get_document_metadata["s3_url"]).split("/")[-2:]
    key = f"{s3_url[0]}/{s3_url[1]}"

    return await repository.download(key=get_document_metadata["s3_url"], name=get_document_metadata["name"])
