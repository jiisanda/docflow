import boto3

from fastapi import File
from ulid import ULID

from api.dependencies.constants import SUPPORTED_FILE_TYPES
from core.config import settings

class DocumentRepository:

    def __init__(self):
        self.s3_client = boto3.resource('s3')
        self.s3_bucket = self.s3_client.Bucket(settings.s3_bucket)


    async def upload(self, file: File):

        file_type = file.content_type
        if file_type in SUPPORTED_FILE_TYPES:
            key = f"{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"
        contents = file.file.read()
        self.s3_bucket.put_object(Bucket=settings.s3_bucket, Key=key, Body=contents)

        return key
