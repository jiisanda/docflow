from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, status, Body, Depends, Query, HTTPException

from api.dependencies.repositories import get_repository
from db.repositories.documents_metadata import DocumentMetadataRepository
from schemas.documents_metadata import DocumentMetadataCreate, DocumentMetadataRead, DocumentMetadataPatch


router = APIRouter(tags=["Document MetaData"])


@router.post(
    "/upload-document",
    response_model=DocumentMetadataRead,
    status_code=status.HTTP_201_CREATED,
    name="upload_documents"
)
async def upload_document(
    document_upload: DocumentMetadataCreate = Body(...),
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> DocumentMetadataRead:
    return await repository.upload(document_upload=document_upload)


@router.get(
    "/documents",
    response_model=List[DocumentMetadataRead],
    status_code=status.HTTP_200_OK,
    name="get_documents",
)
async def get_documents(
    limit: int = Query(default=10, lte=100),
    offset: int = Query(default=0),
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> List[Optional[DocumentMetadataRead]]:
    return await repository.doc_list(limit=limit, offset=offset)


@router.get(
    "/get-document/{document}",
    response_model=Optional[DocumentMetadataRead],
    status_code=status.HTTP_200_OK,
    name="get_document"
)
async def get_document(
    document: Union[str, UUID],
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> Optional[DocumentMetadataRead]:
    try:
        await repository.get(document=document)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No Document with {document}"
        )

    return await repository.get(document=document)


@router.put(
    "/update-doc-details/{document}",
    response_model=DocumentMetadataRead,
    status_code=status.HTTP_200_OK,
    name="update_doc_details",
)
async def update_doc_details(
    document: Union[str, UUID],
    document_patch: DocumentMetadataPatch = Body(...),
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> Optional[DocumentMetadataRead]:
    try:
        await repository.get(document=document)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No Document with: {document}"
        )

    return await repository.patch(
        document=document,
        document_patch=document_patch
    )


@router.delete(
    "/delete-doc/{document}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_document",
)
async def delete_document(
    document: Union[str, UUID],
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
) -> None:
    try:
        await repository.get(document=document)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No document with the detail: {document}."
        )

    return await repository.delete(document=document)
