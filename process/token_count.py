"""Token counting utilities for the process package."""

import json
import tiktoken
from typing import Union, List, Dict, Any, Optional
from dataclasses import dataclass

from .logging import get_logger
from .utils import safe_file_operation

logger = get_logger(__name__)


@dataclass
class TokenResult:
    """Result of token counting operation."""
    tokens: int
    model: str
    success: bool
    error: Optional[str] = None


def get_encoding_for_model(model: str) -> tiktoken.Encoding:
    """
    Get the encoding for the given model.

    Args:
        model: The model name to get encoding for.

    Returns:
        The tiktoken encoding for the model.

    Raises:
        KeyError: If model is not found.
    """
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning(f"Model {model} not found. Using cl100k_base encoding.")
        return tiktoken.get_encoding("cl100k_base")


def calculate_tokens_for_messages(
    messages: List[Dict[str, str]], 
    model: Optional[str] = None
) -> TokenResult:
    """
    Calculate the number of tokens for given messages and model.
    If model is None, use the most cost-efficient available.
    """
    try:
        if not model:
            from .core import select_model_for_content
            content = '\n'.join([m.get('content', '') for m in messages])
            model = select_model_for_content(content).model
        encoding = get_encoding_for_model(model)
        # Use default values if model-specific info is not available
        tokens_per_message = 3
        tokens_per_name = 1
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <assistant>
        return TokenResult(tokens=num_tokens, model=model, success=True)
    except Exception as e:
        logger.error(f"Error calculating tokens for messages: {e}")
        return TokenResult(tokens=0, model=model or '', success=False, error=str(e))


def calculate_tokens_for_text(
    text: str, 
    model: Optional[str] = None
) -> TokenResult:
    """
    Calculate the number of tokens for given text and model.
    If model is None, use the most cost-efficient available.
    """
    try:
        if not model:
            from .core import select_model_for_content
            model = select_model_for_content(text).model
        encoding = get_encoding_for_model(model)
        tokens = len(encoding.encode(text))
        return TokenResult(tokens=tokens, model=model, success=True)
    except Exception as e:
        logger.error(f"Error calculating tokens for text: {e}")
        return TokenResult(tokens=0, model=model or '', success=False, error=str(e))


def calculate_tokens(
    data: Union[str, List[Dict[str, str]]], 
    model: Optional[str] = None
) -> TokenResult:
    """
    Calculate the number of tokens for given data and model.

    Args:
        data: Either a string or list of message dictionaries.
        model: The model name to calculate tokens for.

    Returns:
        TokenResult with token count and metadata.
    """
    if isinstance(data, str):
        return calculate_tokens_for_text(data, model)
    elif isinstance(data, list):
        return calculate_tokens_for_messages(data, model)
    else:
        error_msg = f"Unsupported data type: {type(data)}"
        logger.error(error_msg)
        return TokenResult(tokens=0, model=model or '', success=False, error=error_msg)


@safe_file_operation("token counting")
def calculate_tokens_from_file(
    filepath: str, 
    model: Optional[str] = None
) -> TokenResult:
    """
    Calculate tokens from a file.
    If model is None, use the most cost-efficient available.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Try to parse as JSON first
        try:
            messages = json.loads(content)
            if isinstance(messages, list):
                return calculate_tokens_for_messages(messages, model)
        except json.JSONDecodeError:
            pass
        # Treat as plain text
        return calculate_tokens_for_text(content, model)
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return TokenResult(tokens=0, model=model or '', success=False, error=str(e))


def format_token_result(result: TokenResult, json_output: bool = False) -> Union[str, Dict[str, Any]]:
    """
    Format a TokenResult for output.

    Args:
        result: The TokenResult to format.
        json_output: Whether to return JSON format.

    Returns:
        Formatted result as string or dictionary.
    """
    if json_output:
        return {
            "tokens": result.tokens,
            "model": result.model,
            "success": result.success,
            "error": result.error
        }
    else:
        if result.success:
            return f"Token count: {result.tokens} (model: {result.model})"
        else:
            return f"Error calculating tokens: {result.error}" 