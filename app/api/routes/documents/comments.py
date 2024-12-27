from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends

from app.api.dependencies.auth_utils import get_current_user
from app.api.dependencies.repositories import get_repository
from app.db.repositories.documents.comments import CommentRepository
from app.db.repositories.documents.documents import DocumentRepository
from app.schemas.auth.bands import TokenData
from app.schemas.documents.comments import CommentRead, CommentCreate, CommentUpdate

router = APIRouter(tags=["Comments"])


@router.post(
    "/",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    name="create_comment",
)
async def create_comment(
    comment: CommentCreate,
    user: TokenData = Depends(get_current_user),
    doc_repo: DocumentRepository = Depends(get_repository(DocumentRepository)),
    repository: CommentRepository = Depends(get_repository(CommentRepository)),
) -> CommentRead: ...


@router.get(
    "/{doc_id}",
    response_model=List[CommentRead],
    status_code=status.HTTP_200_OK,
    name="get_comments",
)
async def get_document_comments(
    doc_id: UUID,
    user: TokenData = Depends(get_current_user),
    doc_repo: DocumentRepository = Depends(get_repository(DocumentRepository)),
    repository: CommentRepository = Depends(get_repository(CommentRepository)),
) -> List[CommentRead]: ...


@router.put(
    "/{comment_id}",
    response_model=CommentRead,
    status_code=status.HTTP_200_OK,
    name="update_comment",
)
async def update_comment(
    comment_id: UUID,
    comment_update: CommentUpdate,
    user: TokenData = Depends(get_current_user),
    repository: CommentRepository = Depends(get_repository(CommentRepository)),
) -> CommentRead: ...


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_comment",
)
async def delete_comment(
    comment_id: UUID,
    user: TokenData = Depends(get_current_user),
    repository: CommentRepository = Depends(get_repository(CommentRepository)),
) -> None: ...
