# Digital Village

A Python package for creating multi-agent AI conversations using LM Studio. Create villages of AI characters with unique personalities that can interact, share memories, and have back-and-forth conversations.

## Quick Start

```bash
pip install -r requirements.txt
python example.py
```

## Documentation

For detailed setup and configuration, see the [docs/](docs/) folder:

- **[docs/SETUP.md](docs/SETUP.md)** - Step-by-step setup guide
- **[docs/CONFIG.md](docs/CONFIG.md)** - Configuration options  
- **[docs/VOICES.md](docs/VOICES.md)** - Adding custom voices
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues

## Features

- **Customizable Characters**: Define characters with unique personalities and roles
- **Multiple Conversation Modes**: 
  - Broadcast messages to all characters
  - Direct messages between two characters
  - Back-and-forth conversations
- **Streaming Responses**: See responses as they're generated in real-time
- **Shared Memory**: Characters can share information with the village
- **Colored Output**: Character names are color-coded in the terminal

## Requirements

- Python 3.10+
- LM Studio with a model loaded
- Dependencies: `pip install -r requirements.txt`

## Installation

```bash
pip install -r requirements.txt
```

Make sure LM Studio is running with:
1. A model loaded
2. API server enabled (default: http://192.168.56.1:6842)

## Quick Start

```python
from digital_village import Village

# Create village with default characters
village = Village()
village.setup_default_villagers(4)  # Use 1-4 characters

# Simple broadcast
village.broadcast_message("Alice", "Hello everyone!")
```

## Configuration

### Changing API Host

```python
village = Village(api_host="http://192.168.56.1:6842")
```

### Changing Model

```python
village = Village(model="qwen/qwen3.5-9b")
```

## Creating Custom Characters

### Method 1: Using the Helper Function

```python
from digital_village import Village, create_character

# Create custom characters
my_characters = [
    create_character(
        name="Marcus",
        role="the village tavern keeper",
        personality=[
            "Friendly and welcoming to all travelers",
            "Knows all the gossip in town",
            "Generous with stories and ale",
            "Slightly mysterious about his past"
        ]
    ),
    create_character(
        name="Elena", 
        role="the village healer",
        personality=[
            "Compassionate and gentle",
            "Knowledgeable about herbs and medicine",
            "Patient and always willing to listen"
        ]
    )
]

# Setup village with custom characters
village = Village()
village.setup_characters(my_characters)
```

### Method 2: Manual Definition

```python
my_characters = [
    {
        "name": "Marcus",
        "system_prompt": """You are Marcus, the village tavern keeper.
You are friendly and welcoming to all travelers.
You know all the gossip in town.
You are generous with stories and ale.""",
        "description": "The friendly tavern keeper"
    },
    {
        "name": "Elena",
        "system_prompt": """You are Elena, the village healer.
You are compassionate and gentle.
You are knowledgeable about herbs and medicine.""",
        "description": "The village healer"
    }
]

village.setup_characters(my_characters)
```

## Conversation Modes

### 1. Broadcast Message

Send a message to all characters (except sender):

```python
village.setup_default_villagers(4)

# Alice broadcasts to everyone
village.broadcast_message("Alice", "Hello everyone!")
```

With streaming:
```python
def on_chunk(name, chunk):
    print(chunk, end="", flush=True)

village.broadcast_message("Alice", "Hello!", stream_callback=on_chunk)
```

### 2. Direct Message

Send a message from one character to another:

```python
# Bob sends a direct message to Carol
response = village.direct_message("Bob", "Carol", "Can you help me with something?")
```

### 3. Back-and-Forth Conversation

Multiple characters exchange messages:

```python
village.setup_characters([
    {"name": "Alice", "system_prompt": "...", "description": "..."},
    {"name": "Bob", "system_prompt": "...", "description": "..."}
])

# Alice starts, Bob responds
responses = village.conversation(
    participants=["Alice", "Bob"],
    messages=[
        "Hi Bob! How are you?",
        "I'm doing well, thanks for asking!"
    ]
)
```

## Controlling Number of Characters

```python
# Use only 2 characters
village.setup_default_villagers(2)  # Alice and Bob

# Use only 3 characters  
village.setup_default_villagers(3)  # Alice, Bob, Carol

# Use all 4
village.setup_default_villagers(4)  # Alice, Bob, Carol, Daisy
```

## Shared Memory

Characters can share information with the whole village:

```python
# Bob shares something
village.share_with_village("Bob", "weather", "It's raining today")

# Alice reads it
weather = village.read_from_village("Alice", "weather")
print(weather)  # "It's raining today"
```

## Running the Demo

```bash
python example.py
```

The demo shows:
1. A new resident introduction
2. Characters asking about the village
3. Shared memory in action

## Project Structure

```
ChatBot/
├── digital_village/
│   ├── __init__.py      # Package exports
│   ├── village.py       # Main Village class
│   ├── villager.py      # DigitalVillager agent
│   ├── memory.py        # Shared memory
│   ├── knowledge.py     # Knowledge base
│   ├── events.py        # Event system
│   └── config.py        # Character configuration helpers
├── requirements.txt
├── example.py           # Demo script
└── README.md
```

## Default Characters

| Name | Role | Description |
|------|------|-------------|
| Alice | Explorer | Curious and eager to learn |
| Bob | Blacksmith | Practical and skilled craftsman |
| Carol | Elder | Wise and remembers everything |
| Daisy | Gardener | Patient and loves nature |

## Troubleshooting

### LM Studio Connection Issues

Make sure:
1. LM Studio is running
2. A model is loaded
3. API server is enabled in LM Studio settings

### Responses Not Appearing

Check that:
1. Model is fully loaded in LM Studio
2. API host address is correct in your code

### Color Issues on Windows

The package uses colorama for cross-platform color support. If colors don't appear:
- Try running in a modern terminal (Windows Terminal recommended)
- Or disable colors by modifying the Colors class in example.py
