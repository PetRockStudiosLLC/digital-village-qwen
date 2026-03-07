# =============================================================================
# Shrek and Donkey - Fish Speech Version
# =============================================================================
# Uses Fish Speech TTS instead of Chatterbox
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
from digital_village.fish_tts import FishSpeechTTS


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
    filename = os.path.join(output_folder, f"shrek_donkey_fish_{timestamp}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Shrek and Donkey (Fish Speech)\n")
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

    # ============ FISH SPEECH SETTINGS ============
    enable_tts = True
    fish_api_url = "http://localhost:8080"  # Fish Speech default port

    # Voice settings for each character
    # Option 1: Use voice cloning with reference audio files
    # voice_for_character = {
    #     "Shrek": ("shrek_ref.wav", "clone"),
    #     "Donkey": ("donkey_ref.wav", "clone"),
    # }

    # Option 2: Use preset voices (voice IDs from Fish Speech)
    voice_for_character = {
        "Shrek": "shrek_voice",  # Replace with your voice ID
        "Donkey": "donkey_voice",  # Replace with your voice ID
    }

    # Emotion markers (Fish Speech feature)
    # Add emotion markers to text for more expressive speech
    emotion_for_character = {
        "Shrek": "(gruff) ",  # Gruff tone
        "Donkey": "(excited) ",  # Enthusiastic tone
    }

    # ============ CONVERSATION SETTINGS ============
    starter_message = "Hey Donkey, what are you doing here?"
    num_turns = 5
    # ============================================

    participants = ["Shrek", "Donkey"]

    # Initialize Fish Speech TTS
    tts = None
    if enable_tts:
        try:
            tts = FishSpeechTTS(fish_api_url)
            print(f"{C.GRAY}Fish Speech TTS Enabled: {fish_api_url}{C.RESET}")

            # Load voice clones if using clone mode
            # tts.use_voice_clone("shrek_ref.wav")
            # tts.use_preset("voice_id_here")

        except Exception as e:
            print(f"{C.GRAY}TTS Error: {e}{C.RESET}")

    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.GRAY}  Shrek and Donkey (Fish Speech){C.RESET}")
    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.INFO}Press Ctrl+C to stop{C.RESET}\n")

    all_messages = []

    # Shrek starts
    speaker = "Shrek"
    print(f"{get_color(speaker)}{speaker}:{C.RESET} {starter_message}")
    all_messages.append((speaker, starter_message))

    # Donkey responds
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
        # Add emotion marker
        emotion = emotion_for_character.get("Donkey", "")
        tts_text = emotion + response
        tts.speak(tts_text, wait=True)

    # Loop
    turn = 0
    try:
        while turn < num_turns:
            speaker = participants[turn % 2]
            color = get_color(speaker)

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

            # TTS with emotion
            if tts and response:
                voice_info = voice_for_character.get(speaker, ("", "preset"))
                emotion = emotion_for_character.get(speaker, "")

                # Set voice
                if isinstance(voice_info, tuple):
                    if voice_info[1] == "clone":
                        tts.use_voice_clone(voice_info[0])
                    else:
                        tts.use_preset(voice_info[0])
                else:
                    tts.use_preset(voice_info)

                # Add emotion and speak
                tts_text = emotion + response
                tts.speak(tts_text, wait=True)

            turn += 1

    except KeyboardInterrupt:
        print(f"\n\n{C.GRAY}Conversation stopped.{C.RESET}")

    save_conversation(participants, all_messages)


if __name__ == "__main__":
    main()
