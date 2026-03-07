# Building a Digital Village with Python and LM Studio
## Complete Research Guide (2024-2025)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [LM Studio Integration](#lm-studio-integration)
3. [Digital Persona Design](#digital-persona-design)
4. [Communication Patterns](#communication-patterns)
5. [Memory & State Management](#memory--state-management)
6. [Complete Working Examples](#complete-working-examples)
7. [Best Practices](#best-practices)

---

## Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Digital Village System                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Agent A   │  │   Agent B   │  │   Agent C           │  │
│  │ (Personality)│  │ (Personality)│  │ (Personality)       │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                    │             │
│         └────────────────┼────────────────────┘             │
│                          │                                  │
│              ┌───────────▼───────────┐                      │
│              │  Shared Memory/State  │                      │
│              │  - Village Chat Log   │                      │
│              │  - Agent Knowledge   │                      │
│              │  - Event Queue        │                      │
│              └───────────────────────┘                      │
│                          │                                  │
│         ┌────────────────┼────────────────┐                 │
│         │                │                │                 │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌─────▼─────┐           │
│  │ LM Studio   │  │ LM Studio   │  │ LM Studio │           │
│  │ Instance A  │  │ Instance B  │  │ Instance │           │
│  └─────────────┘  └─────────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Modular Agents**: Each digital person has its own personality and capabilities
2. **Shared Memory**: Village-wide knowledge base accessible to all agents
3. **Event-Driven Communication**: Agents react to events and messages
4. **Context-Aware**: Each agent maintains conversation history
5. **Scalable**: Easy to add more agents to the village

---

## LM Studio Integration

### Installation

```bash
# Install LM Studio Python SDK
pip install lmstudio

# Or install from PyPI
pip install lmstudio
```

### Basic Client Setup

```python
import lmstudio as lms

# Create a client (manages WebSocket connections)
client = lms.Client(
    host="http://192.168.56.1:6842",  # Default LM Studio API port
    model="qwen/qwen3.5-9b"  # e.g., "TheBloke/Llama-2-7b-Chat-GGUF"
)
```

### Creating Multiple Agents

```python
import lmstudio as lms
import json

# Create client (shared across all agents)
client = lms.Client(host="http://192.168.56.1:6842", model="qwen/qwen3.5-9b")

# Define agent personalities
PERSONALITIES = {
    "villager_1": {
        "name": "Alice",
        "system_prompt": "You are Alice, a friendly and curious villager who loves learning about new things. "
                        "You speak in a warm, welcoming tone and always ask questions to understand others better. "
                        "You care about community and helping neighbors.",
        "description": "The friendly newcomer who just moved to the village"
    },
    "villager_2": {
        "name": "Bob",
        "system_prompt": "You are Bob, the village blacksmith. You speak practically and directly, "
                        "focusing on craftsmanship, tools, and practical solutions. "
                        "You have wisdom about building and fixing things.",
        "description": "The skilled blacksmith and village craftsman"
    },
    "villager_3": {
        "name": "Carol",
        "system_prompt": "You are Carol, the village elder who knows all the village history. "
                        "You speak with wisdom and patience, sharing stories and lessons from the past. "
                        "You value tradition and community bonds.",
        "description": "The wise elder who remembers everything"
    }
}
```

### Agent Class Implementation

```python
import lmstudio as lms
from typing import Dict, List, Optional
import json

class DigitalVillager:
    """Represents a single digital villager with personality and memory."""
    
    def __init__(
        self,
        client: lms.Client,
        name: str,
        system_prompt: str,
        description: str,
        memory: Optional[Dict] = None
    ):
        self.client = client
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
        self.memory = memory or {}
        self.chat_history: List[Dict] = []
        self.conversation_context = ""
        
    def remember(self, fact: str):
        """Store a fact in the villager's memory."""
        self.memory[fact] = True
        print(f"[{self.name}] Remembered: {fact}")
        
    def forget(self, fact: str):
        """Remove a fact from memory."""
        if fact in self.memory:
            del self.memory[fact]
            print(f"[{self.name}] Forgot: {fact}")
            
    def get_memory_summary(self) -> str:
        """Get a summary of what the villager knows."""
        return json.dumps(self.memory, indent=2)
    
    def respond_to(self, message: str, context: Optional[str] = None) -> str:
        """Generate a response to a message."""
        
        # Build conversation context
        full_context = context or ""
        if self.conversation_context:
            full_context += f"\n\n{self.conversation_context}"
            
        # Create chat history with system prompt
        chat = lms.Chat(self.system_prompt)
        chat.add_assistant_response(self.description)
        chat.add_user_message(full_context)
        
        # Get response
        response = self.client.llm().respond(chat)
        
        # Update conversation context
        self.conversation_context = full_context + f"\n\n{message}: {response}"
        
        # Add to history
        self.chat_history.append({
            "role": "user",
            "content": message,
            "response": response
        })
        
        return response
    
    def get_personality(self) -> str:
        """Get formatted personality description."""
        return f"""You are {self.name}, {self.description}.

Your personality traits:
- {json.dumps(self.memory, indent=2)}

Current conversation:
{self.conversation_context}"""
```

---

## Digital Persona Design

### Personality Dimensions

Each villager should have multiple personality dimensions:

```python
class VillagerProfile:
    """Defines a villager's complete personality profile."""
    
    def __init__(self, name: str, role: str, traits: Dict):
        self.name = name
        self.role = role
        self.traits = traits
        
    def generate_system_prompt(self) -> str:
        """Generate system prompt from personality profile."""
        
        trait_strings = [
            f"- {k}: {v}" 
            for k, v in self.traits.items()
        ]
        
        return f"""You are {self.name}, the {self.role} of the digital village.

Your personality:
{chr(10).join(trait_strings)}

You should:
- Speak and act consistently with these traits
- Remember your role and responsibilities
- Interact warmly with other villagers
- Share knowledge relevant to your role
"""

# Example villager profiles
VILLAGER_PROFILES = {
    "alice": VillagerProfile(
        name="Alice",
        role="Friendly Neighbor",
        traits={
            "curiosity": "Very high - always asks questions",
            "kindness": "Extremely high - always helpful",
            "energy": "High - enthusiastic about everything",
            "creativity": "Medium - enjoys new ideas"
        }
    ),
    
    "bob": VillagerProfile(
        name="Bob",
        role="Blacksmith",
        traits={
            "practicality": "Very high - focuses on solutions",
            "strength": "High - good at building things",
            "patience": "Medium - takes time to craft",
            "directness": "High - speaks plainly"
        }
    ),
    
    "carol": VillagerProfile(
        name="Carol",
        role="Village Elder",
        traits={
            "wisdom": "Extremely high - knows everything",
            "patience": "Very high - listens carefully",
            "tradition": "Very high - values history",
            "calmness": "High - always composed"
        }
    )
}
```

---

## Communication Patterns

### 1. Direct Message Passing

```python
class VillageMessenger:
    """Handles direct communication between villagers."""
    
    def __init__(self, villagers: Dict[str, DigitalVillager]):
        self.villagers = villagers
        
    def send_message(self, sender: str, receiver: str, message: str) -> str:
        """Send a message from one villager to another."""
        sender_villager = self.villagers[sender]
        receiver_villager = self.villagers[receiver]
        
        # Prepare message with context
        full_message = f"From {sender}: {message}"
        
        # Receiver responds
        response = receiver_villager.respond_to(full_message)
        
        return response
    
    def broadcast(self, sender: str, message: str) -> Dict[str, str]:
        """Broadcast message to all villagers."""
        responses = {}
        
        for villager_name, villager in self.villagers.items():
            if villager_name != sender:
                response = villager.respond_to(f"[Broadcast from {sender}]: {message}")
                responses[villager_name] = response
                
        return responses
```

### 2. Event System

```python
from typing import Callable, Any
from dataclasses import dataclass
import asyncio

@dataclass
class VillageEvent:
    """Represents an event in the village."""
    event_type: str
    source: str
    content: str
    timestamp: float
    
class VillageEventSystem:
    """Manages village-wide events and reactions."""
    
    def __init__(self, villagers: Dict[str, DigitalVillager]):
        self.villagers = villagers
        self.event_handlers: Dict[str, Callable[[VillageEvent], Any]] = {}
        
    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for an event type."""
        self.event_handlers[event_type] = handler
        
    async def trigger_event(self, event_type: str, source: str, content: str):
        """Trigger an event and notify all villagers."""
        event = VillageEvent(
            event_type=event_type,
            source=source,
            content=content,
            timestamp=asyncio.get_event_loop().time()
        )
        
        # Notify all villagers
        for villager_name, villager in self.villagers.items():
            if villager_name != source:
                response = villager.respond_to(f"[Event: {event_type}] From {source}: {content}")
                print(f"[{villager_name}] Reacted to {event_type}: {response}")
        
        # Call registered handlers
        if event_type in self.event_handlers:
            await self.event_handlers[event_type](event)
```

### 3. Shared Memory System

```python
import json
from typing import Dict, Any

class VillageMemory:
    """Shared memory accessible by all villagers."""
    
    def __init__(self):
        self.shared_data: Dict[str, Any] = {}
        self.shared_history: List[Dict] = []
        
    def write(self, key: str, value: Any, source: str):
        """Write to shared memory."""
        self.shared_data[key] = value
        self.shared_history.append({
            "key": key,
            "value": value,
            "source": source,
            "timestamp": time.time()
        })
        
    def read(self, key: str, default: Any = None) -> Any:
        """Read from shared memory."""
        return self.shared_data.get(key, default)
    
    def get_summary(self) -> str:
        """Get memory summary for villagers."""
        return json.dumps(self.shared_data, indent=2)

# Usage
village_memory = VillageMemory()

# Alice writes to shared memory
alice.write("weather", "Sunny and warm today", "Alice")
bob.write("project", "Building the village fountain", "Bob")

# Bob reads shared memory
weather = village_memory.read("weather")
print(f"Weather: {weather}")
```

---

## Memory & State Management

### Conversation History

```python
class ConversationManager:
    """Manages conversation history for villagers."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history: Dict[str, List[Dict]] = {}
        
    def add_message(self, villager: DigitalVillager, role: str, content: str):
        """Add a message to a villager's history."""
        if villager.name not in self.history:
            self.history[villager.name] = []
            
        self.history[villager.name].append({
            "role": role,
            "content": content
        })
        
        # Trim history if too long
        if len(self.history[villager.name]) > self.max_history:
            self.history[villager.name] = self.history[villager.name][-self.max_history:]
            
    def get_context(self, villager: DigitalVillager) -> str:
        """Get conversation context for a villager."""
        history = self.history.get(villager.name, [])
        return "\n".join(f"[{h['role']}] {h['content']}" for h in history)
```

### Knowledge Base

```python
from typing import List

class VillageKnowledgeBase:
    """Shared knowledge base for the village."""
    
    def __init__(self):
        self.knowledge: Dict[str, List[Dict]] = {
            "general": [],
            "alice": [],
            "bob": [],
            "carol": []
        }
        
    def add_knowledge(self, villager: str, category: str, knowledge: str):
        """Add knowledge to a villager."""
        if villager not in self.knowledge:
            self.knowledge[villager] = []
            
        self.knowledge[villager].append({
            "category": category,
            "content": knowledge
        })
        
    def get_knowledge(self, villager: str, category: str) -> str:
        """Get knowledge for a villager."""
        villager_knowledge = self.knowledge.get(villager, [])
        category_knowledge = [
            k for k in villager_knowledge 
            if k["category"] == category
        ]
        return "\n\n".join(k["content"] for k in category_knowledge)
```

---

## Complete Working Examples

### Example 1: Simple Two-Agent Conversation

```python
import lmstudio as lms

# Setup
client = lms.Client(host="localhost:1234", model="llama-2-7b")

# Create two villagers
alice = DigitalVillager(
    client=client,
    name="Alice",
    system_prompt="You are Alice, a friendly villager who loves learning.",
    description="A curious newcomer to the village"
)

bob = DigitalVillager(
    client=client,
    name="Bob",
    system_prompt="You are Bob, the village blacksmith with practical wisdom.",
    description="The skilled craftsman of the village"
)

# Conversation
print("=== Alice and Bob Meet ===\n")

alice_message = "Hello Bob! I'm Alice. I just moved here. What's the village like?"
print(f"Alice: {alice_message}")

response = bob.respond_to(alice_message)
print(f"Bob: {response}")

alice_message = "That sounds wonderful! What should I do first?"
print(f"\nAlice: {alice_message}")

response = bob.respond_to(alice_message)
print(f"Bob: {response}")
```

### Example 2: Multi-Agent Village with Shared Memory

```python
import lmstudio as lms
from typing import Dict

# Setup
client = lms.Client(host="localhost:1234", model="llama-2-7b")

# Create villagers
alice = DigitalVillager(
    client=client,
    name="Alice",
    system_prompt="You are Alice, a friendly and curious villager.",
    description="The friendly newcomer"
)

bob = DigitalVillager(
    client=client,
    name="Bob",
    system_prompt="You are Bob, the village blacksmith.",
    description="The skilled craftsman"
)

carol = DigitalVillager(
    client=client,
    name="Carol",
    system_prompt="You are Carol, the village elder.",
    description="The wise elder"
)

# Create village memory
village_memory = VillageMemory()

# Alice shares something
alice.write("weather", "It's a beautiful sunny day!", "Alice")

# Bob reads and responds
weather = village_memory.read("weather")
if weather:
    bob_message = f"Alice mentioned: {weather}"
    print(f"Bob reads: {bob_message}")
    response = bob.respond_to(bob_message)
    print(f"Bob responds: {response}")
```

### Example 3: Event-Driven Village

```python
import asyncio
from typing import Dict

class Village:
    """Complete village simulation."""
    
    def __init__(self, model: str = "llama-2-7b"):
        self.client = lms.Client(host="localhost:1234", model=model)
        self.villagers = {
            "alice": DigitalVillager(
                client=self.client,
                name="Alice",
                system_prompt="You are Alice, a friendly villager.",
                description="A curious newcomer"
            ),
            "bob": DigitalVillager(
                client=self.client,
                name="Bob",
                system_prompt="You are Bob, the blacksmith.",
                description="The craftsman"
            ),
            "carol": DigitalVillager(
                client=self.client,
                name="Carol",
                system_prompt="You are Carol, the elder.",
                description="The wise elder"
            )
        }
        
    async def start_conversation(self):
        """Start a village conversation."""
        print("=== Village Gathering ===\n")
        
        # Alice starts
        print("Alice: Hello everyone! I'd like to introduce myself.")
        await asyncio.gather(
            self._respond("bob", "Alice"),
            self._respond("carol", "Alice")
        )
        
        # Bob shares
        print("\nBob: I've been working on a new forge design.")
        await asyncio.gather(
            self._respond("alice", "Bob"),
            self._respond("carol", "Bob")
        )
        
    async def _respond(self, villager_name: str, speaker: str):
        """Handle response from a villager."""
        villager = self.villagers[villager_name]
        response = villager.respond_to(f"[{speaker}]: I'd love to hear more!")
        print(f"{villager.name}: {response}")
```

### Example 4: Advanced Village with Memory and Events

```python
import asyncio
import time
from typing import Dict, Any

class AdvancedVillage:
    """Advanced village with full memory and event system."""
    
    def __init__(self, model: str = "llama-2-7b"):
        self.client = lms.Client(host="localhost:1234", model=model)
        self.villagers = {}
        self.village_memory = VillageMemory()
        self.event_system = None
        self.knowledge_base = VillageKnowledgeBase()
        
    def setup_villagers(self):
        """Setup all villagers with personalities."""
        
        # Alice - The Curious Explorer
        self.villagers["alice"] = DigitalVillager(
            client=self.client,
            name="Alice",
            system_prompt="""You are Alice, the village explorer.
You love discovering new things and sharing adventures.
You're friendly, curious, and always eager to learn.
You remember interesting places and experiences.""",
            description="The curious explorer who knows all the trails"
        )
        
        # Bob - The Blacksmith
        self.villagers["bob"] = DigitalVillager(
            client=self.client,
            name="Bob",
            system_prompt="""You are Bob, the village blacksmith.
You're practical, skilled, and focused on craftsmanship.
You value quality tools and strong buildings.
You have knowledge about metalwork and construction.""",
            description="The skilled blacksmith and builder"
        )
        
        # Carol - The Elder
        self.villagers["carol"] = DigitalVillager(
            client=self.client,
            name="Carol",
            system_prompt="""You are Carol, the village elder.
You're wise, patient, and know the village history.
You value tradition and community bonds.
You remember everything that has happened.""",
            description="The wise elder who remembers everything"
        )
        
        # Carol - The Gardener
        self.villagers["daisy"] = DigitalVillager(
            client=self.client,
            name="Daisy",
            system_prompt="""You are Daisy, the village gardener.
You love plants, nature, and growing things.
You're patient and nurturing.
You know all about plants and seasons.""",
            description="The gentle gardener who loves nature"
        )
        
    async def run_scenario(self):
        """Run a village scenario."""
        print("=== Village Scenario: New Tool Needed ===\n")
        
        # Alice discovers a need
        print("Alice: Hey Bob! I need a new hammer for my work.")
        alice_response = self.villagers["alice"].respond_to(
            "Bob needs to help with a hammer request"
        )
        print(f"Alice: {alice_response}")
        
        # Bob responds
        bob_response = self.villagers["bob"].respond_to(
            "Alice needs a new hammer"
        )
        print(f"Bob: {bob_response}")
        
        # Bob writes to shared memory
        self.village_memory.write(
            "project_status",
            "Working on new hammer",
            "Bob"
        )
        
        # Carol reads and comments
        project = self.village_memory.read("project_status")
        if project:
            carol_response = self.villagers["carol"].respond_to(
                f"Bob is working on: {project}"
            )
            print(f"Carol: {carol_response}")
```

---

## Best Practices

### 1. Model Selection

```python
# For production, consider multiple models
VILLAGE_MODELS = {
    "general": "llama-2-7b",      # General conversations
    "creative": "mistral-7b",     # Creative writing
    "knowledge": "vicuna-13b"     # Knowledge-intensive tasks
}

# Switch models per villager if needed
def get_model_for_role(role: str) -> str:
    return VILLAGE_MODELS.get(role, "llama-2-7b")
```

### 2. Rate Limiting

```python
import time
from functools import wraps

def rate_limit(villager: DigitalVillager, min_seconds: float = 2.0):
    """Rate limit villager responses."""
    
    last_response_time = villager.last_response_time or 0
    
    def wrapper(message: str, *args, **kwargs):
        current_time = time.time()
        if current_time - last_response_time < min_seconds:
            time.sleep(min_seconds - (current_time - last_response_time))
        
        result = villager.respond_to(message, *args, **kwargs)
        villager.last_response_time = time.time()
        return result
    
    return wrapper

# Apply rate limiting
villagers["alice"].respond_to = rate_limit(villagers["alice"], 2.0)
```

### 3. Context Management

```python
class ContextManager:
    """Manages conversation context across multiple interactions."""
    
    def __init__(self, max_context_tokens: int = 4000):
        self.max_context_tokens = max_context_tokens
        self.context_window: Dict[str, List[Dict]] = {}
        
    def add_context(self, villager: DigitalVillager, role: str, content: str):
        """Add to context window."""
        if villager.name not in self.context_window:
            self.context_window[villager.name] = []
            
        self.context_window[villager.name].append({
            "role": role,
            "content": content
        })
        
    def get_context(self, villager: DigitalVillager) -> str:
        """Get context for villager."""
        context = self.context_window.get(villager.name, [])
        return "\n".join(f"[{c['role']}] {c['content']}" for c in context)
```

### 4. Error Handling

```python
class SafeVillager(DigitalVillager):
    """Villager with error handling."""
    
    def respond_to(self, message: str, *args, **kwargs) -> str:
        try:
            return super().respond_to(message, *args, **kwargs)
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return "I'm not sure how to respond to that, but I'm here to help!"
```

---

## Quick Start Guide

### Step 1: Install Dependencies

```bash
pip install lmstudio
```

### Step 2: Start LM Studio

1. Download and install LM Studio
2. Load a model (e.g., Llama-2-7b)
3. Start the API server (default: localhost:1234)

### Step 3: Create Your Village

```python
from digital_village import Village

village = Village()
village.setup_villagers()
village.run_scenario()
```

### Step 4: Run Interactively

```python
# Start conversation
alice_message = "Hello everyone!"
for villager_name in ["bob", "carol", "daisy"]:
    response = village.villagers[villager_name].respond_to(alice_message)
    print(f"{villager_name}: {response}")
```

---

## Advanced Patterns

### 1. Role-Based Access

```python
class RoleManager:
    """Manages villager roles and permissions."""
    
    def __init__(self):
        self.roles = {
            "admin": ["alice"],
            "craftsman": ["bob"],
            "elder": ["carol"],
            "gardener": ["daisy"]
        }
        
    def can_access(self, villager_name: str, resource: str) -> bool:
        """Check if villager can access resource."""
        villager_roles = [
            role for role, villagers in self.roles.items()
            if villager_name in villagers
        ]
        
        # Define access rules
        access_rules = {
            "village_memory": ["admin", "elder"],
            "forge": ["craftsman"],
            "garden": ["gardener"]
        }
        
        return villager_roles in access_rules.get(resource, ["admin"])
```

### 2. Multi-Model Ensemble

```python
class EnsembleVillager(DigitalVillager):
    """Uses multiple models for responses."""
    
    def __init__(self, *models):
        self.models = [lms.Client(host="localhost:1234", model=m) for m in models]
        self.primary_model = self.models[0]
        
    def respond_to(self, message: str) -> str:
        """Get response from primary model, fallback to others."""
        try:
            return self.primary_model.llm().respond(message)
        except Exception:
            # Try other models
            for model in self.models[1:]:
                try:
                    return model.llm().respond(message)
                except:
                    continue
            return "I'm not sure how to respond."
```

---

## Summary

This research provides a comprehensive foundation for building a digital village with Python and LM Studio. The key takeaways are:

1. **Use LM Studio Python SDK** for local LLM inference
2. **Design distinct personalities** for each villager
3. **Implement shared memory** for inter-agent communication
4. **Use event-driven architecture** for reactive behavior
5. **Manage conversation context** for coherent interactions
6. **Apply rate limiting** for realistic response times
7. **Handle errors gracefully** for robust systems

The examples provided can be extended and customized for your specific needs. Start with simple two-agent conversations and gradually add complexity as needed.
