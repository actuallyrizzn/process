"""Audio transcription functionality for the process package."""

import os
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

import assemblyai as aai

from .config import ASSEMBLYAI_API_KEY
from .logging import get_logger
from .utils import safe_file_operation

logger = get_logger(__name__)


class OutputFormat(Enum):
    """Output format options for transcription."""
    CONSOLE = "console"
    FILE = "file"
    BOTH = "both"


@dataclass
class TranscriptionConfig:
    """Configuration for transcription."""
    speaker_labels: bool = True
    timeout: int = 300  # 5 minutes timeout
    poll_interval: float = 2.0  # seconds between status checks


@dataclass
class TranscriptionResult:
    """Result of transcription operation."""
    success: bool
    transcript: Optional[str] = None
    utterances: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


def validate_assemblyai_setup() -> bool:
    """
    Validate that AssemblyAI is properly configured.

    Returns:
        True if AssemblyAI is properly configured, False otherwise.
    """
    if not ASSEMBLYAI_API_KEY:
        logger.error("AssemblyAI API key not found. Please set ASSEMBLYAI_KEY environment variable.")
        return False
    
    aai.settings.api_key = ASSEMBLYAI_API_KEY
    return True


def wait_for_completion(
    transcript: aai.Transcript, 
    timeout: int = 300, 
    poll_interval: float = 2.0
) -> bool:
    """
    Wait for transcription to complete with timeout.

    Args:
        transcript: The transcript object to monitor.
        timeout: Maximum time to wait in seconds.
        poll_interval: Time between status checks in seconds.

    Returns:
        True if transcription completed successfully, False if timed out or failed.
    """
    start_time = time.time()
    
    while transcript.status != 'completed':
        if time.time() - start_time > timeout:
            logger.error(f"Transcription timed out after {timeout} seconds")
            return False
        
        if transcript.status == 'error':
            logger.error(f"Transcription failed with status: {transcript.status}")
            return False
        
        logger.debug(f"Transcription status: {transcript.status}")
        time.sleep(poll_interval)
    
    logger.info("Transcription completed successfully")
    return True


def transcribe_audio(
    file_path: str, 
    config: Optional[TranscriptionConfig] = None
) -> TranscriptionResult:
    """
    Transcribe an audio file using AssemblyAI.

    Args:
        file_path: Path to the audio file.
        config: Transcription configuration.

    Returns:
        TranscriptionResult with transcript and metadata.
    """
    if config is None:
        config = TranscriptionConfig()
    
    # Validate AssemblyAI setup
    if not validate_assemblyai_setup():
        return TranscriptionResult(
            success=False,
            error="AssemblyAI API key not configured"
        )
    
    # Validate file exists
    if not os.path.exists(file_path):
        return TranscriptionResult(
            success=False,
            error=f"Audio file not found: {file_path}"
        )
    
    try:
        # Create transcription configuration
        aai_config = aai.TranscriptionConfig(speaker_labels=config.speaker_labels)
        
        # Create transcriber and start transcription
        transcriber = aai.Transcriber()
        logger.info(f"Starting transcription of {file_path}")
        
        transcript = transcriber.transcribe(file_path, config=aai_config)
        
        # Wait for completion
        if not wait_for_completion(transcript, config.timeout, config.poll_interval):
            return TranscriptionResult(
                success=False,
                error="Transcription timed out or failed"
            )
        
        # Extract results
        utterances = []
        full_transcript = ""
        
        for utterance in transcript.utterances:
            utterance_data = {
                "speaker": utterance.speaker,
                "text": utterance.text,
                "start": utterance.start,
                "end": utterance.end
            }
            utterances.append(utterance_data)
            
            if config.speaker_labels:
                full_transcript += f"Speaker {utterance.speaker}: {utterance.text}\n"
            else:
                full_transcript += f"{utterance.text}\n"
        
        return TranscriptionResult(
            success=True,
            transcript=full_transcript.strip(),
            utterances=utterances
        )
    
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return TranscriptionResult(
            success=False,
            error=str(e)
        )


@safe_file_operation("transcription")
def transcribe_file(
    file_path: str,
    output_format: OutputFormat = OutputFormat.CONSOLE,
    output_file: Optional[str] = None,
    config: Optional[TranscriptionConfig] = None
) -> TranscriptionResult:
    """
    Transcribe an audio file and handle output.

    Args:
        file_path: Path to the audio file.
        output_format: How to output the transcription.
        output_file: Path for output file (if needed).
        config: Transcription configuration.

    Returns:
        TranscriptionResult with transcript and metadata.
    """
    if config is None:
        config = TranscriptionConfig()
    
    # Perform transcription
    result = transcribe_audio(file_path, config)
    
    if not result.success:
        return result
    
    # Handle output
    if output_format in [OutputFormat.CONSOLE, OutputFormat.BOTH]:
        print(result.transcript)
    
    if output_format in [OutputFormat.FILE, OutputFormat.BOTH]:
        if output_file is None:
            output_file = 'transcription.txt'
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.transcript)
            logger.info(f"Transcription saved to {output_file}")
        except Exception as e:
            logger.error(f"Error writing transcription to file: {e}")
            return TranscriptionResult(
                success=False,
                error=f"Failed to write output file: {e}"
            )
    
    return result


def format_utterances(utterances: List[Dict[str, Any]]) -> str:
    """
    Format utterances into a readable string.

    Args:
        utterances: List of utterance dictionaries.

    Returns:
        Formatted string representation.
    """
    if not utterances:
        return ""
    
    formatted = []
    for utterance in utterances:
        speaker = utterance.get("speaker", "Unknown")
        text = utterance.get("text", "")
        formatted.append(f"Speaker {speaker}: {text}")
    
    return "\n".join(formatted) 