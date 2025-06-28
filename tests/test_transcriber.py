"""Tests for the transcriber module."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from process.transcriber import (
    OutputFormat,
    TranscriptionConfig,
    TranscriptionResult,
    validate_assemblyai_setup,
    wait_for_completion,
    transcribe_audio,
    transcribe_file,
    format_utterances
)


class TestOutputFormat:
    """Test OutputFormat enum."""
    
    def test_output_format_values(self):
        """Test OutputFormat enum values."""
        assert OutputFormat.CONSOLE.value == "console"
        assert OutputFormat.FILE.value == "file"
        assert OutputFormat.BOTH.value == "both"


class TestTranscriptionConfig:
    """Test TranscriptionConfig dataclass."""
    
    def test_transcription_config_defaults(self):
        """Test TranscriptionConfig with default values."""
        config = TranscriptionConfig()
        
        assert config.speaker_labels is True
        assert config.timeout == 300
        assert config.poll_interval == 2.0
    
    def test_transcription_config_custom(self):
        """Test TranscriptionConfig with custom values."""
        config = TranscriptionConfig(
            speaker_labels=False,
            timeout=600,
            poll_interval=5.0
        )
        
        assert config.speaker_labels is False
        assert config.timeout == 600
        assert config.poll_interval == 5.0


class TestTranscriptionResult:
    """Test TranscriptionResult dataclass."""
    
    def test_transcription_result_success(self):
        """Test TranscriptionResult for successful operation."""
        result = TranscriptionResult(
            success=True,
            transcript="Test transcript",
            utterances=[{"speaker": "A", "text": "Hello"}]
        )
        
        assert result.success is True
        assert result.transcript == "Test transcript"
        assert result.utterances == [{"speaker": "A", "text": "Hello"}]
        assert result.error is None
    
    def test_transcription_result_failure(self):
        """Test TranscriptionResult for failed operation."""
        result = TranscriptionResult(
            success=False,
            error="Test error"
        )
        
        assert result.success is False
        assert result.transcript is None
        assert result.utterances is None
        assert result.error == "Test error"


class TestValidateAssemblyaiSetup:
    """Test validate_assemblyai_setup function."""
    
    @patch('process.transcriber.ASSEMBLYAI_API_KEY', 'test-key')
    def test_validate_assemblyai_setup_with_key(self, mock_aai):
        """Test validation with API key present."""
        with patch('process.transcriber.aai') as mock_aai:
            result = validate_assemblyai_setup()
            
            assert result is True
            mock_aai.settings.api_key = 'test-key'
    
    @patch('process.transcriber.ASSEMBLYAI_API_KEY', None)
    def test_validate_assemblyai_setup_without_key(self):
        """Test validation without API key."""
        result = validate_assemblyai_setup()
        
        assert result is False


class TestWaitForCompletion:
    """Test wait_for_completion function."""
    
    def test_wait_for_completion_success(self):
        """Test successful completion waiting."""
        mock_transcript = Mock()
        mock_transcript.status = 'completed'
        
        result = wait_for_completion(mock_transcript, timeout=10, poll_interval=0.1)
        
        assert result is True
    
    def test_wait_for_completion_timeout(self):
        """Test completion waiting with timeout."""
        mock_transcript = Mock()
        mock_transcript.status = 'processing'
        
        result = wait_for_completion(mock_transcript, timeout=1, poll_interval=0.5)
        
        assert result is False
    
    def test_wait_for_completion_error(self):
        """Test completion waiting with error status."""
        mock_transcript = Mock()
        mock_transcript.status = 'error'
        
        result = wait_for_completion(mock_transcript, timeout=10, poll_interval=0.1)
        
        assert result is False


class TestTranscribeAudio:
    """Test transcribe_audio function."""
    
    @patch('process.transcriber.validate_assemblyai_setup')
    @patch('process.transcriber.aai')
    @patch('process.transcriber.wait_for_completion')
    def test_transcribe_audio_success(self, mock_wait, mock_aai, mock_validate):
        """Test successful audio transcription."""
        mock_validate.return_value = True
        
        # Mock transcript object
        mock_transcript = Mock()
        mock_transcript.status = 'completed'
        mock_utterance = Mock()
        mock_utterance.speaker = 'A'
        mock_utterance.text = 'Hello world'
        mock_utterance.start = 0
        mock_utterance.end = 1000
        mock_transcript.utterances = [mock_utterance]
        
        # Mock transcriber
        mock_transcriber = Mock()
        mock_transcriber.transcribe.return_value = mock_transcript
        mock_aai.Transcriber.return_value = mock_transcriber
        
        # Mock transcription config
        mock_config = Mock()
        mock_aai.TranscriptionConfig.return_value = mock_config
        
        mock_wait.return_value = True
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_file = f.name
        
        try:
            result = transcribe_audio(temp_file)
            
            assert result.success is True
            assert "Hello world" in result.transcript
            assert len(result.utterances) == 1
            assert result.utterances[0]["speaker"] == "A"
            assert result.utterances[0]["text"] == "Hello world"
        finally:
            os.unlink(temp_file)
    
    @patch('process.transcriber.validate_assemblyai_setup')
    def test_transcribe_audio_no_api_key(self, mock_validate):
        """Test audio transcription without API key."""
        mock_validate.return_value = False
        
        result = transcribe_audio("test.mp3")
        
        assert result.success is False
        assert "AssemblyAI API key not configured" in result.error
    
    def test_transcribe_audio_nonexistent_file(self):
        """Test audio transcription with non-existent file."""
        result = transcribe_audio("nonexistent.mp3")
        
        assert result.success is False
        assert "Audio file not found" in result.error


class TestTranscribeFile:
    """Test transcribe_file function."""
    
    @patch('process.transcriber.transcribe_audio')
    def test_transcribe_file_console_output(self, mock_transcribe_audio):
        """Test file transcription with console output."""
        mock_result = TranscriptionResult(
            success=True,
            transcript="Test transcript",
            utterances=[]
        )
        mock_transcribe_audio.return_value = mock_result
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_file = f.name
        
        try:
            result = transcribe_file(temp_file, OutputFormat.CONSOLE)
            
            assert result.success is True
            assert result.transcript == "Test transcript"
        finally:
            os.unlink(temp_file)
    
    @patch('process.transcriber.transcribe_audio')
    def test_transcribe_file_file_output(self, mock_transcribe_audio):
        """Test file transcription with file output."""
        mock_result = TranscriptionResult(
            success=True,
            transcript="Test transcript",
            utterances=[]
        )
        mock_transcribe_audio.return_value = mock_result
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_file = f.name
        
        output_file = "output.txt"
        
        try:
            result = transcribe_file(temp_file, OutputFormat.FILE, output_file)
            
            assert result.success is True
            assert os.path.exists(output_file)
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "Test transcript" in content
        finally:
            os.unlink(temp_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    @patch('process.transcriber.transcribe_audio')
    def test_transcribe_file_transcription_fails(self, mock_transcribe_audio):
        """Test file transcription when transcription fails."""
        mock_result = TranscriptionResult(
            success=False,
            error="Transcription failed"
        )
        mock_transcribe_audio.return_value = mock_result
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_file = f.name
        
        try:
            result = transcribe_file(temp_file, OutputFormat.CONSOLE)
            
            assert result.success is False
            assert result.error == "Transcription failed"
        finally:
            os.unlink(temp_file)


class TestFormatUtterances:
    """Test format_utterances function."""
    
    def test_format_utterances_empty(self):
        """Test formatting empty utterances."""
        result = format_utterances([])
        
        assert result == ""
    
    def test_format_utterances_single(self):
        """Test formatting single utterance."""
        utterances = [{"speaker": "A", "text": "Hello"}]
        
        result = format_utterances(utterances)
        
        assert result == "Speaker A: Hello"
    
    def test_format_utterances_multiple(self):
        """Test formatting multiple utterances."""
        utterances = [
            {"speaker": "A", "text": "Hello"},
            {"speaker": "B", "text": "Hi there"},
            {"speaker": "A", "text": "How are you?"}
        ]
        
        result = format_utterances(utterances)
        
        expected = "Speaker A: Hello\nSpeaker B: Hi there\nSpeaker A: How are you?"
        assert result == expected
    
    def test_format_utterances_missing_fields(self):
        """Test formatting utterances with missing fields."""
        utterances = [
            {"speaker": "A", "text": "Hello"},
            {"text": "No speaker"},  # Missing speaker
            {"speaker": "B"}  # Missing text
        ]
        
        result = format_utterances(utterances)
        
        expected = "Speaker A: Hello\nSpeaker Unknown: No speaker\nSpeaker B: "
        assert result == expected 