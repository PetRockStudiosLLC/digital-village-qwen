"""Auto-transcribe voice files using Whisper."""

import os
import argparse

import whisper


def transcribe_audio(audio_path: str, model_name: str = "base", output_path: str = None) -> str:
    """Transcribe an audio file using Whisper."""
    print(f"Loading Whisper {model_name} model...")
    model = whisper.load_model(model_name)
    
    print(f"Transcribing {audio_path}...")
    result = model.transcribe(audio_path)
    
    transcript = result["text"].strip()
    
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"Saved transcript to {output_path}")
    else:
        txt_path = audio_path.replace(".wav", ".txt").replace(".mp3", ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"Saved transcript to {txt_path}")
    
    return transcript


def transcribe_folder(folder_path: str, model_name: str = "base"):
    """Transcribe all audio files in a folder."""
    print(f"Loading Whisper {model_name} model...")
    model = whisper.load_model(model_name)
    
    audio_extensions = (".wav", ".mp3", ".m4a", ".flac", ".ogg")
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(audio_extensions):
            audio_path = os.path.join(folder_path, filename)
            txt_path = os.path.join(folder_path, filename.rsplit(".", 1)[0] + ".txt")
            
            if os.path.exists(txt_path):
                print(f"Skipping {filename} (transcript already exists)")
                continue
            
            print(f"\nTranscribing {filename}...")
            result = model.transcribe(audio_path)
            transcript = result["text"].strip()
            
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"Saved: {txt_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe voice files with Whisper")
    parser.add_argument("input", help="Audio file or folder")
    parser.add_argument("-m", "--model", default="base", choices=[
        "tiny", "base", "small", "medium", "large-v3", "turbo"
    ], help="Whisper model size (default: base)")
    parser.add_argument("-o", "--output", help="Output transcript file")
    
    args = parser.parse_args()
    
    if os.path.isdir(args.input):
        transcribe_folder(args.input, args.model)
    else:
        transcribe_audio(args.input, args.model, args.output)
