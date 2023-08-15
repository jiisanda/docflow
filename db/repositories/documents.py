from typing import List, Optional

from sqlalchemy import select, join
from sqlalchemy.dialects.postgresql import UUID
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


    async def _get_instance(self, document_id: UUID):

        stmt = (
            select(self.doc_cls)
            .where(doc_cls._id == document_id)
            .where(doc_cls.status != StatusEnum.deleted)
        )

        result = await self.session.execute(stmt)

        return result.first()

    async def model_to_dict(self, model):
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

        db_document = await self._get_instance(document_id=document_id)

        if db_document is None:
            return EntityDoesNotExist
        return DocumentRead(**db_document.dict())


    async def patch(
        self, document_id: UUID, document_patch: DocumentPatch
    ) -> Optional[DocumentRead]:

        db_document = await self._get_instance(document_id=document_id)

        if db_document is None:
            raise EntityDoesNotExist

        document_details = document_patch.dict(exclude_unset=True, exclude={"id"})
        for key, value in document_details.items():
            setattr(db_document, key, value)

        self.session.add(db_document)
        await self.session.commit()
        await self.session.refresh(db_document)

        return DocumentRead(**db_document.dict())

    async def delete(self, document_id: UUID) -> None:

        db_document = await self._get_instance(document_id=document_id)

        if db_document is None:
            raise EntityDoesNotExist

        setattr(db_document, "status", StatusEnum.deleted)
        self.session.add(db_document)

        await self.session.commit()