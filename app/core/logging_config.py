"""
Centralised logging configuration.

Call ``setup_logging()`` once at application startup.  Every module then
uses ``logging.getLogger(__name__)`` to get a child logger that
automatically routes to both console and a rotating log file.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_CONFIGURED = False

# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------
_CONSOLE_FMT = "%(asctime)s │ %(levelname)-7s │ %(name)-30s │ %(message)s"
_FILE_FMT = "%(asctime)s | %(levelname)-7s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
_DATE_FMT = "%H:%M:%S"


def setup_logging(log_dir: Path | str = "logs", level: str = "INFO") -> None:
    """Configure root logger with console + rotating file handlers.

    Safe to call multiple times; only the first call takes effect.
    """
    global _CONFIGURED  # noqa: PLW0603
    if _CONFIGURED:
        return
    _CONFIGURED = True

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # -- Console handler ---------------------------------------------------
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(_CONSOLE_FMT, datefmt=_DATE_FMT))
    root.addHandler(console)

    # -- File handler (rotating, 5 MB × 3 backups) -------------------------
    file_handler = RotatingFileHandler(
        log_dir / "copilot.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_FILE_FMT, datefmt=_DATE_FMT))
    root.addHandler(file_handler)

    # Silence noisy third-party loggers
    for name in ("httpcore", "httpx", "urllib3", "google", "grpc"):
        logging.getLogger(name).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging initialised  level=%s  file=%s", level, log_dir / "copilot.log"
    )
