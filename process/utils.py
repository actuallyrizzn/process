"""Utility functions for the process package."""

import re
import logging
from typing import Callable, Any, TypeVar, Union
from functools import wraps
import validators

from .logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


def is_valid_url(url: str) -> bool:
    """
    Check if the provided string is a valid URL.

    Args:
        url: The string to be checked.

    Returns:
        True if the string is a valid URL, False otherwise.
    """
    if not url or not isinstance(url, str):
        return False
    
    # Use the validators library for robust URL validation
    return validators.url(url) is True


def convert_bytes_to_readable_size(byte_size: Union[int, float], decimals: int = 2) -> str:
    """
    Convert bytes to a more readable string format.

    Args:
        byte_size: The size in bytes to be converted.
        decimals: The number of decimal places to round to.

    Returns:
        The converted size in a readable string format.

    Raises:
        ValueError: If byte_size is negative.
    """
    if byte_size < 0:
        raise ValueError("Byte size cannot be negative")
    
    if byte_size == 0:
        return "0 bytes"
    
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']
    size = float(byte_size)
    
    for unit in units:
        if size < 1024.0:
            return f"{round(size, decimals)} {unit}"
        size /= 102.0
    
    return f"{round(size, decimals)} PB"


def handle_errors(func: Callable[..., T]) -> Callable[..., Union[T, None]]:
    """
    Decorator to handle errors and exceptions in the decorated function.

    Args:
        func: The function to be decorated.

    Returns:
        The wrapper function that handles errors and exceptions.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Union[T, None]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"An error occurred in {func.__name__}: {e}")
            return None
    return wrapper


def safe_file_operation(operation: str = "file operation"):
    """
    Decorator for safe file operations with proper error handling.

    Args:
        operation: Description of the operation for error messages.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, None]]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Union[T, None]:
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                logger.error(f"File not found during {operation}: {e}")
                return None
            except PermissionError as e:
                logger.error(f"Permission denied during {operation}: {e}")
                return None
            except IOError as e:
                logger.error(f"I/O error during {operation}: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error during {operation}: {e}")
                return None
        return wrapper
    return decorator 