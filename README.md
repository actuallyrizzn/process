
# Process

This repository hosts a set of scripts designed to automate the process of downloading a YouTube video, extracting its audio, transcribing the audio, and summarizing the transcribed text. It's perfect for quickly generating summaries of long video content.

Repo URL: [http://github.com/actuallyrizzn/process](http://github.com/actuallyrizzn/process)

## Scripts and Their Functions

The main workflow is controlled by a bash script `process.sh`, which in turn calls several Python scripts and a bash script to complete specific tasks:

### 1. `transcribe.py`
This Python script uses the OpenAI API's Audio.transcribe method to transcribe the audio file. It assumes that you have an OpenAI API key stored in a file named `openai.api`.

### 2. `summarize.py`
This Python script uses the OpenAI API's Completion.create method to generate a summary of the transcribed text. It assumes that you have an OpenAI API key stored in a file named `openai.api`.

## Installation

1. Clone the repository:
```
git clone http://github.com/actuallyrizzn/process.git
```
2. Navigate to the cloned directory:
```
cd process
```
3. Make sure you have the necessary dependencies installed. You can install the Python dependencies using pip:
```
pip install pytube openai
```
4. Install `ffmpeg` on your system. The installation process varies depending on your operating system.

## Usage

Run the `process.sh` script with a YouTube video URL:

```
./process.sh -u <YouTube Video URL>
```

You can also specify a destination directory for the downloaded video:

```
./process.sh -u <YouTube Video URL> -d <Destination Directory>
```

## Dependencies

- bash
- Python 3
- pytube
- openai
- ffmpeg

---

Please replace `<YouTube Video URL>` and `<Destination Directory>` with the actual URL and directory when you use the script.
