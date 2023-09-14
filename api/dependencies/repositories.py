import re

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.models import async_session


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
        await session.commit()

def get_repository(repository):
    def _get_repository(session: AsyncSession = Depends(get_db)):
        return repository(session)

    return _get_repository

async def _get_s3_url(key: str) -> str:
    return f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"

async def _get_key(s3_url: str) -> str:

    pattern = (
        f"https://{settings.s3_bucket}"
        + r"\.s3\."
        + settings.aws_region
        + r"\.amazonaws\.com/"
        + r"(.+)"
    )
    if match:= re.search(pattern, s3_url):
        return match[1]
