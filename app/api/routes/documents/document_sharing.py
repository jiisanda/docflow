from typing import Dict, Union
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse

from app.api.dependencies.auth_utils import get_current_user
from app.api.dependencies.repositories import get_repository, get_key
from app.core.exceptions import HTTP_404
from app.db.repositories.auth.auth import AuthRepository
from app.db.repositories.documents.documents import DocumentRepository
from app.db.repositories.documents.documents_metadata import DocumentMetadataRepository
from app.db.repositories.documents.document_sharing import DocumentSharingRepository
from app.db.repositories.documents.notify import NotifyRepo
from app.schemas.auth.bands import TokenData
from app.schemas.documents.document_sharing import SharingRequest


router = APIRouter(tags=["Document Sharing"])


@router.post(
    "/share-link/{document}",
    status_code=status.HTTP_200_OK,
    name="share_document_link"
)
async def share_link_document(
    document: Union[str, UUID],
    share_request: SharingRequest,
    repository: DocumentSharingRepository = Depends(get_repository(DocumentSharingRepository)),
    auth_repository: AuthRepository = Depends(get_repository(AuthRepository)),
    metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
    notify_repository: NotifyRepo = Depends(get_repository(NotifyRepo)),
    user: TokenData = Depends(get_current_user)
):

    """
    Shares a document link with another user, sends a mail and notifies the receiver.

    Args:
        document (Union[str, UUID]): The ID or name of the document to be shared.
        share_request (SharingRequest): The sharing request containing the details of the sharing operation.
        repository (DocumentSharingRepository): The repository for managing document sharing.
        auth_repository (AuthRepository): The repository for managing User related queries.
        metadata_repository (DocumentMetadataRepository): The repository for managing document metadata.
        notify_repository (NotifyRepo): The repository for managing notification
        user (TokenData): The token data of the authenticated user.

    Returns:
        Dict[str, str]: A dictionary containing the personal URL and shareable link.

    Raises:
        HTTP_404: If no document with the specified ID or name is found.
    """

    try:
        doc = await metadata_repository.get(document=document, owner=user)

        visits = share_request.visits
        share_to = share_request.share_to
        pre_signed_url = await repository.get_presigned_url(doc=doc.__dict__)
        shareable_link = await repository.get_shareable_link(
            owner_id=user.id,
            url=pre_signed_url,
            visits=visits,
            filename=doc.__dict__["name"],
            share_to=share_to,
        )

        if len(share_to) > 0:
            # Send email to the receiver
            await repository.send_mail(user=user, mail_to=share_to, link=shareable_link)

            # send a notification to the receiver
            await notify_repository.notify(
                user=user, receivers=share_to, filename=doc.__dict__["name"], auth_repo=auth_repository
            )

        return {
            "personal_url": pre_signed_url,
            "share_this": shareable_link
        }

    except KeyError as e:
        raise HTTP_404(
            msg=f"No doc: {document}"
        ) from e


@router.get("/doc/{url_id}", tags=["Document Sharing"])
async def redirect_to_share(
        url_id: str,
        repository: DocumentSharingRepository = Depends(get_repository(DocumentSharingRepository)),
        user: TokenData = Depends(get_current_user)
):

    """
    Redirects to a shared document URL.

    Args:
        url_id (str): The ID of the shared document URL.
        repository (DocumentSharingRepository): The repository for managing document sharing.
        user (TokenData): The token data of the authenticated user.

    Returns:
        RedirectResponse: A redirect response to the shared document URL.
    """

    if await repository.confirm_access(user=user, url_id=url_id):
        redirect_url = await repository.get_redirect_url(url_id=url_id)

        return RedirectResponse(redirect_url)


@router.post(
    "share/document",
    status_code=status.HTTP_200_OK,
    name="share_document"
)
async def share_document(
        document: Union[str, UUID],
        share_request: SharingRequest,
        notify: bool = True,
        repository: DocumentSharingRepository = Depends(get_repository(DocumentSharingRepository)),
        document_repo: DocumentRepository = Depends(DocumentRepository),
        metadata_repo: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
        notify_repo: NotifyRepo = Depends(get_repository(NotifyRepo)),
        auth_repo: AuthRepository = Depends(get_repository(AuthRepository)),
        user: TokenData = Depends(get_current_user),
) -> None:

    """
    Share a document with other users, and notifies if notify is set to True (default).

    Args:
        document (Union[str, UUID]): The ID or UUID of the document to be shared.
        share_request (SharingRequest): The sharing request containing the recipients and permissions.
        notify (bool, optional): Whether to send notifications to the recipients. Defaults to True.
        repository (DocumentSharingRepository, optional): The repository for document sharing operations.
        document_repo (DocumentRepository, optional): The repository for document operations.
        metadata_repo (DocumentMetadataRepository, optional): The repository for document metadata operations.
        notify_repo (NotifyRepo, optional): The repository for notification operations.
        auth_repo (AuthRepository, optional): The repository for authentication operations.
        user (TokenData, optional): The authenticated user.

    Raises:
        HTTP_404: If the document is not found.

    Returns:
        None
    """

    if not document:
        raise HTTP_404(
            msg="Enter document id or UUID."
        )
    try:
        get_document_metadata = dict(await metadata_repo.get(document=document, owner=user))
        key = await get_key(s3_url=get_document_metadata["s3_url"])

        file = await document_repo.get_s3_file_object_body(key=key)
        print("Here here")

        return await repository.share_document(
            filename=get_document_metadata["name"],
            document_key=key,
            file=file,
            share_request=share_request,
            notify=notify,
            owner=user,
            notify_repo=notify_repo,
            auth_repo=auth_repo
        )
    except Exception as e:
        raise HTTP_404() from e
