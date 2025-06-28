"""Pytest configuration and fixtures."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from typing import Generator


@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("This is a test file content for testing purposes.")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_text() -> str:
    """Sample text for testing."""
    return "This is a sample text for testing token counting and summarization functionality."


@pytest.fixture
def sample_messages() -> list:
    """Sample messages for testing."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
    ]


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch('process.core.openai.OpenAI') as mock:
        client_instance = Mock()
        mock.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_assemblyai():
    """Mock AssemblyAI."""
    with patch('process.transcriber.aai') as mock:
        yield mock


@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests."""
    with patch('process.logging.setup_logging'):
        yield


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables."""
    with patch.dict(os.environ, {
        'OPENAI_KEY': 'test-openai-key',
        'ASSEMBLYAI_KEY': 'test-assemblyai-key'
    }):
        yield 