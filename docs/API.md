# API Reference

## digital_village.qwen_tts

### get_qwen_tts()

Create a Qwen3-TTS instance.

```python
from digital_village.qwen_tts import get_qwen_tts

tts = get_qwen_tts(
    model_name="Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
    device="auto",           # "auto", "cuda", or "cpu"
    voice_mode="clone",      # "preset", "clone", or "design"
    speaker="ryan",          # Preset speaker name
    language="English",      # Language for TTS
    voice_folder="voices", # Folder for voice references
    model_folder="models",  # Folder for TTS models
)
```

### Qwen3TTS Class

#### speak()

```python
tts.speak(
    text,              # Text to speak
    wait=True,         # Wait for completion?
    show_progress=True, # Show progress?
    voice_name=None,   # Voice to use (for clone mode)
    save_path=None,    # Optional: save to file
)
```

Example:
```python
# Basic
tts.speak("Hello!")

# With emotion
tts.instruct = "angry"
tts.speak("Get out!")

# Save to file
tts.speak("Hello!", save_path="output/hello.wav")
```

#### speak_async()

Speak in background thread.

```python
tts.speak_async("Hello!")  # Non-blocking
```

#### speak_to_file()

Save audio to file without playing.

```python
tts.speak_to_file("Hello!", "output/hello.wav")
```

#### load_voice()

Load voice reference for cloning.

```python
tts.load_voice("Shrek")              # Loads voices/Shrek.wav
tts.load_voice("Shrek", "custom.wav") # Load from specific file
```

#### set_speaker()

Set preset speaker.

```python
tts.set_speaker("eric")
```

#### set_emotion()

Set emotion for VoiceDesign mode.

```python
tts.set_emotion("angry")
```

#### set_language()

Set language.

```python
tts.set_language("English")
```

#### get_speakers()

Get list of available preset speakers.

```python
speakers = tts.get_speakers()
print(speakers)  # ['aiden', 'dylan', 'eric', ...]
```

---

## digital_village.village

### Village

```python
from digital_village.village import Village

village = Village(
    model="qwen/qwen3.5-9b",           # Model name for LM Studio
    api_host="http://192.168.56.1:6842"  # LM Studio API URL
)
```

#### add_villager()

Add a character to the village.

```python
villager = village.add_villager(
    name="Shrek",
    system_prompt="""You are Shrek from Shrek...""",
    description="A grumpy ogre"
)
```

#### respond_to()

Get character response (for internal use).

---

## digital_village.villager

### DigitalVillager

Character agent class.

```python
villager = village.add_villager(...)
```

#### respond_to()

Get character's response.

```python
response = villager.respond_to(
    message,                    # Input message
    context=None,               # Optional context
    stream_callback=None        # Optional streaming callback
)
```

With streaming:
```python
def on_chunk(chunk):
    print(chunk, end="", flush=True)

response = villager.respond_to(
    "Hello!",
    stream_callback=on_chunk
)
```

---

## shrek-donkey-qwen.py

### Configuration Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| LM_STUDIO_HOST | str | "http://192.168.56.1:6842" | LM Studio API URL |
| SPEAKER_FOR_CHARACTER | dict | {"Shrek": "ryan", ...} | Character -> speaker mapping |
| EMOTION_FOR_CHARACTER | dict | {"Shrek": "grumpy, angry, ...", ...} | Character -> emotion mapping |
| SAVE_AUDIO | bool | True | Whether to save audio files |
| AUDIO_FOLDER | str | "output/audio" | Where to save audio |
| STARTER_MESSAGE | str | "Hey Donkey, what are you doing here?" | Opening message |
| NUM_TURNS | int | 5 | Number of conversation turns |

### EMOTION_FOR_CHARACTER

Emotion format: comma-separated descriptive words

Examples:
```python
{
    "Shrek": "grumpy, angry, deep voice, sarcastic",
    "Donkey": "happy, excited, energetic, enthusiastic", 
    "Puss": "smooth, charming, spanish accent",
    "Villain": "evil, menacing, dark, slow",
    "Robot": "monotone, flat, mechanical",
}
```

### combine_audio.py

#### Configuration

```python
AUDIO_FOLDER = "output/audio"  # Source folder
PAUSE_MIN = 0.5              # Minimum pause (seconds)
PAUSE_MAX = 2.0              # Maximum pause (seconds)
```

---

## combine_audio.py Functions

### combine_audio()

Combines all WAV files in `output/audio/` into one file.

```bash
python combine_audio.py
```

Output: `output/conversation_YYYY-MM-DD_HH-MM-SS.wav`

---

## Model Files

### Expected Structure

```
models/
├── Qwen3-TTS-12Hz-0.6B-Base/
│   ├── config.json
│   ├── model.safetensors
│   ├── tokenizer.json
│   └── ...
└── Qwen3-TTS-12Hz-0.6B-CustomVoice/
    ├── config.json
    ├── model.safetensors
    └── ...
```

### Voice Files

```
voices/
├── Shrek.wav    # Reference for Shrek character
├── Donkey.wav   # Reference for Donkey character
└── Name.wav     # Reference for Name character
```

---

## Output Files

### Audio Files

```
output/audio/
├── 001_Donkey.wav
├── 002_Shrek.wav
├── 003_Donkey.wav
└── ...
```

### Combined Audio

```
output/
├── conversation_2026-03-07_11-30-40.wav
└── conversation_2026-03-07_14-22-15.wav
```

### Conversation Logs

```
output/
└── shrek_donkey_qwen_2026-03-07_11-30-40.txt
```
