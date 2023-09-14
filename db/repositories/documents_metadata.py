from typing import List, Optional, Union
from uuid import UUID

from fastapi import status, HTTPException
from sqlalchemy import select, join, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from core.exceptions import HTTP_409, HTTP_404
from db.tables.documents_metadata import DocumentMetadata
from db.tables.base_class import StatusEnum
from schemas.documents_metadata import DocumentMetadataCreate, DocumentMetadataPatch, DocumentMetadataRead


class DocumentMetadataRepository:
    """
    TODO: Add the user field for CRUD
    """
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.doc_cls = aliased(DocumentMetadata, name="doc_cls")


    async def _get_instance(self, document: Union[str, UUID]) -> None:

        try:
            UUID(str(document))
            stmt = (
                select(self.doc_cls)
                .where(self.doc_cls._id == document)
                .where(self.doc_cls.status != StatusEnum.deleted)
            )
        except ValueError:
            stmt = (
                select(self.doc_cls)
                .where(self.doc_cls.name == document)
                .where(self.doc_cls.status != StatusEnum.deleted)
            )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()


    async def _extract_changes(self, document_patch: DocumentMetadataPatch) -> dict:

        if isinstance(document_patch, dict):
            return document_patch
        return document_patch.dict(exclude_unset=True)


    async def _execute_update(self, db_document: DocumentMetadata, changes: dict) -> None:

        stmt = (
            update(DocumentMetadata)
            .where(DocumentMetadata._id == db_document._id)
            .values(changes)
        )

        try:
            await self.session.execute(stmt)
        except Exception as e:
            raise HTTP_409(
                msg=f"Error while updating document: {db_document.name}"
            ) from e


    async def upload(self, document_upload: DocumentMetadataCreate) -> DocumentMetadataRead:
        """
        TODO: To data validation
        """
        if not isinstance(document_upload, dict):
            db_document = DocumentMetadata(**document_upload.dict())
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

        db_document_dict = db_document.__dict__

        return DocumentMetadataRead(**db_document.__dict__)


    async def doc_list(self, limit: int = 10, offset: int = 0) -> List[DocumentMetadataRead]:

        stmt = (
            select(self.doc_cls)
            .select_from(
                join(DocumentMetadata, self.doc_cls, DocumentMetadata._id == self.doc_cls._id)        # Adjusting the join condition
            )
            .where(DocumentMetadata.status != StatusEnum.deleted)
            .offset(offset)
            .limit(limit)
        )

        try:
            result = await self.session.execute(statement=stmt)
            result_list = result.fetchall()
            result_dict = [row.doc_cls.__dict__ for row in result_list]

            for each in result_list:
                each.doc_cls.__dict__.pop('_sa_instance_state', None)

            return [DocumentMetadataRead(**row.doc_cls.__dict__) for row in result_list]
        except Exception as e:
            raise HTTP_404(
                detail="No Documents found"
            ) from e


    async def get(self, document: Union[str, UUID]) -> Union[DocumentMetadataRead, HTTPException]:

        db_document = await self._get_instance(document=document)

        if db_document is None:
            return HTTP_409(
                msg=f"No Document with {document}"
            )

        return DocumentMetadataRead(**db_document.__dict__)


    async def patch(self, document: Union[str, UUID], document_patch: DocumentMetadataPatch) -> Union[DocumentMetadataRead, HTTPException]:
        """
        TODO: To add user permissions for patching
        """

        db_document = await self._get_instance(document=document)

        changes = await self._extract_changes(document_patch)
        if changes:
            await self._execute_update(db_document, changes)

        return DocumentMetadataRead(**db_document.__dict__)


    async def delete(self, document: Union[str, UUID]) -> None:

        db_document = await self._get_instance(document=document)

        setattr(db_document, "status", StatusEnum.deleted)
        self.session.add(db_document)

        await self.session.commit()
