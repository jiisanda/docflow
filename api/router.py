from fastapi import APIRouter

from api.routes.documents_metadata import router as documents_metadata_router

router = APIRouter()

router.include_router(documents_metadata_router, prefix="/document")