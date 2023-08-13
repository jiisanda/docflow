from datetime import datetime
from uuid import UUID, uuid4

from fastapi import UploadFile, File
from typing import List, Optional
from sqlalchemy import Column, LargeBinary, String, Integer, ARRAY, text, DateTime
from sqlalchemy.orm import Session

from db.models import Base, metadata, engine
from db.tables.base_class import StatusEnum
from schemas.documents import DocumentCreate


class Document(Base):
    __tablename__ = "documents"

    _id: UUID = Column(String, default=uuid4, primary_key=True, index=True, nullable=False)
    name: str = Column(String, unique=True)
    s3_url: str = Column(String, unique=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False, server_default=text("NOW()"))
    size: Optional[int] = Column(Integer)
    file_type: Optional[str] = Column(String)
    tags: Optional[List[str]] = Column(ARRAY(String))
    categories: Optional[List[str]] = Column(ARRAY(String))
    status: StatusEnum = Column(String, default=StatusEnum.private)


def create_table(db: Session, document: DocumentCreate):
    db_document = Document(
        name="codeakey_logo.png",
        s3_url="s3://docflow-trial/codeakey_logo.png"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document
