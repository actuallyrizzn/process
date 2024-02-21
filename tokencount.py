import argparse
import json
import tiktoken

# Dictionary mapping model names to their behaviors
model_behavior = {'gpt-3.5-turbo-0613': {'tokens_per_message': 3, 'tokens_per_name': 1}, 'gpt-3.5-turbo-16k-0613': {'tokens_per_message': 3, 'tokens_per_name': 1}, 'gpt-4-0314': {'tokens_per_message': 3, 'tokens_per_name': 1}, 'gpt-4-32k-0314': {'tokens_per_message': 3, 'tokens_per_name': 1}, 'gpt-4-0613': {'tokens_per_message': 3, 'tokens_per_name': 1}, 'gpt-4-32k-0613': {'tokens_per_message': 3, 'tokens_per_name': 1}, 'gpt-3.5-turbo-0301': {'tokens_per_message': 4, 'tokens_per_name': -1}}

def output_message(message, json_output=False):
    """Function to output messages in either human-readable format or JSON format based on the json_output flag."""
    if json_output:
        return json.dumps({"message": message})
    return message

def get_encoding_for_model(model, json_output=False):
    """Get the encoding for the given model."""
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        output_message("Warning: model not found. Using cl100k_base encoding.", json_output)
        return tiktoken.get_encoding("cl100k_base")

def enhanced_num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613", json_output=False):
    """Calculate the number of tokens for given messages and model."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        output_message("Warning: model not found. Using cl100k_base encoding.", json_output)
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens_per_message = 2  # Default values
    tokens_per_name = 1

    behavior = model_behavior.get(model)
    if behavior:
        tokens_per_message = behavior["tokens_per_message"]
        tokens_per_name = behavior["tokens_per_name"]
    elif "gpt-3.5-turbo" in model:
        # Default values for gpt-3.5-turbo, adjust if necessary
        tokens_per_message = 2
        tokens_per_name = 1
    elif "gpt-4" in model:
        # Default values for gpt-4, adjust if necessary
        tokens_per_message = 2
        tokens_per_name = 1
    else:
        error_msg = f"""num_tokens_from_messages() is not implemented for model {model}. Using default token counts."""
        output_message(error_msg, json_output)

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <assistant>

    return num_tokens

def print_output(tokens, filepath, model, json_output=False):
    """Function to print the output in the desired format."""
    if json_output:
        print(json.dumps({"tokens": tokens}))
    else:
        print(f"The text file '{filepath}' contains {tokens} tokens for the model '{model}'.")

def enhanced_argparse_setup():
    """Setup argparse for enhanced token calculation."""
    parser = argparse.ArgumentParser(description='Calculate the number of tokens in a given text file for a specific model.')
    parser.add_argument('filepath', type=str, help='Path to the text file.')
    parser.add_argument('--model', type=str, default="gpt-3.5-turbo-0613",
                        help='The model to calculate tokens for. Supported models are: ' + ', '.join(model_behavior.keys()) + '. Default is gpt-3.5-turbo-0613.')
    parser.add_argument('--json-output', action='store_true', help='Output the token count in JSON format.')
    return parser

def calculate_tokens(data, model="gpt-3.5-turbo-0613", json_output=False):
    """
    Calculate the number of tokens for given data and model.

    Parameters:
    - data (list or str): List of messages or plain text. Each message is a dictionary with "role" and "content" keys.
    - model (str): Model name to calculate tokens for.
    - json_output (bool): Whether to return the result in JSON format.

    Returns:
    - int or str: Token count (as integer) or JSON formatted string based on json_output flag.
    """
    # Handle plain text input
    if isinstance(data, str):
        data = [{"role": "system", "content": data}]

    tokens = enhanced_num_tokens_from_messages(data, model, json_output)
    if json_output:
        return json.dumps({"tokens": tokens})
    return tokens

def main():
    """Main function to calculate and output tokens."""
    parser = enhanced_argparse_setup()
    args = parser.parse_args()

    # Read the content of the file
    with open(args.filepath, 'r') as f:
        content = f.read()

    try:
        # Try parsing the content as JSON
        messages = json.loads(content)
    except json.JSONDecodeError:
        # If parsing as JSON fails, treat content as a single message
        messages = [{"role": "system", "content": content}]

    tokens = enhanced_num_tokens_from_messages(messages, args.model, args.json_output)
    print_output(tokens, args.filepath, args.model, args.json_output)

if __name__ == "__main__":
    main()
