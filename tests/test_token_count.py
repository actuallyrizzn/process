"""Tests for the token_count module."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from process.token_count import (
    TokenResult,
    get_encoding_for_model,
    calculate_tokens_for_messages,
    calculate_tokens_for_text,
    calculate_tokens,
    calculate_tokens_from_file,
    format_token_result
)


class TestTokenResult:
    """Test TokenResult dataclass."""
    
    def test_token_result_creation(self):
        """Test creating a TokenResult instance."""
        result = TokenResult(
            tokens=100,
            model="gpt-3.5-turbo-0613",
            success=True
        )
        
        assert result.tokens == 100
        assert result.model == "gpt-3.5-turbo-0613"
        assert result.success is True
        assert result.error is None
    
    def test_token_result_with_error(self):
        """Test creating a TokenResult instance with error."""
        result = TokenResult(
            tokens=0,
            model="gpt-3.5-turbo-0613",
            success=False,
            error="test error"
        )
        
        assert result.tokens == 0
        assert result.model == "gpt-3.5-turbo-0613"
        assert result.success is False
        assert result.error == "test error"


class TestGetEncodingForModel:
    """Test get_encoding_for_model function."""
    
    @patch('process.token_count.tiktoken.encoding_for_model')
    def test_get_encoding_for_existing_model(self, mock_encoding_for_model):
        """Test getting encoding for existing model."""
        mock_encoding = Mock()
        mock_encoding_for_model.return_value = mock_encoding
        
        result = get_encoding_for_model("gpt-3.5-turbo-0613")
        
        assert result == mock_encoding
        mock_encoding_for_model.assert_called_once_with("gpt-3.5-turbo-0613")
    
    @patch('process.token_count.tiktoken.encoding_for_model')
    @patch('process.token_count.tiktoken.get_encoding')
    def test_get_encoding_for_nonexistent_model(self, mock_get_encoding, mock_encoding_for_model):
        """Test getting encoding for non-existent model."""
        mock_encoding_for_model.side_effect = KeyError("Model not found")
        mock_encoding = Mock()
        mock_get_encoding.return_value = mock_encoding
        
        result = get_encoding_for_model("nonexistent-model")
        
        assert result == mock_encoding
        mock_get_encoding.assert_called_once_with("cl100k_base")


class TestCalculateTokensForMessages:
    """Test calculate_tokens_for_messages function."""
    
    @patch('process.token_count.get_encoding_for_model')
    @patch('process.token_count.get_model_config')
    def test_calculate_tokens_for_messages_success(self, mock_get_config, mock_get_encoding):
        """Test successful token calculation for messages."""
        # Mock encoding
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_get_encoding.return_value = mock_encoding
        
        # Mock config
        mock_config = Mock()
        mock_config.tokens_per_message = 3
        mock_config.tokens_per_name = 1
        mock_get_config.return_value = mock_config
        
        messages = [
            {"role": "system", "content": "Hello"},
            {"role": "user", "content": "World"}
        ]
        
        result = calculate_tokens_for_messages(messages, "gpt-3.5-turbo-0613")
        
        assert result.success is True
        assert result.tokens > 0
        assert result.model == "gpt-3.5-turbo-0613"
        assert result.error is None
    
    @patch('process.token_count.get_encoding_for_model')
    def test_calculate_tokens_for_messages_error(self, mock_get_encoding):
        """Test token calculation for messages with error."""
        mock_get_encoding.side_effect = Exception("Encoding error")
        
        messages = [{"role": "system", "content": "Hello"}]
        
        result = calculate_tokens_for_messages(messages, "gpt-3.5-turbo-0613")
        
        assert result.success is False
        assert result.tokens == 0
        assert result.error == "Encoding error"


class TestCalculateTokensForText:
    """Test calculate_tokens_for_text function."""
    
    @patch('process.token_count.get_encoding_for_model')
    def test_calculate_tokens_for_text_success(self, mock_get_encoding):
        """Test successful token calculation for text."""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_get_encoding.return_value = mock_encoding
        
        result = calculate_tokens_for_text("Hello world", "gpt-3.5-turbo-0613")
        
        assert result.success is True
        assert result.tokens == 5
        assert result.model == "gpt-3.5-turbo-0613"
        assert result.error is None
    
    @patch('process.token_count.get_encoding_for_model')
    def test_calculate_tokens_for_text_error(self, mock_get_encoding):
        """Test token calculation for text with error."""
        mock_get_encoding.side_effect = Exception("Encoding error")
        
        result = calculate_tokens_for_text("Hello world", "gpt-3.5-turbo-0613")
        
        assert result.success is False
        assert result.tokens == 0
        assert result.error == "Encoding error"


class TestCalculateTokens:
    """Test calculate_tokens function."""
    
    @patch('process.token_count.calculate_tokens_for_text')
    def test_calculate_tokens_with_string(self, mock_calc_text):
        """Test calculate_tokens with string input."""
        mock_result = TokenResult(tokens=5, model="test", success=True)
        mock_calc_text.return_value = mock_result
        
        result = calculate_tokens("Hello world", "gpt-3.5-turbo-0613")
        
        assert result == mock_result
        mock_calc_text.assert_called_once_with("Hello world", "gpt-3.5-turbo-0613")
    
    @patch('process.token_count.calculate_tokens_for_messages')
    def test_calculate_tokens_with_messages(self, mock_calc_messages):
        """Test calculate_tokens with messages input."""
        mock_result = TokenResult(tokens=10, model="test", success=True)
        mock_calc_messages.return_value = mock_result
        
        messages = [{"role": "system", "content": "Hello"}]
        result = calculate_tokens(messages, "gpt-3.5-turbo-0613")
        
        assert result == mock_result
        mock_calc_messages.assert_called_once_with(messages, "gpt-3.5-turbo-0613")
    
    def test_calculate_tokens_with_invalid_type(self):
        """Test calculate_tokens with invalid input type."""
        result = calculate_tokens(123, "gpt-3.5-turbo-0613")  # Invalid type
        
        assert result.success is False
        assert result.tokens == 0
        assert "Unsupported data type" in result.error


class TestCalculateTokensFromFile:
    """Test calculate_tokens_from_file function."""
    
    def test_calculate_tokens_from_file_text(self, temp_file):
        """Test token calculation from text file."""
        result = calculate_tokens_from_file(temp_file, "gpt-3.5-turbo-0613")
        
        assert result.success is True
        assert result.tokens > 0
        assert result.model == "gpt-3.5-turbo-0613"
    
    def test_calculate_tokens_from_file_json(self, temp_file):
        """Test token calculation from JSON file."""
        # Write JSON content to temp file
        with open(temp_file, 'w') as f:
            json.dump([{"role": "system", "content": "Hello"}], f)
        
        result = calculate_tokens_from_file(temp_file, "gpt-3.5-turbo-0613")
        
        assert result.success is True
        assert result.tokens > 0
        assert result.model == "gpt-3.5-turbo-0613"
    
    def test_calculate_tokens_from_nonexistent_file(self):
        """Test token calculation from non-existent file."""
        result = calculate_tokens_from_file("nonexistent.txt", "gpt-3.5-turbo-0613")
        
        assert result.success is False
        assert result.tokens == 0
        assert "Error reading file" in result.error


class TestFormatTokenResult:
    """Test format_token_result function."""
    
    def test_format_token_result_success_text(self):
        """Test formatting successful token result as text."""
        result = TokenResult(tokens=100, model="gpt-3.5-turbo-0613", success=True)
        
        formatted = format_token_result(result, json_output=False)
        
        assert "Token count: 100" in formatted
        assert "gpt-3.5-turbo-0613" in formatted
    
    def test_format_token_result_error_text(self):
        """Test formatting failed token result as text."""
        result = TokenResult(
            tokens=0, 
            model="gpt-3.5-turbo-0613", 
            success=False, 
            error="test error"
        )
        
        formatted = format_token_result(result, json_output=False)
        
        assert "Error calculating tokens: test error" in formatted
    
    def test_format_token_result_success_json(self):
        """Test formatting successful token result as JSON."""
        result = TokenResult(tokens=100, model="gpt-3.5-turbo-0613", success=True)
        
        formatted = format_token_result(result, json_output=True)
        
        assert formatted["tokens"] == 100
        assert formatted["model"] == "gpt-3.5-turbo-0613"
        assert formatted["success"] is True
        assert formatted["error"] is None
    
    def test_format_token_result_error_json(self):
        """Test formatting failed token result as JSON."""
        result = TokenResult(
            tokens=0, 
            model="gpt-3.5-turbo-0613", 
            success=False, 
            error="test error"
        )
        
        formatted = format_token_result(result, json_output=True)
        
        assert formatted["tokens"] == 0
        assert formatted["model"] == "gpt-3.5-turbo-0613"
        assert formatted["success"] is False
        assert formatted["error"] == "test error" 