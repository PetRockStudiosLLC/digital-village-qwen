# Configuration Guide

## Main Configuration File: shrek-donkey-qwen.py

```python
# ============================================================
# CONFIGURATION SECTION - Edit these values!
# ============================================================

# LM Studio API Settings
LM_STUDIO_HOST = "http://192.168.56.1:6842"

# Voice mapping (character name -> preset speaker)
SPEAKER_FOR_CHARACTER = {
    "Shrek": "ryan",
    "Donkey": "ryan",
}

# Emotions for each character (used with voice cloning + instruct)
EMOTION_FOR_CHARACTER = {
    "Shrek": "grumpy, angry, deep voice, sarcastic",
    "Donkey": "happy, excited, energetic, enthusiastic",
}

# Audio Settings
SAVE_AUDIO = True              # Save audio files?
AUDIO_FOLDER = "output/audio"  # Where to save audio

# Conversation Settings
STARTER_MESSAGE = "Hey Donkey, what are you doing here?"
NUM_TURNS = 5                 # How many exchanges
```

---

## Voice Modes

The TTS supports three modes:

### 1. Voice Cloning (Default)
Uses your reference audio files to clone voices.

```python
tts = get_qwen_tts(
    voice_mode="clone",      # Voice cloning from audio
    voice_folder="voices",  # Folder with .wav files
    model_folder="models",  # Folder with TTS models
)
```

**Requirements:**
- Reference audio in `voices/{Name}.wav`
- Base model in `models/Qwen3-TTS-12Hz-0.6B-Base/`

### 2. Preset Speakers
Uses built-in speaker voices.

```python
tts = get_qwen_tts(
    voice_mode="preset",     # Built-in voices
    speaker="ryan",         # Choose speaker
    model_folder="models",
)
```

**Available Speakers:** aiden, dylan, eric, ono_anna, ryan, serena, sohee, uncle_fu, vivian

### 3. VoiceDesign (Emotion from Text)
Creates voices from text descriptions.

```python
tts = get_qwen_tts(
    voice_mode="design",    # Text-to-voice
    model_folder="models",
)
tts.instruct = "angry, deep voice"  # Describe the voice
```

---

## Emotion Control

The `instruct` parameter controls voice emotion/style.

### How It Works
- Works with both voice cloning and preset voices
- Add descriptive words: "angry", "happy", "sad", "excited"
- Voice characteristics: "deep", "high", "fast", "slow"

### Examples

```python
# Grumpy Shrek
EMOTION_FOR_CHARACTER = {
    "Shrek": "grumpy, angry, sarcastic, deep voice",
}

# Enthusiastic Donkey  
EMOTION_FOR_CHARACTER = {
    "Donkey": "happy, excited, energetic, fast speech",
}

# Sad character
EMOTION_FOR_CHARACTER = {
    "Character": "sad, slow, soft voice, crying",
}

# villain
EMOTION_FOR_CHARACTER = {
    "Villain": "evil, menacing, dark, slow",
}
```

---

## TTS Module API

### Basic Usage

```python
from digital_village.qwen_tts import get_qwen_tts

# Create TTS instance
tts = get_qwen_tts(
    voice_mode="clone",
    voice_folder="voices",
    model_folder="models",
)

# Load voice
tts.load_voice("Shrek", "voices/Shrek.wav")

# Speak
tts.speak("Hello world!", wait=True)

# Speak with emotion
tts.instruct = "angry"
tts.speak("Get out of my swamp!")

# Save to file
tts.speak("Text", save_path="output/audio/001_Shrek.wav")
```

### Methods

| Method | Description |
|--------|-------------|
| `speak(text, wait=True)` | Speak text |
| `speak_async(text)` | Speak in background |
| `speak_to_file(text, path)` | Save to file |
| `load_voice(name, path)` | Load voice reference |
| `set_speaker(name)` | Set preset speaker |
| `set_emotion(emotion)` | Set emotion |
| `set_language(lang)` | Set language |

---

## Qwen3-TTS Model Details

### Models Available

| Model | Use Case | Size |
|-------|----------|------|
| Qwen3-TTS-12Hz-0.6B-Base | Voice cloning | ~1.2GB |
| Qwen3-TTS-12Hz-0.6B-CustomVoice | Preset speakers + emotions | ~1.2GB |
| Qwen3-TTS-12Hz-0.6B-VoiceDesign | Text-to-voice design | ~1.2GB |

### Performance

- **RTF (Real-Time Factor)**: ~2.5x on RTX 3090
- Means: 10 seconds of audio generates in ~4 seconds

### Streaming

True streaming requires:
1. PyTorch 2.5.1+ with CUDA
2. `faster-qwen3-tts` package

Current implementation generates full audio then plays.

---

## LM Studio Configuration

### Finding Your API URL

1. Open LM Studio
2. Click the "AI Chat" tab (or similar)
3. Look for "API Server" or "Local Server" 
4. Note the URL (usually http://localhost:1234 or http://192.168.56.1:6842)

### Testing Connection

```python
import requests

# Test LM Studio
r = requests.get("http://192.168.56.1:6842/v1/models")
print(r.status_code)  # Should be 200
print(r.json())       # Should show loaded models
```

---

## Advanced: Creating New Conversations

### New Character File

1. Copy `shrek-donkey-qwen.py` to `my_conversation.py`

2. Modify configuration:
```python
# Characters
EMOTION_FOR_CHARACTER = {
    "Character1": "angry, loud",
    "Character2": "soft, quiet",
}

# Starter message
STARTER_MESSAGE = "Hello!"
NUM_TURNS = 10

# LM Studio host
LM_STUDIO_HOST = "http://192.168.56.1:6842"
```

3. Modify character definitions:
```python
shrek = village.add_villager(
    name="Shrek",
    system_prompt="""You are Shrek from Shrek...""",
    description="A grumpy ogre",
)
```

4. Add more characters:
```python
puss = village.add_villager(
    name="Puss",
    system_prompt="""You are Puss in Boots...""",
    description="A suave cat",
)
```

5. Update participants list:
```python
participants = ["Shrek", "Donkey", "Puss"]
```

---

## Environment Variables

Optional settings:

```bash
# HuggingFace cache
export HF_HOME="D:/models/huggingface"

# Disable warnings
export TRANSFORMERS_NO_ADVISORY_WARNINGS=1
export TOKENIZERS_PARALLELISM=false
```
