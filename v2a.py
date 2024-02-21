#!/usr/bin/python3

import os
import subprocess
import math
import argparse
import logging

# Set up the command-line argument parser
parser = argparse.ArgumentParser(description='Convert a video file to an MP3 file and split it into chunks if necessary.')
parser.add_argument('-i', '--input', default='video.mp4', help='The input file to convert.')
parser.add_argument('-o', '--output', default='output.mp3', help='The output file name.')
parser.add_argument('-s', '--size', type=int, default=25, help='The maximum chunk size in MB.')
parser.add_argument('-r', '--remove', action='store_true', help='Remove the original video file after conversion.')
parser.add_argument('-l', '--log', help='The name of the log file.')
args = parser.parse_args()

# Set up logging
if args.log:
    logging.basicConfig(filename=args.log, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Define a function to print messages and optionally log them
def print_and_log(message, level='info'):
    print(message)
    if args.log:
        if level == 'info':
            logging.info(message)
        elif level == 'error':
            logging.error(message)

# Define the input and output files
input_file = args.input
output_file = args.output
chunk_output = 'split'
overlap = 30
chunk_size = args.size * 1024  # Convert size from MB to KB
target_size = 26214400  # Target size in bytes

try:
    print_and_log(f"Estimating size of {input_file}...")

    # Use ffmpeg to convert a 1 minute sample of the video to an MP3 audio file
    subprocess.check_call(['ffmpeg', '-i', input_file, '-c:a', 'libmp3lame', '-b:a', '32k', '-t', '60', 'sample.mp3'])

    # Get the size of the sample file in bytes
    sample_size = os.path.getsize('sample.mp3')

    # Get the duration of the video file in seconds
    duration = float(subprocess.check_output(['ffprobe', '-i', input_file, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0']))

    # Estimate the size of the full audio file based on the sample
    estimated_size = (sample_size / 60) * duration
    os.remove('sample.mp3')

    print_and_log(f"Estimated size of the output file: {estimated_size} bytes")

    # Decide what to do based on the estimated size
    if 0.9 * target_size <= estimated_size <= 1.1 * target_size:
        print_and_log("Estimated size is within 10% of the target size. Adjusting compression level...")
        # Adjust the bitrate based on the estimated size and reconvert the file
        # This would require more complex logic that's beyond the scope of this example
    elif estimated_size < 2 * target_size:
        print_and_log("Estimated size is less than double the target size. Splitting the file into two chunks...")
        chunk_duration = duration / 2
    else:
        print_and_log("Estimated size is more than double the target size. Splitting the file into multiple chunks...")
        chunk_duration = (chunk_size * 8) / 32  # duration in seconds, we divide by the bitrate (32 kbit/s)

    print_and_log(f"Preparing to convert {input_file} to MP3 format...")

    # Use ffmpeg to convert the video file to an MP3 audio file
    subprocess.check_call(['ffmpeg', '-i', input_file, '-c:a', 'libmp3lame', '-b:a', '32k', output_file])

    print_and_log(f"Conversion complete! {output_file} has been created.")

except subprocess.CalledProcessError as err:
    print_and_log(f"ffmpeg command failed with error: {err}", 'error')
    exit(1)

# Check if the output file exists
if not os.path.isfile(output_file):
    print_and_log(f"Error: {output_file} does not exist. Please check if the conversion process was successful.", 'error')
    exit(1)

# Get the size of the file in bytes
filesize = os.path.getsize(output_file)

# Convert the file size from bytes to megabytes
filesizeMB = filesize / (1024 * 1024)

print_and_log(f"Size of the output file: {filesizeMB:.2f} MB")

# If the file is larger than the specified chunk size, split it into smaller chunks
if filesize > target_size:
    print_and_log("The output file is too large. Breaking it down into smaller chunks...")

    # Calculate the number of chunks
    n = math.ceil(duration / chunk_duration)

    # Loop through each chunk
    for i in range(n):
        # Calculate the start time of the chunk
        start = i * chunk_duration - overlap if i * chunk_duration - overlap > 0 else 0

        try:
            # Use ffmpeg to copy a chunk of the audio file to a new file
            subprocess.check_call(['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-i', output_file, '-c', 'copy', '-ss', str(start), '-t', str(chunk_duration), f"{chunk_output}_{i}.mp3"])
            print_and_log(f"Chunk {i} has been created.")

        except subprocess.CalledProcessError as err:
            print_and_log(f"ffmpeg command failed with error: {err}", 'error')
            exit(1)

else:
    print_and_log("The output file is already compressed enough. No further action is required.")

# Remove the original video file if specified by the user
if args.remove:
    try:
        os.remove(input_file)
        print_and_log(f"Original video file {input_file} has been removed.")
    except OSError as err:
        print_and_log(f"Error removing original video file {input_file}: {err}", 'error')

