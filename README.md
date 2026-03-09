# AI Character Chat Generator

A tool for creating multi-character AI conversations with voice synthesis using LM Studio and Qwen TTS.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Web UI
python webui.py
```

Then open http://localhost:7860 in your browser.

---

## Prerequisites

1. **LM Studio** - Download from https://lmstudio.ai
   - Load a model (recommended: Qwen2.5 or similar)
   - Enable API server (default: http://192.168.56.1:6842)

2. **Python 3.10+** with dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Web UI Overview

The Web UI has 4 tabs:

### 1. Characters Tab
Create and manage your characters.

**Creating a Character:**
1. Enter a character name (e.g., "Finn")
2. Write a system prompt describing the character
3. Select a voice file (see Voice Setup below)
4. Add emotion/style notes for TTS
5. Set a default status effect
6. Click "Save Character"

For help writing scene prompts, see [Scene Prompt Guide](docs/SCENE_PROMPTS.md).

**Creating a Character:**
1. Enter a character name (e.g., "Finn")
2. Write a system prompt describing the character
3. Select a voice file (see Voice Setup below)
4. Add emotion/style notes for TTS
5. Set a default status effect
6. Click "Save Character"

**Editing Characters:**
1. Select character(s) from "Select Character to Edit"
2. Click "Load Character" to populate the form
3. Make changes and save again

**Deleting Characters:**
1. Select character(s) from "Select Characters to Delete"
2. Click "Delete Selected"

### 2. Combine Voices Tab
Combine multiple voice clips into a single voice file for TTS cloning.

**To use:**
1. Select a folder from `voices/UNREFINED/` or enter a custom path
2. Enter a character name for the output file
3. Click "Combine Voices"

This creates a single `voices/CharacterName.wav` file from all audio clips in the folder.

### 3. Multi Chat Tab
Generate conversations between characters.

**Options:**
- **Characters** - Select 2+ characters
- **Status Effects Override** - Override character status (format: `Character:Status` per line)
- **Scene Prompt** - Set the context/scene
- **Number of Turns** - How many exchanges

**Buttons:**
- **Generate All** - Creates text + audio in one go
- **Generate Text Only** - Just generates conversation text (editable)
- **Generate Audio** - Converts edited text to audio

### 4. Chat Tab
Talk to characters in real-time.

1. Select character(s)
2. Enter your message
3. Click Send
4. Characters respond with voice audio

---

## Voice Setup

### Option 1: Combine Voice Clips
1. Put voice clips in `voices/UNREFINED/CharacterName/`
2. Go to Combine Voices tab
3. Select the folder and enter character name
4. Click Combine Voices

### Option 2: Manual
1. Place a `.wav` file in `voices/` folder (e.g., `voices/Finn.wav`)
2. Create a transcript file `voices/Finn.txt` with what the voice says

### Transcribing Voices
If you have a voice file but no transcript:
1. Select the voice file in Characters tab
2. Click "Transcribe Voice"
3. Transcript is auto-generated and saved

---

## Status Effects

Each character can have a status effect that changes their dialogue tone:

| Status | Effect |
|--------|--------|
| Normal | Default behavior |
| Drunk | Slurred, unsteady speech |
| Caffeinated | Fast, energetic, jumpy |
| Tired | Slow, long pauses |
| Angry | Aggressive, sharp |
| Happy | Cheerful, excited |
| Sad | Morose, downcast |
| Confused | Hesitant, questioning |
| Excited | Very enthusiastic |
| Scared | Nervous, shaky |

**To use:**
- Set default in Characters tab dropdown
- Override in Multi Chat using format: `Finn:Drunk`

---

## Dialogue Rules

The system uses these rules for optimal TTS output:

1. **No Metadata** - Only raw dialogue, no descriptions or stage directions
2. **TTS Pronunciation** - Numbers as words, expanded abbreviations
3. **Short-Burst** - Max 60 words per response for punchy dialogue
4. **Punctuation for Prosody** - Use `...` for pauses, `!!!` for emphasis

---

## Settings

Configure in Settings tab:
- **LM Studio Host** - API endpoint (default: http://192.168.56.1:6842)
- **Model Name** - Model to use (default: qwen/qwen3.5-9b)
- **Output Folder** - Where audio is saved

---

## Folder Structure

```
ChatBot/
├── webui.py              # Main Web UI
├── transcribe_voices.py   # Voice transcription tool
├── combine_audio.py      # Audio combiner script
├── characters/           # Saved character JSON files
├── voices/               # Voice reference files
│   └── UNREFINED/       # Raw voice clips for combining
├── output/               # Generated audio
│   └── combined/         # Combined conversation audio
└── data/                 # Settings storage
```

---

## Troubleshooting

### LM Studio Connection
- Ensure LM Studio API server is enabled
- Check the host address matches in Settings

### Voice Issues
- Ensure voice file exists in `voices/` folder
- Make sure transcript (.txt) file exists
- Use clear, single-speaker audio (10-30 seconds optimal)

### TTS Errors
- Check that voices are loaded in Multi Chat
- Verify character has a voice file assigned

---

## Command Line Tools

### Combine Audio Files
```bash
python combine_audio.py voices/UNREFINED/Bender
```

### Transcribe Voices
```bash
python transcribe_voices.py voices/
```
