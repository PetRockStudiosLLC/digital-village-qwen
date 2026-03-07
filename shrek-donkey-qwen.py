# =============================================================================
# Shrek and Donkey - Qwen3-TTS Local GPU Version
# =============================================================================
# Loads Qwen3-TTS model locally using GPU
# Press Ctrl+C to stop.
# =============================================================================

# -*- coding: utf-8 -*-
import os
import sys
import datetime
import warnings

# Suppress warnings
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

if sys.platform == "win32":
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

os.environ["PYTHONIOENCODING"] = "utf-8"

from colorama import init

init(autoreset=True)

from digital_village.village import Village
from digital_village.qwen_tts import get_qwen_tts


class C:
    RESET = "\033[0m"
    SHREK = "\033[92m"
    DONKEY = "\033[93m"
    GRAY = "\033[90m"
    INFO = "\033[94m"
    TTS = "\033[96m"


CHAR_COLORS = {"Shrek": C.SHREK, "Donkey": C.DONKEY}


def get_color(name):
    return CHAR_COLORS.get(name, C.SHREK)


def save_conversation(participants, all_messages, output_folder="output"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(output_folder, f"shrek_donkey_qwen_{timestamp}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Shrek and Donkey (Qwen3-TTS Local GPU)\n")
        f.write(f"{'=' * 50}\n")
        f.write(f"Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 50}\n\n")
        for speaker, message in all_messages:
            f.write(f"{speaker}: {message}\n\n")

    print(f"\n{C.GRAY}[Saved to {filename}]{C.RESET}")


def main():
    # ============ CONFIGURATION ============
    LM_STUDIO_HOST = "http://192.168.56.1:6842"
    
    SPEAKER_FOR_CHARACTER = {
        "Shrek": "ryan",
        "Donkey": "ryan",
    }
    
    # Emotions for each character (used with voice cloning + instruct)
    EMOTION_FOR_CHARACTER = {
        "Shrek": "grumpy, angry, deep voice, sarcastic",
        "Donkey": "happy, excited, energetic, enthusiastic",
    }
    
    # Save audio files
    SAVE_AUDIO = True
    AUDIO_FOLDER = "output/audio"
    
    # Audio counter
    audio_count = [0]
    
    def get_audio_path(speaker):
        audio_count[0] += 1
        import os
        os.makedirs(AUDIO_FOLDER, exist_ok=True)
        return os.path.join(AUDIO_FOLDER, f"{audio_count[0]:03d}_{speaker}.wav")
    
    STARTER_MESSAGE = "Hey Donkey, what are you doing here?"
    NUM_TURNS = 5
    # ======================================

    import requests

    # Check LM Studio
    try:
        r = requests.get(f"{LM_STUDIO_HOST}/v1/models", timeout=5)
        if r.status_code == 200:
            models = r.json()
            print(f"{C.GRAY}LM Studio: {len(models.get('data', []))} models loaded{C.RESET}")
    except Exception as e:
        print(f"{C.SHREK}Error: Cannot connect to LM Studio at {LM_STUDIO_HOST}{C.RESET}")
        return

    village = Village(
        model="qwen/qwen3.5-9b",
        api_host=LM_STUDIO_HOST,
    )

    shrek = village.add_villager(
        name="Shrek",
        system_prompt="""You are Shrek from Shrek. You are grumpy but lovable, sarcastic, and speaks in a gruff Scottish accent.
You love onions, swamps, and being left alone. You often say 'Better out than in.'
IMPORTANT: Keep responses VERY SHORT - 1-2 sentences max, about 50-100 words total. No long stories.""",
        description="A grumpy ogre who loves his swamp",
    )

    donkey = village.add_villager(
        name="Donkey",
        system_prompt="""You are Donkey from Shrek. You are talkative, optimistic, loyal, and very friendly.
You love singing, making friends, and annoying Shrek. You never stop talking.
IMPORTANT: Keep responses VERY SHORT - 1-2 sentences max, about 50-100 words total. No long stories.""",
        description="A loud, friendly donkey who won't shut up",
    )

    # Setup TTS with voice cloning + emotions
    tts = None
    try:
        # Use clone mode with emotions via instruct
        tts = get_qwen_tts(
            voice_mode="clone",  # Use voice cloning
            language="English",
            voice_folder="voices",
            model_folder="models",
        )
        print(f"{C.GRAY}Qwen3-TTS: Loading model (GPU, voice cloning + emotions)...{C.RESET}")
        
        # Load custom voices from voices/ folder
        tts.load_voice("Shrek")
        tts.load_voice("Donkey")
        
    except Exception as e:
        print(f"{C.SHREK}TTS Error: {e}{C.RESET}")
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print(f"{C.SHREK}TTS Error: {e}{C.RESET}")
        import traceback
        traceback.print_exc()

    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.GRAY}  Shrek and Donkey (Qwen3-TTS Local GPU){C.RESET}")
    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.INFO}Press Ctrl+C to stop{C.RESET}\n")

    all_messages = []
    participants = ["Shrek", "Donkey"]

    # Shrek starts
    speaker = "Shrek"
    print(f"{get_color(speaker)}{speaker}:{C.RESET} {STARTER_MESSAGE}")
    all_messages.append((speaker, STARTER_MESSAGE))

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
        f"Shrek says: {STARTER_MESSAGE}", stream_callback=stream_handler
    )
    if not response:
        print(f"{C.SHREK}[Warning: Empty response from Donkey]{C.RESET}")
    print()
    all_messages.append(("Donkey", response or ""))

    # TTS for Donkey - SYNCHRONOUS (waits for completion)
    if tts and response:
        emotion = EMOTION_FOR_CHARACTER.get("Donkey", "")
        tts.instruct = emotion  # Set emotion
        print(f"{C.TTS}[TTS: Donkey]{C.RESET} ", end="", flush=True)
        try:
            tts.speak(response, wait=True, show_progress=True, voice_name="Donkey", save_path=get_audio_path("Donkey") if SAVE_AUDIO else None)
        except Exception as e:
            print(f"{C.SHREK}TTS Error: {e}{C.RESET}")

    turn = 0
    try:
        while turn < NUM_TURNS:
            speaker = participants[turn % 2]
            color = get_color(speaker)

            context_parts = [f"{s}: {m}" for s, m in all_messages]
            context = f"Continue the conversation naturally.\n\n" + "\n".join(context_parts)

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
            if not response:
                print(f"{C.SHREK}[Warning: Empty response from {speaker}]{C.RESET}")
            print()
            all_messages.append((speaker, response or ""))

            # TTS - SYNCHRONOUS (waits for completion before next turn)
            if tts and response:
                emotion = EMOTION_FOR_CHARACTER.get(speaker, "")
                tts.instruct = emotion  # Set emotion
                print(f"{C.TTS}[TTS: {speaker}]{C.RESET} ", end="", flush=True)
                try:
                    tts.speak(response, wait=True, show_progress=True, voice_name=speaker, save_path=get_audio_path(speaker) if SAVE_AUDIO else None)
                except Exception as e:
                    print(f"{C.SHREK}TTS Error: {e}{C.RESET}")

            turn += 1

    except KeyboardInterrupt:
        print(f"\n\n{C.GRAY}Conversation stopped.{C.RESET}")

    save_conversation(participants, all_messages)


if __name__ == "__main__":
    main()
