
# Process

This repository hosts a set of scripts designed to automate the process of downloading a YouTube video, extracting its audio, transcribing the audio, and summarizing the transcribed text. It's perfect for quickly generating summaries of long video content.

Repo URL: [http://github.com/actuallyrizzn/process](http://github.com/actuallyrizzn/process)

## Scripts and Their Functions

The main workflow is controlled by a bash script `process.sh`, which in turn calls several Python scripts and a bash script to complete specific tasks:

### 1. `process`
This is the master script that coordinates the entire process. It takes a YouTube video URL as input and outputs a summarized text of the video content.

Usage: ./process <youtube url>

### 2. `ytget.py`
This Python script downloads a YouTube video. It uses the `pytube` library to do this.

### 3. `v2a.sh`
This bash script uses `ffmpeg` to convert the downloaded video file to an audio file. If the audio file is larger than 25MB, it is split into smaller chunks using `ffmpeg`.

### 4. `transcribe.py`
This Python script uses the OpenAI API's Audio.transcribe method to transcribe the audio file. It assumes that you have an OpenAI API key stored in a file named `openai.api`.

### 5. `chnk.py`
This Python script chunks large text files into smaller pieces. This is useful when the transcribed text is too large to be sent to an API in one go.

### 6. `summarize.py`
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
