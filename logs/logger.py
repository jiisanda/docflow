from os.path import join, abspath, dirname
import logging
import logging.config


LOGGER_NAME: str = "docflow"
LOG_FORMAT: str = "%(asctime)s [%(levelname)s] | %(name)s | %(filename)s | %(funcName)s | %(lineno)d | %(message)s"
LOG_LEVEL: int = logging.DEBUG

BASE_DIR = abspath(dirname(__file__))

LOG_FILE: str = join(BASE_DIR, "docflow.log")

LOGGING = {
    "version": 1,
    "disable_existing_logger": False,
    "formatters":  {
        "standard": {
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "level": "DEBUG",
            "filename": LOG_FILE,
            "mode": 'a',
            "encoding": "utf-8",
            "maxBytes": 500000,
            "backupCount": 4
        }
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True
        },
        LOGGER_NAME: {
            "handlers": ["default", "file"],
            "level": LOG_LEVEL,
            "propagate": False
        },
        "sqlalchemy": {
            "handlers": ["file"],
            "level": "WARNING"
        },
        "s3": {
            "handlers": ["file"],
            "level": "WARNING"
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": True
        },
        "uvicorn.asgi": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": True
        },
    },
}

logging.config.dictConfig(LOGGING)

# loggers
docflow_logger = logging.getLogger("docflow")
s3_logger = logging.getLogger("s3")
sqlalchemy_logger = logging.getLogger("sqlalchemy")

