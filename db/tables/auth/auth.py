from sqlalchemy import Column, String, Text

from api.dependencies.repositories import get_ulid
from db.models import Base


class User(Base):
    __tablename__ = "user_table"

    id = Column(String(26), primary_key=True, default=get_ulid, unique=True, index=True, nullable=False)
    username: str = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Text)
