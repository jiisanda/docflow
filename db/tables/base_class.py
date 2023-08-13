import enum

from sqlalchemy import Enum

class StatusEnum(enum.Enum):
    public = "public"
    private = "private"
    shared = "shared"
    deleted = "deleted"