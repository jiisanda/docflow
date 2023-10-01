from datetime import datetime, timezone
from uuid import uuid4

from typing import List, Optional
from sqlalchemy import Column, String, Integer, ARRAY, text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from db.models import Base, metadata, engine
from db.tables.base_class import StatusEnum


class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id: UUID = Column(UUID(as_uuid=True), default=uuid4, primary_key=True, index=True, nullable=False)
    owner_id: Mapped[str] = Column(String, ForeignKey("users.id"), nullable=False)
    name: str = Column(String)
    s3_url: str = Column(String, unique=True)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
        server_default=text("NOW()")
    )
    size: Optional[int] = Column(Integer)
    file_type: Optional[str] = Column(String)
    tags: Optional[List[str]] = Column(ARRAY(String))
    categories: Optional[List[str]] = Column(ARRAY(String))
    status: Enum = Column(Enum(StatusEnum), default=StatusEnum.private)
    file_hash: Optional[str] = Column(String)

    owner = relationship("User", back_populates="owner_of")


def create_table():
    metadata.drop_all(engine)
    metadata.create_all(engine)
