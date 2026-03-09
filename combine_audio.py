#!/usr/bin/env python3
"""
Combine all conversation audio files into one with random pauses between clips.
"""

import os
import glob
import soundfile as sf
import numpy as np
import random
from datetime import datetime
import argparse

PAUSE_MIN = 0.5  # Minimum pause seconds
PAUSE_MAX = 2.0  # Maximum pause seconds

def combine_audio(audio_folder):
    # Find all wav files and sort
    files = []
    for ext in ["*.wav", "*.x-wav", "*.WAV"]:
        files.extend(glob.glob(os.path.join(audio_folder, ext)))
    files = sorted(files)
    
    if not files:
        print(f"No audio files found in {audio_folder}")
        return
    
    print(f"Found {len(files)} audio files")
    
    # Read and concatenate
    audio_data = []
    sample_rate = None
    
    for f in files:
        print(f"  - {os.path.basename(f)}")
        data, sr = sf.read(f)
        audio_data.append(data)
        sample_rate = sr
    
    # Add random pause between each clip
    combined_parts = []
    for i, audio in enumerate(audio_data):
        combined_parts.append(audio)
        if i < len(audio_data) - 1:  # Don't add pause after last clip
            pause_seconds = random.uniform(PAUSE_MIN, PAUSE_MAX)
            pause_samples = int(sr * pause_seconds)
            pause = np.zeros(pause_samples)
            combined_parts.append(pause)
            print(f"    + pause: {pause_seconds:.1f}s")
    
    combined = np.concatenate(combined_parts)
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = "output/combined"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"conversation_{timestamp}.wav")
    sf.write(output_file, combined, sample_rate)
    print(f"\nSaved: {output_file}")
    print(f"Duration: {len(combined)/sample_rate:.1f}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", nargs="?", default="output/audio", help="Folder with audio files")
    args = parser.parse_args()
    combine_audio(args.folder)
