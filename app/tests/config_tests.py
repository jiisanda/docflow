import asyncio
import pytest
import pytest_asyncio

from fastapi import FastAPI
from httpx import AsyncClient
from typing import Callable, Generator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.schemas.documents.documents_metadata import DocumentMetadataCreate
from app.db.models import metadata

test_db = (
    f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_server}:{settings.postgres_port}/{settings.postgres_db}"
)

engine = create_async_engine(
    test_db,
    echo=settings.db_echo_log,
    future=True,
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all(engine))
        await connection.run_sync(metadata.drop_all(engine))
        async with async_session(bind=connection) as session:
            yield session
            await session.flush()
            await session.rollback()


@pytest.fixture()
def override_get_db(db_session: AsyncSession) -> Callable:
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest.fixture()
def app(override_get_db: Callable) -> FastAPI:
    from app.api.dependencies.repositories import get_db
    from main import app

    app.dependency_overrides[get_db] = override_get_db

    return app


@pytest_asyncio.fixture()
async def async_client(app: FastAPI) -> AsyncSession:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture()
def upload_document_metadata():
    def _upload_document_metadata(
        name: str = "hello.pdf",
        s3_url: str = f"s3://{settings.s3_test_bucket}/codeakey_logo.png",
        status = "private",
    ):
        return DocumentMetadataCreate(name=name, s3_url=s3_url, status=status)

    return _upload_document_metadata


@pytest.fixture()
def upload_documents_metadata(upload_document_metadata):
    def _upload_documents_metadata(_qty: int = 1):
        return [
            upload_document_metadata(name=f"{i}.test", s3_url=f"s3://{settings.s3_test_bucket}/{i}.test", status="private")
            for i in range(_qty)
        ]

    return _upload_documents_metadata
