# =============================================================================
# Shrek and Donkey Conversation
# =============================================================================
# Shrek and Donkey chat with TTS using your custom voices!
# Press Ctrl+C to stop.
# =============================================================================

# -*- coding: utf-8 -*-
import os
import sys
import datetime

if sys.platform == "win32":
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

os.environ["PYTHONIOENCODING"] = "utf-8"

from colorama import init

init(autoreset=True)

from digital_village import Village, create_character
from digital_village.tts import ChatterboxTTS


class C:
    RESET = "\033[0m"
    SHREK = "\033[92m"
    DONKEY = "\033[93m"
    GRAY = "\033[90m"
    INFO = "\033[94m"


CHAR_COLORS = {"Shrek": C.SHREK, "Donkey": C.DONKEY}


def get_color(name):
    return CHAR_COLORS.get(name, C.SHREK)


def save_conversation(participants, all_messages, output_folder="output"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(output_folder, f"shrek_donkey_{timestamp}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Shrek and Donkey Conversation\n")
        f.write(f"{'=' * 50}\n")
        f.write(f"Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 50}\n\n")
        for speaker, message in all_messages:
            f.write(f"{speaker}: {message}\n\n")

    print(f"\n{C.GRAY}[Saved to {filename}]{C.RESET}")


def main():
    # Create characters
    shrek = create_character(
        name="Shrek",
        role="an ogre living in a swamp",
        personality=["Gruff but good-hearted", "Loves privacy", "Sarcastic but loyal"],
    )

    donkey = create_character(
        name="Donkey",
        role="a chatty donkey",
        personality=["Extremely talkative", "Optimistic", "Very friendly and loyal"],
    )

    village = Village()
    village.setup_characters([shrek, donkey])

    # TTS
    enable_tts = True

    # Your custom voices from Chatterbox
    voice_for_character = {
        "Shrek": ("Shrek.wav", "clone"),
        "Donkey": ("Donkey.wav", "clone"),
    }

    # Conversation settings
    starter_message = "Hey Donkey, what are you doing here?"
    num_turns = 5  # How many back-and-forths

    participants = ["Shrek", "Donkey"]

    # Initialize TTS
    tts = None
    if enable_tts:
        try:
            tts = ChatterboxTTS("http://localhost:8004")
            print(f"{C.GRAY}TTS Enabled{C.RESET}")
        except Exception as e:
            print(f"{C.GRAY}TTS Error: {e}{C.RESET}")

    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.GRAY}  Shrek and Donkey{C.RESET}")
    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.INFO}Press Ctrl+C to stop{C.RESET}\n")

    all_messages = []

    # Shrek starts
    speaker = "Shrek"
    print(f"{get_color(speaker)}{speaker}:{C.RESET} {starter_message}")
    all_messages.append((speaker, starter_message))

    # Donkey responds (first turn)
    print(f"\n{get_color('Donkey')}Donkey:{C.RESET} ", end="", flush=True)

    full_response = ""

    def stream_handler(chunk):
        nonlocal full_response
        full_response += chunk
        try:
            print(chunk, end="", flush=True)
        except:
            sys.stdout.buffer.write(chunk.encode("utf-8"))
            sys.stdout.buffer.flush()

    response = village.villagers["Donkey"].respond_to(
        f"Shrek says: {starter_message}", stream_callback=stream_handler
    )
    print()
    all_messages.append(("Donkey", response))

    # TTS for Donkey
    if tts and response:
        tts.use_cloned_voice("Donkey.wav")
        tts.speak(response, wait=True)

    # Loop for remaining turns
    turn = 0
    try:
        while turn < num_turns:
            # Alternate speakers
            speaker = participants[turn % 2]  # Shrek, Donkey, Shrek, Donkey...
            color = get_color(speaker)

            # Build context from all previous messages
            context_parts = [f"{s}: {m}" for s, m in all_messages]
            context = f"Continue the conversation naturally.\n\n" + "\n".join(
                context_parts
            )

            villager = village.villagers[speaker]
            print(f"\n{color}{speaker}:{C.RESET} ", end="", flush=True)

            full_response = ""

            def stream_handler2(chunk):
                nonlocal full_response
                full_response += chunk
                try:
                    print(chunk, end="", flush=True)
                except:
                    sys.stdout.buffer.write(chunk.encode("utf-8"))
                    sys.stdout.buffer.flush()

            response = villager.respond_to(context, stream_callback=stream_handler2)
            print()
            all_messages.append((speaker, response))

            # TTS - wait for it to finish before next turn!
            if tts and response:
                voice_info = voice_for_character.get(speaker, ("Shrek.wav", "clone"))
                tts.use_cloned_voice(voice_info[0])
                tts.speak(response, wait=True)  # BLOCK until done!

            turn += 1

    except KeyboardInterrupt:
        print(f"\n\n{C.GRAY}Conversation stopped.{C.RESET}")

    save_conversation(participants, all_messages)


if __name__ == "__main__":
    main()
