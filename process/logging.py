"""Logging configuration for the process package."""

import logging
import sys
from typing import Optional
from .config import LOG_LEVEL, LOG_FORMAT


def setup_logging(
    level: str = LOG_LEVEL,
    format_string: str = LOG_FORMAT,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger('process')
    logger.setLevel(getattr(logging, level.upper()))

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = 'process') -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


# Create default logger
logger = get_logger() 