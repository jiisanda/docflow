from sqlalchemy import Column, Integer, String

from db.models import Base



class DocumentSharing(Base):
    __tablename__ = "share_url"

    url_id: str = Column(String, primary_key=True, nullable=False, unique=True)
    url: str = Column(String, unique=True)
    visits: int = Column(Integer)
