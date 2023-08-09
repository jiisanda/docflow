from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import Optional, List

class DocumentBase(BaseModel):
    _id: UUID
    name: str
    s3_url: str
    created_at: datetime
    size: Optional[int]
    file_type: Optional[str]
    tags: Optional[List[str]]
    categories: Optional[List[str]]
