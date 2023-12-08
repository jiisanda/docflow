import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from core.config import settings
from core.exceptions import HTTP_500

logger = logging.getLogger("sqlalchemy")

engine = create_engine(
    url=settings.sync_database_url,
    echo=settings.db_echo_log,
)

async_engine = create_async_engine(
    url=settings.async_database_url,
    echo=settings.db_echo_log,
    query_cache_size=0,
)

session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()
metadata = Base.metadata


async def check_tables():
    try:
        with Session(engine) as _session:
            # Create tables
            metadata.create_all(engine)
            _session.commit()
            logger.info("Tables created if they didn't already exist.")
    except OperationalError as e:
        logger.error(f"Error Creating table: {e}")
        raise HTTP_500(msg="An error occurred while creating tables.")
