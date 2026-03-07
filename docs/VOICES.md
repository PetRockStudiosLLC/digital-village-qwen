# Adding New Voices Guide

## Overview

Voice cloning uses reference audio to create a unique voice for each character. The TTS learns voice characteristics from 3-15 second clips.

## Requirements

### Audio File Format
- **Format**: WAV (recommended) or MP3
- **Duration**: 3-15 seconds optimal
- **Quality**: Clear speech, minimal background noise
- **Content**: Single speaker, no music

### File Naming
```
voices/
├── Shrek.wav      # Reference for Shrek
├── Donkey.wav     # Reference for Donkey  
└── NEW_CHAR.wav   # Reference for NEW_CHAR
```

## Step-by-Step

### 1. Prepare Voice Audio

**Recording Tips:**
- Use voice recorder on phone or computer
- Speak clearly with consistent volume
- Avoid background music or noise
- 5-10 seconds of continuous speech works best
- Include varied emotions for better results

**Converting Audio:**
```bash
# Using ffmpeg (if needed)
ffmpeg -i input.mp3 -ar 24000 -ac 1 output.wav
```

### 2. Add to voices/ Folder

Put your WAV file in the `voices/` folder:
```
voices/
├── Shrek.wav
├── Donkey.wav
└── MyCharacter.wav   # Add new voice here
```

### 3. Update Script

Edit `shrek-donkey-qwen.py`:

**Option A: Load voice by filename (automatic)**
```python
# If file is "voices/MyCharacter.wav"
tts.load_voice("MyCharacter")  # Automatically finds voices/MyCharacter.wav
```

**Option B: Specify full path**
```python
tts.load_voice("MyCharacter", "path/to/voice.wav")
```

### 4. Add to Configuration

```python
# Add character emotion
EMOTION_FOR_CHARACTER = {
    "Shrek": "grumpy, angry, deep voice",
    "Donkey": "happy, excited, energetic",
    "MyCharacter": "sneaky, mysterious, slow",  # Add your character
}

# Add to conversation participants
participants = ["Shrek", "Donkey", "MyCharacter"]
```

### 5. Run

```bash
python shrek-donkey-qwen.py
```

## Voice Quality Tips

### Best Results
- ✅ Clear audio with no background noise
- ✅ Single speaker throughout
- ✅ 5-10 seconds length
- ✅ Natural speech, not read from script
- ✅ Same language as intended use

### Avoid
- ❌ Music in background
- ❌ Multiple speakers
- ❌ Very short (< 2 seconds)
- ❌ Very long (> 20 seconds)
- ❌ Poor audio quality
- ❌ Reverb/echo effects

## Preset Speakers (No Cloning)

If you don't have voice clips, use built-in speakers:

```python
# Edit shrek-donkey-qwen.py
tts = get_qwen_tts(
    voice_mode="preset",  # Use built-in voices
    speaker="eric",       # Choose from list below
)
```

**Available Speakers:**
- aiden
- dylan  
- eric
- ono_anna
- ryan
- serena
- sohee
- uncle_fu
- vivian

## Voice Design (Text Description)

Create voices from text descriptions:

```python
tts = get_qwen_tts(
    voice_mode="design",
)

# Describe the voice
tts.instruct = "angry deep voice with british accent"
tts.speak("I am very angry!")
```

## Troubleshooting

### Voice not loading
```
[Qwen3-TTS] Voice file not found: voices/MyChar.wav
```
- Check file exists in `voices/` folder
- Check filename matches (case sensitive)

### Voice sounds wrong
- Try different reference audio
- Longer clips work better
- Ensure clear audio without noise

### "Model not support" error
- Ensure `models/Qwen3-TTS-12Hz-0.6B-Base/` folder exists
- Or let script download automatically

## Examples

### Example 1: Adding Puss in Boots

1. Record voice: `voices/puss.wav`
2. Add to script:
```python
tts.load_voice("puss")
EMOTION_FOR_CHARACTER["puss"] = "smooth, charming, spanish accent"
```
3. Add to conversation

### Example 2: Using Celebrity Voice

1. Find short clip of celebrity speaking
2. Convert to WAV
3. Save as `voices/celebrity.wav`
4. Load and use

### Example 3: Creating Monster Voice

1. Record voice
2. Add heavy emotion:
```python
tts.instruct = "monster, scary, deep, growling"
tts.speak("I am the monster!")
```

## Batch Processing Multiple Voices

```python
# Load all voices in folder
import os
for filename in os.listdir("voices"):
    if filename.endswith(".wav"):
        name = filename.replace(".wav", "")
        tts.load_voice(name)
        print(f"Loaded: {name}")
```
