import logging

from logging.config import dictConfig

from core.log_config import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("docflow")
