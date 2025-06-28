"""Tests for the config module."""

import pytest
from unittest.mock import patch

from process.config import (
    validate_api_keys
)


class TestValidateApiKeys:
    """Test validate_api_keys function."""
    
    @patch('process.config.OPENAI_API_KEY', 'test-openai-key')
    @patch('process.config.ASSEMBLYAI_API_KEY', 'test-assemblyai-key')
    def test_validate_api_keys_both_present(self):
        """Test validation when both API keys are present."""
        result = validate_api_keys()
        
        assert result['openai'] is True
        assert result['assemblyai'] is True
    
    @patch('process.config.OPENAI_API_KEY', None)
    @patch('process.config.ASSEMBLYAI_API_KEY', 'test-assemblyai-key')
    def test_validate_api_keys_openai_missing(self):
        """Test validation when OpenAI API key is missing."""
        result = validate_api_keys()
        
        assert result['openai'] is False
        assert result['assemblyai'] is True
    
    @patch('process.config.OPENAI_API_KEY', 'test-openai-key')
    @patch('process.config.ASSEMBLYAI_API_KEY', None)
    def test_validate_api_keys_assemblyai_missing(self):
        """Test validation when AssemblyAI API key is missing."""
        result = validate_api_keys()
        
        assert result['openai'] is True
        assert result['assemblyai'] is False
    
    @patch('process.config.OPENAI_API_KEY', None)
    @patch('process.config.ASSEMBLYAI_API_KEY', None)
    def test_validate_api_keys_both_missing(self):
        """Test validation when both API keys are missing."""
        result = validate_api_keys()
        
        assert result['openai'] is False
        assert result['assemblyai'] is False 