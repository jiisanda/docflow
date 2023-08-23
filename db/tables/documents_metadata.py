from datetime import datetime, timezone
from uuid import uuid4

from fastapi import UploadFile, File
from typing import List, Optional
from sqlalchemy import Column, LargeBinary, String, Integer, ARRAY, text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from core.config import settings
from db.models import Base, metadata, engine
from db.tables.base_class import StatusEnum


class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    _id: UUID = Column(UUID(as_uuid=True), default=uuid4, primary_key=True, index=True, nullable=False)
    name: str = Column(String, unique=True)
    s3_url: str = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False, server_default=text("NOW()"))
    size: Optional[int] = Column(Integer)
    file_type: Optional[str] = Column(String)
    tags: Optional[List[str]] = Column(ARRAY(String))
    categories: Optional[List[str]] = Column(ARRAY(String))
    status: Enum = Column(Enum(StatusEnum), default=StatusEnum.private)


def create_document():
    document_metadata = DocumentMetadata(
        name="codeakey_logo.png",
        s3_url=f"s3://{settings.s3_bucket}/codeakey_logo.png",
        status="private",
    )

    with Session(engine) as session:
        session.add(document_metadata)
        session.commit()


def create_table():
    metadata.drop_all(engine)
    metadata.create_all(engine)
    create_document()
