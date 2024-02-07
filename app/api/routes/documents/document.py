from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, status, File, UploadFile, Depends
from fastapi.responses import FileResponse
from sqlalchemy.engine import Row

from app.api.dependencies.auth_utils import get_current_user
from app.api.dependencies.repositories import get_repository
from app.core.exceptions import HTTP_400, HTTP_404
from app.db.repositories.auth.auth import AuthRepository
from app.db.repositories.documents.documents import DocumentRepository
from app.db.repositories.documents.documents_metadata import DocumentMetadataRepository
from app.schemas.auth.bands import TokenData
from app.schemas.documents.documents_metadata import DocumentMetadataRead


router = APIRouter(tags=["Document"])


@router.post(
    "/upload",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    name="upload_document"
)
async def upload(
    files: List[UploadFile] = File(...),
    folder: Optional[str] = None,
    repository: DocumentRepository = Depends(DocumentRepository),
    metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
    user_repository: AuthRepository = Depends(get_repository(AuthRepository)),
    user: TokenData = Depends(get_current_user)
) -> Union[DocumentMetadataRead, List[Dict[str, str]]]:

    """
    Uploads a document to the specified folder.

    Args:
        files (List[UploadFile]): The files to be uploaded.
        folder (Optional[str]): The folder where the document will be stored. Defaults to None.
        repository (DocumentRepository): The repository for managing documents.
        metadata_repository (DocumentMetadataRepository): The repository for managing document metadata.
        user_repository (AuthRepository): The repository for managing user authentication.
        user (TokenData): The token data of the authenticated user.

    Returns:
        Union[DocumentMetadataRead, Dict[str, str]]: If the file is added, returns the uploaded document metadata.
            If the file is updated, returns the patched document metadata.
            Otherwise, returns a response dictionary.

    Raises:
        HTTP_400: If no input file is provided.
    """

    if not files:
        raise HTTP_400(
            msg="No input files provided..."
        )

    responses = []
    for file in files:
        response = await repository.upload(
            metadata_repo=metadata_repository,
            user_repo=user_repository,
            file=file,
            folder=folder,
            user=user
        )
        if response["response"] == "file added":
            return await metadata_repository.upload(document_upload=response["upload"])
        elif response["response"] == "file updated":
            return await metadata_repository.patch(
                document=response["upload"]["name"],
                document_patch=response["upload"],
                owner=user,
                user_repo=user_repository,
                is_owner=response["is_owner"]
            )
    return responses


@router.get(
    "{file_name}/download",
    status_code=status.HTTP_200_OK,
    name="download_document"
)
async def download(
    file_name: str,
    repository: DocumentRepository = Depends(DocumentRepository),
    metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
    user: TokenData = Depends(get_current_user),
) -> object:

    """
    Downloads a document with the specified file name.

    Args:
        file_name (str): The name of the file to be downloaded.
        repository (DocumentRepository): The repository for managing documents.
        metadata_repository (DocumentMetadataRepository): The repository for managing document metadata.
        user (TokenData): The token data of the authenticated user.

    Returns:
        object: The downloaded document.

    Raises:
        HTTP_400: If no file name is provided.
        HTTP_404: If no file with the specified name is found.
    """

    if not file_name:
        raise HTTP_400(
            msg="No file name..."
        )
    try:
        get_document_metadata = dict(await metadata_repository.get(document=file_name, owner=user))

        return await repository.download(s3_url=get_document_metadata["s3_url"], name=get_document_metadata["name"])
    except Exception as e:
        raise HTTP_404(
            msg=f"No file with {file_name}"
        ) from e


@router.delete(
    "/{file_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="add_to_bin"
)
async def add_to_bin(
        file_name: str,
        metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        user: TokenData = Depends(get_current_user),
) -> None:

    """
    Adds a document to the bin for deletion.

    Args:
        file_name (str): The name of the file to be added to the bin.
        metadata_repository (DocumentMetadataRepository): The repository for managing document metadata.
        user (TokenData): The token data of the authenticated user.

    Returns:
        None: If the file is added to the bin.
    """

    return await metadata_repository.delete(document=file_name, owner=user)


@router.get(
    "/trash",
    status_code=status.HTTP_200_OK,
    response_model=None,
    name="list_of_bin",
)
async def list_bin(
        metadata_repo: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        owner: TokenData = Depends(get_current_user)
) -> Dict[str, List[Row | Row] | int]:

    """
    List bin.

    Args:
        metadata_repo: The document metadata repository.
        owner: The token data of the owner.

    Returns:
        Dict[str, List[Row | Row] | int]: The list of bin.

    """

    return await metadata_repo.bin_list(owner=owner)


@router.delete(
    "/trash/{file_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="permanently_delete_doc"
)
async def perm_delete(
        file_name: str = None,
        delete_all: bool = False,
        repository: DocumentRepository = Depends(DocumentRepository),
        metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        user: TokenData = Depends(get_current_user),
) -> None:

    """
    Permanently deletes a document.

    Args:
        file_name (str, optional): The name of the file to be permanently deleted. Defaults to None.
        delete_all (bool): Flag indicating whether to delete all documents in the bin. Defaults to False.
        repository (DocumentRepository): The repository for managing documents.
        metadata_repository (DocumentMetadataRepository): The repository for managing document metadata.
        user (TokenData): The token data of the authenticated user.

    Returns:
        None: If the file is permanently deleted.

    Raises:
        HTTP_404: If no file with the specified name is found.
    """

    try:
        get_documents_metadata = dict(await metadata_repository.bin_list(owner=user))
        if len(get_documents_metadata["response"]) > 0:
            return await repository.perm_delete(
                file=file_name,
                bin_list=get_documents_metadata["response"],
                delete_all=delete_all,
                meta_repo=metadata_repository,
                user=user
            )

    except Exception as e:
        raise HTTP_404(
            msg=f"No file with {file_name}"
        ) from e


@router.post(
    "/restore/{file}",
    status_code=status.HTTP_200_OK,
    response_model=DocumentMetadataRead,
    name="restore_from_bin",
)
async def restore_bin(
        file: str,
        metadata_repo: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        user: TokenData = Depends(get_current_user)
) -> DocumentMetadataRead:

    """
    Restore bin.

    Args:
        file: The file to restore.
        metadata_repo: The document metadata repository.
        user: The token data of the user.

    Returns:
        DocumentMetadataRead: The restored document metadata.

    """

    return await metadata_repo.restore(file=file, owner=user)


@router.delete(
    "/trash",
    status_code=status.HTTP_204_NO_CONTENT,
    name="empty_trash",
)
async def empty_trash(
        metadata_repo: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        user: TokenData = Depends(get_current_user)
) -> None:

    """
    Deletes all documents in the trash bin for the authenticated user.

    Args:
        metadata_repo (DocumentMetadataRepository): The repository for accessing document metadata.
        user (TokenData): The token data of the authenticated user.

    Returns:
        None
    """

    return await metadata_repo.empty_bin(owner=user)


@router.get(
    "/preview/{document}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="preview_document"
)
async def get_document_preview(
        document: Union[str, UUID],
        repository: DocumentRepository = Depends(DocumentRepository),
        metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        user: TokenData = Depends(get_current_user)
) -> FileResponse:

    """
    Get the preview of a document.

    Args:
        document (Union[str, UUID]): The ID or name of the document.
        repository (DocumentRepository): The repository for accessing document data.
        metadata_repository (DocumentMetadataRepository): The repository for accessing document metadata.
        user (TokenData): The user token data.

    Returns:
        FileResponse: The file response containing the document preview.

    Raises:
        HTTP_404: If the document ID or name is not provided or if the document does not exist.
        HTTP_400: If the file type is not supported for preview.
    """

    if not document:
        raise HTTP_404(
            msg="Enter document id or name."
        )
    try:
        get_document_metadata = dict(await metadata_repository.get(document=document, owner=user))
        return await repository.preview(document=get_document_metadata)
    except TypeError as e:
        raise HTTP_404(
            msg="Document does not exists."
        ) from e
    except ValueError as e:
        raise HTTP_400(
            msg="File type is not supported for preview"
        ) from e
