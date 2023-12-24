import os.path
import re
import ulid

from fastapi import Depends
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from db.models import async_session


class TempFileResponse(FileResponse):
    def __init__(self, path, *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self.file_path = path

    def __del__(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
        await session.commit()


def get_repository(repository):
    def _get_repository(session: AsyncSession = Depends(get_db)):
        return repository(session)

    return _get_repository


async def get_s3_url(key: str) -> str:
    return f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"


async def get_key(s3_url: str) -> str:

    pattern = (
        f"https://{settings.s3_bucket}"
        + r"\.s3\."
        + settings.aws_region
        + r"\.amazonaws\.com/"
        + r"(.+)"
    )
    if match := re.search(pattern, s3_url):
        return match[1]


def get_ulid():
    return str(ulid.ULID())
