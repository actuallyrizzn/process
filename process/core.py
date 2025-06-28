"""Core functionality for the process package."""

import time
import random
import threading
import os
from typing import Callable, Any, Dict, Optional, List
from dataclasses import dataclass

import openai

from .config import OPENAI_API_KEY
from .logging import get_logger

logger = get_logger(__name__)

DEFAULT_MAX_RETRIES = 15
DEFAULT_BASE_WAIT_TIME = 2


@dataclass
class ModelSelection:
    """Result of model selection process."""
    model: str
    max_tokens: int
    prompt_tokens: int


class Spinner:
    """A class to manage a spinning cursor in the terminal."""
    
    def __init__(self):
        self.stop_spinner = False
        self.spinner_thread: Optional[threading.Thread] = None

    def spinner(self) -> None:
        """Display a spinning cursor."""
        import sys
        while not self.stop_spinner:
            for cursor in '|/-\\':
                if self.stop_spinner:
                    break
                sys.stdout.write(cursor)
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write('\b')

    def start(self) -> None:
        """Start the spinning cursor."""
        self.stop_spinner = False
        self.spinner_thread = threading.Thread(target=self.spinner)
        self.spinner_thread.start()

    def stop(self) -> None:
        """Stop the spinning cursor."""
        self.stop_spinner = True
        if self.spinner_thread:
            self.spinner_thread.join()


def backoff_and_retry(
    api_call: Callable[[], Any], 
    max_retries: int = DEFAULT_MAX_RETRIES
) -> Any:
    """
    Retry an API call with exponential backoff in case of rate limit errors.

    Args:
        api_call: The API call function to retry.
        max_retries: Maximum number of retry attempts.

    Returns:
        The result of the API call.

    Raises:
        Exception: If all retries are exhausted.
    """
    last_exception = None
    
    for i in range(max_retries):
        try:
            return api_call()
        except openai.RateLimitError as e:
            last_exception = e
            wait_time = (DEFAULT_BASE_WAIT_TIME ** i) + random.random()
            logger.warning(f"Rate limit reached. Waiting for {wait_time:.2f} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise e
    
    # If we've retried the maximum number of times, re-raise the last error
    if last_exception:
        raise last_exception
    
    raise Exception("Maximum retries exceeded")


def get_available_models(client: Optional[openai.OpenAI] = None) -> List[Dict[str, Any]]:
    """
    Fetch available OpenAI models and their properties.
    Returns a list of dicts with id, context_window, and other metadata.
    """
    if client is None:
        client = create_openai_client()
    if client is None:
        return []
    try:
        models = client.models.list().data
        # Filter for chat/completions models (e.g., gpt-*)
        filtered = [m for m in models if m.id.startswith('gpt-')]
        # Optionally, sort by price or context window if available
        return [{"id": m.id, **m.__dict__} for m in filtered]
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        return []


def get_most_cost_efficient_model(client: Optional[openai.OpenAI] = None) -> Optional[str]:
    """
    Return the most cost-efficient available model (e.g., gpt-3.5-turbo, gpt-4o if present).
    """
    models = get_available_models(client)
    # Prefer gpt-4o, then gpt-3.5-turbo, then gpt-4, etc.
    preferred = [
        'gpt-4o',
        'gpt-3.5-turbo',
        'gpt-4',
    ]
    for pref in preferred:
        for m in models:
            if m["id"].startswith(pref):
                return m["id"]
    # Fallback to first available
    if models:
        return models[0]["id"]
    return None


def select_model_for_content(content: str) -> ModelSelection:
    """
    Select the most cost-efficient available model and token limits based on content length.
    """
    from .token_count import calculate_tokens
    token_result = calculate_tokens(content)
    client = create_openai_client()
    model = get_most_cost_efficient_model(client)
    if not model:
        logger.warning("No available OpenAI models found. Using fallback.")
        model = os.environ.get("OPENAI_FALLBACK_MODEL", "gpt-3.5-turbo")
    # Try to get context window (max_tokens) from model info
    max_tokens = 4096  # Default fallback
    available_models = get_available_models(client)
    for m in available_models:
        if m["id"] == model:
            max_tokens = getattr(m, "context_window", 4096) or 4096
            break
    if not token_result.success:
        logger.warning(f"Failed to calculate tokens: {token_result.error}")
        return ModelSelection(
            model=model,
            max_tokens=int(0.95 * max_tokens),
            prompt_tokens=int(0.5 * max_tokens)
        )
    # Use 95% of max_tokens for safety
    return ModelSelection(
        model=model,
        max_tokens=int(0.95 * max_tokens),
        prompt_tokens=int(0.5 * max_tokens)
    )


def validate_openai_setup() -> bool:
    """
    Validate that OpenAI is properly configured.

    Returns:
        True if OpenAI is properly configured, False otherwise.
    """
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found. Please set OPENAI_KEY environment variable.")
        return False
    
    openai.api_key = OPENAI_API_KEY
    return True


def create_openai_client() -> Optional[openai.OpenAI]:
    """
    Create and configure an OpenAI client.

    Returns:
        Configured OpenAI client or None if configuration is invalid.
    """
    if not validate_openai_setup():
        return None
    
    return openai.OpenAI(api_key=OPENAI_API_KEY) 