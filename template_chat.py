# =============================================================================
# TEMPLATE: Direct Chat with Character (with TTS)
# =============================================================================
# Chat directly with a character! Type your messages and get TTS responses.
# Press Ctrl+C to exit.
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
from digital_village.tts import ChatterboxTTS


# Character colors
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    YOU = "\033[96m"  # Cyan for user
    ALICE = "\033[96m"  # Cyan
    BOB = "\033[93m"  # Yellow
    CAROL = "\033[95m"  # Magenta
    DAISY = "\033[92m"  # Green
    GRAY = "\033[90m"
    INFO = "\033[94m"


CHAR_COLORS = {
    "Alice": C.ALICE,
    "Bob": C.BOB,
    "Carol": C.CAROL,
    "Daisy": C.DAISY,
}


def get_color(name: str) -> str:
    return CHAR_COLORS.get(name, C.ALICE)


def main():
    # ============================================
    # EDIT YOUR SETTINGS HERE
    # ============================================

    # Choose your character: 'Alice', 'Bob', 'Carol', or 'Daisy'
    character_name = "Bob"

    # Choose the voice (from Chatterbox: Alice, Adrian, Elena, Cora, etc.)
    character_voice = "Adrian"

    # TTS settings
    enable_tts = True
    tts_api_url = "http://localhost:8004"

    # ============================================
    # END SETTINGS
    # ============================================

    # Setup
    village = Village()
    village.setup_default_villagers(4)

    villager = village.villagers[character_name]
    color = get_color(character_name)

    # Setup TTS
    tts = None
    if enable_tts:
        try:
            tts = ChatterboxTTS(tts_api_url, voice=character_voice)
            print(f"{C.GRAY}TTS Enabled: {tts_api_url}{C.RESET}")
        except Exception as e:
            print(f"{C.GRAY}TTS Error: {e}{C.RESET}")

    # Intro
    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.GRAY}  Direct Chat with {character_name}{C.RESET}")
    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.INFO}Type your message and press Enter to chat.{C.RESET}")
    print(f"{C.INFO}Press Ctrl+C to exit.{C.RESET}")
    print()

    # Initial greeting from character
    print(f"{color}{character_name}:{C.RESET} ", end="", flush=True)

    import sys

    def stream_handler(chunk):
        try:
            print(chunk, end="", flush=True)
        except:
            sys.stdout.buffer.write(chunk.encode("utf-8"))
            sys.stdout.buffer.flush()

    greeting = villager.respond_to(
        "Say hello and introduce yourself warmly.", stream_callback=stream_handler
    )
    print()

    # TTS greeting
    if tts:
        try:
            tts.speak(greeting, wait=True)
        except:
            pass

    # Chat loop
    print()
    while True:
        try:
            # Get user input
            user_input = input(f"{C.YOU}You:{C.RESET} ").strip()
            if not user_input:
                continue

            # Character responds
            print(f"{color}{character_name}:{C.RESET} ", end="", flush=True)

            full_response = ""

            def stream_handler2(chunk):
                nonlocal full_response
                full_response += chunk
                try:
                    print(chunk, end="", flush=True)
                except:
                    sys.stdout.buffer.write(chunk.encode("utf-8"))
                    sys.stdout.buffer.flush()

            response = villager.respond_to(user_input, stream_callback=stream_handler2)
            print()

            # TTS response
            if tts and response:
                try:
                    tts.speak(response, wait=True)
                except:
                    pass

        except KeyboardInterrupt:
            print(f"\n\n{C.GRAY}Chat ended.{C.RESET}")
            break
        except Exception as e:
            print(f"\n{C.GRAY}Error: {e}{C.RESET}")
            break


if __name__ == "__main__":
    main()
