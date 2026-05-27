"""Centralized structured logger."""
from __future__ import annotations

import logging
import sys
from typing import Optional

from app.config import settings


_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


def setup_logging(level: Optional[str] = None) -> None:
    """Configure root logging once at startup."""
    log_level = (level or settings.LOG_LEVEL).upper()

    logging.basicConfig(
        level=log_level,
        format=_LOG_FORMAT,
        stream=sys.stdout,
        force=True,
    )

    # Quieten noisy libraries
    for noisy in ("httpx", "httpcore", "sqlalchemy.engine.Engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger."""
    return logging.getLogger(name)
