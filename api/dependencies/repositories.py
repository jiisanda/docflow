from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import async_session


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
        await session.commit()

def get_repository(repository):
    def _get_repository(session: AsyncSession = Depends(get_db)):
        return repository(session)

    return _get_repository