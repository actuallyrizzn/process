"""Command-line interface for the process package."""

import argparse
import sys
from typing import Optional

from .logging import setup_logging, get_logger
from .config import validate_api_keys
from .summarizer import SummarizationConfig, summarize_file
from .transcriber import TranscriptionConfig, transcribe_file, OutputFormat
from .token_count import calculate_tokens_from_file, format_token_result

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        description="Process - LLM utilities for transcription and summarization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe an audio file
  python -m process transcribe audio.mp3 --output both

  # Summarize a text file
  python -m process summarize input.txt --output summary.txt

  # Count tokens in a file
  python -m process tokens input.txt --model gpt-4
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser('transcribe', help='Transcribe audio files')
    transcribe_parser.add_argument('file_path', help='Path to the audio file')
    transcribe_parser.add_argument('--output', choices=['console', 'file', 'both'], 
                                  default='console', help='Output format')
    transcribe_parser.add_argument('--output-file', help='Output file path')
    transcribe_parser.add_argument('--no-speaker-labels', action='store_true',
                                  help='Disable speaker diarization')
    transcribe_parser.add_argument('--timeout', type=int, default=300,
                                  help='Timeout in seconds')
    
    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Summarize text files')
    summarize_parser.add_argument('input_file', help='Path to input file')
    summarize_parser.add_argument('--output', help='Path to output file')
    summarize_parser.add_argument('--engine', default=None,
                                 help='OpenAI model to use (default: most cost-efficient available)')
    summarize_parser.add_argument('--temperature', type=float, default=0.5,
                                 help='Temperature for generation')
    summarize_parser.add_argument('--max-tokens', type=int, default=8192,
                                 help='Maximum tokens for generation')
    summarize_parser.add_argument('--prompt', help='Custom summarization prompt')
    summarize_parser.add_argument('--cleanup', action='store_true',
                                 help='Delete input file after processing')
    
    # Tokens command
    tokens_parser = subparsers.add_parser('tokens', help='Count tokens in files')
    tokens_parser.add_argument('filepath', help='Path to the file')
    tokens_parser.add_argument('--model', default=None,
                              help='Model to calculate tokens for (default: most cost-efficient available)')
    tokens_parser.add_argument('--json', action='store_true',
                              help='Output in JSON format')
    
    # Show models command
    show_models_parser = subparsers.add_parser('show-models', help='List available OpenAI models')
    
    # Global options
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    parser.add_argument('--log-file', help='Log file path')
    
    return parser


def handle_transcribe(args: argparse.Namespace) -> int:
    """Handle the transcribe command."""
    # Setup logging
    setup_logging(level=args.log_level, log_file=args.log_file)
    
    # Validate API keys
    api_keys = validate_api_keys()
    if not api_keys['assemblyai']:
        logger.error("AssemblyAI API key required for transcription")
        return 1
    
    # Create config
    config = TranscriptionConfig(
        speaker_labels=not args.no_speaker_labels,
        timeout=args.timeout
    )
    
    # Determine output format
    output_format = OutputFormat(args.output)
    
    # Perform transcription
    result = transcribe_file(
        file_path=args.file_path,
        output_format=output_format,
        output_file=args.output_file,
        config=config
    )
    
    if result.success:
        logger.info("Transcription completed successfully")
        return 0
    else:
        logger.error(f"Transcription failed: {result.error}")
        return 1


def handle_summarize(args: argparse.Namespace) -> int:
    """Handle the summarize command."""
    # Setup logging
    setup_logging(level=args.log_level, log_file=args.log_file)
    
    # Validate API keys
    api_keys = validate_api_keys()
    if not api_keys['openai']:
        logger.error("OpenAI API key required for summarization")
        return 1
    
    # Create config
    config = SummarizationConfig(
        engine=args.engine,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        prompt=args.prompt
    )
    
    # Perform summarization
    result = summarize_file(
        input_file=args.input_file,
        output_file=args.output,
        config=config,
        cleanup=args.cleanup
    )
    
    if result.success:
        logger.info(f"Summarization completed successfully. Generated {len(result.summaries)} summaries.")
        return 0
    else:
        logger.error(f"Summarization failed: {result.error}")
        return 1


def handle_tokens(args: argparse.Namespace) -> int:
    """Handle the tokens command."""
    # Setup logging
    setup_logging(level=args.log_level, log_file=args.log_file)
    
    # Calculate tokens
    result = calculate_tokens_from_file(args.filepath, args.model)
    
    if result.success:
        output = format_token_result(result, args.json)
        if args.json:
            import json
            print(json.dumps(output))
        else:
            print(output)
        return 0
    else:
        logger.error(f"Token counting failed: {result.error}")
        return 1


def handle_show_models(args: argparse.Namespace) -> int:
    """Handle the show-models command."""
    from .core import create_openai_client, get_available_models
    setup_logging(level=args.log_level, log_file=args.log_file)
    client = create_openai_client()
    models = get_available_models(client)
    if not models:
        print("No models found or failed to fetch models.")
        return 1
    print("Available OpenAI models:")
    for m in models:
        print(f"- {m['id']}")
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'transcribe':
            return handle_transcribe(args)
        elif args.command == 'summarize':
            return handle_summarize(args)
        elif args.command == 'tokens':
            return handle_tokens(args)
        elif args.command == 'show-models':
            return handle_show_models(args)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 