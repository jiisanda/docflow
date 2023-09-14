import boto3
import hashlib
from random import randint
from typing import Any, Dict, Union

from botocore.exceptions import NoCredentialsError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from api.dependencies.repositories import _get_key
from core.config import settings
from db.tables.document_sharing import DocumentSharing
from schemas.document_sharing import DocumentSharingRead


class DocumentSharingRepository:

    def __init__(self, session: AsyncSession) -> None:
        self.client = boto3.client('s3')

        self.session = session


    async def _generate_id(self, url: str) -> str:
        hash_object = hashlib.md5()
        hash_object.update(url.encode('utf-8'))

        n = randint(0, 25)

        return hash_object.hexdigest()[n:n+6]


    async def get_presigned_url(self, doc: Dict[str, Any]) -> Union[str, Dict[str, str]]:
        try:
            params = {
                'Bucket': settings.s3_bucket,
                'Key': await _get_key(s3_url=doc["s3_url"])
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


    async def get_shareable_link(self, url: str, visits: int):

        url_id = await self._generate_id(url=url)
        share_entry = DocumentSharing(
            url_id=url_id,
            url=url,
            visits=visits
        )

        try:
            self.session.add(share_entry)
            await self.session.commit()
            await self.session.refresh(share_entry)
        except IntegrityError as e:
            raise e

        response = share_entry.__dict__
        return {
            "share_this_link": f"http://localhost:8000/doc/{response['url_id']}",
            "visits": response["visits"]
        }
