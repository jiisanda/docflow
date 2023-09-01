from typing import Any, Dict
import boto3

from fastapi import File
from ulid import ULID

from api.dependencies.constants import SUPPORTED_FILE_TYPES
from core.config import settings

class DocumentRepository:

    def __init__(self):
        self.s3_client = boto3.resource('s3')
        self.s3_bucket = self.s3_client.Bucket(settings.s3_bucket)


    async def _get_s3_url(self, key: str) -> str:
        return f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"
    """
        url = boto3.client('s3').generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.s3_bucket,
                "Key": key
            }
        )

        return url
    """

    async def upload(self, file: File) -> Dict[str, Any]:

        file_type = file.content_type
        if file_type in SUPPORTED_FILE_TYPES:
            key = f"username/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"
        contents = file.file.read()

        self.s3_bucket.put_object(Bucket=settings.s3_bucket, Key=key, Body=contents)

        return {
            "name": file.filename,
            "s3_url": await self._get_s3_url(key=key),
            "size": file.file.tell(),
        }
