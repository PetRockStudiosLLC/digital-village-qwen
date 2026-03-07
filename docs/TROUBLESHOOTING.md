# Troubleshooting Guide

## Quick Diagnostics

Run this to check your setup:

```python
# Test 1: PyTorch CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Test 2: LM Studio Connection
python -c "import requests; r = requests.get('http://192.168.56.1:6842/v1/models'); print('LM Studio:', r.status_code)"

# Test 3: Dependencies
python -c "import pygame, soundfile, librosa, qwen_tts; print('All OK')"
```

---

## Common Errors

### 1. "Connection refused" - LM Studio

**Error:**
```
requests.exceptions.ConnectionError: Connection refused
```

**Cause:** LM Studio API not accessible

**Fix:**
1. Open LM Studio
2. Ensure a model is loaded
3. Enable API server in LM Studio settings
4. Check URL matches: `http://192.168.56.1:6842`

---

### 2. "No module named 'qwen_tts'"

**Error:**
```
ModuleNotFoundError: No module named 'qwen_tts'
```

**Cause:** Qwen TTS package not installed

**Fix:**
```bash
pip install qwen-tts
```

---

### 3. "CUDA not available"

**Error:**
```
[Qwen3-TTS] Loading model on cpu...
```

**Cause:** PyTorch not using GPU

**Fix:**
```bash
# Check PyTorch version
python -c "import torch; print(torch.__version__)"

# Reinstall with CUDA
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

Verify:
```python
python -c "import torch; print(torch.cuda.is_available())"  # Should be True
```

---

### 4. "Model not found" / "Unrecognized model"

**Error:**
```
ValueError: Unrecognized model in models\Qwen3-TTS-12Hz-0.6B-Base
```

**Cause:** Model folder incomplete or wrong structure

**Fix:**

Option A: Delete folder and let it download:
```bash
rm -rf models/Qwen3-TTS-12Hz-0.6B-Base
# Run script - will download automatically
```

Option B: Download manually:
```bash
pip install huggingface-hub
huggingface-cli download Qwen/Qwen3-TTS-12Hz-0.6B-Base --local-dir models/Qwen3-TTS-12Hz-0.6B-Base
```

---

### 5. "Voice file not found"

**Error:**
```
[Qwen3-TTS] Voice file not found: voices\Shrek.wav
```

**Cause:** Voice file missing or wrong path

**Fix:**
1. Check file exists: `dir voices\`
2. Check filename exactly matches (case sensitive)
3. WAV format required

---

### 6. Audio Not Playing

**Error:** Script runs but no sound

**Cause:** pygame not installed or not initialized

**Fix:**
```bash
pip install pygame
```

Test:
```python
python -c "import pygame; pygame.init(); print('pygame OK')"
```

---

### 7. "Empty response" from LM Studio

**Error:**
```
Donkey: [Warning: Empty response from Donkey]
```

**Cause:** Model not responding or thinking enabled

**Fix:**
1. Disable "thinking" in LM Studio settings
2. Check model loaded correctly
3. Try different model

---

### 8. Very Slow Generation

**Expected:** ~2-4 seconds for typical response
**Problem:** Taking 30+ seconds

**Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| CPU instead of GPU | Install CUDA PyTorch |
| Model too large | Use smaller model in LM Studio |
| Wrong API URL | Check LM Studio port |
| Network issue | Disable any proxies |

---

### 9. Flash Attention Warning

**Warning:**
```
Warning: flash-attn is not installed. Will only run the manual PyTorch version.
```

**This is OK!** Just a warning. TTS still works.

For faster inference (optional):
```bash
pip install flash-attn
```
Note: Requires CUDA toolkit and specific PyTorch build.

---

### 10. SoX Warning

**Warning:**
```
'sox' is not recognized as an internal or external command
```

**This is OK!** SoX is optional. TTS still works without it.

---

## Windows-Specific Issues

### Colors Not Showing

**Problem:** No colored output

**Fix:**
- Use Windows Terminal instead of cmd.exe
- Or run: `chcp 65001` before running

### Long Paths Not Working

**Problem:** Files not found in deep folders

**Fix:**
Enable long paths in Windows:
```bash
git config --global core.longpaths true
```

---

## Performance Issues

### Low FPS / Slow Audio

**If audio plays but has artifacts:**

Check sample rate:
```python
# Should be 24000
import soundfile as sf
data, sr = sf.read("output/audio/001_Donkey.wav")
print(f"SR: {sr}")
```

### High Memory Usage

If script crashes with OOM:

1. Close other GPU applications
2. Use smaller LLM model in LM Studio
3. Reduce conversation history in villager.py

---

## Getting Help

If you're still stuck:

1. **Check LM Studio:** Is model loaded? API enabled?
2. **Check console output:** Error messages usually explain the problem
3. **Try fresh start:** 
   ```bash
   # Clear Python cache
   find . -type d -name __pycache__ -exec rm -rf {} +
   ```
4. **Test components separately:**
   ```python
   # Test TTS alone
   from digital_village.qwen_tts import get_qwen_tts
   tts = get_qwen_tts(voice_mode="preset", speaker="ryan")
   tts.speak("Hello!")
   ```

---

## Error Code Reference

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Unauthorized - check API key |
| 403 | Forbidden - check permissions |
| 404 | Not found - wrong URL |
| 500 | Server error - restart LM Studio |
| Connection refused | LM Studio not running |

---

## Common Solutions Summary

| Problem | Quick Fix |
|---------|-----------|
| LM Studio not connecting | Restart LM Studio, check URL |
| No GPU | Reinstall PyTorch with CUDA |
| Voice not loading | Check file path exactly |
| No audio | Install pygame |
| Model not found | Delete models/ folder, let redownload |
| Empty responses | Disable thinking in LM Studio |
