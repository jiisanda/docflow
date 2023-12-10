import os.path
import tempfile
from typing import Any, Dict, List
import boto3
import hashlib

from botocore.exceptions import ClientError
from fastapi import File
from fastapi.responses import FileResponse
from sqlalchemy.engine import Row
from ulid import ULID

from api.dependencies.constants import SUPPORTED_FILE_TYPES
from api.dependencies.repositories import get_key, get_s3_url
from core.config import settings
from core.exceptions import HTTP_400, HTTP_404
from db.repositories.documents.documents_metadata import DocumentMetadataRepository
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
        """
        Uploads a file to the specified folder in the document repository.

        Args:
            @param metadata_repo: The repository for accessing metadata.
            @param user_repo: The repository for accessing user information.
            @param file: The file to be uploaded.
            @param folder: The folder in which the file should be uploaded.
            @param user: The token data of the user.

        Returns:
            @return: A dictionary containing the response and upload information.

        Raises:
            HTTP_400: If the file type is not supported.
        """

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
                Filename=r"/app/downloads/docflow_" + f"{name}"
            )
        except ClientError as e:
            raise HTTP_404(
                msg=f"File not found: {e}"
            ) from e

        return {"message": f"successfully downloaded {name} in downloads folder."}

    async def perm_delete(
            self, file: str, bin_list: List[Row | Row],
            delete_all: bool, meta_repo: DocumentMetadataRepository, user: TokenData
    ) -> None:

        if delete_all:
            for files in bin_list:
                s3_url = files.DocumentMetadata.s3_url

                key = await get_key(s3_url=s3_url)
                await self._delete_object(key=key)
                await meta_repo.perm_delete(document=None, owner=user, delete_all=delete_all)
        else:
            for files in bin_list:
                if files.DocumentMetadata.name == file:
                    s3_url = files.DocumentMetadata.s3_url

                    key = await get_key(s3_url=s3_url)
                    await self._delete_object(key=key)
                    await meta_repo.perm_delete(document=files.DocumentMetadata.id, owner=user, delete_all=False)
                    break

    async def preview(self, document: Dict[str, Any]) -> FileResponse:

        key = await get_key(s3_url=document["s3_url"])

        s3_object = self.client.get_object(Bucket=settings.s3_bucket, Key=key)
        file = s3_object['Body'].read()

        # Determining the file extension from the key and media type for File Response
        _, extension = os.path.splitext(key)
        if extension.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            media_type = 'image/' + extension.lower().lstrip('.')
        elif extension.lower() == '.pdf':
            media_type = 'application/pdf'
        else:
            raise ValueError("Unsupported file type.")

        # Creating a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp:
            temp.write(file)
            temp_path = temp.name

        return FileResponse(temp_path, media_type=media_type)
