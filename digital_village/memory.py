"""
VillageMemory - Shared memory accessible by all villagers.
"""

import json
import time
from typing import Dict, Any, List


class VillageMemory:
    """
    Shared memory accessible by all villagers in the digital village.

    This provides a way for villagers to:
    - Share information with each other
    - Store village-wide knowledge
    - Track events and activities
    """

    def __init__(self):
        self.shared_data: Dict[str, Any] = {}
        self.shared_history: List[Dict] = []

    def write(self, key: str, value: Any, source: str):
        """
        Write to shared memory.

        Args:
            key: The memory key
            value: The value to store
            source: Who wrote this (villager name)
        """
        self.shared_data[key] = value
        self.shared_history.append(
            {"key": key, "value": value, "source": source, "timestamp": time.time()}
        )

    def read(self, key: str, default: Any = None) -> Any:
        """
        Read from shared memory.

        Args:
            key: The memory key
            default: Default value if key doesn't exist

        Returns:
            The stored value or default
        """
        return self.shared_data.get(key, default)

    def get_summary(self) -> str:
        """Get memory summary for villagers."""
        return json.dumps(self.shared_data, indent=2)

    def clear(self):
        """Clear all shared memory."""
        self.shared_data.clear()
        self.shared_history.clear()

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent memory history."""
        return self.shared_history[-limit:]
