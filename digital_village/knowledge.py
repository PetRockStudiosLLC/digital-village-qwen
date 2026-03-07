"""
VillageKnowledgeBase - Shared knowledge base for the village.
"""

from typing import Dict, List, Any


class VillageKnowledgeBase:
    """
    Shared knowledge base for the village.

    This allows villagers to:
    - Store categorized knowledge
    - Query knowledge by category
    - Share expertise across the village
    """

    def __init__(self):
        self.knowledge: Dict[str, List[Dict[str, str]]] = {
            "general": [],
            "history": [],
            "skills": [],
            "stories": [],
        }

    def add_knowledge(self, villager: str, category: str, knowledge: str):
        """
        Add knowledge to a category.

        Args:
            villager: Who is adding the knowledge
            category: Category to add to
            knowledge: The knowledge content
        """
        if category not in self.knowledge:
            self.knowledge[category] = []

        self.knowledge[category].append({"villager": villager, "content": knowledge})

    def get_knowledge(self, villager: str = None, category: str = None) -> str:
        """
        Get knowledge for a villager or category.

        Args:
            villager: Filter by villager (optional)
            category: Filter by category (optional)

        Returns:
            Formatted knowledge string
        """
        if category and category in self.knowledge:
            category_knowledge = self.knowledge[category]
            if villager:
                category_knowledge = [
                    k for k in category_knowledge if k["villager"] == villager
                ]
            return "\n\n".join(k["content"] for k in category_knowledge)

        if villager:
            villager_knowledge = []
            for cat_knowledge in self.knowledge.values():
                villager_knowledge.extend(
                    [k for k in cat_knowledge if k["villager"] == villager]
                )
            return "\n\n".join(k["content"] for k in villager_knowledge)

        all_knowledge = []
        for cat, cat_knowledge in self.knowledge.items():
            for k in cat_knowledge:
                all_knowledge.append(f"[{cat}] {k['content']}")
        return "\n\n".join(all_knowledge)

    def get_categories(self) -> List[str]:
        """Get all available categories."""
        return list(self.knowledge.keys())

    def clear(self):
        """Clear all knowledge."""
        for category in self.knowledge:
            self.knowledge[category].clear()
