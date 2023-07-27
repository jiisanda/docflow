from datetime import datetime
from uuid import UUID, uuid4

from fastapi import UploadFile, File
from typing import List, Optional
from sqlalchemy import Column, LargeBinary, String, Integer, ARRAY

from db.models import Base, metadata, engine


class Document(Base):
    __tablename__ = "documents"

    _id: UUID = Column(default=uuid4, primary_key=True, index=True, nullable=False)
    name: Optional[str] = Column(String, unique=True)
    data: Optional[str] = Column(LargeBinary)
    created_at: datetime = Column(default=datetime.utcnow, nullable=False, server_default=text("NOW()"))
    size: Optional[int] = Column(Integer)
    file_type: Optional[str] = Column(String)
    tags: Optional[List[str]] = Column(ARRAY(String))
    categories: Optional[List[str]] = Column(ARRAY(String))
