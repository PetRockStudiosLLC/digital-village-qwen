# -*- coding: utf-8 -*-
"""
Example script demonstrating the Digital Village package.

Before running:
1. Install LM Studio and load a model
2. Start the LM Studio API server
3. Install dependencies: pip install -r requirements.txt
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


def get_color(name: str) -> str:
    colors = {
        "Alice": Colors.ALICE,
        "Bob": Colors.BOB,
        "Carol": Colors.CAROL,
        "Daisy": Colors.DAISY,
    }
    return colors.get(name, Colors.RESET)


def main():
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Digital Village Demo{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}\n")

    print(f"{Colors.INFO}Make sure LM Studio is running!{Colors.RESET}\n")

    # Create village - specify number of characters (1-4)
    village = Village()
    village.setup_default_villagers(num_characters=4)

    print(
        f"{Colors.GRAY}Village initialized:{Colors.RESET} {village.get_character_names()}\n"
    )

    # ===== SCENARIO 1: New Resident =====
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Scenario 1: New Resident Introduction{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}\n")

    print(
        f"{Colors.ALICE}Alice:{Colors.RESET} Hello everyone! I just moved to the village."
    )

    # Broadcast to all characters
    for villager_name in ["Bob", "Carol", "Daisy"]:
        villager = village.villagers[villager_name]
        color = get_color(villager_name)

        print(f"\n{color}{villager_name}:{Colors.RESET} ", end="", flush=True)

        def stream_handler(chunk):
            print(chunk, end="", flush=True)

        villager.respond_to(
            "[Broadcast from Alice]: Hello everyone! I just moved to the village.",
            stream_callback=stream_handler,
        )
        print()

    # ===== SCENARIO 2: Direct Message =====
    print(f"\n{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Scenario 2: Direct Message (Bob to Carol){Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}\n")

    print(f"{Colors.BOB}Bob:{Colors.RESET} (asking Carol directly)")
    response = village.direct_message(
        "Bob", "Carol", "Do you remember the old stories about the bridge?"
    )
    print(f"{Colors.CAROL}Carol:{Colors.RESET} {response}\n")

    # ===== SCENARIO 3: Back-and-forth =====
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Scenario 3: Back-and-Forth Conversation{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}\n")

    village2 = Village()
    village2.setup_default_villagers(num_characters=3)

    print(
        f"{Colors.ALICE}Alice:{Colors.RESET} I have an idea for the village festival!"
    )
    print(f"{Colors.BOB}Bob:{Colors.RESET} What is it?")

    responses = village2.conversation(
        participants=["Alice", "Bob", "Carol"],
        messages=[
            "I have an idea for the village festival!",
            "What is it?",
            "That sounds wonderful!",
        ],
    )

    # ===== SCENARIO 4: Custom Characters =====
    print(f"\n{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Scenario 4: Custom Characters{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}\n")

    # Create custom characters
    marcus = create_character(
        name="Marcus",
        role="the village tavern keeper",
        personality=[
            "Friendly and welcoming to all travelers",
            "Knows all the gossip in town",
            "Generous with stories and ale",
        ],
    )

    elena = create_character(
        name="Elena",
        role="the village healer",
        personality=["Compassionate and gentle", "Knowledgeable about herbs"],
    )

    custom_village = Village()
    custom_village.setup_characters([marcus, elena])

    print(
        f"{Colors.INFO}Custom characters: {custom_village.get_character_names()}{Colors.RESET}\n"
    )

    print(f"{Colors.ALICE}Marcus:{Colors.RESET} Welcome to my tavern!")
    response = custom_village.direct_message(
        "Marcus", "Elena", "Nice tavern you have here!"
    )
    print(f"{Colors.DAISY}Elena:{Colors.RESET} {response}\n")

    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.GRAY}  Done!{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")


if __name__ == "__main__":
    main()
