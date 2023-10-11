from typing import Any, Dict
import boto3
import hashlib

from botocore.exceptions import ClientError
from fastapi import File
from ulid import ULID

from api.dependencies.constants import SUPPORTED_FILE_TYPES
from api.dependencies.repositories import get_key, get_s3_url
from core.config import settings
from core.exceptions import HTTP_400, HTTP_404
from schemas.auth.bands import TokenData


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

    @staticmethod
    async def _calculate_file_hash(file: File) -> str:

        file.file.seek(0)
        contents = file.file.read()
        file.file.seek(0)

        return hashlib.sha256(contents).hexdigest()

    async def _upload_new_file(
            self, file: File, folder: str, contents, file_type: str, user: TokenData
    ) -> Dict[str, Any]:

        if folder is None:
            key = f"{user.id}/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"
        else:
            key = f"{user.id}/{folder}/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"

        self.s3_bucket.put_object(Bucket=settings.s3_bucket, Key=key, Body=contents)

        return {
            "response": "file added",
            "upload": {
                "owner_id": user.id,
                "name": file.filename,
                "s3_url": await get_s3_url(key=key),
                "size": len(contents),
                "file_type": file_type,
                "file_hash": await self._calculate_file_hash(file=file)
            }
        }

    async def _upload_new_version(
            self, doc: dict, file: File, contents, file_type: str, new_file_hash: str, is_owner: bool
    ) -> Dict[str, Any]:

        key = await get_key(s3_url=doc["s3_url"])

        self.s3_bucket.put_object(Bucket=settings.s3_bucket, Key=key, Body=contents)

        return {
            "response": "file updated",
            "is_owner": is_owner,
            "upload": {
                "name": file.filename,
                "s3_url": await get_s3_url(key=key),
                "size": len(contents),
                "file_type": file_type,
                "file_hash": new_file_hash
            }
        }

    async def upload(self, metadata_repo, user_repo, file: File, folder: str, user: TokenData) -> Dict[str, Any]:

        file_type = file.content_type
        if file_type not in SUPPORTED_FILE_TYPES:
            raise HTTP_400(
                msg=f"File type {file_type} not supported."
            )

        contents = file.file.read()

        doc = (await metadata_repo.get(document=file.filename, owner=user)).__dict__
        # check if change in file
        new_file_hash = await self._calculate_file_hash(file=file)
        if "status_code" in doc.keys():
            # getting document irrespective of user
            if get_doc := (await metadata_repo.get_doc(filename=file.filename)):
                get_doc = get_doc.__dict__
                # Check if logged-in user has update access
                logged_in_user = (await user_repo.get_user(field="username", detail=user.username)).__dict__
                if (get_doc["access_to"] is not None) and logged_in_user["email"] in get_doc["access_to"]:
                    if get_doc['file_hash'] != new_file_hash:
                        # can upload a version to a file...
                        print(f"Have update access, to a file... owner: {get_doc['owner_id']}")
                        return await self._upload_new_version(
                            doc=get_doc, file=file, contents=contents, file_type=file_type,
                            new_file_hash=await self._calculate_file_hash(file=file),
                            is_owner=False
                        )
                else:
                    return await self._upload_new_file(
                        file=file, folder=folder, contents=contents, file_type=file_type, user=user
                    )
            return await self._upload_new_file(
                file=file, folder=folder, contents=contents, file_type=file_type, user=user
            )

        print("File already present, checking if there is an update...")

        if doc["file_hash"] != new_file_hash:
            print("File has been updated, uploading new version...")
            return await self._upload_new_version(doc=doc, file=file, contents=contents, file_type=file_type,
                                                  new_file_hash=new_file_hash, is_owner=True)

        return {
            "response": "File already present and no changes detected.",
            "upload": "Noting to update..."
        }

    async def download(self, s3_url: str, name: str) -> Dict[str, str]:

        key = get_key(s3_url=s3_url)

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
