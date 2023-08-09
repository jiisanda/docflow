from fastapi import FastAPI, status, Depends
from sqlalchemy.orm import Session

from core.config import settings
from db.models import Base, engine, session
from db.tables.documents import create_table
from schemas import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
)

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
async def init_tables(document: schemas.DocumentCreate, db: Session = Depends(get_db)):
    create_table(db=db, document=document)
    
    return "Created"