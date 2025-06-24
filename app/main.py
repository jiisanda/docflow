from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.router import router
from app.core.config import settings
from app.db.models import check_tables
from app.logs.logger import docflow_logger
from app.scripts.init_bucket import create_bucket_if_not_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    docflow_logger.info("Starting DocFlow...")
    
    try:
        docflow_logger.info("Initializing Tables and Storage buckets...")
        await check_tables()
        await create_bucket_if_not_exists()
        docflow_logger.info("Tables and Storage buckets successfully created.")
    except Exception as e:
        docflow_logger.error(f"Error during startup: {e}")
        raise
    yield 

app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
    lifespan=lifespan,
)

app.include_router(router=router, prefix=settings.api_prefix)


FAVICON_PATH = "favicon.ico"


@app.get(FAVICON_PATH, include_in_schema=False, tags=["Default"])
async def favicon():
    return FileResponse(FAVICON_PATH)


@app.get("/", tags=["Default"])
async def root():
    return {
        "API": "DocFlow - Document Management API is running! 🚀",
        "version": settings.version,
        "docs": f"{settings.host_url}{settings.docs_url}",
        "storage": "MinIO" if settings.s3_endpoint_url else "AWS S3"
    }


@app.get("/health", tags=["Default"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DocFlow API",
        "version": settings.version
    }
