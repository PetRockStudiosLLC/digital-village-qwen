# Digital Village - Conversation Templates

Quick reference for setting up conversations with Digital Village.

## Basic Setup

```python
# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from colorama import init
init(autoreset=True)

from digital_village import Village, create_character

# Colors for characters
class C:
    RESET = '\033[0m'
    ALICE = '\033[96m'   # Cyan
    BOB = '\033[93m'     # Yellow
    CAROL = '\033[95m'   # Magenta
    DAISY = '\033[92m'   # Green
```

## Character Setup

### Option 1: Default Characters (1-4)
```python
village = Village()
village.setup_default_villagers(2)  # 1, 2, 3, or 4
```

### Option 2: Custom Characters
```python
# Using helper function
alice = create_character(
    name="Alice",
    role="the explorer",
    personality=["Curious", "Brave", "Friendly"]
)

bob = create_character(
    name="Bob", 
    role="the warrior",
    personality=["Strong", "Loyal", "Protective"]
)

village.setup_characters([alice, bob])
```

### Option 3: Manual Definition
```python
my_chars = [
    {
        "name": "Marcus",
        "system_prompt": "You are Marcus, the tavern keeper...",
        "description": "The friendly tavern keeper"
    }
]
village.setup_characters(my_chars)
```

## Conversation Types

### 1. Back-and-Forth (Predefined Messages)
```python
responses = village.conversation(
    participants=["Alice", "Bob", "Carol"],
    messages=[
        "Message from Alice",
        "Message from Bob responding",
        "Message from Carol responding"
    ]
)
```

### 2. Continuous Loop (Auto-Responses)
```python
# Characters will keep responding to each other
responses = village.continuous_conversation(
    participants=["Alice", "Bob"],
    starter_message="I found something amazing!",
    num_turns=5  # How many times to respond after first message
```
Press Ctrl+C to stop the loop anytime.

### 3. Direct Message (One-on-One)
```python
response = village.direct_message("Alice", "Bob", "Hey, can you help me?")
```

### 4. Broadcast (One to All)
```python
responses = village.broadcast_message("Alice", "Hello everyone!")
```

## TTS (Text-to-Speech)

Enable TTS in `template_loop.py`:

```python
# TTS Settings
enable_tts = True  # Set to False to disable
tts_api_url = "http://localhost:8004"  # Your Chatterbox endpoint

# Voice per character
voice_for_character = {
    'Alice': 'nova',
    'Bob': 'onyx',
    'Carol': 'fable',
    'Daisy': 'shimmer'
}
```

Available voices: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

Or use custom voice-cloned voices if you've set them up in Chatterbox.

## Output

Conversations auto-save to `output/` folder as `conversation_YYYY-MM-DD_HH-MM-SS.txt`

## Templates

- `template_2char.py` - Simple 2-character conversation
- `template_custom.py` - Custom characters
- `template_loop.py` - Continuous loop with TTS support
