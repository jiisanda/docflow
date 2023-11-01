from datetime import datetime, timezone
from uuid import uuid4

from typing import List, Optional
from sqlalchemy import Column, String, Integer, ARRAY, text, DateTime, Enum, ForeignKey, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from db.models import Base, metadata, async_engine
from db.tables.base_class import StatusEnum


doc_user_access = Table(
    'doc_user_access',
    Base.metadata,
    Column('doc_id', UUID(as_uuid=True), ForeignKey('document_metadata.id', ondelete='CASCADE')),
    Column('user_id', String(26), ForeignKey('users.id')),
    UniqueConstraint('doc_id', 'user_id', name="uq_doc_user_access_doc_user")
)


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
    access_to: Optional[List[str]] = Column(ARRAY(String))

    update_access = relationship("User", secondary=doc_user_access, passive_deletes=True)
    owner = relationship("User", back_populates="owner_of")
