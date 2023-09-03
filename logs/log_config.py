from os.path import abspath, dirname, join
from pydantic_settings import BaseSettings


class LogConfig(BaseSettings):
    """Logging configs to be set"""

    LOGGER_NAME: str = "docflow"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    BASE_DIR = abspath(dirname(__file__))
    
    LOG_FILE: str = join(BASE_DIR + "\logs", "docflow.log")

    # logging config
    version = 1
    disable_existing_logger = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "level": "DEBUG",
            "filename": LOG_FILE,
            "mode": 'a',
            "encoding": "utf-8",
            "maxBytes": 500000,
            "backupCount": 4
        }
    }
    loggers = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }
