from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Union
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, update, insert, delete
from sqlalchemy.engine import Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.exceptions import http_409, http_404
from app.db.repositories.auth.auth import AuthRepository
from app.db.tables.documents.documents_metadata import DocumentMetadata, doc_user_access
from app.db.tables.base_class import StatusEnum
from app.schemas.auth.bands import TokenData
from app.schemas.documents.bands import DocumentMetadataPatch
from app.schemas.documents.documents_metadata import (
    DocumentMetadataCreate,
    DocumentMetadataRead,
)


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

    async def _execute_update(
        self, db_document: DocumentMetadata | Dict[str, Any], changes: dict
    ) -> None:

        if isinstance(db_document, dict):
            stmt = (
                update(DocumentMetadata)
                .where(DocumentMetadata.id == db_document.get("id"))
                .values(changes)
            )
            doc_name = db_document.get("name")
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
            raise http_409(msg=f"Error while updating document: {doc_name}") from e

    async def _update_access_and_permission(self, db_document, changes, user_repo):

        access_given_to = changes.get("access_to", [])
        # if access_to has email ids, update doc_user_access table with doc_id and user_id
        for user_email in access_given_to:
            try:
                user_id = (
                    await user_repo.get_user(field="email", detail=user_email)
                ).__dict__["id"]
                # update doc_user_access table with doc_id and user_id
                await self._update_doc_user_access(db_document, user_id)

            except IntegrityError as e:
                raise http_409(msg=f"User '{user_email}' already has access...") from e
            except AttributeError as e:
                raise http_404(
                    msg=f"The user with '{user_email}' does not exists, make sure user has account in DocFlow."
                ) from e

    async def _update_doc_user_access(self, db_document, user_id):

        stmt = insert(doc_user_access).values(
            doc_id=db_document.__dict__["id"], user_id=user_id
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def _delete_access(self, document) -> None:
        await self.session.execute(
            doc_user_access.delete().where(doc_user_access.c.doc_id == document.id)
        )

    async def _auto_delete(self, bin_items: List) -> bool:

        now = datetime.now(timezone.utc)
        deleted_any = False
        for doc in bin_items:
            if doc.deleted_at is not None and doc.deleted_at <= now:
                stmt = delete(DocumentMetadata).where(DocumentMetadata.id == doc.id)
                await self.session.execute(stmt)
                deleted_any = True
        if deleted_any:
            await self.session.commit()
        return deleted_any

    async def get_doc(self, filename: str) -> Dict[str, Any]:
        """
        Get document by filename irrespective of logged-in user.

        Args:
            self: The instance of the class.
            filename (str): The name of the document.

        Returns:
            Dict[str, Any]: The document metadata.
        """

        stmt = (
            select(DocumentMetadata)
            .where(DocumentMetadata.name == filename)
            .where(self.doc_cls.status != StatusEnum.deleted)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def upload(
        self, document_upload: DocumentMetadataCreate
    ) -> DocumentMetadataRead:

        if not isinstance(document_upload, dict):
            db_document = DocumentMetadata(**document_upload.model_dump())
        else:
            db_document = DocumentMetadata(**document_upload)

        try:
            self.session.add(db_document)
            await self.session.commit()
            await self.session.refresh(db_document)
        except IntegrityError as e:
            raise http_404(
                msg=f"Document with name: {document_upload.name} already exists.",
            ) from e

        return DocumentMetadataRead(**db_document.__dict__)

    async def doc_list(
        self, owner: TokenData, limit: int = 10, offset: int = 0
    ) -> Dict[str, Union[List[DocumentMetadataRead], Any]]:

        stmt = (
            select(self.doc_cls)
            .join(DocumentMetadata, DocumentMetadata.id == self.doc_cls.id)
            .where(DocumentMetadata.owner_id == owner.id)
            .where(DocumentMetadata.status != StatusEnum.deleted)
            .offset(offset)
            .limit(limit)
        )

        try:
            result = await self.session.execute(stmt)
            result_list = result.fetchall()

            for row in result_list:
                row.doc_cls.__dict__.pop("_sa_instance_state", None)

            result = [
                DocumentMetadataRead(**row.doc_cls.__dict__) for row in result_list
            ]
            return {"response": result, "no_of_docs": len(result)}
        except Exception as e:
            raise http_404(msg="No Documents found") from e

    async def get(
        self, document: Union[str, UUID], owner: TokenData
    ) -> Union[DocumentMetadataRead, HTTPException]:

        db_document = await self._get_instance(document=document, owner=owner)
        if db_document is None:
            return http_409(msg=f"No Document with {document}")

        return DocumentMetadataRead(**db_document.__dict__)

    async def patch(
        self,
        document: Union[str, UUID],
        document_patch: DocumentMetadataPatch,
        owner: TokenData,
        user_repo: AuthRepository,
        is_owner: bool,
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

        try:
            db_document = await self._get_instance(document=document, owner=owner)

            setattr(db_document, "status", StatusEnum.deleted)
            setattr(db_document, "tags", None)
            setattr(db_document, "access_to", None)
            setattr(db_document, "file_type", None)
            setattr(db_document, "categories", None)
            setattr(
                db_document,
                "deleted_at",
                datetime.now(timezone.utc) + timedelta(days=30),
            )

            # delete entry from doc_user_access table
            await self._delete_access(document=db_document)

            self.session.add(db_document)

            await self.session.commit()
        except Exception as e:
            raise http_404(msg=f"No file with {document}") from e

    async def bin_list(self, owner: TokenData) -> Dict[str, List[Row | Row] | int]:

        stmt = (
            select(DocumentMetadata)
            .where(DocumentMetadata.owner_id == owner.id)
            .where(DocumentMetadata.status == StatusEnum.deleted)
        )

        result = (await self.session.execute(stmt)).scalars().all()
        if await self._auto_delete(result):
            result = (await self.session.execute(stmt)).scalars().all()

        serialized = []
        for doc in result:
            d = {k: v for k, v in doc.__dict__.items() if k != "_sa_instance_state"}
            serialized.append(DocumentMetadataRead(**d))

        return {"response": serialized, "no_of_docs": len(serialized)}

    async def restore(self, file: str, owner: TokenData) -> DocumentMetadataRead:

        stmt = (
            select(DocumentMetadata)
            .where(DocumentMetadata.owner_id == owner.id)
            .where(DocumentMetadata.name == file)
            .where(DocumentMetadata.status == StatusEnum.deleted)
        )
        db_doc = (await self.session.execute(stmt)).scalar_one_or_none()
        if db_doc is None:
            raise http_404(msg=f"'{file}' not found in trash")

        await self._execute_update(db_document=db_doc, changes={"status": StatusEnum.private, "deleted_at": None})
        await self.session.commit()
        d = {k: v for k, v in db_doc.__dict__.items() if k != "_sa_instance_state"}
        return DocumentMetadataRead(**d)

    async def perm_delete_a_doc(self, document: UUID | None, owner: TokenData) -> None:

        stmt = (
            delete(DocumentMetadata)
            .where(DocumentMetadata.owner_id == owner.id)
            .where(DocumentMetadata.id == document)
            .where(DocumentMetadata.status == StatusEnum.deleted)
        )

        await self.session.execute(stmt)

    async def empty_bin(self, owner: TokenData):

        stmt = (
            delete(DocumentMetadata)
            .where(DocumentMetadata.owner_id == owner.id)
            .where(DocumentMetadata.status == StatusEnum.deleted)
        )

        await self.session.execute(stmt)

    async def archive(self, file: str, user: TokenData):

        doc = await self._get_instance(document=file, owner=user)

        if doc and doc.status == StatusEnum.archived:
            raise http_409(msg="Doc is already archived")

        if doc is None:
            raise http_404(msg="Doc does not exist")

        await self._execute_update(db_document=doc, changes={"status": StatusEnum.archived})
        await self.session.commit()
        d = {k: v for k, v in doc.__dict__.items() if k != "_sa_instance_state"}
        return DocumentMetadataRead(**d)

    async def archive_list(self, user: TokenData) -> Dict[str, List[str] | int]:

        stmt = (
            select(DocumentMetadata)
            .where(DocumentMetadata.owner_id == user.id)
            .where(DocumentMetadata.status == StatusEnum.archived)
        )

        result = (await self.session.execute(stmt)).scalars().all()
        serialized = [
            DocumentMetadataRead(**{k: v for k, v in doc.__dict__.items() if k != "_sa_instance_state"})
            for doc in result
        ]
        return {"response": serialized, "no_of_docs": len(serialized)}

    async def un_archive(self, file: str, user: TokenData) -> DocumentMetadataRead:

        doc = await self._get_instance(document=file, owner=user)

        if doc and doc.status == StatusEnum.archived:
            change = {"status": "private"}
            await self._execute_update(db_document=doc, changes=change)
            return DocumentMetadataRead(**doc.__dict__)
        if doc and doc.status != StatusEnum.archived:
            raise http_409(msg="Doc is not archived")
        raise http_404(msg="Doc does not exits")
