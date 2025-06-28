"""Text summarization functionality for the process package."""

import json
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

import openai

from .logging import get_logger
from .core import backoff_and_retry, create_openai_client, validate_openai_setup, select_model_for_content
from .utils import safe_file_operation

logger = get_logger(__name__)


@dataclass
class SummarizationConfig:
    """Configuration for summarization."""
    prompt_max_tokens: int = 2500
    engine: Optional[str] = None  # None means auto-select
    temperature: float = 0.5
    max_tokens: int = 8192
    prompt: str = "This is a transcribed text (without diarization) from an online video. Could you summarize the main topics or points of view presented by the speakers in bullet point form?"


@dataclass
class SummarizationResult:
    """Result of summarization operation."""
    success: bool
    summaries: List[str]
    error: Optional[str] = None


def get_chunk(
    text: str, 
    max_tokens: int, 
    model: str
) -> Tuple[str, int]:
    """
    Get a chunk of text that fits within the token limit using binary search.

    Args:
        text: The text to chunk.
        max_tokens: Maximum tokens allowed in the chunk.
        model: The model to use for token counting.

    Returns:
        Tuple of (chunk_text, tokens_used).
    """
    from .token_count import calculate_tokens
    left = 0
    right = len(text)
    
    while left < right:
        middle = (left + right) // 2
        chunk = text[:middle]
        
        token_result = calculate_tokens(chunk, model)
        if not token_result.success:
            logger.warning(f"Failed to calculate tokens for chunk: {token_result.error}")
            # Fallback: return a smaller chunk
            return text[:max(0, middle - 100)], 0
        
        tokens_in_chunk = token_result.tokens
        
        if tokens_in_chunk == max_tokens:
            return chunk, tokens_in_chunk
        elif tokens_in_chunk < max_tokens:
            left = middle + 1
        else:
            right = middle - 1

    # Get the final chunk
    final_chunk = text[:left]
    final_token_result = calculate_tokens(final_chunk, model)
    if not final_token_result.success:
        logger.warning(f"Failed to calculate tokens for final chunk: {final_token_result.error}")
        return final_chunk, 0
    
    return final_chunk, final_token_result.tokens


def chunk_text(
    text: str, 
    prompt: str, 
    max_tokens: int, 
    model: str
) -> List[str]:
    """
    Split text into chunks that fit within token limits.

    Args:
        text: The text to chunk.
        prompt: The prompt that will be prepended to each chunk.
        max_tokens: Maximum tokens per chunk.
        model: The model to use for token counting.

    Returns:
        List of text chunks.
    """
    from .token_count import calculate_tokens
    # Calculate tokens for the prompt
    prompt_result = calculate_tokens(prompt, model)
    if not prompt_result.success:
        logger.warning(f"Failed to calculate prompt tokens: {prompt_result.error}")
        # Fallback: assume prompt takes 100 tokens
        prompt_tokens = 100
    else:
        prompt_tokens = prompt_result.tokens
    
    # Calculate tokens for the full text
    text_result = calculate_tokens(text, model)
    if not text_result.success:
        logger.warning(f"Failed to calculate text tokens: {text_result.error}")
        # Fallback: return the text as a single chunk
        return [text]
    
    text_tokens = text_result.tokens
    
    chunks = []
    if prompt_tokens + text_tokens > max_tokens:
        tokens_per_chunk = max_tokens - prompt_tokens
        start_idx = 0
        
        logger.info("Starting chunking process...")
        while start_idx < len(text):
            logger.debug(f"Getting chunk starting from index {start_idx}...")
            chunk, tokens_used = get_chunk(text[start_idx:], tokens_per_chunk, model)
            logger.debug(f"Chunk obtained with {tokens_used} tokens.")
            chunks.append(chunk)
            start_idx += len(chunk)
    else:
        chunks = [text]
    
    logger.info(f"Text broken into {len(chunks)} chunks.")
    return chunks


def summarize_chunk(
    chunk: str, 
    chunk_index: int, 
    total_chunks: int, 
    config: SummarizationConfig,
    client: openai.OpenAI
) -> Optional[str]:
    """
    Summarize a single chunk of text.

    Args:
        chunk: The text chunk to summarize.
        chunk_index: Index of this chunk (1-based).
        total_chunks: Total number of chunks.
        config: Summarization configuration.
        client: OpenAI client.

    Returns:
        Summary text or None if failed.
    """
    from .token_count import calculate_tokens
    try:
        system_message = f"You are a helpful assistant. You are reading chunk {chunk_index} of {total_chunks}."
        user_message = f"{config.prompt} \n\nChunk {chunk_index} of {total_chunks}:\n\n{chunk}\n\n"
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        # Calculate message tokens
        message_result = calculate_tokens(messages, config.engine)
        if not message_result.success:
            logger.warning(f"Failed to calculate message tokens: {message_result.error}")
            # Fallback: use a conservative token limit
            api_max_tokens = min(1000, config.max_tokens)
        else:
            token_count_for_messages = message_result.tokens
            api_max_tokens = config.max_tokens - token_count_for_messages
            api_max_tokens = max(1, min(api_max_tokens, config.max_tokens))

        logger.debug("Getting response from OpenAI API...")
        response = backoff_and_retry(lambda: client.chat.completions.create(
            model=config.engine,
            messages=messages,
            max_tokens=api_max_tokens,
            temperature=config.temperature
        ))
        
        summary = response.choices[0].message.content.strip()
        logger.debug(f"Summary for chunk {chunk_index}: {summary[:100]}...")
        
        return summary
    
    except Exception as e:
        logger.error(f"Error summarizing chunk {chunk_index}: {e}")
        return None


def summarize_text(
    text: str, 
    config: Optional[SummarizationConfig] = None
) -> SummarizationResult:
    """
    Summarize text using OpenAI API.

    Args:
        text: The text to summarize.
        config: Summarization configuration.

    Returns:
        SummarizationResult with summaries and metadata.
    """
    if config is None:
        config = SummarizationConfig()
    if not validate_openai_setup():
        return SummarizationResult(success=False, summaries=[], error="OpenAI API key not configured")
    client = create_openai_client()
    if client is None:
        return SummarizationResult(success=False, summaries=[], error="Failed to create OpenAI client")
    # Auto-select model if not specified
    if not config.engine:
        selection = select_model_for_content(text)
        config.engine = selection.model
        config.max_tokens = selection.max_tokens
    # Chunk the text
    chunks = chunk_text(text, config.prompt, config.prompt_max_tokens, config.engine)
    summaries = []
    for idx, chunk in enumerate(chunks, start=1):
        logger.info(f"Processing chunk {idx} of {len(chunks)}...")
        summary = summarize_chunk(chunk, idx, len(chunks), config, client)
        if summary is not None:
            summaries.append(summary)
        else:
            logger.error(f"Failed to summarize chunk {idx}")
    if summaries:
        return SummarizationResult(success=True, summaries=summaries)
    else:
        return SummarizationResult(success=False, summaries=[], error="Failed to generate any summaries")


@safe_file_operation("summarization")
def summarize_file(
    input_file: str, 
    output_file: Optional[str] = None,
    config: Optional[SummarizationConfig] = None,
    cleanup: bool = False
) -> SummarizationResult:
    """
    Summarize text from a file.

    Args:
        input_file: Path to input file.
        output_file: Path to output file (optional).
        config: Summarization configuration.
        cleanup: Whether to delete the input file after processing.

    Returns:
        SummarizationResult with summaries and metadata.
    """
    if config is None:
        config = SummarizationConfig()
    
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Summarize the text
        result = summarize_text(text, config)
        
        if result.success and output_file:
            # Write summaries to output file
            with open(output_file, 'w', encoding='utf-8') as f:
                for summary in result.summaries:
                    f.write(summary + '\n')
            logger.info(f"Summaries written to {output_file}")
        
        # Cleanup if requested
        if cleanup and result.success:
            try:
                os.remove(input_file)
                logger.info(f"Cleaned up input file: {input_file}")
            except Exception as e:
                logger.error(f"Error cleaning up file {input_file}: {e}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing file {input_file}: {e}")
        return SummarizationResult(
            success=False,
            summaries=[],
            error=str(e)
        ) 