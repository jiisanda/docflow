import hashlib
import os
import tempfile
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError
from fastapi import File
from starlette.responses import FileResponse
from ulid import ULID

from app.api.dependencies.constants import SUPPORTED_FILE_TYPES
from app.api.dependencies.repositories import TempFileResponse, get_key, get_s3_url
from app.core.config import settings
from app.core.exceptions import http_400, http_404
from app.db.repositories.documents.documents_metadata import DocumentMetadataRepository
from app.schemas.auth.bands import TokenData


async def perm_delete(
    file: str, delete_all: bool, meta_repo: DocumentMetadataRepository, user: TokenData
) -> None:

    if delete_all:
        await meta_repo.empty_bin(owner=user)
    else:
        doc = await meta_repo.bin_list(owner=user)
        for docs in doc.get("response"):
            if docs.DocumentMetadata.name == file:
                doc_id = docs.DocumentMetadata.id
                await meta_repo.perm_delete_a_doc(document=doc_id, owner=user)


class DocumentRepository:

    def __init__(self):
        boto3_config = {
            "aws_access_key_id": settings.aws_access_key_id,
            "aws_secret_access_key": settings.aws_secret_key,
            "region_name": settings.aws_region,
        }

        if settings.s3_endpoint_url:
            boto3_config["endpoint_url"] = settings.s3_endpoint_url

        self.s3_client = boto3.resource("s3", **boto3_config)
        self.client = boto3.client("s3", **boto3_config)
        self.s3_bucket = self.s3_client.Bucket(settings.s3_bucket)
        try:
            self.client.put_bucket_versioning(
                Bucket=settings.s3_bucket, VersioningConfiguration={"Status": "Enabled"}
            )
        except Exception as e:
            # Minio does not support versioning in all configurations
            ...

    @staticmethod
    async def _calculate_file_hash(file: File) -> str:

        file.file.seek(0)
        contents = file.file.read()
        file.file.seek(0)

        return hashlib.sha256(contents).hexdigest()

    async def get_s3_file_object_body(self, key: str):
        s3_object = self.client.get_object(Bucket=settings.s3_bucket, Key=key)
        file = s3_object["Body"].read()

        return file

    async def _delete_object(self, key: str) -> None:

        try:
            self.client.delete_object(Bucket=settings.s3_bucket, Key=key)
        except Exception as e:
            raise e

    async def _upload_new_file(
        self, file: File, folder: str, contents, file_type: str, user: TokenData
    ) -> Dict[str, Any]:

        if folder is None:
            key = f"{user.id}/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"
        else:
            key = f"{user.id}/{folder}/{str(ULID())}.{SUPPORTED_FILE_TYPES[file_type]}"

        self.s3_bucket.put_object(Key=key, Body=contents)

        return {
            "response": "file_added",
            "upload": {
                "owner_id": user.id,
                "name": file.filename,
                "s3_url": await get_s3_url(key=key),
                "size": len(contents),
                "file_type": file_type,
                "file_hash": await self._calculate_file_hash(file=file),
            },
        }

    async def _upload_new_version(
        self,
        doc: dict,
        file: File,
        contents,
        file_type: str,
        new_file_hash: str,
        is_owner: bool,
    ) -> Dict[str, Any]:

        key = await get_key(s3_url=doc["s3_url"])

        self.s3_bucket.put_object(Key=key, Body=contents)

        return {
            "response": "file_updated",
            "is_owner": is_owner,
            "upload": {
                "name": file.filename,
                "s3_url": await get_s3_url(key=key),
                "size": len(contents),
                "file_type": file_type,
                "file_hash": new_file_hash,
            },
        }

    async def upload(
        self, metadata_repo, user_repo, file: File, folder: str, user: TokenData
    ) -> Dict[str, Any]:
        """
        Uploads a file to the specified folder in the document repository.

        Args:
            metadata_repo: The repository for accessing metadata.
            user_repo: The repository for accessing user information.
            file: The file to be uploaded.
            folder: The folder in which the file should be uploaded.
            user: The token data of the user.

        Returns:
            @return: A dictionary containing the response and upload information.

        Raises:
            HTTP_400: If the file type is not supported.
        """

        file_type = file.content_type
        if file_type not in SUPPORTED_FILE_TYPES:
            raise http_400(msg=f"File type {file_type} not supported.")

        contents = await file.read()

        doc = (await metadata_repo.get(document=file.filename, owner=user)).__dict__
        # hash of the file uploaded to check if change in file
        new_file_hash: str = await self._calculate_file_hash(file=file)
        try:
            if "status_code" in doc.keys():
                # getting document irrespective of user
                if get_doc := await metadata_repo.get_doc(filename=file.filename):
                    get_doc = get_doc.__dict__
                    # Check if logged-in user has update access
                    logged_in_user = (
                        await user_repo.get_user(field="username", detail=user.username)
                    ).__dict__
                    if (get_doc["access_to"] is not None) and logged_in_user[
                        "email"
                    ] in get_doc["access_to"]:
                        if get_doc["file_hash"] != new_file_hash:
                            # can upload a version to a file...
                            print(
                                f"Have update access, to a file... owner: {get_doc['owner_id']}"
                            )
                            return await self._upload_new_version(
                                doc=get_doc,
                                file=file,
                                contents=contents,
                                file_type=file_type,
                                new_file_hash=await self._calculate_file_hash(
                                    file=file
                                ),
                                is_owner=False,
                            )
                    else:
                        return await self._upload_new_file(
                            file=file,
                            folder=folder,
                            contents=contents,
                            file_type=file_type,
                            user=user,
                        )
                return await self._upload_new_file(
                    file=file,
                    folder=folder,
                    contents=contents,
                    file_type=file_type,
                    user=user,
                )

            print(
                f"File {file.filename} already present, checking if there is an update..."
            )

            if doc["file_hash"] != new_file_hash:
                print("File has been updated, uploading new version...")
                return await self._upload_new_version(
                    doc=doc,
                    file=file,
                    contents=contents,
                    file_type=file_type,
                    new_file_hash=new_file_hash,
                    is_owner=True,
                )

            return {
                "response": "File already present and no changes detected.",
                "upload": "Noting to update...",
            }
        except Exception as e:
            raise http_404(msg="Error uploading the file...") from e

    async def download(self, s3_url: str, name: str) -> Dict[str, str]:

        key = get_key(s3_url=s3_url)

        try:
            self.s3_client.meta.client.download_file(
                Bucket=settings.s3_bucket,
                Key=await key,
                Filename=r"/app/downloads/docflow_" + f"{name}",
            )
        except ClientError as e:
            raise http_404(msg=f"File not found: {e}") from e

        return {"message": f"successfully downloaded {name} in downloads folder."}

    async def preview(self, document: Dict[str, Any]) -> FileResponse:

        key = await get_key(s3_url=document["s3_url"])

        file = await self.get_s3_file_object_body(key)

        # Determining the file extension from the key and media type for File Response
        _, extension = os.path.splitext(key)
        if extension.lower() in [".jpg", ".jpeg", ".png", ".gif"]:
            media_type = "image/" + extension.lower().lstrip(".")
        elif extension.lower() == ".pdf":
            media_type = "application/pdf"
        else:
            raise ValueError("Unsupported file type.")

        # Creating a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp:
            temp.write(file)
            temp_path = temp.name

        return TempFileResponse(temp_path, media_type=media_type)
