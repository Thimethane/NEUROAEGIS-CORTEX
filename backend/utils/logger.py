"""
Logging Configuration
Centralized logging setup for AegisAI
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from config.settings import settings


def setup_logging(log_file: Optional[Path] = None):
    """
    Configure logging for the application
    
    Args:
        log_file: Optional log file path
    """

    log_file = log_file or settings.LOG_FILE

    root_logger = logging.getLogger()

    # ? IMPORTANT: prevent duplicate handlers
    if root_logger.handlers:
        return root_logger

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)

    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)

    return root_logger
