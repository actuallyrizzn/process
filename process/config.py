"""Configuration settings for the process package."""

import os
from typing import Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default settings
default_temperature = 0.5
default_max_retries = 15
default_base_wait_time = 2
default_prompt_max_tokens = 2500

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_KEY')
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_KEY')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def validate_api_keys() -> Dict[str, bool]:
    """Validate that required API keys are present."""
    return {
        'openai': bool(OPENAI_API_KEY),
        'assemblyai': bool(ASSEMBLYAI_API_KEY)
    } 