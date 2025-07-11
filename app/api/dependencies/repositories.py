import os.path
import re
from typing import Optional

import ulid

from fastapi import Depends
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import async_session


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
    if settings.s3_endpoint_url:
        # minio URL format
        return f"{settings.s3_endpoint_url}/{settings.s3_bucket}/{key}"
    return f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"


async def get_key(s3_url: str) -> Optional[str]:
    if settings.s3_endpoint_url:
        # minio url format: http://host:9000/bucket/key
        # remove the endpoint and bucket form the URL
        url_without_endpoint = s3_url.replace(settings.s3_endpoint_url, "")
        url_without_bucket = url_without_endpoint.replace(f"/{settings.s3_bucket}/", "")
        return url_without_bucket.lstrip("/")
    else:
        pattern = (
            f"https://{settings.s3_bucket}"
            + r"\.s3\."
            + settings.aws_region
            + r"\.amazonaws\.com/"
            + r"(.+)"
        )
        if match := re.search(pattern, s3_url):
            return match[1]
        return None


def get_ulid():
    return str(ulid.ULID())
