import logging
from logging.config import dictConfig


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default",
        }
    },
    "loggers": {
        "app": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
        "app.db": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
        "app.auth": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
    },
}

def setup_logging() -> None:
    dictConfig(LOGGING_CONFIG)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)



