# Digital Village - Shrek & Donkey Edition

A conversational AI demo using Qwen3-TTS for voice synthesis and LM Studio for chat. Characters speak with custom voices and emotions.

## Quick Start

```bash
# Activate conda environment
conda activate HeartMula

# Run the conversation
python shrek-donkey-qwen.py
```

## Requirements

1. **LM Studio** running with:
   - A model loaded (e.g., qwen/qwen3.5-9b)
   - API server enabled (default: http://192.168.56.1:6842)

2. **Conda Environment**: HeartMula with PyTorch + CUDA

3. **Models** in `models/` folder:
   - `Qwen3-TTS-12Hz-0.6B-Base/` (for voice cloning)
   - `Qwen3-TTS-12Hz-0.6B-CustomVoice/` (for preset voices)

4. **Voice files** in `voices/` folder:
   - `Shrek.wav`
   - `Donkey.wav`

## Features

- 🎭 Custom voice cloning from reference audio
- 😊 Emotion control via `instruct` parameter
- 💾 Auto-saves audio to `output/audio/`
- 🎧 Combines clips with random pauses
- 🚀 GPU-accelerated TTS (~2.5x realtime)

## Project Structure

```
ChatBot/
├── digital_village/          # Core package
│   ├── qwen_tts.py        # Qwen3-TTS wrapper
│   ├── village.py          # Conversation manager
│   └── villager.py        # Character agent
├── models/                  # TTS models (download separately)
│   ├── Qwen3-TTS-12Hz-0.6B-Base/
│   └── Qwen3-TTS-12Hz-0.6B-CustomVoice/
├── voices/                  # Voice reference audio
│   ├── Shrek.wav
│   └── Donkey.wav
├── output/                  # Generated audio
│   └── audio/
├── shrek-donkey-qwen.py   # Main demo script
├── combine_audio.py        # Audio post-processing
└── docs/                  # Documentation
```

## Configuration

Edit `shrek-donkey-qwen.py`:

```python
# LM Studio API
LM_STUDIO_HOST = "http://192.168.56.1:6842"

# Emotions for characters
EMOTION_FOR_CHARACTER = {
    "Shrek": "grumpy, angry, deep voice, sarcastic",
    "Donkey": "happy, excited, energetic, enthusiastic",
}

# Save audio?
SAVE_AUDIO = True

# Number of conversation turns
NUM_TURNS = 5
```

## Running

```bash
conda activate HeartMula
python shrek-donkey-qwen.py
```

Press Ctrl+C to stop. Audio saves to `output/audio/`.

## Combining Audio

After running, combine clips:

```bash
python combine_audio.py
```

Output: `output/conversation_YYYY-MM-DD_HH-MM-SS.wav`

## Troubleshooting

### No audio playing
- Install pygame: `pip install pygame`

### Model not found
- Ensure `models/` folder has both model folders
- Or let it download automatically (requires internet)

### LM Studio connection error
- Check API URL matches LM Studio settings
- Ensure LM Studio API server is enabled
