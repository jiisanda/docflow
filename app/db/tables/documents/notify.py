from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, String, Text, Enum, DateTime, text
from sqlalchemy.dialects.postgresql import UUID

from app.db.tables.base_class import NotifyEnum
from app.db.models import Base


class Notify(Base):
    __tablename__ = 'notify'

    id: UUID = Column(UUID(as_uuid=True), default=uuid4, primary_key=True, index=True, nullable=False)
    receiver_id: str = Column(String, nullable=False)
    message: str = Column(Text, nullable=False)
    status: Enum = Column(Enum(NotifyEnum), default=NotifyEnum.unread)
    notified_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
        server_default=text("NOW()")
    )
