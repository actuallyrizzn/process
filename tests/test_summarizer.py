"""Tests for the summarizer module."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from process.summarizer import (
    SummarizationConfig,
    SummarizationResult,
    get_chunk,
    chunk_text,
    summarize_chunk,
    summarize_text,
    summarize_file
)


class TestSummarizationConfig:
    """Test SummarizationConfig dataclass."""
    
    def test_summarization_config_defaults(self):
        """Test SummarizationConfig with default values."""
        config = SummarizationConfig()
        
        assert config.prompt_max_tokens == 2500
        assert config.engine == "gpt-3.5-turbo-0613"
        assert config.temperature == 0.5
        assert config.max_tokens == 8192
        assert "summarize" in config.prompt.lower()
    
    def test_summarization_config_custom(self):
        """Test SummarizationConfig with custom values."""
        config = SummarizationConfig(
            prompt_max_tokens=1000,
            engine="gpt-4",
            temperature=0.7,
            max_tokens=4000,
            prompt="Custom prompt"
        )
        
        assert config.prompt_max_tokens == 1000
        assert config.engine == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 4000
        assert config.prompt == "Custom prompt"


class TestSummarizationResult:
    """Test SummarizationResult dataclass."""
    
    def test_summarization_result_success(self):
        """Test SummarizationResult for successful operation."""
        result = SummarizationResult(
            success=True,
            summaries=["Summary 1", "Summary 2"]
        )
        
        assert result.success is True
        assert result.summaries == ["Summary 1", "Summary 2"]
        assert result.error is None
    
    def test_summarization_result_failure(self):
        """Test SummarizationResult for failed operation."""
        result = SummarizationResult(
            success=False,
            summaries=[],
            error="Test error"
        )
        
        assert result.success is False
        assert result.summaries == []
        assert result.error == "Test error"


class TestGetChunk:
    """Test get_chunk function."""
    
    @patch('process.summarizer.calculate_tokens')
    def test_get_chunk_success(self, mock_calculate_tokens):
        """Test successful chunking."""
        # Mock token calculation to return different token counts
        def mock_token_calc(text, model):
            mock_result = Mock()
            mock_result.success = True
            # Return token count based on text length
            mock_result.tokens = len(text) // 10
            return mock_result
        
        mock_calculate_tokens.side_effect = mock_token_calc
        
        text = "This is a test text that should be chunked properly"
        chunk, tokens = get_chunk(text, 5, "gpt-3.5-turbo-0613")
        
        assert len(chunk) > 0
        assert tokens > 0
    
    @patch('process.summarizer.calculate_tokens')
    def test_get_chunk_token_calculation_failure(self, mock_calculate_tokens):
        """Test chunking when token calculation fails."""
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Token calculation failed"
        mock_calculate_tokens.return_value = mock_result
        
        text = "This is a test text"
        chunk, tokens = get_chunk(text, 5, "gpt-3.5-turbo-0613")
        
        assert len(chunk) > 0
        assert tokens == 0


class TestChunkText:
    """Test chunk_text function."""
    
    @patch('process.summarizer.calculate_tokens')
    def test_chunk_text_small_content(self, mock_calculate_tokens):
        """Test chunking small content that doesn't need chunking."""
        # Mock token calculations
        def mock_token_calc(data, model):
            mock_result = Mock()
            mock_result.success = True
            if isinstance(data, str):
                mock_result.tokens = 100  # Small text
            else:
                mock_result.tokens = 50   # Small prompt
            return mock_result
        
        mock_calculate_tokens.side_effect = mock_token_calc
        
        text = "Small text content"
        chunks = chunk_text(text, "Test prompt", 1000, "gpt-3.5-turbo-0613")
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    @patch('process.summarizer.calculate_tokens')
    @patch('process.summarizer.get_chunk')
    def test_chunk_text_large_content(self, mock_get_chunk, mock_calculate_tokens):
        """Test chunking large content that needs chunking."""
        # Mock token calculations
        def mock_token_calc(data, model):
            mock_result = Mock()
            mock_result.success = True
            if isinstance(data, str):
                mock_result.tokens = 2000  # Large text
            else:
                mock_result.tokens = 50    # Small prompt
            return mock_result
        
        mock_calculate_tokens.side_effect = mock_token_calc
        
        # Mock chunking
        mock_get_chunk.return_value = ("chunk", 500)
        
        text = "Large text content " * 100
        chunks = chunk_text(text, "Test prompt", 1000, "gpt-3.5-turbo-0613")
        
        assert len(chunks) > 1
        assert mock_get_chunk.called


class TestSummarizeChunk:
    """Test summarize_chunk function."""
    
    @patch('process.summarizer.calculate_tokens')
    @patch('process.summarizer.backoff_and_retry')
    def test_summarize_chunk_success(self, mock_backoff, mock_calculate_tokens):
        """Test successful chunk summarization."""
        # Mock token calculation
        mock_result = Mock()
        mock_result.success = True
        mock_result.tokens = 100
        mock_calculate_tokens.return_value = mock_result
        
        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test summary"
        mock_backoff.return_value = mock_response
        
        config = SummarizationConfig()
        client = Mock()
        
        result = summarize_chunk("Test chunk", 1, 2, config, client)
        
        assert result == "Test summary"
        mock_backoff.assert_called_once()
    
    @patch('process.summarizer.calculate_tokens')
    def test_summarize_chunk_token_calculation_failure(self, mock_calculate_tokens):
        """Test chunk summarization when token calculation fails."""
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Token calculation failed"
        mock_calculate_tokens.return_value = mock_result
        
        config = SummarizationConfig()
        client = Mock()
        
        result = summarize_chunk("Test chunk", 1, 2, config, client)
        
        assert result is None


class TestSummarizeText:
    """Test summarize_text function."""
    
    @patch('process.summarizer.validate_openai_setup')
    @patch('process.summarizer.create_openai_client')
    @patch('process.summarizer.chunk_text')
    @patch('process.summarizer.summarize_chunk')
    def test_summarize_text_success(self, mock_summarize_chunk, mock_chunk_text, 
                                   mock_create_client, mock_validate):
        """Test successful text summarization."""
        mock_validate.return_value = True
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        mock_chunk_text.return_value = ["chunk1", "chunk2"]
        mock_summarize_chunk.side_effect = ["summary1", "summary2"]
        
        result = summarize_text("Test text")
        
        assert result.success is True
        assert result.summaries == ["summary1", "summary2"]
        assert result.error is None
    
    @patch('process.summarizer.validate_openai_setup')
    def test_summarize_text_no_openai_key(self, mock_validate):
        """Test text summarization without OpenAI API key."""
        mock_validate.return_value = False
        
        result = summarize_text("Test text")
        
        assert result.success is False
        assert result.summaries == []
        assert "OpenAI API key not configured" in result.error
    
    @patch('process.summarizer.validate_openai_setup')
    @patch('process.summarizer.create_openai_client')
    def test_summarize_text_client_creation_fails(self, mock_create_client, mock_validate):
        """Test text summarization when client creation fails."""
        mock_validate.return_value = True
        mock_create_client.return_value = None
        
        result = summarize_text("Test text")
        
        assert result.success is False
        assert result.summaries == []
        assert "Failed to create OpenAI client" in result.error


class TestSummarizeFile:
    """Test summarize_file function."""
    
    def test_summarize_file_success(self, temp_file):
        """Test successful file summarization."""
        with patch('process.summarizer.summarize_text') as mock_summarize_text:
            mock_result = SummarizationResult(
                success=True,
                summaries=["Summary 1", "Summary 2"]
            )
            mock_summarize_text.return_value = mock_result
            
            result = summarize_file(temp_file, "output.txt")
            
            assert result.success is True
            assert result.summaries == ["Summary 1", "Summary 2"]
            mock_summarize_text.assert_called_once()
    
    def test_summarize_file_with_cleanup(self, temp_file):
        """Test file summarization with cleanup."""
        with patch('process.summarizer.summarize_text') as mock_summarize_text:
            mock_result = SummarizationResult(
                success=True,
                summaries=["Summary"]
            )
            mock_summarize_text.return_value = mock_result
            
            result = summarize_file(temp_file, "output.txt", cleanup=True)
            
            assert result.success is True
            # File should be cleaned up
            assert not os.path.exists(temp_file)
    
    def test_summarize_file_nonexistent(self):
        """Test file summarization with non-existent file."""
        result = summarize_file("nonexistent.txt")
        
        assert result.success is False
        assert "Error processing file" in result.error 