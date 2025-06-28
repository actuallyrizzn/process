import argparse
import os
import assemblyai as aai
from dotenv import load_dotenv

# Load .env file and get the API key
load_dotenv()
aai.settings.api_key = os.getenv('ASSEMBLYAI_KEY')

def transcribe(file_path, speaker_labels=True):
    # Configuration for transcription with diarization
    config = aai.TranscriptionConfig(speaker_labels=speaker_labels)

    # Create a transcriber object
    transcriber = aai.Transcriber()

    # Transcribe the audio file
    transcript = transcriber.transcribe(file_path, config=config)

    # Wait for the transcription to complete
    while transcript.status != 'completed':
        # Implement a suitable wait mechanism, e.g., sleep
        pass

    return transcript

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Transcribe audio files using AssemblyAI.")
    parser.add_argument('file_path', help="Path to the audio file for transcription")
    parser.add_argument('--output', choices=['console', 'file', 'both'], default='console', 
                        help="Output transcription to console, file, or both")
    args = parser.parse_args()

    # Transcribe the audio file
    transcript = transcribe(args.file_path)

    # Output handling
    if args.output in ['console', 'both']:
        for utterance in transcript.utterances:
            print(f"Speaker {utterance.speaker}: {utterance.text}")

    if args.output in ['file', 'both']:
        with open('transcription.txt', 'w') as file:
            for utterance in transcript.utterances:
                file.write(f"Speaker {utterance.speaker}: {utterance.text}\n")

if __name__ == '__main__':
    main()
