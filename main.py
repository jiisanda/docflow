from fastapi import FastAPI
from fastapi.responses import FileResponse

from api.router import router
from core.config import settings


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
    return {"API": "Document Management API... Docker's up!!! is it? or not... Yes it is!!!"}
