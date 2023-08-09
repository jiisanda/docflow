from fastapi import APIRouter

router = APIRouter()

router.include_router(prefix="/document")