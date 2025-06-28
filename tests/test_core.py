"""Tests for the core module."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from process.core import (
    ModelSelection,
    Spinner,
    backoff_and_retry,
    select_model_for_content,
    validate_openai_setup,
    create_openai_client
)


class TestModelSelection:
    """Test ModelSelection dataclass."""
    
    def test_model_selection_creation(self):
        """Test creating a ModelSelection instance."""
        selection = ModelSelection(
            model="gpt-4",
            max_tokens=8000,
            prompt_tokens=4000
        )
        
        assert selection.model == "gpt-4"
        assert selection.max_tokens == 8000
        assert selection.prompt_tokens == 4000


class TestSpinner:
    """Test Spinner class."""
    
    def test_spinner_creation(self):
        """Test creating a Spinner instance."""
        spinner = Spinner()
        
        assert spinner.stop_spinner is False
        assert spinner.spinner_thread is None
    
    def test_spinner_start_stop(self):
        """Test starting and stopping the spinner."""
        spinner = Spinner()
        
        # Start spinner
        spinner.start()
        assert spinner.stop_spinner is False
        assert spinner.spinner_thread is not None
        assert spinner.spinner_thread.is_alive()
        
        # Stop spinner
        spinner.stop()
        assert spinner.stop_spinner is True
        # Give thread time to finish
        time.sleep(0.1)
        assert not spinner.spinner_thread.is_alive()


class TestBackoffAndRetry:
    """Test backoff_and_retry function."""
    
    def test_successful_api_call(self):
        """Test successful API call without retries."""
        mock_api_call = Mock(return_value="success")
        
        result = backoff_and_retry(mock_api_call)
        
        assert result == "success"
        mock_api_call.assert_called_once()
    
    def test_api_call_with_rate_limit_then_success(self):
        """Test API call that hits rate limit then succeeds."""
        from openai import RateLimitError
        
        mock_api_call = Mock()
        mock_api_call.side_effect = [RateLimitError("Rate limit"), "success"]
        
        result = backoff_and_retry(mock_api_call, max_retries=2)
        
        assert result == "success"
        assert mock_api_call.call_count == 2
    
    def test_api_call_with_rate_limit_exhausts_retries(self):
        """Test API call that exhausts retries due to rate limiting."""
        from openai import RateLimitError
        
        mock_api_call = Mock()
        mock_api_call.side_effect = RateLimitError("Rate limit")
        
        with pytest.raises(RateLimitError):
            backoff_and_retry(mock_api_call, max_retries=3)
        
        assert mock_api_call.call_count == 3
    
    def test_api_call_with_other_exception(self):
        """Test API call with non-rate-limit exception."""
        mock_api_call = Mock()
        mock_api_call.side_effect = ValueError("Other error")
        
        with pytest.raises(ValueError):
            backoff_and_retry(mock_api_call)
        
        mock_api_call.assert_called_once()


class TestSelectModelForContent:
    """Test select_model_for_content function."""
    
    @patch('process.core.calculate_tokens')
    def test_select_model_for_small_content(self, mock_calculate_tokens):
        """Test model selection for small content."""
        mock_result = Mock()
        mock_result.success = True
        mock_result.tokens = 1000
        mock_calculate_tokens.return_value = mock_result
        
        selection = select_model_for_content("Small content")
        
        assert selection.model == "gpt-4-0613"
        assert selection.max_tokens > 0
        assert selection.prompt_tokens > 0
    
    @patch('process.core.calculate_tokens')
    def test_select_model_for_large_content(self, mock_calculate_tokens):
        """Test model selection for large content."""
        mock_result = Mock()
        mock_result.success = True
        mock_result.tokens = 8000
        mock_calculate_tokens.return_value = mock_result
        
        selection = select_model_for_content("Large content")
        
        assert selection.model == "gpt-3.5-turbo-16k-0613"
        assert selection.max_tokens > 0
        assert selection.prompt_tokens > 0
    
    @patch('process.core.calculate_tokens')
    @patch('process.core.get_model_config')
    def test_select_model_with_token_calculation_failure(self, mock_get_config, mock_calculate_tokens):
        """Test model selection when token calculation fails."""
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Token calculation failed"
        mock_calculate_tokens.return_value = mock_result
        
        mock_config = Mock()
        mock_config.name = "gpt-3.5-turbo-0613"
        mock_config.max_tokens = 4096
        mock_get_config.return_value = mock_config
        
        selection = select_model_for_content("Content")
        
        assert selection.model == "gpt-3.5-turbo-0613"
        assert selection.max_tokens > 0
        assert selection.prompt_tokens > 0


class TestValidateOpenaiSetup:
    """Test validate_openai_setup function."""
    
    @patch('process.core.OPENAI_API_KEY', 'test-key')
    def test_validate_openai_setup_with_key(self):
        """Test validation with API key present."""
        result = validate_openai_setup()
        
        assert result is True
    
    @patch('process.core.OPENAI_API_KEY', None)
    def test_validate_openai_setup_without_key(self):
        """Test validation without API key."""
        result = validate_openai_setup()
        
        assert result is False


class TestCreateOpenaiClient:
    """Test create_openai_client function."""
    
    @patch('process.core.validate_openai_setup')
    @patch('process.core.openai.OpenAI')
    def test_create_openai_client_success(self, mock_openai, mock_validate):
        """Test successful client creation."""
        mock_validate.return_value = True
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        result = create_openai_client()
        
        assert result == mock_client
        mock_openai.assert_called_once_with(api_key='test-openai-key')
    
    @patch('process.core.validate_openai_setup')
    def test_create_openai_client_validation_fails(self, mock_validate):
        """Test client creation when validation fails."""
        mock_validate.return_value = False
        
        result = create_openai_client()
        
        assert result is None 