from fastapi import APIRouter

from api.routes.documents_metadata import router as documents_metadata_router
from api.routes.documents import router as documents_router
from api.routes.document_organization import router as document_organization_router
from api.routes.document_sharing import router as document_sharing_router

router = APIRouter()

router.include_router(documents_router, prefix="/document")
router.include_router(documents_metadata_router, prefix="/document-metadata")
router.include_router(document_organization_router, prefix="/search")
router.include_router(document_sharing_router, prefix="/share")
