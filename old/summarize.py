import json
import traceback
import os
import openai
import sys
import argparse
from dotenv import load_dotenv
from mergecore import log, backoff_and_retry
from tokencount import calculate_tokens

# Load .env file if it exists
load_dotenv()
openai.api_key = os.environ.get('OPENAI_KEY')

# Here's the updated version of the generate_summaries function with more logging statements for better visibility into the progress.

def generate_summaries(prompt_max_tokens=2500, 
                       input_file=None, 
                       output_file=None, 
                       cleanup=False, 
                       engine="gpt-3.5-turbo-0613", 
                       temperature=0.5, 
                       max_tokens=int(8192), 
                       prompt="This is a transcribed text (without diarization) from an online video. Could you summarize the main topics or points of view presented by the speakers in bullet point form?", 
                       log_file=None):

    if input_file:
        transcript_file = input_file
        try:
            with open(transcript_file, 'r') as file:
                data = file.read()

            log("Calculating tokens for prompt...")
            prompt_token_output = calculate_tokens(prompt, model=engine, json_output=True)
            if isinstance(prompt_token_output, str):
                prompt_token_output = json.loads(prompt_token_output)
            prompt_token_count = prompt_token_output['tokens']
            log(f"Prompt token count: {prompt_token_count}")

            log("Calculating tokens for data...")
            data_token_output = calculate_tokens(data, model=engine, json_output=True)
            if isinstance(data_token_output, str):
                data_token_output = json.loads(data_token_output)
            data_token_count = data_token_output['tokens']
            log(f"Data token count: {data_token_count}")

            chunks_text = []
            if prompt_token_count + data_token_count > prompt_max_tokens:
                tokens_per_chunk = prompt_max_tokens - prompt_token_count
                start_idx = 0

                log("Starting chunking process...")
                while start_idx < len(data):
                    log(f"Getting chunk starting from index {start_idx}...")
                    chunk, tokens_used = get_chunk(data[start_idx:], tokens_per_chunk, model=engine)
                    log(f"Chunk obtained with {tokens_used} tokens.")
                    chunks_text.append(chunk)
                    start_idx += len(chunk)
            else:
                chunks_text = [data]

            log(f"Transcript broken into {len(chunks_text)} chunks.")
            with open(output_file, 'w') as outfile:
                for idx, chunk_text in enumerate(chunks_text, start=1):
                    log(f"Processing chunk {idx}...")
                    system_message = f"You are a helpful assistant. You are reading chunk {idx} of {len(chunks_text)}."
                    user_message = f"{prompt} \n\nChunk {idx} of {len(chunks_text)}:\n\n{chunk_text}\n\n"
                    messages = [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message},
                    ]

                    log("Calculating message tokens...")
                    message_token_output = calculate_tokens(messages, model=engine, json_output=True)
                    if isinstance(message_token_output, str):
                        message_token_output = json.loads(message_token_output)

                    token_count_for_messages = message_token_output['tokens']
                    api_max_tokens = max_tokens - token_count_for_messages
                    api_max_tokens = max(1, min(api_max_tokens, max_tokens))

                    log("Getting response from OpenAI API...")
                    response = backoff_and_retry(lambda: openai.ChatCompletion.create(
                        model=engine,
                        messages=messages,
                        max_tokens=api_max_tokens,
                        temperature=temperature
                    ))
                    summary = response['choices'][0]['message']['content'].strip()

                    log(f"Summary for chunk {idx}: {summary}")
                    outfile.write(summary + '\n')
                log("Summaries generated.")

            if cleanup and input_file:
                try:
                    log("Starting cleanup...")
                    os.remove(input_file)
                except Exception as e:
                    log(f"Error occurred while deleting file {input_file}: {e}")
                return

            log("Cleanup completed.")
        except Exception as e:
            log(f"Error occurred: {traceback.format_exc()}")
            return
    else:
        log("Error: No input source provided. Please specify an input file.")
        return output_file

# Adding a visual indicator in the get_chunk function to show progress during the chunk size reduction process

# Implementing the binary search approach in the get_chunk function

# Correcting the mistake in the get_chunk function

def get_chunk(text, max_tokens, model):
    left = 0
    right = len(text)
    
    while left < right:
        middle = (left + right) // 2
        chunk = text[:middle]
        
        token_output = calculate_tokens(chunk, model=model, json_output=True)
        if isinstance(token_output, str):
            token_output = json.loads(token_output)
        
        tokens_in_chunk = token_output['tokens']
        
        if tokens_in_chunk == max_tokens:
            return chunk, tokens_in_chunk
        elif tokens_in_chunk < max_tokens:
            left = middle + 1
        else:
            right = middle - 1

    # Corrected the JSON parsing before accessing the 'tokens' field
    final_chunk = text[:left]
    final_token_output = calculate_tokens(final_chunk, model=model, json_output=True)
    if isinstance(final_token_output, str):
        final_token_output = json.loads(final_token_output)
    final_tokens_in_chunk = final_token_output['tokens']
    
    return final_chunk, final_tokens_in_chunk

def cli_main():
    parser = argparse.ArgumentParser(description='Generate summaries from text chunks.')
    parser.add_argument('--prompt_max_tokens', type=int, default=2500, help='Specify max tokens for the prompt.')
    parser.add_argument('-i', '--input_file', help='Specify the input file.')
    parser.add_argument('-o', '--output_file', help='Specify the output file.')
    parser.add_argument('--cleanup', dest='cleanup', action='store_true', help='Enable cleanup of original files.')
    parser.add_argument('--engine', default="gpt-3.5-turbo-0613", help='Specify the engine to be used.')
    parser.add_argument('--temperature', type=float, default=0.5, help='Specify the temperature.')
    parser.add_argument('--max_tokens', type=int, default=int(8192 * 0.8), help='Specify max tokens.')
    parser.add_argument('--prompt', default="This is a transcribed text (without diarization) from an online video. Could you summarize the main topics or points of view presented by the speakers in bullet point form?", help='Specify the prompt.')
    parser.add_argument('--log_file', help='Specify a log file to which output will be logged.')
    parser.set_defaults(cleanup=False)
    args = parser.parse_args()

    openai.api_key = os.getenv('OPENAI_KEY')
    if openai.api_key is None:
        log("Error: OpenAI API key not found. Please make sure the OPENAI_KEY environment variable is set.")
        sys.exit(1)

    generate_summaries(
        prompt_max_tokens=args.prompt_max_tokens,
        input_file=args.input_file,
        output_file=args.output_file,
        cleanup=args.cleanup,
        engine=args.engine,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        prompt=args.prompt,
        log_file=args.log_file
    )

if __name__ == "__main__":
    try:
        cli_main()
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()
