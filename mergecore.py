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

def spinner():
    while not stop_spinner:
        for cursor in '|/-\\':
            sys.stdout.write(cursor)
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')

def spin_cursor():
    global stop_spinner
    stop_spinner = False
    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()

def stop_cursor():
    global stop_spinner
    stop_spinner = True

def log(message):
    """Log a message to stdout or a file, if specified."""
    print(message)
    #if args.log_file is not None:
    #    with open(args.log_file, 'a') as f:
    #        f.write(message + '\n')

def backoff_and_retry(api_call, max_retries=15):
    last_exception = None
    for i in range(max_retries):
        try:
            # Try to make the API call
            return api_call()
        except openai.error.RateLimitError as e:
            # If a rate limit error is encountered, wait and then retry
            last_exception = e
            wait_time = (2 ** i) + random.random()
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
        max_token_limit = 16000
    else:
        model = 'gpt-4'
        max_token_limit = 8000

    # Calculate max_token and prompt_token
    max_token = int(0.95 * max_token_limit)
    prompt_token = int(0.5 * max_token)

    return {
        'model': model,
        'max_token': max_token,
        'prompt_token': prompt_token
    }
