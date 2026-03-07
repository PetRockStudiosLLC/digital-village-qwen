# =============================================================================
# Finn and Jake - Qwen3-TTS Local GPU Version
# =============================================================================
# Loads Qwen3-TTS model locally using GPU
# Press Ctrl+C to stop.
# =============================================================================

# -*- coding: utf-8 -*-
import os
import sys
import datetime
import warnings
import numpy as np

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
    FINN = "\033[92m"
    JAKE = "\033[93m"
    GRAY = "\033[90m"
    INFO = "\033[94m"
    TTS = "\033[96m"


CHAR_COLORS = {"Finn": C.FINN, "Jake": C.JAKE}


def get_color(name):
    return CHAR_COLORS.get(name, C.FINN)


def save_conversation(participants, all_messages, output_folder="output"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(output_folder, f"finn_jake_qwen_{timestamp}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Finn and Jake (Qwen3-TTS Local GPU)\n")
        f.write(f"{'=' * 50}\n")
        f.write(f"Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 50}\n\n")
        for speaker, message in all_messages:
            f.write(f"{speaker}: {message}\n\n")

    print(f"\n{C.GRAY}[Saved to {filename}]{C.RESET}")
    
    return filename


def combine_audio_files(audio_folder, output_filename):
    """Combine all audio files in folder into one."""
    if not os.path.exists(audio_folder):
        print(f"{C.GRAY}[No audio files to combine]{C.RESET}")
        return
    
    import glob
    import soundfile as sf
    
    audio_files = sorted(glob.glob(os.path.join(audio_folder, "*.wav")))
    
    if not audio_files:
        print(f"{C.GRAY}[No audio files to combine]{C.RESET}")
        return
    
    print(f"{C.GRAY}[Combining {len(audio_files)} audio files...]{C.RESET}")
    
    combined = []
    sample_rate = 24000
    
    for filepath in audio_files:
        audio_data, sr = sf.read(filepath)
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        combined.append(audio_data)
        if audio_files.index(filepath) < len(audio_files) - 1:
            pause_duration = np.random.uniform(0.25, 1.25)
            silence = np.zeros(int(sr * pause_duration))
            combined.append(silence)
    
    final_audio = np.concatenate(combined)
    sf.write(output_filename, final_audio, sr)
    print(f"{C.GRAY}[Saved combined audio to {output_filename}]{C.RESET}")


def main():
    # ============ CONFIGURATION ============
    LM_STUDIO_HOST = "http://192.168.56.1:6842"
    
    # Emotions for each character (used with voice cloning + instruct)
    EMOTION_FOR_CHARACTER = {
        "Finn": "young, heroic, energetic, adventurous",
        "Jake": "laid-back, chill, funny, silly",
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
    
    STARTER_MESSAGE = input("Enter starter prompt (or press Enter for default): ").strip()
    if not STARTER_MESSAGE:
        STARTER_MESSAGE = "Jake, I think I heard something in the bushes!"
    
    try:
        NUM_TURNS = int(input("Number of turns: ").strip())
    except ValueError:
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
        print(f"{C.FINN}Error: Cannot connect to LM Studio at {LM_STUDIO_HOST}{C.RESET}")
        return

    village = Village(
        model="qwen/qwen3.5-9b",
        api_host=LM_STUDIO_HOST,
    )

    finn = village.add_villager(
        name="Finn",
        system_prompt="""You are Finn, the Human from Adventure Time. You are heroic, brave, optimistic, and always ready to help others.
You love adventures, sword-fighting, and doing the right thing. You live in the Tree House with Jake.
IMPORTANT: Keep responses VERY SHORT - 1-2 sentences max, about 50-100 words total. No long stories.""",
        description="A heroic 12-year-old human boy",
    )

    jake = village.add_villager(
        name="Jake",
        system_prompt="""You are Jake the Dog from Adventure Time. You are a magical stretchy dog who is laid-back, chill, and always supportive of Finn.
You love eating, sleeping, and playing video games. You can stretch your body into any shape.
IMPORTANT: Keep responses VERY SHORT - 1-2 sentences max, about 50-100 words total. No long stories.""",
        description="A magical stretchy dog",
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
        tts.load_voice("Finn")
        tts.load_voice("Jake")
        
    except Exception as e:
        print(f"{C.FINN}TTS Error: {e}{C.RESET}")
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print(f"{C.FINN}TTS Error: {e}{C.RESET}")
        import traceback
        traceback.print_exc()

    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.GRAY}  Finn and Jake (Qwen3-TTS Local GPU){C.RESET}")
    print(f"{C.GRAY}{'=' * 50}{C.RESET}")
    print(f"{C.INFO}Press Ctrl+C to stop{C.RESET}\n")

    all_messages = []
    participants = ["Finn", "Jake"]

    # Finn starts
    speaker = "Finn"
    print(f"{get_color(speaker)}{speaker}:{C.RESET} {STARTER_MESSAGE}")
    all_messages.append((speaker, STARTER_MESSAGE))

    # Jake responds
    print(f"\n{get_color('Jake')}Jake:{C.RESET} ", end="", flush=True)

    full_response = ""

    def stream_handler(chunk):
        nonlocal full_response
        full_response += chunk
        try:
            print(chunk, end="", flush=True)
        except:
            sys.stdout.buffer.write(chunk.encode("utf-8"))
            sys.stdout.buffer.flush()

    response = village.villagers["Jake"].respond_to(
        f"Finn says: {STARTER_MESSAGE}", stream_callback=stream_handler
    )
    if not response:
        print(f"{C.FINN}[Warning: Empty response from Jake]{C.RESET}")
    print()
    all_messages.append(("Jake", response or ""))

    # TTS for Jake - SYNCHRONOUS (waits for completion)
    if tts and response:
        emotion = EMOTION_FOR_CHARACTER.get("Jake", "")
        tts.instruct = emotion  # Set emotion
        print(f"{C.TTS}[TTS: Jake]{C.RESET} ", end="", flush=True)
        try:
            tts.speak(response, wait=False, show_progress=True, voice_name="Jake", save_path=get_audio_path("Jake") if SAVE_AUDIO else None, non_streaming=True)
        except Exception as e:
            print(f"{C.FINN}TTS Error: {e}{C.RESET}")

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
                print(f"{C.FINN}[Warning: Empty response from {speaker}]{C.RESET}")
            print()
            all_messages.append((speaker, response or ""))

            # TTS - SYNCHRONOUS (waits for completion before next turn)
            if tts and response:
                emotion = EMOTION_FOR_CHARACTER.get(speaker, "")
                tts.instruct = emotion  # Set emotion
                print(f"{C.TTS}[TTS: {speaker}]{C.RESET} ", end="", flush=True)
                try:
                    tts.speak(response, wait=False, show_progress=True, voice_name=speaker, save_path=get_audio_path(speaker) if SAVE_AUDIO else None, non_streaming=True)
                except Exception as e:
                    print(f"{C.FINN}TTS Error: {e}{C.RESET}")

            turn += 1

    except KeyboardInterrupt:
        print(f"\n\n{C.GRAY}Conversation stopped.{C.RESET}")

    txt_file = save_conversation(participants, all_messages)
    
    if SAVE_AUDIO and audio_count[0] > 0:
        combine_audio_files(AUDIO_FOLDER, txt_file.replace(".txt", "_combined.wav"))


if __name__ == "__main__":
    main()
