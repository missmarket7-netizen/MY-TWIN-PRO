"""
Centralised Logging Service.
Structured logs with request correlation, level control, and Sentry integration.
"""
import logging
import os
import sys
from typing import Optional

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(correlation_id)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_correlation_id: Optional[str] = None


class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = _correlation_id or "-"
        return True


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    handler.addFilter(CorrelationFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Quiet noisy libraries
    for lib in ["httpx", "httpcore", "urllib3", "asyncio", "uvicorn.access"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    logging.info("Logging initialised")


def set_correlation_id(cid: str):
    global _correlation_id
    _correlation_id = cid


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
