from typing import Any, Dict, List, Union

from app.api.dependencies.constants import SUPPORTED_FILE_TYPES
from app.schemas.documents.documents_metadata import DocumentMetadataRead


class DocumentOrgRepository:

    def __init__(self):
        ...

    @staticmethod
    async def _search_tags(docs: List[DocumentMetadataRead], tags: List[str]) -> List[Dict[str, str]]:

        result = []
        for doc in docs:
            doc = doc.__dict__
            result.extend(
                doc
                for tag in tags
                if doc["tags"] and ''.join(tag.split()) in doc["tags"]
            )

        return result or None

    @staticmethod
    async def _search_category(docs: List[DocumentMetadataRead], categories: List[str]) -> List[Dict[str, str]]:

        result = []
        for doc in docs:
            doc = doc.__dict__
            result.extend(
                doc
                for category in categories
                if doc["categories"] and ''.join(category.split()) in doc["categories"]
            )

        return result or None

    @staticmethod
    async def _search_file_type(docs: List[DocumentMetadataRead], file_types: List[str]) -> List[Dict[str, str]]:

        result = []
        for doc in docs:
            doc = doc.__dict__
            for ftype in file_types:
                ftype = ''.join(ftype.split())
                result.extend(
                    doc
                    for key, val in SUPPORTED_FILE_TYPES.items()
                    if val == ftype and key == doc["file_type"]
                )

        return result or None

    @staticmethod
    async def _search_by_status(docs: List[DocumentMetadataRead], status: List[str]) -> List[Dict[str, str]]:

        result = []
        for doc in docs:
            doc = doc.__dict__
            result.extend(
                doc
                for stat in status
                if str(doc["status"]) == f"StatusEnum.{stat}"
            )

        return result or None

    async def search_doc(
        self, 
        docs: List[DocumentMetadataRead],
        tags: str, 
        categories: str,
        file_types: str, 
        status: str
    ) -> Union[List[List[Dict[str, Any]]], None]:

        results = []

        if tags:
            tags = tags.split(',')
            results.append(await self._search_tags(docs=docs, tags=tags))

        if categories:
            categories = categories.split(',')
            results.append(await self._search_category(docs=docs, categories=categories))

        if file_types:
            file_type = file_types.split(',')
            results.append(await self._search_file_type(docs=docs, file_types=file_type))

        if status:
            _status = status.split(',')
            results.append(await self._search_by_status(docs=docs, status=_status))

        return results
