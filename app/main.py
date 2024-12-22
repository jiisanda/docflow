from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.router import router
from app.core.config import settings
from app.db.models import check_tables


app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
)

app.include_router(router=router, prefix=settings.api_prefix)


FAVICON_PATH = "favicon.ico"


@app.get(FAVICON_PATH, include_in_schema=False, tags=["Default"])
async def favicon():
    return FileResponse(FAVICON_PATH)


@app.get("/", tags=["Default"])
async def root():
    return {
        "API": "Document Management API... Docker's up!!! is it? or not... Yes it is!!!"
    }


@app.on_event("startup")
async def app_startup() -> None:
    return await check_tables()
