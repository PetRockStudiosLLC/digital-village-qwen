# =============================================================================
# TEMPLATE: Custom Characters Conversation
# =============================================================================
# Use this template to create your own characters with unique personalities
# Edit the characters and conversation below!
# =============================================================================

# -*- coding: utf-8 -*-
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

from colorama import init

init(autoreset=True)

from digital_village import Village, create_character


# Colors - Add more as needed
class C:
    RESET = "\033[0m"
    # Default characters
    ALICE = "\033[96m"
    BOB = "\033[93m"
    CAROL = "\033[95m"
    DAISY = "\033[92m"
    # Custom characters
    MARCUS = "\033[96m"
    ELENA = "\033[92m"
    THOMAS = "\033[93m"


def main():
    # ============================================
    # EDIT YOUR CHARACTERS HERE
    # ============================================

    # Create character 1
    char1 = create_character(
        name="Marcus",
        role="the village tavern keeper",
        personality=[
            "Friendly and welcoming to all travelers",
            "Knows all the gossip in town",
            "Generous with stories and ale",
            "Slightly mysterious about his past",
        ],
    )

    # Create character 2
    char2 = create_character(
        name="Elena",
        role="the village healer",
        personality=[
            "Compassionate and gentle",
            "Knowledgeable about herbs and medicine",
            "Patient and always willing to listen",
            "Quiet but observant",
        ],
    )

    # Create character 3 (optional)
    char3 = create_character(
        name="Thomas",
        role="the village merchant",
        personality=[
            "Clever with numbers",
            "Always looking for a good deal",
            "Well-traveled and knowledgeable",
            "Slightly greedy but fair",
        ],
    )

    # ============================================
    # END CHARACTERS
    # ============================================

    # Setup village with custom characters
    village = Village()
    village.setup_characters([char1, char2])  # Add char3 if you want

    print(f"Characters: {village.get_character_names()}\n")

    # ============================================
    # EDIT YOUR CONVERSATION HERE
    # ============================================

    # Option 1: Back-and-forth
    responses = village.conversation(
        participants=["Marcus", "Elena"],
        messages=[
            "Elena! Good to see you at the tavern.",
            "Hello Marcus. It's been a busy day.",
            "The roads have been busy lately. More travelers than usual.",
            "Yes, I've noticed. Many seem to be fleeing the cities.",
            "Hard times everywhere it seems. Drink?",
            "Thank you, that would be nice.",
        ],
    )

    # Option 2: Direct message (uncomment to use)
    # response = village.direct_message("Marcus", "Elena", "Can you come to the tavern?")
    # print(f"Elena: {response}")

    # Option 3: Broadcast (uncomment to use)
    # responses = village.broadcast_message("Marcus", "Free ale tonight!")

    # ============================================
    # END CONVERSATION
    # ============================================


if __name__ == "__main__":
    main()
