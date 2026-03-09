# Adding New Voices Guide

## Overview

Voice cloning uses reference audio to create a unique voice for each character. The TTS learns voice characteristics from audio clips.

## Recommended: Using the Web UI

### Method 1: Combine Voice Clips (Easiest)

1. Put multiple voice clips in `voices/UNREFINED/CharacterName/`
   ```
   voices/UNREFINED/Finn/
   ├── Finn_clip1.wav
   ├── Finn_clip2.wav
   └── Finn_clip3.wav
   ```

2. Open Web UI: `python webui.py`

3. Go to **Combine Voices** tab

4. Select the folder and enter character name

5. Click **Combine Voices**

This creates `voices/Finn.wav` from all clips.

### Method 2: Single Voice File

1. Place a `.wav` file in `voices/` folder:
   ```
   voices/
   ├── Finn.wav
   └── Jake.wav
   ```

2. (Optional) Create transcript file:
   ```
   voices/
   ├── Finn.wav
   └── Finn.txt   # Contains what Finn says in the audio
   ```

3. In Web UI Characters tab, select the voice file

4. Click **Transcribe Voice** to auto-generate transcript

---

## Audio File Requirements

- **Format**: WAV (recommended) or MP3
- **Duration**: 10-30 seconds optimal
- **Quality**: Clear speech, minimal background noise
- **Content**: Single speaker, no music

### Recording Tips
- Use voice recorder on phone or computer
- Speak clearly with consistent volume
- Avoid background music or noise
- 5-15 seconds of continuous speech works best
- Include varied emotions for better results

---

## Using Voices in Characters

1. Go to **Characters** tab in Web UI
2. Select voice file from dropdown
3. Add emotion/style notes (e.g., "young, heroic, energetic")
4. Save character

The voice will be used when generating conversations.

---

## Troubleshooting

### Voice not loading
- Check file exists in `voices/` folder
- Check filename matches (case sensitive)
- Ensure .wav file is valid audio

### Voice sounds wrong
- Try different reference audio
- Longer clips work better
- Ensure clear audio without noise
- Combine multiple clips for better results

### Transcript issues
- Click "Transcribe Voice" button in Characters tab
- Or manually create .txt file with transcript

---

## Command Line Tools

### Combine Audio Files
```bash
python combine_audio.py voices/UNREFINED/Finn
```

### Transcribe Voices
```bash
python transcribe_voices.py voices/
```

---

## Best Practices

- ✅ Clear audio with no background noise
- ✅ Single speaker throughout
- ✅ 10-20 seconds length
- ✅ Natural speech
- ✅ Same language as intended use

- ❌ Music in background
- ❌ Multiple speakers
- ❌ Very short (< 3 seconds)
- ❌ Very long (> 30 seconds)
- ❌ Poor audio quality
