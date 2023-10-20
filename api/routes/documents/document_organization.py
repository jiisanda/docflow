from fastapi import APIRouter, Depends, status, Query

from api.dependencies.repositories import get_repository
from api.dependencies.auth_utils import get_current_user
from db.repositories.documents.documents_metadata import DocumentMetadataRepository
from db.repositories.documents.document_organization import DocumentOrgRepository
from schemas.auth.bands import TokenData

router = APIRouter(tags=["Document Search"])


@router.get(
    "",
    # response_model=List[DocumentMetadataRead],
    status_code=status.HTTP_200_OK,
    name="search_document",
)
async def search_document(
    limit: int = Query(default=10, lt=100),
    offset: int = Query(default=0),
    tag: str = None,
    category: str = None,
    file_types: str = None,
    doc_status: str = None,
    repository: DocumentOrgRepository = Depends(DocumentOrgRepository),
    repository_metadata: DocumentMetadataRepository = Depends(get_repository(DocumentMetadataRepository)),
    user: TokenData = Depends(get_current_user),
):

    """
    Searches for documents based on specified criteria.

    Args:
        limit (int): The maximum number of documents to retrieve. Defaults to 10.
        offset (int): The number of documents to skip. Defaults to 0.
        tag (str, optional): The tag to filter documents by. Defaults to None.
        category (str, optional): The category to filter documents by. Defaults to None.
        file_types (str, optional): The file types to filter documents by. Defaults to None.
        doc_status (str, optional): The status of documents to filter by. Defaults to None.
        repository (DocumentOrgRepository): The repository for managing document organization.
        repository_metadata (DocumentMetadataRepository): The repository for managing document metadata.
        user (TokenData): The token data of the authenticated user.

    Returns:
        List[DocumentMetadataRead] or List[Dict[str, Any]]: The list of matching documents.
    """

    doc_list = await repository_metadata.doc_list(limit=limit, offset=offset, owner=user)
    doc_list = doc_list[f"documents of {user.username}"]
    if tag is None and category is None and file_types is None and doc_status is None:
        return doc_list

    else:
        return await repository.search_doc(
            docs=doc_list,
            tags=tag,
            categories=category,
            file_types=file_types,
            status=doc_status
        )
