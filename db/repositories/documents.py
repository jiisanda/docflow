from typing import Any, Dict
import boto3
import re

from botocore.exceptions import ClientError
from fastapi import File
from ulid import ULID

from api.dependencies.constants import SUPPORTED_FILE_TYPES
from core.config import settings
from core.exceptions import HTTP_404

class DocumentRepository:

    def __init__(self):
        self.s3_client = boto3.resource('s3')
        self.client = boto3.client('s3')
        self.s3_bucket = self.s3_client.Bucket(settings.s3_bucket)
        self.client.put_bucket_versioning(
            Bucket=settings.s3_bucket,
            VersioningConfiguration={
                'Status': 'Enabled'
            }
        )


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


    async def upload(self, metadata_repo, file: File, folder: str) -> Dict[str, Any]:

        file_type = file.content_type
        if file_type not in SUPPORTED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_type} not supported."
            )

        contents = file.file.read()

        doc = (await metadata_repo.get(document=file.filename)).__dict__
        if "status_code" in doc.keys():
            if folder is None:
                key = f"username/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"
            else:
                key = f"username/{folder}/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"

            self.s3_bucket.put_object(Bucket=settings.s3_bucket, Key=key, Body=contents)

            return {
                "result": "file added",
                "name": file.filename,
                "s3_url": await self._get_s3_url(key=key),
                "size": file.file.tell(),
                "file_type": file_type,
            }
        else:
            print("File already present, updating the file...")
            key = await self._get_key(s3_url=doc["s3_url"])

            self.s3_bucket.put_object(Bucket=settings.s3_bucket, Key=key, Body=contents)

            return {
                "result": f"Successfully updated file... new version to {file.filename} upgraded..."
            }


    async def download(self, s3_url: str, name: str) -> Dict[str, str]:

        key = self._get_key(s3_url=s3_url)

        try:
            self.s3_client.meta.client.download_file(
                Bucket=settings.s3_bucket,
                Key=await key,
                Filename=r"downloads\docflow_" + f"{name}"
            )
        except ClientError as e:
            raise HTTP_404(
                msg=f"File not found: {e}"
            ) from e

        return {"message": f"successfully downloaded {name} in downloads folder."}
