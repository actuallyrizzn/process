#!/usr/bin/python3

import os
import sys
import argparse
import nltk
import logging

# Function to split text into tokens
def tokenize(text):
    return text.split()

# Function to chunk text into smaller pieces
def chunk_text(file_name, max_tokens=4096):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, file_name)

    try:
        logging.info(f"Opening the file: {file_path}")
        with open(file_path, 'r') as file:
            text = file.read()
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Failed to open the file. Error: {str(e)}")
        sys.exit(1)

    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = []

    logging.info("Starting text chunking...")
    try:
        for sentence in sentences:
            sentence_tokens = tokenize(sentence)
            if len(sentence_tokens) > max_tokens:
                for i in range(0, len(sentence_tokens), max_tokens):
                    end_index = min(i + max_tokens, len(sentence_tokens))
                    chunk = sentence_tokens[i:end_index]
                    chunks.append(' '.join(chunk))
            else:
                if len(current_chunk) + len(sentence_tokens) > max_tokens:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = sentence_tokens
                else:
                    current_chunk.extend(sentence_tokens)
    except Exception as e:
        logging.error(f"Failed during text chunking. Error: {str(e)}")
        sys.exit(1)

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    logging.info(f"Text chunking completed. {len(chunks)} chunks created.")
    return chunks

# Function to write chunks to files
def write_chunks_to_files(chunks, output_dir):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    except PermissionError as e:
        logging.error(f"Failed to create output directory. Error: {str(e)}")
        sys.exit(1)

    logging.info(f"Writing chunks to the output directory: {output_dir}")
    try:
        for i, chunk in enumerate(chunks):
            with open(f"{output_dir}/chunk_{i+1}.txt", 'w') as file:
                file.write(chunk)
    except PermissionError as e:
        logging.error(f"Failed to write chunk to file. Error: {str(e)}")
        sys.exit(1)

# Using argparse for command line argument handling
parser = argparse.ArgumentParser(description='This script splits a text file into chunks of a specified size, preserving sentence boundaries where possible.')
parser.add_argument('file_name', help='The name of the file to chunk.')
parser.add_argument('--max_tokens', type=int, default=4096, help='The maximum number of tokens per chunk. Default is 4096.')
parser.add_argument('--keep_file', action='store_true', help='Keep the original file after chunking.')
parser.add_argument('--log', help='Log file to write the progress updates. If not provided, updates are printed to the console.')

args = parser.parse_args()

if args.log:
    logging.basicConfig(filename=args.log, level=logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

file_name = args.file_name
max_tokens = args.max_tokens
keep_file = args.keep_file

script_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = script_dir

logging.info(f"Starting to process the file: {file_name}")
chunks = chunk_text(file_name, max_tokens)

if len(chunks) > 1:
    if not keep_file:
        try:
            logging.info(f"Deleting the original file: {file_name}")
            os.remove(os.path.join(script_dir, file_name))
        except PermissionError as e:
            logging.error(f"Failed to delete the original file. Error: {str(e)}")
            sys.exit(1)
    write_chunks_to_files(chunks, output_dir)
else:
    logging.info("No changes needed.")
