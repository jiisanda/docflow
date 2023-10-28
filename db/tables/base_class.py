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

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
