# Step-by-Step Setup Guide

## Prerequisites

### 1. Install LM Studio
1. Download from https://lmstudio.ai/
2. Install and open LM Studio
3. Download a model (recommended: Qwen2.5-7B-Instruct or similar)
4. Load the model
5. Enable API server (usually automatic, default port 6842)

### 2. Install Python
- Python 3.10+ required
- Download from https://python.org/

---

## Setup Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run LM Studio

1. Open LM Studio
2. Load your chosen model
3. Make sure API server is enabled
4. Note the API URL (default: http://192.168.56.1:6842)

### Step 3: Configure Settings (First Run)

1. Run the Web UI:
   ```bash
   python webui.py
   ```
2. Go to Settings tab
3. Verify/change LM Studio Host URL
4. Set your preferred model name
5. Click Save Settings

### Step 4: Add Voice Files (Optional but Recommended)

**Option A: Combine voice clips**
1. Put multiple voice clips in `voices/UNREFINED/CharacterName/`
2. Go to Combine Voices tab in Web UI
3. Select the folder and enter character name
4. Click Combine Voices

**Option B: Single voice file**
1. Place a `.wav` file in `voices/` folder (e.g., `voices/Finn.wav`)
2. Create a transcript `voices/Finn.txt` with what the voice says

### Step 5: Create Characters

1. Go to Characters tab
2. Enter character name
3. Write system prompt (character personality)
4. Select voice file
5. Add emotion/style notes
6. Set default status effect
7. Click Save Character

### Step 6: Generate Conversations

1. Go to Multi Chat tab
2. Select 2+ characters
3. (Optional) Set status overrides
4. Write a scene prompt
5. Choose number of turns
6. Click Generate All or Generate Text Only

---

## Quick Reference

| Task | Where | How |
|------|-------|-----|
| Create character | Characters tab | Fill form, Save |
| Edit character | Characters tab | Select, Load, Edit, Save |
| Combine voices | Combine Voices tab | Select folder, enter name, Combine |
| Generate chat | Multi Chat tab | Select chars, write scene, Generate |
| Talk to character | Chat tab | Select char, type message, Send |
| Change settings | Settings tab | Edit values, Save |

---

## Troubleshooting

### "Connection refused" error
- LM Studio not running → Start LM Studio and load a model
- Wrong API URL → Check LM Studio settings for correct port

### "No module named 'qwen_tts'" or other missing modules
```bash
pip install -r requirements.txt
```

### Voice issues
- Ensure voice file is in `voices/` folder
- Make sure transcript (.txt) file exists
- Use clear, single-speaker audio (10-30 seconds optimal)

---

## Need Help?

1. Check LM Studio is running and API is enabled
2. Check model is loaded in LM Studio
3. Try restarting the Web UI
4. Check console for error messages
