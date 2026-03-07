# Step-by-Step Setup Guide

## Prerequisites

### 1. Install LM Studio
1. Download from https://lmstudio.ai/
2. Install and open LM Studio
3. Download a model (recommended: Qwen/Qwen2.5-7B-Instruct or similar)
4. Load the model
5. Enable API server (usually automatic)

### 2. Install Anaconda
1. Download from https://www.anaconda.com/download
2. Install Anaconda

### 3. Install Git (optional but recommended)
- Download from https://git-scm.com/

---

## Setup Steps

### Step 1: Clone or Download Project

```bash
# If using Git:
git clone <repo-url> ChatBot
cd ChatBot

# Or download ZIP and extract
```

### Step 2: Create Conda Environment

```bash
# Open Anaconda Prompt
conda create -n HeartMula python=3.10 pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
conda activate HeartMula
```

### Step 3: Install Dependencies

```bash
pip install pygame soundfile librosa requests colorama
pip install qwen-tts transformers accelerate
```

### Step 4: Download TTS Models

Create a `models/` folder in the project root:

```
models/
├── Qwen3-TTS-12Hz-0.6B-Base/
└── Qwen3-TTS-12Hz-0.6B-CustomVoice/
```

**Option A: Download via Python (automatic)**
- The script will download automatically on first run

**Option B: Manual download**
```bash
# Install huggingface-cli
pip install huggingface-hub

# Download models
huggingface-cli download Qwen/Qwen3-TTS-12Hz-0.6B-Base --local-dir models/Qwen3-TTS-12Hz-0.6B-Base
huggingface-cli download Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice --local-dir models/Qwen3-TTS-12Hz-0.6B-CustomVoice
```

### Step 5: Add Voice Files (Optional)

1. Record or find audio clips of voices you want (WAV format, 3-15 seconds)
2. Put them in `voices/` folder:
   ```
   voices/
   ├── Shrek.wav    # Reference for Shrek character
   └── Donkey.wav   # Reference for Donkey character
   ```

### Step 6: Run LM Studio

1. Open LM Studio
2. Load your chosen model
3. Make sure API server is enabled (usually default port 1234 or 6842)
4. Note the API URL (e.g., http://192.168.56.1:6842)

### Step 7: Configure

Edit `shrek-donkey-qwen.py`:
```python
# Set your LM Studio API URL
LM_STUDIO_HOST = "http://192.168.56.1:6842"
```

### Step 8: Run!

```bash
conda activate HeartMula
python shrek-donkey-qwen.py
```

---

## How to Customize

### Add New Characters

1. Edit `shrek-donkey-qwen.py`
2. Add to `EMOTION_FOR_CHARACTER`:
```python
EMOTION_FOR_CHARACTER = {
    "Shrek": "grumpy, angry, deep voice",
    "Donkey": "happy, excited, energetic",
    "NEW_CHARACTER": "sad, slow, deep",  # Add here
}
```

3. Add voice file: `voices/NEW_CHARACTER.wav`

4. Modify conversation logic to include new character

### Change Emotions

Edit the emotion strings in `EMOTION_FOR_CHARACTER`:
```python
EMOTION_FOR_CHARACTER = {
    "Shrek": "happy, cheerful",  # Now sounds happy
    "Donkey": "scared, nervous",  # Now sounds scared
}
```

### Use Preset Voices Instead of Cloning

Edit `qwen_tts.py` or script to use `voice_mode="preset"`:
```python
tts = get_qwen_tts(
    voice_mode="preset",  # Use built-in voices
    speaker="ryan",       # Choose from: ryan, eric, vivian, etc.
)
```

### Change Output Folder

Edit configuration:
```python
AUDIO_FOLDER = "my_audio"  # Instead of output/audio
```

---

## Audio Files Explained

- Individual clips: `output/audio/001_Donkey.wav`, `002_Shrek.wav`, etc.
- Combined: `output/conversation_2026-03-07_11-30-40.wav`

Run `combine_audio.py` to combine individual clips.

---

## Troubleshooting

### "Connection refused" error
- LM Studio not running → Start LM Studio and load a model
- Wrong API URL → Check LM Studio settings for correct port
- Firewall blocking → Allow Python through firewall

### "No module named 'qwen_tts'"
```bash
pip install qwen-tts
```

### "CUDA not available"
```bash
# Check PyTorch has CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

If False, reinstall PyTorch with CUDA:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### Audio not playing
```bash
pip install pygame
```

### Models not downloading
- Check internet connection
- Try manual download with huggingface-cli

---

## Need Help?

1. Check LM Studio is running and API is enabled
2. Check model is loaded in LM Studio
3. Try restarting everything
4. Check console for error messages
