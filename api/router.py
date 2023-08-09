from fastapi import APIRouter

from api.routes.documents import router as documents_router

router = APIRouter()

router.include_router(documents_router, prefix="/document")