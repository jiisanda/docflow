from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query

from api.dependencies.repositories import get_repository
from db.repositories.documents_metadata import DocumentMetadataRepository
from db.repositories.document_sharing import DocumentSharingRepository
from schemas.document_sharing import SharingRequest


router = APIRouter(tags=["Document Sharing"])


@router.post(
    "/{document}",
    status_code=status.HTTP_200_OK,
    name="share_document"
)
async def share_document(
    document: Union[str, UUID],
    share_request: SharingRequest,
    repository: DocumentSharingRepository = Depends(get_repository(DocumentSharingRepository)),
    metadata_repository: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository))
):

    doc = await metadata_repository.get(document=document)
    visits = share_request.visits
    presigned_url = await repository.get_presigned_url(doc=doc.__dict__)
    shareable_link = await repository.get_shareable_link(url=presigned_url, visits=visits)

    return {
        "personal_url": presigned_url,
        "share_this": shareable_link
    }
