from fastapi import UploadFile
from io import BytesIO

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings


engine = create_engine(
    url=settings.sync_database_url,
    echo=settings.db_echo_log,
)

session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

metadata = MetaData()
Base = declarative_base()
