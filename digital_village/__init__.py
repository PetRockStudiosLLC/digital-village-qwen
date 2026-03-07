"""
Digital Village - A multi-agent system using Python and LM Studio

This package implements a "digital village" of AI agents that can interact
with each other, share knowledge, and maintain conversation history.
"""

from .village import Village
from .villager import DigitalVillager
from .memory import VillageMemory
from .knowledge import VillageKnowledgeBase
from .events import VillageEventSystem
from .config import DEFAULT_CHARACTERS, create_character

__version__ = "0.1.0"
__all__ = [
    "Village",
    "DigitalVillager",
    "VillageMemory",
    "VillageKnowledgeBase",
    "VillageEventSystem",
    "DEFAULT_CHARACTERS",
    "create_character",
]
