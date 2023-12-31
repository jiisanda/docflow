import os.path

import boto3
import hashlib
import tempfile
from datetime import datetime, timedelta, timezone
from random import randint
from typing import Any, Dict, List, Union

from botocore.exceptions import NoCredentialsError
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.mail_service import mail_service
from app.api.dependencies.repositories import get_key
from app.core.config import settings
from app.core.exceptions import HTTP_404, HTTP_500
from app.db.tables.auth.auth import User
from app.db.tables.documents.document_sharing import DocumentSharing
from app.db.repositories.auth.auth import AuthRepository
from app.db.repositories.documents.notify import NotifyRepo
from app.schemas.auth.bands import TokenData
from app.schemas.documents.document_sharing import SharingRequest


class DocumentSharingRepository:

    def __init__(self, session: AsyncSession) -> None:
        self.client = boto3.client('s3')

        self.session = session

    async def get_user_mail(self, user: TokenData):

        stmt = (
            select(User)
            .where(User.id == user.id)
        )

        execute = await self.session.execute(stmt)

        return execute.scalar_one_or_none().__dict__["email"]

    @staticmethod
    async def _generate_id(url: str) -> str:
        hash_object = hashlib.md5()
        hash_object.update(url.encode('utf-8'))

        n = randint(0, 25)

        return hash_object.hexdigest()[n:n+6]

    async def _get_saved_links(self, filename: str) -> Dict[str, Any]:

        stmt = (
            select(DocumentSharing)
            .where(DocumentSharing.filename == filename)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_visits(self, filename: str, visits_left: int):
        if visits_left > 1:
            await self.session.execute(
                update(DocumentSharing)
                .where(DocumentSharing.filename == filename)
                .values(visits=visits_left-1)
            )
        elif visits_left == 1:
            await self.session.execute(
                delete(DocumentSharing)
                .where(DocumentSharing.filename == filename)
            )

    async def cleanup_expired_links(self):

        now = datetime.now(timezone.utc)

        stmt = (
            delete(DocumentSharing)
            .where(DocumentSharing.expires_at <= now)
        )
        try:
            await self.session.execute(stmt)
        except Exception as e:
            raise HTTP_500() from e

    async def get_presigned_url(self, doc: Dict[str, Any]) -> Union[str, Dict[str, str]]:
        try:
            params = {
                'Bucket': settings.s3_bucket,
                'Key': await get_key(s3_url=doc["s3_url"])
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

    async def get_shareable_link(self, owner_id: str, url: str, visits: int, filename: str, share_to: List[str]):

        # task to clean uo the database for expired links
        await self.cleanup_expired_links()

        if ans := await self._get_saved_links(filename=filename):
            ans = ans.__dict__
            return {
                "note": f"Links already shared... valid Till {ans['expires_at']}",
                "response": {
                    "shareable_link": f"{settings.host_url}{settings.api_prefix}/doc/{ans['url_id']}",
                    "visits_left": ans["visits"]
                }
            }

        url_id = await self._generate_id(url=url)
        share_entry = DocumentSharing(
            url_id=url_id,
            owner_id=owner_id,
            filename=filename,
            url=url,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=3599),
            visits=visits,
            share_to=share_to
        )
        try:
            self.session.add(share_entry)
            await self.session.commit()
            await self.session.refresh(share_entry)

            response = share_entry.__dict__
            return {
                "shareable_link": f"{settings.host_url}{settings.api_prefix}/doc/{response['url_id']}",
                "visits": response["visits"]
            }
        except Exception as e:
            raise HTTP_500() from e

    async def get_redirect_url(self, url_id: str):

        stmt = (
            select(DocumentSharing)
            .where(DocumentSharing.url_id == url_id)
        )

        result = await self.session.execute(stmt)
        try:
            result = result.scalar_one_or_none().__dict__

            await self.update_visits(filename=result["filename"], visits_left=result["visits"])

            return result["url"]
        except AttributeError as e:
            raise HTTP_404(
                msg="Shared URL link either expired or reached the limit of visits..."
            ) from e

    async def send_mail(self, user: TokenData, mail_to: Union[List[str], None], link: str) -> None:

        if mail_to:

            user_mail = await self.get_user_mail(user)
            subj = f"DocFlow: {user.username} share a document"
            content = f"""
                    Visit the link: {link}, to access the document shared by {user.username} | {user_mail}.
                    """

            for mails in mail_to:
                mail_service(mail_to=mails, subject=subj, content=content, file_path=None)

    async def confirm_access(self, user: TokenData, url_id: str | None) -> bool:
        # check if login user is owner or to whom it is shared
        stmt = (
            select(DocumentSharing)
            .where(DocumentSharing.url_id == url_id)
        )

        result = await self.session.execute(stmt)
        try:
            result = result.scalar_one_or_none().__dict__
            user_mail = await self.get_user_mail(user)

            return (
                result.get("owner_id") == user.id
                or user_mail in result.get("share_to")
                or user.username in result.get("share_to")
            )
        except Exception as e:
            raise HTTP_404(
                msg="The link has expired..."
            ) from e

    async def share_document(
            self, filename: str,
            document_key: str,
            file: Any,
            share_request: SharingRequest,
            notify: bool,
            owner: TokenData,
            notify_repo: NotifyRepo,
            auth_repo: AuthRepository,
    ) -> None:

        user_mail = await self.get_user_mail(owner)
        share_to = share_request.share_to

        # Determining extension
        _, extension = os.path.splitext(document_key)

        # Creating temp file to share
        with tempfile.NamedTemporaryFile(delete=True, suffix=extension) as temp:
            temp.write(file)
            temp_path = temp.name

            subject = f"{owner.username} shared a file with you using DocFlow"
            for mails in share_to:
                content = f"""
                Hello {mails}! 
                
                Hope you are well? {owner.username} | {user_mail} shared a file with you as an attachment. 
                
                Regards,
                DocFlow
                """
                mail_service(mail_to=mails, subject=subject, content=content, file_path=temp_path)

        if notify:
            return await notify_repo.notify(user=owner, receivers=share_to, filename=filename, auth_repo=auth_repo)
