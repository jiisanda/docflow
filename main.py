from fastapi import FastAPI, status, Depends
from sqlalchemy.orm import Session

from api.router import router
from core.config import settings
from db.models import Base, engine, session
from db.tables.documents import create_table
from schemas import documents

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
)

app.include_router(router=router, prefix=settings.api_prefix)

# Dependency
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"API": "Document Management API"}


@app.get("/init-tables")
async def init_tables():

    create_table()
