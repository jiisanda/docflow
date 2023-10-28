from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import Optional, List

from db.tables.base_class import StatusEnum
from db.tables.base_class import NotifyEnum


# Document Metadata
class DocumentMetadataBase(BaseModel):
    _id: UUID
    owner_id: str
    name: str
    s3_url: str
    created_at: datetime
    size: Optional[int]
    file_type: Optional[str]
    tags: Optional[List[str]]
    categories: Optional[List[str]]
    status: StatusEnum
    file_hash: Optional[str]
    access_to: Optional[List[str]]


class DocumentMetadataPatch(BaseModel):
    name: str = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    access_to: Optional[List[str]] = None


# Document Sharing
class DocumentSharingBase(BaseModel):
    url_id: str
    owner_id: str
    filename: str
    url: str
    expires_at: datetime
    visits: int
    share_to: Optional[List[str]] = None


class DocUserAccess(BaseModel):
    id: str
    doc_id: UUID
    user_id: str

    class Config:
        from_attribute = True


class DocUserAccessCreate(BaseModel):
    doc_id: str
    user_id: str


# Notifications
class Notification(BaseModel):
    id: UUID
    receiver_id: str
    message: str
    status: NotifyEnum
    notified_at: datetime


class NotifyPatchStatus(BaseModel):
    status: NotifyEnum = NotifyEnum.unread
