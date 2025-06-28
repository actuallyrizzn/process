#!/usr/bin/python3
import tempfile
import time
import openai
import sys
import threading
import random
import argparse
from dotenv import load_dotenv
from tokencount import calculate_tokens

# Load .env file if it exists
load_dotenv()

# Constants
MAX_RETRIES = 15
BASE_WAIT_TIME = 2
TOKEN_LIMITS = {
    'gpt-3.5-turbo-16k': 16000,
    'gpt-4': 8000
}

class Spinner:
    """A class to manage a spinning cursor in the terminal."""
    def __init__(self):
        self.stop_spinner = False
        self.spinner_thread = threading.Thread(target=self.spinner)

    def spinner(self):
        """Display a spinning cursor."""
        while not self.stop_spinner:
            for cursor in '|/-\\':
                sys.stdout.write(cursor)
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write('\b')

    def start(self):
        """Start the spinning cursor."""
        self.stop_spinner = False
        self.spinner_thread.start()

    def stop(self):
        """Stop the spinning cursor."""
        self.stop_spinner = True

def log(message):
    """Log a message to stdout."""
    print(message)

def backoff_and_retry(api_call, max_retries=MAX_RETRIES):
    """Retry an API call with exponential backoff in case of rate limit errors."""
    last_exception = None
    for i in range(max_retries):
        try:
            # Try to make the API call
            return api_call()
        except openai.error.RateLimitError as e:
            # If a rate limit error is encountered, wait and then retry
            last_exception = e
            wait_time = (BASE_WAIT_TIME ** i) + random.random()
            log(f"Rate limit reached. Waiting for {wait_time} seconds...")
            time.sleep(wait_time)
    # If we've retried the maximum number of times, re-raise the last error
    if last_exception:
        raise last_exception

def research(file_name):
    """
    Researches the document and determines appropriate GPT model and token limits.

    Args:
    - file_name (str): Path to the file to be summarized.

    Returns:
    - dict: Model, max_token, and prompt_token values.
    """
    # Determine token count of the file
    token_count = calculate_tokens(file_name)

    # Decision-making based on token count
    if token_count > 7000:
        model = 'gpt-3.5-turbo-16k'
        max_token_limit = TOKEN_LIMITS[model]
    else:
        model = 'gpt-4'
        max_token_limit = TOKEN_LIMITS[model]

    # Calculate max_token and prompt_token
    max_token = int(0.95 * max_token_limit)
    prompt_token = int(0.5 * max_token)

    return {
        'model': model,
        'max_token': max_token,
        'prompt_token': prompt_token
    }
