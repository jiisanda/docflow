from typing import Any, Dict, List, Union
from uuid import UUID

from fastapi import APIRouter, status, Body, Depends, Query, HTTPException
from sqlalchemy.engine import Row

from api.dependencies.repositories import get_repository
from api.dependencies.auth_utils import get_current_user
from core.exceptions import HTTP_404
from db.repositories.auth.auth import AuthRepository
from db.repositories.documents.documents_metadata import DocumentMetadataRepository
from schemas.auth.bands import TokenData
from schemas.documents.bands import DocumentMetadataPatch
from schemas.documents.documents_metadata import DocumentMetadataCreate, DocumentMetadataRead


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
    user: TokenData = Depends(get_current_user),
) -> DocumentMetadataRead:
    document_upload.owner_id = user.id
    return await repository.upload(document_upload=document_upload)


@router.get(
    "/documents-metadata",
    response_model=Dict[str, Union[List[DocumentMetadataRead], Any]],
    status_code=status.HTTP_200_OK,
    name="get_documents_metadata",
)
async def get_documents_metadata(
    limit: int = Query(default=10, lt=100),
    offset: int = Query(default=0),
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
    user: TokenData = Depends(get_current_user),
) -> Dict[str, Union[List[DocumentMetadataRead], Any]]:
    return await repository.doc_list(limit=limit, offset=offset, owner=user)


@router.get(
    "/get-document-metadata/{document}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    name="get_document-metadata"
)
async def get_document_metadata(
    document: Union[str, UUID],
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
    user: TokenData = Depends(get_current_user),
) -> Union[DocumentMetadataRead, HTTPException]:
    return await repository.get(document=document, owner=user)


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
    user_repository: AuthRepository = Depends(get_repository(AuthRepository)),
    user: TokenData = Depends(get_current_user),
) -> Union[DocumentMetadataRead, HTTPException]:
    try:
        await repository.get(document=document, owner=user)
    except Exception as e:
        raise HTTP_404(
            msg=f"No Document with: {document}"
        ) from e

    return await repository.patch(
        document=document,
        document_patch=document_patch,
        owner=user,
        user_repo=user_repository,
        is_owner=True
    )


@router.delete(
    "/delete-doc-metadata/{document}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_document_metadata",
)
async def delete_document_metadata(
    document: Union[str, UUID],
    repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
    user: TokenData = Depends(get_current_user),
) -> None:
    """
    Deletes the metadata of a document and moves it to the bin.

    Args:
        document (Union[str, UUID]): The identifier of the document to delete.
        repository (DocumentMetadataRepository): The repository for accessing document metadata.
            Defaults to the result of the `get_repository` function with `DocumentMetadataRepository` as the argument.
        user (TokenData): The token data of the current user. Defaults to the result of the `get_current_user` function.

    Returns:
        None (204_NO_CONTENT)

    Raises:
        HTTP_404: If no document with the specified identifier is found.
    """

    try:
        await repository.get(document=document, owner=user)
    except Exception as e:
        raise HTTP_404(
            msg=f"No document with the detail: {document}."
        ) from e

    return await repository.delete(document=document, owner=user)


@router.get(
    "/bin",
    status_code=status.HTTP_200_OK,
    response_model=None,
    name="list_of_bin"
)
async def list_bin(
        repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        owner: TokenData = Depends(get_current_user)
) -> Dict[str, List[Row | Row] | int]:

    return await repository.bin_list(owner=owner)


@router.delete(
    "/perm-delete",
    status_code=status.HTTP_204_NO_CONTENT,
    name="permanently_delete_doc",
)
async def perm_delete(
        document_id: UUID = None,
        delete_all: bool = False,
        repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        user: TokenData = Depends(get_current_user),
) -> None:

    return await repository.perm_delete(document=document_id, owner=user, delete_all=delete_all)
