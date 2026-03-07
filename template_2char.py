# =============================================================================
# TEMPLATE: Simple 2-Character Conversation
# =============================================================================
# Use this template for a quick back-and-forth between 2 characters
# Just edit the messages array and run!
# =============================================================================

# -*- coding: utf-8 -*-
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

from colorama import init

init(autoreset=True)

from digital_village import Village


# Colors
class C:
    RESET = "\033[0m"
    ALICE = "\033[96m"  # Cyan
    BOB = "\033[93m"  # Yellow
    CAROL = "\033[95m"  # Magenta
    DAISY = "\033[92m"  # Green


def main():
    # Setup: Choose 1-4 characters
    village = Village()
    village.setup_default_villagers(2)  # Change to 1, 2, 3, or 4

    print(f"Characters: {village.get_character_names()}\n")

    # ============================================
    # EDIT YOUR CONVERSATION HERE
    # ============================================

    # Format: participants = ["Character1", "Character2"]
    # Format: messages = ["Message from Character1", "Response from Character2", ...]

    responses = village.conversation(
        participants=["Alice", "Bob"],
        messages=[
            "Bob, I found something amazing in the forest!",
            "What is it Alice?",
            "It's an old ruins! We should explore it together!",
            "That sounds dangerous. Are you sure?",
            "Of course! Think of the adventure!",
            "Alright, I'm in. When do we leave?",
        ],
    )

    # ============================================
    # END CONVERSATION
    # ============================================


if __name__ == "__main__":
    main()
