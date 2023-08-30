from fastapi import APIRouter

from api.routes.documents_metadata import router as documents_metadata_router
from api.routes.documents import router as documents_router

router = APIRouter()

router.include_router(documents_metadata_router, prefix="/document-metadata")
router.include_router(documents_router, prefix="/document")