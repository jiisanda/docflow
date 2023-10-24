import enum


class StatusEnum(enum.Enum):
    public = "public"
    private = "private"
    shared = "shared"
    deleted = "deleted"
    archived = "archived"


class NotifyEnum(enum.Enum):
    read = "read"
    unread = "unread"
