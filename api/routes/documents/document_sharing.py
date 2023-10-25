from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse

from api.dependencies.auth_utils import get_current_user
from api.dependencies.repositories import get_repository
from core.exceptions import HTTP_404
from db.repositories.auth.auth import AuthRepository
from db.repositories.documents.documents_metadata import DocumentMetadataRepository
from db.repositories.documents.document_sharing import DocumentSharingRepository
from schemas.auth.bands import TokenData
from schemas.documents.document_sharing import SharingRequest


router = APIRouter(tags=["Document Sharing"])


@router.post(
    "/share/{document}",
    status_code=status.HTTP_200_OK,
    name="share_document"
)
async def share_document(
    document: Union[str, UUID],
    share_request: SharingRequest,
    repository: DocumentSharingRepository = Depends(get_repository(DocumentSharingRepository)),
    auth_repository: AuthRepository = Depends(get_repository(AuthRepository)),
    metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
    user: TokenData = Depends(get_current_user)
):
    """
    Shares a document with another user, sends a mail and notifies the receiver.

    Args:
        document (Union[str, UUID]): The ID or name of the document to be shared.
        share_request (SharingRequest): The sharing request containing the details of the sharing operation.
        repository (DocumentSharingRepository): The repository for managing document sharing.
        auth_repository (AuthRepository): The repository for managing User related queries.
        metadata_repository (DocumentMetadataRepository): The repository for managing document metadata.
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
            await repository.notify(
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
