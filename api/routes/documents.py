from fastapi import APIRouter, status, File, UploadFile, HTTPException

from schemas.documents_metadata import DocumentMetadataRead

router = APIRouter(tags=["Document"])

@router.post(
    "/upload",
    # response_model=DocumentMetadataRead,
    status_code=status.HTTP_201_CREATED,
    name="upload_document"
)
async def upload(
    file: UploadFile = File(...),
):
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No file"
        )

    name = file.filename
    file_type = file.content_type

    return {"name": name, "type": file_type}
