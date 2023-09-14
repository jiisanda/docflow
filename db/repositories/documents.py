from typing import Any, Dict
import boto3
import hashlib

from botocore.exceptions import ClientError
from fastapi import File
from ulid import ULID

from api.dependencies.constants import SUPPORTED_FILE_TYPES
from api.dependencies.repositories import _get_key, _get_s3_url
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


    async def _calculate_file_hash(self, file: File) -> str:

        file.file.seek(0)
        contents = file.file.read()
        file.file.seek(0)

        return hashlib.sha256(contents).hexdigest()


    async def _upload_new_file(self, file: File, folder: str, contents, file_type: str) -> Dict[str, Any]:

        if folder is None:
            key = f"username/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"
        else:
            key = f"username/{folder}/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"

        self.s3_bucket.put_object(Bucket=settings.s3_bucket, Key=key, Body=contents)

        return {
            "response": "file added",
            "upload": {
                "name": file.filename,
                "s3_url": await _get_s3_url(key=key),
                "size": len(contents),
                "file_type": file_type,
                "file_hash": await self._calculate_file_hash(file=file)
            }
        }


    async def _upload_new_version(self, doc: dict, file: File, contents, file_type: str, new_file_hash: str) -> Dict[str, Any]:

        key = await _get_key(s3_url=doc["s3_url"])

        self.s3_bucket.put_object(Bucket=settings.s3_bucket, Key=key, Body=contents)

        return {
            "response": "file updated",
            "upload": {
                "name": file.filename,
                "s3_url": await _get_s3_url(key=key),
                "size": len(contents),
                "file_type": file_type,
                "file_hash": new_file_hash
            }
        }


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
            return await self._upload_new_file(file=file, folder=folder, contents=contents, file_type=file_type)

        print("File already present, checking if there is an update...")

        new_file_hash = await self._calculate_file_hash(file=file)
        if doc["file_hash"] != new_file_hash:
            print("File has been updated, uploading new version...")
            return await self._upload_new_version(doc=doc, file=file, contents=contents, file_type=file_type, new_file_hash=new_file_hash)

        return {
            "response": "File already present and no changes detected.",
            "upload": "Noting to update..."
        }


    async def download(self, s3_url: str, name: str) -> Dict[str, str]:

        key = _get_key(s3_url=s3_url)

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
