# =============================================================================
# TEMPLATE: Continuous Loop Conversation
# =============================================================================
# Characters loop forever. Edit starter message and run!
# Press Ctrl+C to stop. Conversation saves to timestamped file.
# =============================================================================

# -*- coding: utf-8 -*-
import os
import sys
import datetime

# Fix Windows Unicode output
if sys.platform == "win32":
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

os.environ["PYTHONIOENCODING"] = "utf-8"

from colorama import init

init(autoreset=True)

from digital_village import Village
from digital_village.tts import ChatterboxTTS, get_tts


# Character colors - extend as needed
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Default characters
    ALICE = "\033[96m"  # Cyan
    BOB = "\033[93m"  # Yellow
    CAROL = "\033[95m"  # Magenta
    DAISY = "\033[92m"  # Green

    # System
    GRAY = "\033[90m"
    INFO = "\033[94m"


# Map character names to colors
CHAR_COLORS = {
    "Alice": C.ALICE,
    "Bob": C.BOB,
    "Carol": C.CAROL,
    "Daisy": C.DAISY,
}


def get_color(name: str) -> str:
    """Get color for a character, or default to cyan."""
    return CHAR_COLORS.get(name, C.ALICE)


def save_conversation(
    participants: list,
    all_messages: list,
    starter_message: str,
    output_folder: str = "output",
):
    """Save conversation to a timestamped text file in output folder."""
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(output_folder, f"conversation_{timestamp}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Digital Village Conversation\n")
        f.write(f"{'=' * 50}\n")
        f.write(f"Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Characters: {', '.join(participants)}\n")
        f.write(f"Starter: {starter_message}\n")
        f.write(f"{'=' * 50}\n\n")

        for speaker, message in all_messages:
            f.write(f"{speaker}: {message}\n\n")

    print(f"\n{C.GRAY}[Conversation saved to {filename}]{C.RESET}")
    return filename


def main():
    # ============================================
    # EDIT YOUR SETTINGS HERE
    # ============================================

    # Characters: 2-4 from ['Alice', 'Bob', 'Carol', 'Daisy']
    village = Village()
    village.setup_default_villagers(2)  # Change to 2, 3, or 4

    # Starting message
    starter_message = "I just found a mysterious treasure map in the forest!"

    # How many times to respond after the first message
    num_turns = 10

    # Output folder for saved conversations
    output_folder = "output"

    # TTS Settings (Text-to-Speech)
    enable_tts = True  # Set to False to disable TTS
    tts_api_url = "http://localhost:8004"  # Your Chatterbox port

    # Voice for each character (use names from Chatterbox: Alice, Adrian, Elena, etc.)
    voice_for_character = {
        "Alice": "Alice",
        "Bob": "Adrian",  # Male voice
        "Carol": "Elena",
        "Daisy": "Cora",
    }

    # TTS settings
    tts_speed = 1.0  # Playback speed (1.0 = normal)

    # ============================================
    # END SETTINGS
    # ============================================

    participants = village.get_character_names()

    # Initialize TTS
    tts = None
    if enable_tts:
        try:
            tts = get_tts(api_url=tts_api_url)
            print(f"{C.GRAY}TTS Enabled: {tts_api_url}{C.RESET}")
        except Exception as e:
            print(f"{C.GRAY}TTS Error: {e}{C.RESET}")

    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.GRAY}  Digital Village - Continuous Conversation{C.RESET}")
    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.INFO}Characters: {participants}{C.RESET}")
    print(f"{C.INFO}Press Ctrl+C to stop{C.RESET}")
    if enable_tts:
        print(f"{C.INFO}TTS: Enabled{C.RESET}")
    print()

    # Track all messages for saving
    all_messages = []

    # First message
    speaker = participants[0]
    color = get_color(speaker)
    print(f"\n{color}{speaker}:{C.RESET} {starter_message}")
    all_messages.append((speaker, starter_message))

    # Get first response
    try:
        import sys

        villager = village.villagers[speaker]
        print(f"\n{color}{speaker}:{C.RESET} ", end="", flush=True)

        full_response = ""

        def chunk_handler(chunk):
            nonlocal full_response
            full_response += chunk
            try:
                print(chunk, end="", flush=True)
            except (UnicodeEncodeError, AttributeError):
                sys.stdout.buffer.write(chunk.encode("utf-8"))
                sys.stdout.buffer.flush()

        response = villager.respond_to(
            f"Message from {speaker}: {starter_message}", stream_callback=chunk_handler
        )
        print()
        all_messages.append((speaker, response))

        # TTS for response
        if tts and response:
            voice = voice_for_character.get(speaker, "Alice")
            tts.set_voice(voice)
            try:
                tts.speak(response, wait=True, speed=tts_speed)
            except Exception as e:
                pass

    except KeyboardInterrupt:
        save_conversation(participants, all_messages, starter_message)
        return

    # Continuous loop
    turn = 0
    try:
        while turn < num_turns:
            next_idx = (turn + 1) % len(participants)
            speaker = participants[next_idx]
            color = get_color(speaker)

            # Build context from all previous messages
            context_parts = [f"{s}: {m}" for s, m in all_messages]
            context = (
                f"Continue the conversation naturally.\n\nConversation:\n"
                + "\n".join(context_parts)
            )

            villager = village.villagers[speaker]
            print(f"\n{color}{speaker}:{C.RESET} ", end="", flush=True)

            full_response = ""

            def chunk_handler(chunk):
                nonlocal full_response
                full_response += chunk
                try:
                    print(chunk, end="", flush=True)
                except (UnicodeEncodeError, AttributeError):
                    sys.stdout.buffer.write(chunk.encode("utf-8"))
                    sys.stdout.buffer.flush()

            response = villager.respond_to(context, stream_callback=chunk_handler)
            print()
            all_messages.append((speaker, response))

            # TTS for response
            if tts and response:
                voice = voice_for_character.get(speaker, "Alice")
                tts.set_voice(voice)
                try:
                    tts.speak(response, wait=True, speed=tts_speed)
                except Exception as e:
                    pass

            turn += 1

    except KeyboardInterrupt:
        print(f"\n\n{C.GRAY}Conversation stopped.{C.RESET}")

    # Save when done
    save_conversation(participants, all_messages, starter_message, output_folder)


if __name__ == "__main__":
    main()
