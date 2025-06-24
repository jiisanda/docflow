import os
import logging
import logging.config
from pathlib import Path

LOGGER_NAME: str = "docflow"
LOG_FORMAT: str = (
    "%(asctime)s [%(levelname)s] | %(name)s | %(filename)s | %(funcName)s | %(lineno)d | %(message)s"
)
LOG_LEVEL: int = logging.DEBUG


def get_log_file_path():
    """
    Get a writable log file path, trying multiple locations.
    Returns None if no writable location is found.
    """
    possible_locations = [
        "/usr/src/app/logs/docflow.log",
        "/app/logs/docflow.log",
        "/tmp/docflow.log",
        "docflow.log",
    ]

    for log_path in possible_locations:
        try:
            log_file = Path(log_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)

            test_write = log_file.parent / f"test_write_{os.getpid()}.tmp"
            test_write.touch()
            test_write.unlink()

            return str(log_file)
        except (OSError, PermissionError):
            continue

    return None


LOG_FILE = get_log_file_path()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "console": {
            "format": "%(asctime)s [%(levelname)s] | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "console",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "error_console": {
            "level": "ERROR",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO", "propagate": False},
        LOGGER_NAME: {
            "handlers": ["console", "error_console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "sqlalchemy": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "s3": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "uvicorn.error": {"level": "INFO", "handlers": ["console"], "propagate": False},
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.asgi": {"level": "INFO", "handlers": ["console"], "propagate": False},
    },
}

if LOG_FILE:
    LOGGING["handlers"]["file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "standard",
        "level": "DEBUG",
        "filename": LOG_FILE,
        "mode": "a",
        "encoding": "utf-8",
        "maxBytes": 500000,
        "backupCount": 4,
    }

    LOGGING["loggers"][LOGGER_NAME]["handlers"].append("file")
    LOGGING["loggers"]["sqlalchemy"]["handlers"].append("file")
    LOGGING["loggers"]["s3"]["handlers"].append("file")

try:
    logging.config.dictConfig(LOGGING)
except Exception as e:
    logging.basicConfig(
        level=LOG_LEVEL, format=LOG_FORMAT, handlers=[logging.StreamHandler()]
    )
    print(f"Warning: Failed to configure logging: {e}")

docflow_logger = logging.getLogger(LOGGER_NAME)
s3_logger = logging.getLogger("s3")
sqlalchemy_logger = logging.getLogger("sqlalchemy")

if LOG_FILE:
    docflow_logger.info(f"File logging enabled: {LOG_FILE}")
else:
    docflow_logger.warning("File logging disabled - no writable location found")
