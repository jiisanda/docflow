from typing import List, Optional

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ARRAY, ForeignKey
from sqlalchemy.orm import Mapped

from db.models import Base


class DocumentSharing(Base):
    __tablename__ = "share_url"

    url_id: str = Column(String, primary_key=True, nullable=False, unique=True)
    filename: str = Column(String, unique=True, nullable=False)
    owner_id: Mapped[str] = Column(String, ForeignKey("users.id"), nullable=False)
    url: str = Column(String, unique=True)
    expires_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    visits: int = Column(Integer)
    share_to: Optional[List[str]] = Column(ARRAY(String))
