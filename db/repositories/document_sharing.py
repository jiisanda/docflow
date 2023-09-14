import boto3
from typing import Any, Dict

from botocore.exceptions import NoCredentialsError

from api.dependencies.repositories import _get_key
from core.config import settings


class DocumentSharingRepository:

    def __init__(self):
        self.s3_client = boto3.resource('s3')
        self.client = boto3.client('s3')
        self.s3_bucket = self.s3_client.Bucket(settings.s3_bucket)


    async def get_presigned_url(self, doc: Dict[str, Any]):
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
