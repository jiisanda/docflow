from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, status, Body, Depends, Query, HTTPException

from api.dependencies.repositories import get_repository
from core.exceptions import HTTP_404
from db.repositories.documents.documents_metadata import DocumentMetadataRepository
from schemas.documents.documents_metadata import DocumentMetadataCreate, DocumentMetadataRead, DocumentMetadataPatch


router = APIRouter(tags=["Document MetaData"])


@router.post(
    "/upload-document-metadata",
    response_model=DocumentMetadataRead,
    status_code=status.HTTP_201_CREATED,
    name="upload_documents_metadata"
)
async def upload_document_metadata(
    document_upload: DocumentMetadataCreate = Body(...),
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> DocumentMetadataRead:
    return await repository.upload(document_upload=document_upload)


@router.get(
    "/documents-metadata",
    response_model=List[DocumentMetadataRead],
    status_code=status.HTTP_200_OK,
    name="get_documents_metadata",
)
async def get_documents_metadata(
    limit: int = Query(default=10, lt=100),
    offset: int = Query(default=0),
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> List[Optional[DocumentMetadataRead]]:
    return await repository.doc_list(limit=limit, offset=offset)


@router.get(
    "/get-document-metadata/{document}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    name="get_document-metadata"
)
async def get_document_metadata(
    document: Union[str, UUID],
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> Union[DocumentMetadataRead, HTTPException]:
    return await repository.get(document=document)


@router.put(
    "/update-doc-metadata-details/{document}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    name="update_doc_metadata_details",
)
async def update_doc_metadata_details(
    document: Union[str, UUID],
    document_patch: DocumentMetadataPatch = Body(...),
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> Union[DocumentMetadataRead, HTTPException]:
    try:
        await repository.get(document=document)
    except Exception as e:
        raise HTTP_404(
            msg=f"No Document with: {document}"
        ) from e

    return await repository.patch(
        document=document,
        document_patch=document_patch
    )


@router.delete(
    "/delete-doc-metadata/{document}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_document_metadata",
)
async def delete_document_metadata(
    document: Union[str, UUID],
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> None:
    try:
        await repository.get(document=document)
    except Exception as e:
        raise HTTP_404(
            msg=f"No document with the detail: {document}."
        ) from e

    return await repository.delete(document=document)
