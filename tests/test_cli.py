"""Tests for the CLI module."""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from process.cli import (
    create_parser,
    handle_transcribe,
    handle_summarize,
    handle_tokens,
    main
)


class TestCreateParser:
    """Test create_parser function."""
    
    def test_create_parser_has_subcommands(self):
        """Test that parser has expected subcommands."""
        parser = create_parser()
        
        # Check that subparsers exist
        assert hasattr(parser, '_subparsers')
        subparsers = parser._subparsers._group_actions[0]
        
        # Check that all expected commands exist
        expected_commands = ['transcribe', 'summarize', 'tokens']
        for command in expected_commands:
            assert command in subparsers.choices
    
    def test_transcribe_subcommand_arguments(self):
        """Test transcribe subcommand has expected arguments."""
        parser = create_parser()
        transcribe_parser = parser._subparsers._group_actions[0].choices['transcribe']
        
        # Check required arguments
        assert 'file_path' in [action.dest for action in transcribe_parser._actions]
        
        # Check optional arguments (excluding global args that are on main parser)
        optional_args = [action.dest for action in transcribe_parser._actions if action.option_strings]
        expected_optional = ['output', 'output_file', 'no_speaker_labels', 'timeout']
        for arg in expected_optional:
            assert arg in optional_args
    
    def test_summarize_subcommand_arguments(self):
        """Test summarize subcommand has expected arguments."""
        parser = create_parser()
        summarize_parser = parser._subparsers._group_actions[0].choices['summarize']
        
        # Check required arguments
        assert 'input_file' in [action.dest for action in summarize_parser._actions]
        
        # Check optional arguments (excluding global args that are on main parser)
        optional_args = [action.dest for action in summarize_parser._actions if action.option_strings]
        expected_optional = ['output', 'engine', 'temperature', 'max_tokens', 'prompt', 'cleanup']
        for arg in expected_optional:
            assert arg in optional_args
    
    def test_tokens_subcommand_arguments(self):
        """Test tokens subcommand has expected arguments."""
        parser = create_parser()
        tokens_parser = parser._subparsers._group_actions[0].choices['tokens']
        
        # Check required arguments
        assert 'filepath' in [action.dest for action in tokens_parser._actions]
        
        # Check optional arguments (excluding global args that are on main parser)
        optional_args = [action.dest for action in tokens_parser._actions if action.option_strings]
        expected_optional = ['model', 'json']
        for arg in expected_optional:
            assert arg in optional_args
    
    def test_global_arguments(self):
        """Test that global arguments are on the main parser."""
        parser = create_parser()
        
        # Check global arguments
        global_args = [action.dest for action in parser._actions if action.option_strings]
        expected_global = ['log_level', 'log_file']
        for arg in expected_global:
            assert arg in global_args


class TestHandleTranscribe:
    """Test handle_transcribe function."""
    
    @patch('process.cli.setup_logging')
    @patch('process.cli.validate_api_keys')
    @patch('process.cli.transcribe_file')
    def test_handle_transcribe_success(self, mock_transcribe_file, mock_validate_api_keys, mock_setup_logging):
        """Test successful transcribe command."""
        # Mock API keys validation
        mock_validate_api_keys.return_value = {'assemblyai': True, 'openai': True}
        
        # Mock transcription result
        mock_result = Mock()
        mock_result.success = True
        mock_transcribe_file.return_value = mock_result
        
        # Create mock args
        args = Mock()
        args.log_level = 'INFO'
        args.log_file = None
        args.file_path = 'test.mp3'
        args.output = 'console'
        args.output_file = None
        args.no_speaker_labels = False
        args.timeout = 300
        
        result = handle_transcribe(args)
        
        assert result == 0
        mock_transcribe_file.assert_called_once()
    
    @patch('process.cli.setup_logging')
    @patch('process.cli.validate_api_keys')
    def test_handle_transcribe_no_assemblyai_key(self, mock_validate_api_keys, mock_setup_logging):
        """Test transcribe command without AssemblyAI API key."""
        # Mock API keys validation
        mock_validate_api_keys.return_value = {'assemblyai': False, 'openai': True}
        
        # Create mock args
        args = Mock()
        args.log_level = 'INFO'
        args.log_file = None
        args.file_path = 'test.mp3'
        args.output = 'console'
        args.output_file = None
        args.no_speaker_labels = False
        args.timeout = 300
        
        result = handle_transcribe(args)
        
        assert result == 1
    
    @patch('process.cli.setup_logging')
    @patch('process.cli.validate_api_keys')
    @patch('process.cli.transcribe_file')
    def test_handle_transcribe_failure(self, mock_transcribe_file, mock_validate_api_keys, mock_setup_logging):
        """Test transcribe command with transcription failure."""
        # Mock API keys validation
        mock_validate_api_keys.return_value = {'assemblyai': True, 'openai': True}
        
        # Mock transcription result
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Transcription failed"
        mock_transcribe_file.return_value = mock_result
        
        # Create mock args
        args = Mock()
        args.log_level = 'INFO'
        args.log_file = None
        args.file_path = 'test.mp3'
        args.output = 'console'
        args.output_file = None
        args.no_speaker_labels = False
        args.timeout = 300
        
        result = handle_transcribe(args)
        
        assert result == 1


class TestHandleSummarize:
    """Test handle_summarize function."""
    
    @patch('process.cli.setup_logging')
    @patch('process.cli.validate_api_keys')
    @patch('process.cli.summarize_file')
    def test_handle_summarize_success(self, mock_summarize_file, mock_validate_api_keys, mock_setup_logging):
        """Test successful summarize command."""
        # Mock API keys validation
        mock_validate_api_keys.return_value = {'assemblyai': True, 'openai': True}
        
        # Mock summarization result
        mock_result = Mock()
        mock_result.success = True
        mock_result.summaries = ["Summary 1", "Summary 2"]
        mock_summarize_file.return_value = mock_result
        
        # Create mock args
        args = Mock()
        args.log_level = 'INFO'
        args.log_file = None
        args.input_file = 'input.txt'
        args.output = 'output.txt'
        args.engine = 'gpt-3.5-turbo-0613'
        args.temperature = 0.5
        args.max_tokens = 8192
        args.prompt = None
        args.cleanup = False
        
        result = handle_summarize(args)
        
        assert result == 0
        mock_summarize_file.assert_called_once()
    
    @patch('process.cli.setup_logging')
    @patch('process.cli.validate_api_keys')
    def test_handle_summarize_no_openai_key(self, mock_validate_api_keys, mock_setup_logging):
        """Test summarize command without OpenAI API key."""
        # Mock API keys validation
        mock_validate_api_keys.return_value = {'assemblyai': True, 'openai': False}
        
        # Create mock args
        args = Mock()
        args.log_level = 'INFO'
        args.log_file = None
        args.input_file = 'input.txt'
        args.output = 'output.txt'
        args.engine = 'gpt-3.5-turbo-0613'
        args.temperature = 0.5
        args.max_tokens = 8192
        args.prompt = None
        args.cleanup = False
        
        result = handle_summarize(args)
        
        assert result == 1


class TestHandleTokens:
    """Test handle_tokens function."""
    
    @patch('process.cli.setup_logging')
    @patch('process.cli.calculate_tokens_from_file')
    @patch('process.cli.format_token_result')
    def test_handle_tokens_success_text(self, mock_format_result, mock_calculate_tokens, mock_setup_logging):
        """Test successful tokens command with text output."""
        # Mock token calculation result
        mock_result = Mock()
        mock_result.success = True
        mock_result.tokens = 100
        mock_result.model = 'gpt-3.5-turbo-0613'
        mock_calculate_tokens.return_value = mock_result
        
        # Mock formatted result
        mock_format_result.return_value = "Token count: 100 (model: gpt-3.5-turbo-0613)"
        
        # Create mock args
        args = Mock()
        args.log_level = 'INFO'
        args.log_file = None
        args.filepath = 'test.txt'
        args.model = 'gpt-3.5-turbo-0613'
        args.json = False
        
        with patch('builtins.print') as mock_print:
            result = handle_tokens(args)
            
            assert result == 0
            mock_print.assert_called_once_with("Token count: 100 (model: gpt-3.5-turbo-0613)")
    
    @patch('process.cli.setup_logging')
    @patch('process.cli.calculate_tokens_from_file')
    @patch('process.cli.format_token_result')
    def test_handle_tokens_success_json(self, mock_format_result, mock_calculate_tokens, mock_setup_logging):
        """Test successful tokens command with JSON output."""
        # Mock token calculation result
        mock_result = Mock()
        mock_result.success = True
        mock_result.tokens = 100
        mock_result.model = 'gpt-3.5-turbo-0613'
        mock_calculate_tokens.return_value = mock_result
        
        # Mock formatted result
        mock_format_result.return_value = {"tokens": 100, "model": "gpt-3.5-turbo-0613"}
        
        # Create mock args
        args = Mock()
        args.log_level = 'INFO'
        args.log_file = None
        args.filepath = 'test.txt'
        args.model = 'gpt-3.5-turbo-0613'
        args.json = True
        
        with patch('builtins.print') as mock_print:
            with patch('json.dumps') as mock_json_dumps:
                mock_json_dumps.return_value = '{"tokens": 100}'
                result = handle_tokens(args)
                
                assert result == 0
                mock_json_dumps.assert_called_once()
                mock_print.assert_called_once_with('{"tokens": 100}')
    
    @patch('process.cli.setup_logging')
    @patch('process.cli.calculate_tokens_from_file')
    def test_handle_tokens_failure(self, mock_calculate_tokens, mock_setup_logging):
        """Test tokens command with calculation failure."""
        # Mock token calculation result
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Token calculation failed"
        mock_calculate_tokens.return_value = mock_result
        
        # Create mock args
        args = Mock()
        args.log_level = 'INFO'
        args.log_file = None
        args.filepath = 'test.txt'
        args.model = 'gpt-3.5-turbo-0613'
        args.json = False
        
        result = handle_tokens(args)
        
        assert result == 1


class TestMain:
    """Test main function."""
    
    @patch('process.cli.create_parser')
    def test_main_no_command(self, mock_create_parser):
        """Test main function with no command."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.parse_args.return_value = Mock(command=None)
        mock_create_parser.return_value = mock_parser
        
        result = main()
        
        assert result == 1
        mock_parser.print_help.assert_called_once()
    
    @patch('process.cli.create_parser')
    @patch('process.cli.handle_transcribe')
    def test_main_transcribe_command(self, mock_handle_transcribe, mock_create_parser):
        """Test main function with transcribe command."""
        # Mock parser
        mock_parser = Mock()
        mock_args = Mock(command='transcribe')
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        mock_handle_transcribe.return_value = 0
        
        result = main()
        
        assert result == 0
        mock_handle_transcribe.assert_called_once_with(mock_args)
    
    @patch('process.cli.create_parser')
    @patch('process.cli.handle_summarize')
    def test_main_summarize_command(self, mock_handle_summarize, mock_create_parser):
        """Test main function with summarize command."""
        # Mock parser
        mock_parser = Mock()
        mock_args = Mock(command='summarize')
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        mock_handle_summarize.return_value = 0
        
        result = main()
        
        assert result == 0
        mock_handle_summarize.assert_called_once_with(mock_args)
    
    @patch('process.cli.create_parser')
    @patch('process.cli.handle_tokens')
    def test_main_tokens_command(self, mock_handle_tokens, mock_create_parser):
        """Test main function with tokens command."""
        # Mock parser
        mock_parser = Mock()
        mock_args = Mock(command='tokens')
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        mock_handle_tokens.return_value = 0
        
        result = main()
        
        assert result == 0
        mock_handle_tokens.assert_called_once_with(mock_args)
    
    @patch('process.cli.create_parser')
    def test_main_unknown_command(self, mock_create_parser):
        """Test main function with unknown command."""
        # Mock parser
        mock_parser = Mock()
        mock_args = Mock(command='unknown')
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        result = main()
        
        assert result == 1
    
    @patch('process.cli.create_parser')
    def test_main_keyboard_interrupt(self, mock_create_parser):
        """Test main function with keyboard interrupt."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.parse_args.side_effect = KeyboardInterrupt()
        mock_create_parser.return_value = mock_parser
        
        result = main()
        
        assert result == 1
    
    @patch('process.cli.create_parser')
    def test_main_exception(self, mock_create_parser):
        """Test main function with exception."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.parse_args.side_effect = Exception("Test error")
        mock_create_parser.return_value = mock_parser
        
        result = main()
        
        assert result == 1 