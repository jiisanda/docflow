from typing import Any, Dict, List, Union
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, join, update, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from core.exceptions import HTTP_409, HTTP_404
from db.repositories.auth.auth import AuthRepository
from db.tables.documents.documents_metadata import DocumentMetadata, doc_user_access
from db.tables.base_class import StatusEnum
from schemas.auth.bands import TokenData
from schemas.documents.bands import DocumentMetadataPatch
from schemas.documents.documents_metadata import DocumentMetadataCreate, DocumentMetadataRead


class DocumentMetadataRepository:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.doc_cls = aliased(DocumentMetadata, name="doc_cls")

    async def _get_instance(self, document: Union[str, UUID], owner: TokenData):

        try:
            UUID(str(document))
            stmt = (
                select(self.doc_cls)
                .where(self.doc_cls.owner_id == owner.id)
                .where(self.doc_cls.id == document)
                .where(self.doc_cls.status != StatusEnum.deleted)
            )
        except ValueError:
            stmt = (
                select(self.doc_cls)
                .where(self.doc_cls.owner_id == owner.id)
                .where(self.doc_cls.name == document)
                .where(self.doc_cls.status != StatusEnum.deleted)
            )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def _extract_changes(document_patch: DocumentMetadataPatch) -> dict:

        if isinstance(document_patch, dict):
            return document_patch
        return document_patch.model_dump(exclude_unset=True)

    async def _execute_update(self, db_document: DocumentMetadata | Dict[str, Any], changes: dict) -> None:

        if isinstance(db_document, dict):
            stmt = (
                update(DocumentMetadata)
                .where(DocumentMetadata.id == db_document.get('id'))
                .values(changes)
            )
            doc_name = db_document.get('name')
        else:
            stmt = (
                update(DocumentMetadata)
                .where(DocumentMetadata.id == db_document.id)
                .values(changes)
            )
            doc_name = db_document.name

        try:
            await self.session.execute(stmt)
        except Exception as e:
            raise HTTP_409(
                msg=f"Error while updating document: {doc_name}"
            ) from e

    async def _update_access_and_permission(self, db_document, changes, user_repo):
        access_given_to = changes.get("access_to", [])
        # if access_to has email ids, update doc_user_access table with doc_id and user_id
        for user_email in access_given_to:
            try:
                user_id = (await user_repo.get_user(field="email", detail=user_email)).__dict__["id"]
                # update doc_user_access table with doc_id and user_id
                await self._update_doc_user_access(db_document, user_id)

            except IntegrityError as e:
                raise HTTP_409(
                    msg=f"User '{user_email}' already has access..."
                ) from e
            except AttributeError as e:
                raise HTTP_404(
                    msg=f"The user with '{user_email}' does not exists, make sure user has account in DocFlow."
                ) from e

    async def _update_doc_user_access(self, db_document, user_id):
        stmt = insert(doc_user_access).values(doc_id=db_document.__dict__["id"], user_id=user_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_doc(self, filename: str) -> Dict[str, Any]:
        """
        Get document by filename irrespective of logged-in user
        @param filename:
        @return: Dict[str, Any]
        """

        stmt = (
            select(DocumentMetadata)
            .where(DocumentMetadata.name == filename)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def upload(self, document_upload: DocumentMetadataCreate) -> DocumentMetadataRead:

        if not isinstance(document_upload, dict):
            db_document = DocumentMetadata(**document_upload.model_dump())
        else:
            db_document = DocumentMetadata(**document_upload)

        try:
            self.session.add(db_document)
            await self.session.commit()
            await self.session.refresh(db_document)
        except IntegrityError as e:
            raise HTTP_404(
                msg=f"Document with name: {document_upload.name} already exists.",
            ) from e

        return DocumentMetadataRead(**db_document.__dict__)

    async def doc_list(
            self, owner: TokenData, limit: int = 10, offset: int = 0
    ) -> Dict[str, Union[List[DocumentMetadataRead], Any]]:

        stmt = (
            select(self.doc_cls)
            .select_from(
                join(DocumentMetadata, self.doc_cls, DocumentMetadata.id == self.doc_cls.id)  # Adjusting the
                # join condition
            )
            .where(DocumentMetadata.owner_id == owner.id)
            .where(DocumentMetadata.status != StatusEnum.deleted)
            .offset(offset)
            .limit(limit)
        )

        try:
            result = await self.session.execute(statement=stmt)
            result_list = result.fetchall()

            for each in result_list:
                each.doc_cls.__dict__.pop('_sa_instance_state', None)
            result = [DocumentMetadataRead(**row.doc_cls.__dict__) for row in result_list]
            return {
                f"documents of {owner.username}": result,
                "no_of_docs": len(result)
            }
        except Exception as e:
            raise HTTP_404(
                msg="No Documents found"
            ) from e

    async def get(self, document: Union[str, UUID], owner: TokenData) -> Union[DocumentMetadataRead, HTTPException]:

        db_document = await self._get_instance(document=document, owner=owner)
        if db_document is None:
            return HTTP_409(
                msg=f"No Document with {document}"
            )

        return DocumentMetadataRead(**db_document.__dict__)

    async def patch(
            self,
            document: Union[str, UUID], document_patch: DocumentMetadataPatch, owner: TokenData,
            user_repo: AuthRepository, is_owner: bool
    ) -> Union[DocumentMetadataRead, HTTPException]:

        if is_owner:
            db_document = await self._get_instance(document=document, owner=owner)
            changes = await self._extract_changes(document_patch)

            await self._update_access_and_permission(db_document, changes, user_repo)

            await self._execute_update(db_document, changes)

        else:
            # This condition will be activated when, the new version of file is added by a privileged member
            # here privileged member is one who have access to update the document.
            db_document = await self.get_doc(filename=document)
            changes = await self._extract_changes(document_patch)

            if changes:
                await self._execute_update(db_document, changes)

        return DocumentMetadataRead(**db_document.__dict__)

    async def delete(self, document: Union[str, UUID], owner: TokenData) -> None:

        db_document = await self._get_instance(document=document, owner=owner)

        setattr(db_document, "status", StatusEnum.deleted)
        self.session.add(db_document)

        await self.session.commit()
