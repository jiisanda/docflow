from fastapi import APIRouter, status


router = APIRouter(tags=["Document Sharing"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    name="share_document"
)
async def share_document():
    ...

