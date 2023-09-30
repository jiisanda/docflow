from sqlalchemy import Column, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

from api.dependencies.repositories import get_ulid
from db.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(26), primary_key=True, default=get_ulid, unique=True, index=True, nullable=False)
    username: str = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    user_since = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    owner_of = relationship("DocumentMetadata", back_populates="owner")
