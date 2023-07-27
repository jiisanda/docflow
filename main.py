from fastapi import FastAPI, status

from core.config import settings
from db.models import Base, engine


app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
)


@app.get("/")
async def root():
    return {"API": "Document Management API"}
