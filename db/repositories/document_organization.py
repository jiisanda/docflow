from typing import Any, Dict, List, Union

from api.dependencies.constants import SUPPORTED_FILE_TYPES

class DocumentOrgRepository:

    def __init__(self):
        ...


    async def search_tags(self, docs: List[Dict[str, Any]], tags: List[str]) -> List[Dict[str, str]]:

        result = []
        for doc in docs:
            doc = doc.__dict__
            result.extend(
                doc
                for tag in tags
                if doc["tags"] is not None and ''.join(tag.split()) in doc["tags"]
            )

        return result or None


    async def search_category(self, docs: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, str]]:

        result = []
        for doc in docs:
            doc = doc.__dict__
            result.extend(
                doc
                for category in categories
                if doc["categories"] is not None and ''.join(category.split()) in doc["categories"]
            )

        return result or None


    async def search_file_type(self, docs: List[Dict[str, str]], file_type: List[str]) -> List[Dict[str, str]]:

        result = []
        for doc in docs:
            doc = doc.__dict__
            for ftype in file_type:
                ftype = ''.join(ftype.split())
                result.extend(
                    doc
                    for key, val in SUPPORTED_FILE_TYPES.items()
                    if val == ftype and key == doc["file_type"]
                )

        return result or None


    async def search_by_status(self, docs: List[Dict[str, str]], status: str) -> List[Dict[str, str]]:

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
        docs: List[Dict[str, Any]], 
        tags: str, 
        categories:str, 
        file_type: str, 
        status: str
    ) -> Union[List[Dict[str, Any]], None]:

        results = []

        if tags is not None:
            tags = tags.split(',')
            results.append(await self.search_tags(docs=docs, tags=tags))

        if categories is not None:
            categories = categories.split(',')
            results.append(await self.search_category(docs=docs, categories=categories))

        if file_type is not None:
            file_type = file_type.split(',')
            results.append(await self.search_file_type(docs=docs, file_type=file_type))

        if status is not None:
            status = status.split(',')
            results.append(await self.search_by_status(docs=docs, status=status))

        return results
