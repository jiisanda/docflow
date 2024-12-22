import enum


class StatusEnum(enum.Enum):
    """
    Enum for status of document
    """

    public = "public"
    private = "private"
    shared = "shared"
    deleted = "deleted"
    archived = "archived"


class NotifyEnum(enum.Enum):
    """
    Enum for status of notification
    """

    read = "read"
    unread = "unread"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
