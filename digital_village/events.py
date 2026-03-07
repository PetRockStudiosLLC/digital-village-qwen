"""
VillageEventSystem - Manages village-wide events and reactions.
"""

from typing import Callable, Any
from dataclasses import dataclass
import time


@dataclass
class VillageEvent:
    """Represents an event in the village."""
    event_type: str
    source: str
    content: str
    timestamp: float


class VillageEventSystem:
    """
    Manages village-wide events and reactions.
    
    This system allows villagers to:
    - Register event handlers
    - Trigger events that notify all villagers
    - Respond to village events
    """
    
    def __init__(self, villagers):
        """
        Initialize event system.
        
        Args:
            villagers: Dictionary of villager instances
        """
        self.villagers = villagers
        self.event_handlers: Dict[str, Callable[[VillageEvent], Any]] = {}
        
    def register_handler(self, event_type: str, handler: Callable):
        """
        Register a handler for an event type.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        self.event_handlers[event_type] = handler
        
    def trigger_event(self, event_type: str, source: str, content: str):
        """
        Trigger an event and notify all villagers.
        
        Args:
            event_type: Type of event
            source: Who triggered the event
            content: Event content/message
        """
        event = VillageEvent(
            event_type=event_type,
            source=source,
            content=content,
            timestamp=time.time()
        )
        
        # Notify all villagers
        for villager_name, villager in self.villagers.items():
            if villager_name != source:
                response = villager.respond_to(
                    f"[Event: {event_type}] From {source}: {content}"
                )
                print(f"[{villager_name}] Reacted to {event_type}: {response}")
        
        # Call registered handlers
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type](event)
            except Exception as e:
                print(f"Event handler error: {e}")
