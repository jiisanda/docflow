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
                if doc["tags"] and ''.join(tag.split()) in doc["tags"]
            )

        return result or None


    async def search_category(self, docs: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, str]]:

        result = []
        for doc in docs:
            doc = doc.__dict__
            result.extend(
                doc
                for category in categories
                if doc["categories"] and ''.join(category.split()) in doc["categories"]
            )

        return result or None


    async def search_file_type(self, docs: List[Dict[str, str]], file_types: List[str]) -> List[Dict[str, str]]:

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
        file_types: str, 
        status: str
    ) -> Union[List[Dict[str, Any]], None]:

        results = []

        if tags:
            tags = tags.split(',')
            results.append(await self.search_tags(docs=docs, tags=tags))

        if categories:
            categories = categories.split(',')
            results.append(await self.search_category(docs=docs, categories=categories))

        if file_types:
            file_type = file_type.split(',')
            results.append(await self.search_file_type(docs=docs, file_types=file_types))

        if status:
            status = status.split(',')
            results.append(await self.search_by_status(docs=docs, status=status))

        return results
