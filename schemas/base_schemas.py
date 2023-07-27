from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class DocumentBase(BaseModel):
    _id: UUID
    name: Optional[str]
    data: Optional[str]
    created_at: datetime
    size: Optional[int]
    file_type: Optional[str]
    tags: Optional[List[str]]
    categories: Optional[List[str]]
