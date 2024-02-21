import re

def is_valid_url(url):
    """
    Check if the provided string is a valid URL.

    Parameters:
    - url (str): The string to be checked.

    Returns:
    - bool: True if the string is a valid URL, False otherwise.
    """
    # A simple regex pattern to check the validity of a URL
    pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return bool(pattern.match(url))

def convert_bytes_to_readable_size(byte_size):
    """Convert bytes to a more readable string format."""
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if byte_size < 1024.0:
            return f"{byte_size:.2f} {unit}"
        byte_size /= 1024.0

def handle_errors(func):
    """Decorator to handle errors and exceptions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
    return wrapper
