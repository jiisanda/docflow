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

    """
    Uploads document metadata.

    Args:
        document_upload (DocumentMetadataCreate): The document metadata to be uploaded.
        repository (DocumentMetadataRepository): The repository for managing document metadata.
        user (TokenData): The token data of the authenticated user.

    Returns:
        DocumentMetadataRead: The uploaded document metadata.
    """

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

    """
    Retrieves a list of document metadata.

    Args:
        limit (int): The maximum number of documents to retrieve. Defaults to 10.
        offset (int): The number of documents to skip. Defaults to 0.
        repository (DocumentMetadataRepository): The repository for managing document metadata.
        user (TokenData): The token data of the authenticated user.

    Returns:
        Dict[str, Union[List[DocumentMetadataRead], Any]]: A dictionary containing the list of document metadata.
    """

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

    """
    Retrieves the metadata of a specific document.

    Args:
        document (Union[str, UUID]): The ID or name of the document.
        repository (DocumentMetadataRepository): The repository for managing document metadata.
        user (TokenData): The token data of the authenticated user.

    Returns:
        Union[DocumentMetadataRead, HTTPException]: The document metadata if found, otherwise an HTTPException.
    """

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

    """
    Updates the details of a document's metadata.

    Args:
        document (Union[str, UUID]): The ID or name of the document.
        document_patch (DocumentMetadataPatch): The document metadata patch containing the updated details.
        repository (DocumentMetadataRepository): The repository for managing document metadata.
        user_repository (AuthRepository): The repository for managing user authentication.
        user (TokenData): The token data of the authenticated user.

    Returns:
        Union[DocumentMetadataRead, HTTPException]: The updated document metadata if successful,
        otherwise an HTTPException.

    Raises:
        HTTP_404: If no document with the specified ID or name is found.
    """

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

    """
    List bin.

    Args:
        repository: The document metadata repository.
        owner: The token data of the owner.

    Returns:
        Dict[str, List[Row | Row] | int]: The list of bin.

    """

    return await repository.bin_list(owner=owner)


@router.post(
    "/restore",
    status_code=status.HTTP_200_OK,
    response_model=DocumentMetadataRead,
    name="restore_from_bin"
)
async def restore_bin(
        file: str,
        repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        user: TokenData = Depends(get_current_user)
) -> DocumentMetadataRead:

    """
    Restore bin.

    Args:
        file: The file to restore.
        repository: The document metadata repository.
        user: The token data of the user.

    Returns:
        DocumentMetadataRead: The restored document metadata.

    """

    return await repository.restore(file=file, owner=user)


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

    """
    Permanently delete document.

    Args:
        document_id: The ID of the document to delete.
        delete_all: Flag indicating whether to delete all documents.
        repository: The document metadata repository.
        user: The token data of the user.

    Returns:
        None

    """

    return await repository.perm_delete(document=document_id, owner=user, delete_all=delete_all)


@router.post(
    "/archive",
    response_model=DocumentMetadataRead,
    status_code=status.HTTP_200_OK,
    name="archive_a_document"
)
async def archive(
        file_name: str,
        repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        user: TokenData = Depends(get_current_user),
) -> DocumentMetadataRead:

    """
    Archive a document.

    Args:
        file_name (str): The name of the file to be archived.
        repository (DocumentMetadataRepository): The repository for document metadata.
        user (TokenData): The user token data.

    Returns:
        DocumentMetadataRead: The archived document metadata.

    """

    return await repository.archive(file=file_name, user=user)


@router.get(
    "/archive/list",
    response_model=None,
    status_code=status.HTTP_200_OK,
    name="archived_doc_list"
)
async def archive_list(
        repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        user: TokenData = Depends(get_current_user),
) -> Dict[str, List[str] | int]:

    """
    Get the list of archived documents.

    Args:
        repository (DocumentMetadataRepository): The repository for document metadata.
        user (TokenData): The user token data.

    Returns:
        Dict[str, List[str] | int]: A dictionary containing the list of archived documents.

    """

    return await repository.archive_list(user=user)


@router.post(
    "/un-archive",
    response_model=DocumentMetadataRead,
    status_code=status.HTTP_200_OK,
    name="remove_doc_from_archive"
)
async def un_archive(
        file: str,
        repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        user: TokenData = Depends(get_current_user),
) -> DocumentMetadataRead:

    """
    Un-archive a document.

    Args:
        file (str): The name of the file to be un-archived.
        repository (DocumentMetadataRepository): The repository for document metadata.
        user (TokenData): The user token data.

    Returns:
        DocumentMetadataRead: The un-archived document metadata.

    """

    return await repository.un_archive(file=file, user=user)
