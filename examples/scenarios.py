# -*- coding: utf-8 -*-
"""
Example Scenarios - Different ways to use Digital Village

Run any of these scenarios by uncommenting the one you want to try:
    python examples/scenario_*.py
"""

import os

os.environ["PYTHONIOENCODING"] = "utf-8"

from colorama import init

init(autoreset=True)

from digital_village import Village, create_character


# ANSI colors
class Colors:
    RESET = "\033[0m"
    ALICE = "\033[96m"
    BOB = "\033[93m"
    CAROL = "\033[95m"
    DAISY = "\033[92m"
    INFO = "\033[94m"
    GRAY = "\033[90m"


# =============================================================================
# SCENARIO 1: Simple 2-Character Conversation
# =============================================================================
def scenario_two_characters():
    """Only use 2 characters"""
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Scenario: Two Characters{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}\n")

    village = Village()
    village.setup_default_villagers(num_characters=2)  # Only Alice & Bob

    print(
        f"{Colors.INFO}Using characters: {village.get_character_names()}{Colors.RESET}\n"
    )

    # Direct conversation between two
    print(f"{Colors.ALICE}Alice:{Colors.RESET} Hi Bob! What are you working on?")

    response = village.direct_message(
        "Alice", "Bob", "Hi Bob! What are you working on?"
    )
    print(f"{Colors.BOB}Bob:{Colors.RESET} {response}\n")


# =============================================================================
# SCENARIO 2: Custom Characters
# =============================================================================
def scenario_custom_characters():
    """Create your own characters"""
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Scenario: Custom Characters{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}\n")

    # Create custom characters using the helper
    tavern_keeper = create_character(
        name="Marcus",
        role="the village tavern keeper",
        personality=[
            "Friendly and welcoming to all travelers",
            "Knows all the gossip in town",
            "Generous with stories and ale",
            "Slightly mysterious about his past",
        ],
    )

    healer = create_character(
        name="Elena",
        role="the village healer",
        personality=[
            "Compassionate and gentle",
            "Knowledgeable about herbs and medicine",
            "Patient and always willing to listen",
            "Quiet but observant",
        ],
    )

    merchant = create_character(
        name="Thomas",
        role="the village merchant",
        personality=[
            "Clever with numbers",
            "Always looking for a good deal",
            "Well-traveled and knowledgeable",
            "Slightly greedy but fair",
        ],
    )

    # Setup village with custom characters
    village = Village()
    village.setup_characters([tavern_keeper, healer, merchant])

    print(
        f"{Colors.INFO}Custom characters: {village.get_character_names()}{Colors.RESET}\n"
    )

    # Marcus greets the village
    print(f"\n{Colors.ALICE}Marcus:{Colors.RESET} Welcome to my tavern, travelers!")

    responses = village.broadcast_message(
        "Marcus", "Welcome to my tavern! First round is free!"
    )
    for name, response in responses.items():
        color = getattr(Colors, name.upper(), Colors.RESET)
        print(f"{color}{name}:{Colors.RESET} {response}\n")


# =============================================================================
# SCENARIO 3: Back-and-Forth Conversation
# =============================================================================
def scenario_conversation():
    """Multiple characters exchange messages"""
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Scenario: Back-and-Forth Conversation{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}\n")

    village = Village()
    village.setup_default_villagers(3)

    # Alice starts a conversation with Bob and Carol
    responses = village.conversation(
        participants=["Alice", "Bob", "Carol"],
        messages=[
            "I found something strange in the forest today...",
            "What did you find?",
            "That's interesting, tell us more!",
        ],
    )

    print(f"\n{Colors.GRAY}--- Conversation Summary ---{Colors.RESET}")
    for name, response in responses.items():
        color = getattr(Colors, name.upper(), Colors.RESET)
        print(f"{color}{name}:{Colors.RESET} {response[:100]}...")


# =============================================================================
# SCENARIO 4: Direct Message
# =============================================================================
def scenario_direct_message():
    """One-on-one conversation"""
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Scenario: Direct Message{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}\n")

    village = Village()
    village.setup_default_villagers(4)

    # Bob asks Carol for advice
    print(f"{Colors.BOB}Bob:{Colors.RESET} (asking Carol for advice)")

    response = village.direct_message(
        "Bob",
        "Carol",
        "I've been thinking about the old well. Do you remember anything about it?",
    )
    print(f"{Colors.CAROL}Carol:{Colors.RESET} {response}\n")


# =============================================================================
# SCENARIO 5: Village Meeting
# =============================================================================
def scenario_village_meeting():
    """All characters discuss a topic"""
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Scenario: Village Meeting{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}\n")

    village = Village()
    village.setup_default_villagers(4)

    topic = "Should we repair the old bridge?"

    print(f"{Colors.INFO}Topic: {topic}{Colors.RESET}\n")

    # Carol (the elder) brings up the topic
    responses = village.broadcast_message("Carol", topic)

    for name, response in responses.items():
        color = getattr(Colors, name.upper(), Colors.RESET)
        print(f"{color}{name}:{Colors.RESET} {response}\n")


# =============================================================================
# Run a scenario (uncomment to try)
# =============================================================================
if __name__ == "__main__":
    # Uncomment the scenario you want to run:

    # scenario_two_characters()
    # scenario_custom_characters()
    # scenario_conversation()
    # scenario_direct_message()
    scenario_village_meeting()
