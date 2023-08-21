from typing import List, Optional, Union
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, join, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, class_mapper
from pydantic import parse_obj_as

from db.errors import EntityDoesNotExist
from db.tables.documents import Document
from db.tables.base_class import StatusEnum
from schemas.documents import DocumentCreate, DocumentPatch, DocumentRead


class DocumentRepository:
    """
    TODO: Add the user field for CRUD
    """
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.doc_cls = aliased(Document, name="doc_cls")


    async def _get_instance(self, document: Union[str, UUID]) -> None:

        if isinstance(document, UUID):
            stmt = (
                select(self.doc_cls)
                .where(self.doc_cls._id == document)
                .where(self.doc_cls.status != StatusEnum.deleted)
            )
        else:
            stmt = (
                select(self.doc_cls)
                .where(self.doc_cls.name == document)
                .where(self.doc_cls.status != StatusEnum.deleted)
            )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()


    async def _extract_changes(self, document_patch: DocumentPatch) -> dict:

        return {field: value for field, value in document_patch if value is not None}


    async def _execute_update(self, db_document: Document, changes: dict) -> None:

        stmt = (
            update(Document)
            .where(Document._id == db_document._id)
            .values(changes)
        )
        await self.session.execute(stmt)


    async def model_to_dict(self, model) -> dict:
        return {column.name: getattr(model, column.name) for column in class_mapper(model.__class__).mapped_table.columns}


    async def upload(self, document_upload: DocumentCreate) -> DocumentRead:
        """
        TODO: Add Try Except and handle error cases
        """

        db_document = Document(**document_upload.dict())

        self.session.add(db_document)
        await self.session.commit()
        await self.session.refresh(db_document)

        db_document_dict = await self.model_to_dict(db_document)

        return parse_obj_as(DocumentRead, db_document_dict)


    async def doc_list(self, limit: int = 10, offset: int = 0) -> List[DocumentRead]:
        """
        TODO: Add try except and handle error cases
        """

        stmt = (
            select(self.doc_cls)
            .select_from(
                join(Document, self.doc_cls, Document._id == self.doc_cls._id)        # Adjusting the join condition
            )
            .where(Document.status != StatusEnum.deleted)
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement=stmt)
        result_list = result.fetchall()

        result_dict = [row.doc_cls.__dict__ for row in result_list]

        for each in result_list:
            each.doc_cls.__dict__.pop('_sa_instance_state', None)

        return [DocumentRead(**row.doc_cls.__dict__) for row in result_list]


    async def get(self, document_id: UUID) -> Optional[DocumentRead]:

        db_document = await self._get_instance(document=document_id)

        if db_document is None:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"No Document with the id {document_id}"
            )

        ans_dict = db_document.doc_cls.__dict__
        del ans_dict['_sa_instance_state']

        return parse_obj_as(DocumentRead, ans_dict)


    async def get_from_name(self, document_name: str) -> Optional[DocumentRead]:

        stmt = (
            select(self.doc_cls)
            .where(self.doc_cls.name == document_name)
            .where(self.doc_cls.status != StatusEnum.deleted)
        )

        response = await self.session.execute(stmt)
        result = response.first()
        result_dict = result.doc_cls.__dict__
        del result_dict['_sa_instance_state']

        return parse_obj_as(DocumentRead, result_dict)


    async def patch(self, document_name: str, document_patch: DocumentPatch) -> DocumentRead:
        """
        TODO: To add user permissions for patching
        """

        db_document = await self._get_instance(document=document_name)

        if db_document is None:
            raise EntityDoesNotExist

        changes = await self._extract_changes(document_patch)
        if changes:
            await self._execute_update(db_document, changes)

        return DocumentRead(**db_document.__dict__)


    async def delete(self, document_id: UUID) -> None:

        db_document = await self._get_instance(document=document_id)

        if db_document is None:
            raise EntityDoesNotExist

        setattr(db_document, "status", StatusEnum.deleted)
        self.session.add(db_document)

        await self.session.commit()
