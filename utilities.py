import re

def is_valid_url(url: str) -> bool:
    """
    Check if the provided string is a valid URL.

    Parameters:
    - url (str): The string to be checked.

    Returns:
    - bool: True if the string is a valid URL, False otherwise.
    """
    # A more comprehensive regex pattern to check the validity of a URL
    pattern = re.compile(
        r'^(https?://)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*/?$'
    )
    return bool(pattern.match(url))

def convert_bytes_to_readable_size(byte_size: float, decimals: int = 2) -> str:
    """
    Convert bytes to a more readable string format.

    Parameters:
    - byte_size (float): The size in bytes to be converted.
    - decimals (int): The number of decimal places to round to.

    Returns:
    - str: The converted size in a readable string format.
    """
    if byte_size < 0:
        raise ValueError("Byte size cannot be negative")
    if byte_size == 0:
        return "0 bytes"
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if byte_size < 1024.0:
            return f"{round(byte_size, decimals)} {unit}"
        byte_size /= 1024.0

def handle_errors(func):
    """
    Decorator to handle errors and exceptions in the decorated function.

    Parameters:
    - func: The function to be decorated.

    Returns:
    - The wrapper function that handles errors and exceptions.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
    return wrapper
