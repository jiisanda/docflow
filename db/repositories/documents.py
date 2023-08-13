from uuid import UUID
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from db.errors import EntityDoesNotExist
from db.tables.documents import Document
from db.tables.base_class import StatusEnum
from schemas.documents import DocumentCreate, DocumentPatch, Document


class DocumentRepository:
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


    async def upload(self, document_upload: DocumentCreate) -> Document:
        db_document = Document(**document_upload.dict())

        self.session.add(db_document)
        await self.session.commit()
        await self.session.refresh(db_document)

        return Document(**db_document.dict())


    async def doc_list(self, limit: int = 10, offset: int = 0) -> List[Document]:

        stmt = (
            (select(self.doc_cls).where(Document.status != StatusEnum.deleted))
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement=stmt)

        return [Document(**document.dict()) for document in result]


    async def get(self, document_id: UUID) -> Optional[Document]:

        db_document = await self._get_instance(document_id=document_id)

        if db_document is None:
            return EntityDoesNotExist
        return Document(**db_document.dict())


    async def patch(
        self, document_id: UUID, document_patch: DocumentPatch
    ) -> Optional[Document]:

        db_document = await self._get_instance(document_id=document_id)

        if db_document is None:
            raise EntityDoesNotExist

        document_details = document_patch.dict(exclude_unset=True, exclude={"id"})
        for key, value in document_details.items():
            setattr(db_document, key, value)

        self.session.add(db_document)
        await self.session.commit()
        await self.session.refresh(db_document)

        return Document(**db_document.dict())

    async def delete(self, document_id: UUID) -> None:

        db_document = await self._get_instance(document_id=document_id)

        if db_document is None:
            raise EntityDoesNotExist

        setattr(db_document, "status", StatusEnum.deleted)
        self.session.add(db_document)

        await self.session.commit()