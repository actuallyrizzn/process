#!/usr/bin/python3
import argparse
from pytube import YouTube

def progress_function(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining

    percentage_of_completion = bytes_downloaded / total_size * 100
    print(f"\r{percentage_of_completion:.2f}% downloaded", end="")

def complete_function(stream, file_path):
    print("\nDownload completed and saved to:", file_path)

def download_video(url, output_filename=None, output_path='.'):
    yt = YouTube(url)
    yt.register_on_progress_callback(progress_function)
    yt.register_on_complete_callback(complete_function)

    # If no output filename is given, use the video's title and add .mp4 extension
    if not output_filename:
        output_filename = yt.title + ".mp4"

    # Select the lowest resolution MP4 stream
    video = sorted(
        [stream for stream in yt.streams.filter(file_extension='mp4', progressive=True)],
        key=lambda x: x.resolution if x.resolution else "9999"
    )[0]

    video.download(output_path, filename=output_filename)

def main():
    parser = argparse.ArgumentParser(description='Download YouTube video with specified output name.')
    parser.add_argument('url', help='The URL of the YouTube video.')
    parser.add_argument('-f', '--file', dest='output_filename', default=None, help='The desired output filename without extension. Defaults to the YouTube video title if not specified.')
    parser.add_argument('--output_path', default='.', help='The output path for the downloaded video.')
    args = parser.parse_args()

    download_video(args.url, args.output_filename, args.output_path)

if __name__ == '__main__':
    main()
