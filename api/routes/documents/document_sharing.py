from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse

from api.dependencies.auth_utils import get_current_user
from api.dependencies.repositories import get_repository
from core.exceptions import HTTP_404
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
    metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
    user: TokenData = Depends(get_current_user)
):

    doc = await metadata_repository.get(document=document, owner=user)
    if doc:
        visits = share_request.visits
        pre_signed_url = await repository.get_presigned_url(doc=doc.__dict__)
        shareable_link = await repository.get_shareable_link(
            url=pre_signed_url,
            visits=visits,
            filename=doc.__dict__["name"]
        )

        return {
            "personal_url": pre_signed_url,
            "share_this": shareable_link
        }
    else:
        raise HTTP_404(
            msg=f"No doc: {document}"
        )


@router.get("/doc/{url_id}", tags=["Document Sharing"])
async def redirect_to_share(
        url_id: str,
        repository: DocumentSharingRepository = Depends(get_repository(DocumentSharingRepository))
):

    redirect_url = await repository.get_redirect_url(url_id=url_id)

    return RedirectResponse(redirect_url)
