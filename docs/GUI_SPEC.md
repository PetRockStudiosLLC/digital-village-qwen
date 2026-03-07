# Digital Village GUI Specification

## Overview

A modern PySide6 GUI application for creating AI conversations with custom voices and emotions.

---

## Framework

- **PySide6** (Qt for Python)
- **Blender-like modern styling**

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  [Settings] [📂 Load Preset] [💾 Save Preset]  [Export]  │
├──────────────────┬──────────────────────────────────────────┤
│                  │                                          │
│  CHARACTERS      │    CONVERSATION LOG                      │
│  ───────────    │    ───────────────                      │
│                  │                                          │
│  [+ Add]        │    [Shrek]: Hey Donkey...              │
│  ─────────      │    [Donkey]: Hi! I'm...               │
│  🟢 Shrek      │    [Shrek]: Go away...               │
│    Voice: Clone│                                          │
│    Emotion: 😠  │    [Progress: ████████░░░ 80%]       │
│    [▶ Preview] │                                          │
│                  │                                          │
│  🟡 Donkey     │                                          │
│    Voice: Clone│                                          │
│    Emotion: 😊  │                                          │
│    [▶ Preview] │                                          │
│                  │                                          │
├──────────────────┴──────────────────────────────────────────┤
│  TIMELINE ─────────────────────────────────────────────  │
│  [|] ▶ ═══════●═════════════════════════════ 00:47       │
├─────────────────────────────────────────────────────────────┤
│  [▶ Play] [⏹ Stop] [🔊 Vol]  │ Mode: [Stream] [Gen Only] │
│  [Individual ☐] [Combine ☑] [Final ☐] │ [▶ Generate]     │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### Toolbar (Top)
- Settings (LM Studio API, output folder, etc.)
- Load Preset - Load character config from JSON
- Save Preset - Save current characters to JSON
- Export - Bundle transcript + audio together

### Character Panel (Left)

**Features:**
- List of characters with color indicators
- Each character has:
  - Name (editable)
  - Voice mode: Clone / Preset / VoiceDesign
  - Voice file selector (Clone) OR preset dropdown (Preset)
  - Emotion input field
  - **Live Preview** button - test current settings
- Add/Remove character buttons
- Drag to reorder

**Character Data Structure:**
```python
{
    "name": "Shrek",
    "voice_mode": "clone",  # clone, preset, design
    "voice_file": "voices/Shrek.wav",  # for clone
    "preset_speaker": "ryan",  # for preset
    "emotion": "grumpy, angry, deep voice"
}
```

### Conversation Panel (Right)

**Features:**
- Scrollable text view
- Color-coded by character
- Real-time updates as characters respond
- Progress bar per generation step
- Timestamps optional

### Timeline (Bottom)

**Features:**
- Audio waveform visualization
- Playback scrubber
- Current time / Total time display
- Play / Stop / Volume controls

### Control Bar

**Play Controls:**
- Play / Stop / Volume slider

**Mode Toggle:**
- **Stream**: Generate → Play immediately → Continue
- **Generate Only**: Generate all → Save → Optional: Play combined

**Output Options:**
- [ ] Individual files - Save each clip separately
- [x] Combine - Create final conversation.wav
- [ ] Play final - Play combined after generation

**Generate Button:**
- Starts conversation generation

### Settings Panel (Modal)

**Options:**
- LM Studio API URL
- Model selection (from available)
- Output folder path
- Pause duration (min/max seconds)
- Preview test phrase
- Default emotions

---

## Generate Modes

| Mode | Behavior |
|------|----------|
| **Stream** | Generate → Play immediately → Next character |
| **Generate Only** | Generate all audio files → Save → Optional: Play combined |

---

## Output Options

| Option | What it does |
|--------|-------------|
| Individual files | Saves 001_Char.wav, 002_Char.wav to output/audio/ |
| Combine | Creates conversation_YYYY-MM-DD_HH-MM-SS.wav |
| Play final | Plays combined audio after all generation complete |

---

## Additional Features

### Live Preview
- Click preview button to test voice/emotion with sample phrase
- Shows in Timeline after generation

### Progress Bars
- Per-character progress during generation
- Overall progress in status bar

### Export
- Creates folder with:
  - transcript.txt (full conversation)
  - conversation.wav (combined audio)
  - individual clips (optional)

### Presets
- Save character configurations as JSON
- Load presets from file
- Include voices, emotions, settings

---

## File Structure

```
ChatBot/
├── gui/                        # New GUI module
│   ├── __init__.py
│   ├── main_window.py          # Main PySide6 window
│   ├── character_panel.py      # Left panel
│   ├── conversation_panel.py  # Right panel
│   ├── timeline.py             # Bottom timeline
│   ├── toolbar.py             # Top toolbar
│   ├── settings_dialog.py     # Settings modal
│   ├── control_bar.py         # Bottom controls
│   ├── style.py               # Blender-style theme
│   └── preset_manager.py      # Save/load presets
├── shrek-donkey-qwen.py       # CLI version (keep)
├── combine_audio.py            # CLI tool (keep)
├── digital_village/           # Core package (keep)
└── docs/                      # Documentation (keep)
```

---

## Configuration Files

### Preset Format (JSON)
```json
{
    "name": "Shrek & Donkey",
    "characters": [
        {
            "name": "Shrek",
            "voice_mode": "clone",
            "voice_file": "voices/Shrek.wav",
            "emotion": "grumpy, angry, deep voice"
        },
        {
            "name": "Donkey", 
            "voice_mode": "clone",
            "voice_file": "voices/Donkey.wav",
            "emotion": "happy, excited, energetic"
        }
    ],
    "settings": {
        "lm_studio_host": "http://192.168.56.1:6842",
        "num_turns": 5,
        "starter_message": "Hey Donkey, what are you doing here?"
    }
}
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space | Play/Pause |
| Ctrl+G | Generate |
| Ctrl+S | Save Preset |
| Ctrl+O | Load Preset |
| Ctrl+E | Export |
| Esc | Stop / Close dialog |

---

## Dependencies

```bash
pip install PySide6
```

---

## Future Enhancements (v2)

- Multiple conversation threads
- Voice mixer (adjust pitch, speed per voice)
- More waveform visualization options
- Network sync (control from phone?)
- Plugin system for custom TTS engines
