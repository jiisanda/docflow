from typing import Any, Dict
import boto3
import re

from botocore.exceptions import ClientError
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


    async def _get_key(self, s3_url: str) -> str:

        pattern = (
            f"https://{settings.s3_bucket}"
            + r"\.s3\."
            + settings.aws_region
            + r"\.amazonaws\.com/"
            + r"(.+)"
        )
        if match:= re.search(pattern, s3_url):
            return match[1]


    async def upload(self, file: File, folder: str) -> Dict[str, Any]:

        file_type = file.content_type
        if file_type in SUPPORTED_FILE_TYPES:
            if folder is None:
                key = f"username/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"
            else:
                key = f"username/{folder}/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"
        contents = file.file.read()

        self.s3_bucket.put_object(Bucket=settings.s3_bucket, Key=key, Body=contents)

        return {
            "name": file.filename,
            "s3_url": await self._get_s3_url(key=key),
            "size": file.file.tell(),
            "file_type": file_type,
        }


    async def download(self, s3_url: str, name: str) -> Dict[str, str]:

        key = self._get_key(s3_url=s3_url)

        self.s3_client.meta.client.download_file(
            Bucket=settings.s3_bucket,
            Key=await key,
            Filename=r"downloads\docflow_" + f"{name}"
        )

        return {"message": f"successfully downloaded {name} in downloads folder."}
