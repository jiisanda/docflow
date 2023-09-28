import boto3
import hashlib
from datetime import datetime, timedelta, timezone
from random import randint
from typing import Any, Dict, Union

from botocore.exceptions import NoCredentialsError
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.repositories import get_key
from core.config import settings
from core.exceptions import HTTP_404
from db.tables.documents.document_sharing import DocumentSharing


class DocumentSharingRepository:

    def __init__(self, session: AsyncSession) -> None:
        self.client = boto3.client('s3')

        self.session = session

    @staticmethod
    async def _generate_id(url: str) -> str:
        hash_object = hashlib.md5()
        hash_object.update(url.encode('utf-8'))

        n = randint(0, 25)

        return hash_object.hexdigest()[n:n+6]

    async def _get_saved_links(self, filename: str) -> Dict[str, Any]:

        stmt = (
            select(DocumentSharing)
            .where(DocumentSharing.filename == filename)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_visits(self, filename: str, visits_left: int):
        if visits_left-1 > 0:
            await self.session.execute(
                update(DocumentSharing)
                .where(DocumentSharing.filename == filename)
                .values(visits=visits_left-1)
            )
        elif visits_left-1 == 0:
            await self.session.execute(
                delete(DocumentSharing)
                .where(DocumentSharing.filename == filename)
            )

    async def cleanup_expired_links(self):

        now = datetime.now(timezone.utc)

        stmt = (
            delete(DocumentSharing)
            .where(DocumentSharing.expires_at <= now)
        )

        await self.session.execute(stmt)

    async def get_presigned_url(self, doc: Dict[str, Any]) -> Union[str, Dict[str, str]]:
        try:
            params = {
                'Bucket': settings.s3_bucket,
                'Key': await get_key(s3_url=doc["s3_url"])
            }
            response = self.client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=3600
            )
        except NoCredentialsError as e:
            return {
                "error": f"Invalid AWS Credentials: {e}"
            }

        return response

    async def get_shareable_link(self, url: str, visits: int, filename: str):

        # task to clean uo the database for expired links
        await self.cleanup_expired_links()

        if ans := await self._get_saved_links(filename=filename):
            ans = ans.__dict__
            return {
                "note": f"Links already shared... valid Till {ans['expires_at']}",
                "response": {
                    "shareable_link": f"http://localhost:8000/doc/{ans['url_id']}",
                    "visits_left": ans["visits"]
                }
            }

        url_id = await self._generate_id(url=url)
        share_entry = DocumentSharing(
            url_id=url_id,
            filename=filename,
            url=url,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=3599),
            visits=visits
        )

        self.session.add(share_entry)
        await self.session.commit()
        await self.session.refresh(share_entry)

        response = share_entry.__dict__
        return {
            "shareable_link": f"http://localhost:8000/doc/{response['url_id']}",
            "visits": response["visits"]
        }

    async def get_redirect_url(self, url_id: str):

        stmt = (
            select(DocumentSharing)
            .where(DocumentSharing.url_id == url_id)
        )

        result = await self.session.execute(stmt)
        try:
            result = result.scalar_one_or_none().__dict__

            await self.update_visits(filename=result["filename"], visits_left=result["visits"])

            return result["url"]
        except AttributeError as e:
            raise HTTP_404(
                msg="Shared URL link either expired or reached the limit of visits..."
            ) from e
