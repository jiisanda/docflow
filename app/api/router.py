from fastapi import APIRouter

from app.api.routes.auth.auth import router as auth_router
from app.api.routes.documents.documents_metadata import router as documents_metadata_router
from app.api.routes.documents.document import router as documents_router
from app.api.routes.documents.document_organization import router as document_organization_router
from app.api.routes.documents.document_sharing import router as document_sharing_router
from app.api.routes.documents.notify import router as notify_router

router = APIRouter()

router.include_router(auth_router, prefix="/u")
router.include_router(documents_router, prefix="/document")
router.include_router(notify_router, prefix="/notifications")
router.include_router(documents_metadata_router, prefix="/document-metadata")
router.include_router(document_organization_router, prefix="/filter")
router.include_router(document_sharing_router)
