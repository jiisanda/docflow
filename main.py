from fastapi import FastAPI
from fastapi.responses import FileResponse

from api.router import router
from core.config import settings
from db.models import Base, engine
from db.tables.documents.documents_metadata import create_table

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
)

app.include_router(router=router, prefix=settings.api_prefix)


favicon_path = 'favicon.ico'


@app.get(favicon_path, include_in_schema=False, tags=["Default"])
async def favicon():
    return FileResponse(favicon_path)


@app.get("/", tags=["Default"])
async def root():
    return {"API": "Document Management API"}


@app.get("/init-tables", tags=["Default"])
async def init_tables():

    create_table()
