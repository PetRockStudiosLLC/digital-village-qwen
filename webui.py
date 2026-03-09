"""Web UI for AI Character Chat Generator."""

import os
import json
import glob
import gradio as gr
from datetime import datetime

from digital_village.village import Village
from digital_village.qwen_tts import Qwen3TTS


CHARACTERS_FOLDER = "characters"
SETTINGS_FILE = "data/settings.json"

# Global dialogue constraint for voice-only output (no metadata/descriptions)
DIALOGUE_CONSTRAINT = """
GLOBAL DIALOGUE CONSTRAINT: THE "NO-METADATA" PROTOCOL
Strict Output Rule: 
- NO narrative descriptions or stage directions (e.g., do not output "He walks across the room" or "[Bender laughs]").
- NO introductory or concluding filler (e.g., do not output "Here is your dialogue:" or "Bender says:").
- NO internal thoughts or character state headers.
- NEVER include your character name in the response - the system adds that automatically.
- ONLY output the raw, spoken dialogue - just what the character says.

Failure State: If you include any text that is not intended to be read aloud by a voice actor, the generation is a failure. Treat this as a "Voice-Only" transmission.

---

TTS PRONUNCIATION RULE:
- Write all numbers as words (e.g., 'three-thousand' instead of '3000').
- Expand all abbreviations to their full phonetic sound (e.g., 'Doctor' instead of 'Dr.', 'Mister' instead of 'Mr.', 'Saint' instead of 'St.').
- The TTS will read exactly what you write, so write it to sound good when spoken.

SHORT-BURST CONSTRAINT:
- Strictly limit each character's dialogue block to a maximum of 60 words.
- Prioritize punchy, fast-paced exchanges over long speeches.
- Keep clips under 30 seconds - short and snappy is better.

PUNCTUATION-FOR-PROSODY RULE:
- Use expressive punctuation to guide the voice engine.
- Use ellipses (...) for hesitant pauses.
- Use multiple question marks (???) for extreme confusion.
- Use dashes (—) for abrupt interruptions or shifts in thought.
- Use exclamation marks (!) for emphasis and energy.
"""


def ensure_characters_folder():
    """Ensure characters folder exists."""
    os.makedirs(CHARACTERS_FOLDER, exist_ok=True)


def get_characters():
    """Get all saved characters."""
    ensure_characters_folder()
    characters = []
    for filename in os.listdir(CHARACTERS_FOLDER):
        if filename.endswith(".json"):
            filepath = os.path.join(CHARACTERS_FOLDER, filename)
            with open(filepath, "r") as f:
                characters.append(json.load(f))
    return characters


def get_voice_files():
    """Get available voice files."""
    voices_folder = "voices"
    if os.path.exists(voices_folder):
        files = [f for f in os.listdir(voices_folder) if f.endswith(".wav")]
        return [""] + sorted(files)
    return [""]


def transcribe_voice_file(voice_filename):
    """Auto-transcribe a voice file if transcript doesn't exist."""
    if not voice_filename:
        return "No voice file selected", ""
    
    voices_folder = "voices"
    wav_path = os.path.join(voices_folder, voice_filename)
    txt_path = wav_path.replace(".wav", ".txt")
    
    if not os.path.exists(wav_path):
        return f"Voice file not found: {voice_filename}", ""
    
    # Always regenerate transcript
    try:
        import whisper
        print(f"Transcribing {voice_filename}...")
        model = whisper.load_model("base")
        result = model.transcribe(wav_path)
        transcript = result["text"].strip()
        
        # Save transcript
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"Saved transcript: {txt_path}")
        return f"Transcript saved! ({len(transcript)} chars)", transcript
    except Exception as e:
        print(f"Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return f"Transcription error: {e}", ""


def load_character_for_edit(name):
    """Load a character for editing."""
    if not name:
        return "", "", "", "", "", "No character selected"
    
    safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
    filepath = os.path.join(CHARACTERS_FOLDER, f"{safe_name}.json")
    
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            char = json.load(f)
        return (
            char.get("name", ""),
            char.get("system_prompt", ""),
            char.get("voice_file", ""),
            char.get("emotion", ""),
            char.get("status_effect", "Normal"),
            f"Loaded: {name}"
        )
    return "", "", "", "", "Normal", f"Character not found: {name}"


# Common status effects
STATUS_EFFECTS = ["Normal", "Drunk", "Caffeinated", "Tired", "Angry", "Happy", "Sad", "Confused", "Excited", "Scared"]


def save_character(name, system_prompt, voice_file, emotion, status_effect="Normal"):
    """Save a character."""
    ensure_characters_folder()
    
    # Auto-transcribe voice file if selected
    if voice_file:
        transcribe_voice_file(voice_file)
    
    character = {
        "name": name,
        "system_prompt": system_prompt,
        "voice_file": voice_file,
        "emotion": emotion,
        "status_effect": status_effect
    }
    
    # Save as individual file
    safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
    filepath = os.path.join(CHARACTERS_FOLDER, f"{safe_name}.json")
    with open(filepath, "w") as f:
        json.dump(character, f, indent=2)
    
    return f"Character '{name}' saved!"


def delete_character(name):
    """Delete a character."""
    ensure_characters_folder()
    
    safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
    filepath = os.path.join(CHARACTERS_FOLDER, f"{safe_name}.json")
    
    if os.path.exists(filepath):
        os.remove(filepath)
        return f"Character '{name}' deleted!"
    return f"Character '{name}' not found!"


def combine_voice_files(source_folder, character_name):
    """Combine voice files from a folder into a single file in voices/."""
    if not source_folder:
        return "No folder selected", ""
    
    if not character_name:
        return "No character name provided", ""
    
    # If it's not an absolute path, assume it's a folder name in voices/UNREFINED
    folder_path = source_folder
    if not os.path.isabs(source_folder):
        folder_path = os.path.join("voices/UNREFINED", source_folder)
    
    if not os.path.exists(folder_path):
        return f"Folder not found: {folder_path}", ""
    
    # Find audio files
    files = []
    for ext in ["*.wav", "*.x-wav", "*.WAV", "*.mp3"]:
        files.extend(glob.glob(os.path.join(folder_path, ext)))
    files = sorted(files)
    
    if not files:
        return "No audio files found in folder", ""
    
    # Combine audio
    import soundfile as sf
    import numpy as np
    import random
    
    combined = []
    sample_rate = None
    
    for f in files:
        data, sr = sf.read(f)
        if len(data.shape) > 1:
            data = data.mean(axis=1)
        combined.append(data)
        sample_rate = sr
        pause = np.zeros(int(sr * random.uniform(0.3, 0.8)))
        combined.append(pause)
    
    result = np.concatenate(combined)
    
    # Save to voices folder with character name
    voices_folder = "voices"
    os.makedirs(voices_folder, exist_ok=True)
    output_path = os.path.join(voices_folder, f"{character_name}.wav")
    sf.write(output_path, result, sample_rate)
    
    duration = len(result) / sample_rate
    return f"Combined {len(files)} files → {character_name}.wav ({duration:.1f}s)", output_path


def get_unrefined_folders():
    """Get list of subfolders in voices/UNREFINED."""
    unrefined = "voices/UNREFINED"
    if os.path.exists(unrefined):
        folders = [f for f in os.listdir(unrefined) if os.path.isdir(os.path.join(unrefined, f))]
        return [""] + sorted(folders)
    return [""]


def load_json(filepath, default):
    """Load JSON file or return default."""
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return default


def save_json(filepath, data):
    """Save JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def get_settings():
    """Get settings."""
    return load_json(SETTINGS_FILE, {
        "lm_studio_host": "http://192.168.56.1:6842",
        "model_name": "qwen/qwen3.5-9b",
        "output_folder": "output",
    })


def chat_with_character(selected_characters, user_message, chat_history, status_overrides_text="", auto_playback=True):
    """Chat with selected character(s)."""
    # Handle string input from textbox
    if isinstance(selected_characters, str):
        if selected_characters:
            selected_characters = [c.strip() for c in selected_characters.split(",")]
        else:
            selected_characters = []
    
    status_overrides = parse_status_overrides(status_overrides_text)
    
    if not selected_characters:
        return chat_history, None, "Please select at least one character."
    
    if not user_message:
        return chat_history, None, "Please enter a message."
    
    settings = get_settings()
    characters = get_characters()
    
    # Filter to selected characters
    chars = [c for c in characters if c["name"] in selected_characters]
    
    if not chars:
        return chat_history, None, "Selected characters not found."
    
    # Apply status overrides
    for char in chars:
        if char["name"] in status_overrides:
            char["status_effect"] = status_overrides[char["name"]]
        elif "status_effect" not in char:
            char["status_effect"] = "Normal"
    
    # Setup Village
    village = Village(
        model=settings["model_name"],
        api_host=settings["lm_studio_host"],
    )
    
    # Add all characters to village
    for char in chars:
        base_prompt = char.get("system_prompt", "")
        if not base_prompt:
            base_prompt = f"You are {char['name']}. Keep responses SHORT - 1-2 sentences max."
        
        # Add status effect tone
        status_effect = char.get("status_effect", "Normal")
        status_tone = get_status_tone_prompt(status_effect, char["name"])
        
        full_prompt = base_prompt + "\n\n" + DIALOGUE_CONSTRAINT
        if status_tone:
            full_prompt += f"\n\nSTATUS EFFECT: {status_tone}"
        full_prompt += "\n\nIMPORTANT: Always speak in FIRST PERSON as if you are the character. Never refer to yourself by name or speak in third person."
        
        village.add_villager(
            name=char["name"],
            system_prompt=full_prompt,
            description=f"Character: {char['name']}",
        )
    
    # Build context
    char_names = ", ".join([c["name"] for c in chars])
    context = f"You ({char_names}) are in a conversation with a user.\n\n"
    
    for role, msg in chat_history:
        if role == "user":
            context += f"User: {msg}\n"
        else:
            context += f"{role}: {msg}\n"
    
    context += f"\nUser: {user_message}\n\n"
    
    # All characters respond
    responses = []
    for char in chars:
        full_context = context + f"Everyone responds naturally. {char['name']}:"
        villager = village.villagers[char["name"]]
        response = villager.respond_to(full_context)
        
        if not response:
            response = "..."
        responses.append((char["name"], response))
    
    # Update chat history
    new_history = chat_history + [("user", user_message)] + responses
    
    # Generate audio for all
    audio_paths = []
    try:
        models_folder = "models"
        voices_folder = "voices"
        
        tts = Qwen3TTS(
            voice_mode="clone",
            voice_folder=voices_folder,
            model_folder=models_folder,
        )
        
        for char in chars:
            voice_file = char.get("voice_file")
            if voice_file:
                full_path = os.path.join(voices_folder, voice_file)
                tts.load_voice(char["name"], full_path)
            else:
                tts.load_voice(char["name"])
        
        output_folder = settings.get("output_folder", "output")
        os.makedirs(output_folder, exist_ok=True)
        
        for name, response in responses:
            tts.instruct = next((c.get("emotion", "") for c in chars if c["name"] == name), "")
            audio_path = os.path.join(output_folder, f"chat_{name}.wav")
            tts.speak(response, wait=auto_playback, voice_name=name, save_path=audio_path, non_streaming=True)
            audio_paths.append(audio_path)
    except Exception as e:
        print(f"Audio error: {e}")
    
    # Combine audio if multiple
    combined_path = None
    if len(audio_paths) > 1:
        import soundfile as sf
        import numpy as np
        
        combined = []
        sr = 24000
        for ap in audio_paths:
            audio_data, sample_rate = sf.read(ap)
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            combined.append(audio_data)
            silence = np.zeros(int(sample_rate * 0.5))
            combined.append(silence)
        
        final_audio = np.concatenate(combined)
        combined_path = os.path.join(output_folder, "chat_combined.wav")
        sf.write(combined_path, final_audio, sr)
    
    return new_history, combined_path or (audio_paths[0] if audio_paths else None), "Done"


def clear_chat():
    """Clear chat history."""
    return [], None, "Chat cleared"


def save_settings(lm_host, model_name, output_folder):
    """Save settings."""
    save_json(SETTINGS_FILE, {
        "lm_studio_host": lm_host,
        "model_name": model_name,
        "output_folder": output_folder,
    })
    return "Settings saved!"


def unload_llm(api_host):
    """Unload the LLM from LM Studio to free VRAM."""
    try:
        import requests
        
        # Get list of models
        response = requests.get(f"{api_host}/api/v1/models", timeout=10)
        
        if response.status_code != 200:
            return f"Failed to get models: {response.status_code}"
        
        models = response.json()
        print(f"Models response: {type(models)}")
        
        # Find models with loaded instances
        loaded = []
        
        # Format: {"models": [...]} with loaded_instances inside each
        if isinstance(models, dict) and "models" in models:
            for m in models.get("models", []):
                instances = m.get("loaded_instances", [])
                if instances:
                    loaded.append({
                        "model": m,
                        "instances": instances
                    })
        
        if not loaded:
            return "No model currently loaded"
        
        # Get the first loaded instance
        first_loaded = loaded[0]
        instances = first_loaded["instances"]
        model_info = first_loaded["model"]
        
        instance_id = instances[0].get("id") if instances else None
        model_key = model_info.get("key") if model_info else None
        
        # Use instance_id if available, otherwise model key
        unload_id = instance_id or model_key
        
        if not unload_id:
            print(f"Could not find unload ID. Model: {model_info}, Instances: {instances}")
            return "Could not determine model to unload"
        
        print(f"Unloading model: {unload_id}")
        
        # Send unload request
        unload_response = requests.post(
            f"{api_host}/api/v1/models/unload",
            json={"instance_id": unload_id},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if unload_response.status_code == 200:
            print(f"LLM unloaded: {unload_id}")
            return f"LLM unloaded: {unload_id}"
        else:
            print(f"Failed to unload: {unload_response.status_code} - {unload_response.text}")
            return f"Failed: {unload_response.status_code}"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error: {e}"


def generate_random_scene_prompt():
    """Generate a random scene prompt using the LLM with 2-3 characters."""
    import random
    
    characters = get_characters()
    
    if len(characters) < 2:
        return "Need at least 2 characters to generate a scene prompt.", []
    
    # Pick 2-3 random characters
    num_chars = random.choice([2, 3]) if len(characters) >= 3 else 2
    selected_chars = random.sample(characters, num_chars)
    char_names = [c["name"] for c in selected_chars]
    
    # Get character descriptions for context
    char_descriptions = []
    for c in selected_chars:
        desc = c.get("system_prompt", "")[:200]  # First 200 chars
        char_descriptions.append(f"{c['name']}: {desc}")
    
    settings = get_settings()
    
    # Create prompt for the LLM
    prompt = f"""Generate a creative, fun scene prompt for a conversation between {len(char_names)} characters: {', '.join(char_names)}.

Character descriptions:
{chr(10).join(char_descriptions)}

The scene prompt should:
- Be 1-3 sentences
- Set a clear location and situation
- Describe what each character is doing or feeling
- Be interesting and lead to dialogue

Return ONLY the scene prompt, nothing else."""

    try:
        from openai import OpenAI
        client = OpenAI(api_key="not-needed", base_url=f"{settings['lm_studio_host']}/v1")
        
        response = client.chat.completions.create(
            model=settings["model_name"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.8
        )
        
        scene_prompt = response.choices[0].message.content.strip()
        
        # Unload the LLM after generating
        unload_result = unload_llm(settings["lm_studio_host"])
        
        return scene_prompt, char_names
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error generating prompt: {e}", []


def parse_status_overrides(status_text):
    """Parse status override text into a dict. Format: Character:Status, one per line."""
    overrides = {}
    if not status_text:
        return overrides
    for line in status_text.strip().split("\n"):
        line = line.strip()
        if ":" in line:
            char_name, status = line.split(":", 1)
            overrides[char_name.strip()] = status.strip()
    return overrides


def get_status_tone_prompt(status_effect, character_name):
    """Get tone guidelines based on status effect."""
    if not status_effect or status_effect == "From Character" or status_effect == "Normal":
        return ""
    
    tone_guides = {
        "Drunk": f"{character_name} is drunk. Speak with slurred, unsteady speech. Use rambling sentences. Occasionally stumble over words. Be overly friendly or emotional.",
        "Caffeinated": f"{character_name} is highly caffeinated. Speak very fast, energetic, and jumpy. Lots of nervous energy. Talk a mile a minute.",
        "Tired": f"{character_name} is exhausted. Speak slowly, with long pauses. Use tired, drawling speech. Hard to keep eyes open.",
        "Angry": f"{character_name} is furious. Speak with aggression, sharp tone. Short, clipped responses. Maybe yell or shout.",
        "Happy": f"{character_name} is ecstatic. Very cheerful, upbeat. Use excited tone, maybe laugh. Everything is great!",
        "Sad": f"{character_name} is depressed. Speak slowly, morose. Use downcast tone. Everything is bleak.",
        "Confused": f"{character_name} is very confused. Question everything. Use hesitant speech, lots of 'um' and 'uh'. Can't follow what's happening.",
        "Excited": f"{character_name} is super excited. Can barely contain energy. Speak fast with enthusiasm!",
        "Scared": f"{character_name} is terrified. Nervous, shaky voice. Speak in whispers or high-pitched panic. Look out for dangers!"
    }
    
    return tone_guides.get(status_effect, "")


def generate_chat(selected_characters, starter_message, num_turns, combine_audio, status_overrides_text="", auto_playback=True):
    """Generate a chat between characters."""
    # Handle string input from textbox
    if isinstance(selected_characters, str):
        if selected_characters:
            selected_characters = [c.strip() for c in selected_characters.split(",")]
        else:
            selected_characters = []
    
    # Parse status overrides
    status_overrides = parse_status_overrides(status_overrides_text)
    
    if not selected_characters or len(selected_characters) < 2:
        yield "Please select at least 2 characters.", "Please select at least 2 characters.", 0, None, None
        return
    
    settings = get_settings()
    characters = get_characters()
    
    # Filter to selected characters
    chars = [c for c in characters if c["name"] in selected_characters]
    
    if len(chars) < 2:
        yield "Selected characters not found.", "Selected characters not found.", 0, None, None
        return
    
    # Apply status overrides
    for char in chars:
        if char["name"] in status_overrides:
            char["status_effect"] = status_overrides[char["name"]]
        elif "status_effect" not in char:
            char["status_effect"] = "Normal"
    
    # Setup Village
    village = Village(
        model=settings["model_name"],
        api_host=settings["lm_studio_host"],
    )
    
    for char in chars:
        # Add 1st person reminder to system prompt
        base_prompt = char.get("system_prompt", "")
        if not base_prompt:
            base_prompt = f"You are {char['name']}. Keep responses SHORT - 1-2 sentences max."
        
        # Add status effect tone
        status_effect = char.get("status_effect", "Normal")
        status_tone = get_status_tone_prompt(status_effect, char["name"])
        
        full_prompt = base_prompt + "\n\n" + DIALOGUE_CONSTRAINT
        if status_tone:
            full_prompt += f"\n\nSTATUS EFFECT: {status_tone}"
        full_prompt += "\n\nIMPORTANT: Always speak in FIRST PERSON as if you are the character. Never refer to yourself by name or speak in third person."
        
        village.add_villager(
            name=char["name"],
            system_prompt=full_prompt,
            description=f"Character: {char['name']}",
        )
    
    # Setup TTS
    models_folder = "models"
    voices_folder = "voices"
    
    # Create timestamped output folder with character names
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    char_names = "_".join([c["name"] for c in chars])
    output_folder = os.path.join(settings["output_folder"], f"{timestamp}_{char_names}")
    os.makedirs(output_folder, exist_ok=True)
    
    tts = Qwen3TTS(
        voice_mode="clone",
        voice_folder=voices_folder,
        model_folder=models_folder,
    )
    
    yield "Loading TTS model...", "Loading TTS model...", 0, None, None
    
            # Load voices
    for char in chars:
        voice_path = char.get("voice_file")
        if voice_path:
            full_path = os.path.join(voices_folder, voice_path)
            tts.load_voice(char["name"], full_path)
        else:
            tts.load_voice(char["name"])
    
    yield "Loading AI model...", "Loading AI model...", 0, None, None
    
    # Generate conversation
    all_messages = []
    participants = [c["name"] for c in chars]
    import random
    random.shuffle(participants)  # Randomize who starts
    
    # First message - use starter as scene prompt, not a character message
    scene_prompt = starter_message
    all_messages.append(("SCENE", scene_prompt))
    
    # Generate responses
    max_messages = num_turns * len(participants) * 2  # Allow extra for butt-ins
    current = 0
    
    yield "Starting conversation...", "Starting conversation...", 0, None, None
    
    def find_mentioned_char(response, participants, last_speaker):
        """Check if any character is mentioned in the response."""
        response_lower = response.lower()
        for name in participants:
            if name.lower() in response_lower and name != last_speaker:
                return name
        return None
    
    def get_next_speaker(participants, all_messages, chars):
        """Get next speaker, prioritizing those who haven't spoken recently."""
        # Count how many times each character has spoken
        speak_count = {}
        for speaker, _ in all_messages:
            if speaker != "SCENE":
                speak_count[speaker] = speak_count.get(speaker, 0) + 1
        
        # Get characters who have spoken the least
        min_count = min(speak_count.values()) if speak_count else 0
        least_spoken = [p for p in participants if speak_count.get(p, 0) == min_count]
        
        # If only one character has spoken, don't let them speak again immediately
        if len(all_messages) > 1:
            last_speaker = all_messages[-1][0]
            if last_speaker in least_spoken and len(least_spoken) > 1:
                least_spoken.remove(last_speaker)
        
        # Randomly pick from least spoken characters
        return random.choice(least_spoken) if least_spoken else participants[0]
    
    # Phase 1: Generate all text responses first
    yield "Starting text generation...", "Generating text...", 10, None, None
    
    message_index = 0
    while message_index < max_messages:
        # Find the next character to speak
        if message_index < len(participants):
            char_name = participants[message_index % len(participants)]
            is_butt_in = False
        else:
            # Check last response for butt-ins
            last_response = all_messages[-1][1] if all_messages else ""
            last_speaker = all_messages[-1][0] if all_messages else None
            mentioned = find_mentioned_char(last_response, participants, last_speaker)
            
            if mentioned:
                char_name = mentioned
                is_butt_in = True
            else:
                # No butt-in, get who hasn't spoken much
                char_name = get_next_speaker(participants, all_messages, chars)
                is_butt_in = False
        
        current += 1
        progress = 10 + int((current / max_messages) * 50)  # 10-60%
        
        char = next((c for c in chars if c["name"] == char_name), None)
        if not char:
            break
        
        context = f"Scene: {scene_prompt}\n\n" + "\n".join([f"{s}: {m}" for s, m in all_messages if s != "SCENE"])
        
        villager = village.villagers[char_name]
        
        # Generate response
        response = villager.respond_to(context)
        
        if not response:
            response = f"{char_name} says something..."
        
        all_messages.append((char_name, response))
        
        # Update display
        chat_text = ""
        for speaker, msg in all_messages:
            if speaker == "SCENE":
                chat_text += f"🎬 **SCENE**: {msg}\n\n---\n\n"
            else:
                chat_text += f"👤 **{speaker}**: {msg}\n\n"
        
        yield chat_text, f"Text: {char_name}...", progress, None, None
        
        # Check if we've done enough messages
        char_messages = len([m for m in all_messages if m[0] != "SCENE"])
        if char_messages >= num_turns * len(participants):
            break
        
        message_index += 1
    
    # Phase 2: Generate TTS for each response
    if combine_audio:
        yield chat_text, "Generating audio...", 70, None, None
        
        for i, (speaker, msg) in enumerate([m for m in all_messages if m[0] != "SCENE"]):
            char = next((c for c in chars if c["name"] == speaker), None)
            if not char:
                continue
            
            tts.instruct = char.get("emotion", "")
            audio_num = i + 1
            output_path = os.path.join(output_folder, f"{audio_num}_{speaker}.wav")
            
            try:
                tts.speak(msg, wait=auto_playback, voice_name=speaker, save_path=output_path)
            except Exception as e:
                print(f"Audio error: {e}")
            
            progress = 70 + int(((i + 1) / len([m for m in all_messages if m[0] != "SCENE"])) * 25)
            yield chat_text, f"Audio: {speaker} ({i+1}/{len([m for m in all_messages if m[0] != 'SCENE'])})", progress, output_path, None
        
        # Combine audio
        yield chat_text, "Combining audio...", 95, None, None
    
    latest_audio_path = None
    if combine_audio:
        # Combine all audio files
        import glob
        import soundfile as sf
        import numpy as np
        
        audio_files = sorted(glob.glob(os.path.join(output_folder, "*.wav")), key=lambda x: int(os.path.basename(x).split("_")[0]))
        
        if audio_files:
            combined = []
            sr = 24000
            
            for filepath in audio_files:
                audio_data, sample_rate = sf.read(filepath)
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)
                combined.append(audio_data)
                pause_duration = np.random.uniform(0.25, 1.25)
                silence = np.zeros(int(sample_rate * pause_duration))
                combined.append(silence)
            
            final_audio = np.concatenate(combined)
            combined_path = os.path.join(output_folder, "combined.wav")
            sf.write(combined_path, final_audio, sr)
            latest_audio_path = combined_path
    
    # Unload LLM to free VRAM
    try:
        unload_result = unload_llm(settings["lm_studio_host"])
        print(f"Unload result: {unload_result}")
    except Exception as e:
        print(f"Error unloading: {e}")
        unload_result = f"Error: {e}"
    
    yield chat_text, f"Done! {unload_result}", 100, None, latest_audio_path
    return


def generate_text_only(selected_characters, starter_message, num_turns, status_overrides_text=""):
    """Generate only text for a chat between characters (no audio)."""
    if isinstance(selected_characters, str):
        if selected_characters:
            selected_characters = [c.strip() for c in selected_characters.split(",")]
        else:
            selected_characters = []
    
    status_overrides = parse_status_overrides(status_overrides_text)
    
    if not selected_characters or len(selected_characters) < 2:
        yield "Please select at least 2 characters.", "Please select at least 2 characters.", 0
        return
    
    settings = get_settings()
    characters = get_characters()
    chars = [c for c in characters if c["name"] in selected_characters]
    
    if len(chars) < 2:
        yield "Selected characters not found.", "Selected characters not found.", 0
        return
    
    # Apply status overrides
    for char in chars:
        if char["name"] in status_overrides:
            char["status_effect"] = status_overrides[char["name"]]
        elif "status_effect" not in char:
            char["status_effect"] = "Normal"
    
    village = Village(
        model=settings["model_name"],
        api_host=settings["lm_studio_host"],
    )
    
    for char in chars:
        base_prompt = char.get("system_prompt", "")
        if not base_prompt:
            base_prompt = f"You are {char['name']}. Keep responses SHORT - 1-2 sentences max."
        
        status_effect = char.get("status_effect", "Normal")
        status_tone = get_status_tone_prompt(status_effect, char["name"])
        
        full_prompt = base_prompt + "\n\n" + DIALOGUE_CONSTRAINT
        if status_tone:
            full_prompt += f"\n\nSTATUS EFFECT: {status_tone}"
        full_prompt += "\n\nIMPORTANT: Always speak in FIRST PERSON as if you are the character. Never refer to yourself by name or speak in third person."
        
        village.add_villager(
            name=char["name"],
            system_prompt=full_prompt,
            description=f"Character: {char['name']}",
        )
    
    yield "Loading AI model...", "Loading AI model...", 0
    
    all_messages = []
    participants = [c["name"] for c in chars]
    import random
    random.shuffle(participants)
    scene_prompt = starter_message
    all_messages.append(("SCENE", scene_prompt))
    
    max_messages = num_turns * len(participants) * 2
    current = 0
    
    yield "Starting conversation...", "Starting conversation...", 0
    
    def find_mentioned_char(response, participants, last_speaker):
        response_lower = response.lower()
        for name in participants:
            if name.lower() in response_lower and name != last_speaker:
                return name
        return None
    
    def get_next_speaker(participants, all_messages, chars):
        speak_count = {}
        for speaker, _ in all_messages:
            if speaker != "SCENE":
                speak_count[speaker] = speak_count.get(speaker, 0) + 1
        min_count = min(speak_count.values()) if speak_count else 0
        least_spoken = [p for p in participants if speak_count.get(p, 0) == min_count]
        if len(all_messages) > 1:
            last_speaker = all_messages[-1][0]
            if last_speaker in least_spoken and len(least_spoken) > 1:
                least_spoken.remove(last_speaker)
        return random.choice(least_spoken) if least_spoken else participants[0]
    
    yield "Generating text...", "Generating text...", 10
    
    message_index = 0
    while message_index < max_messages:
        if message_index < len(participants):
            char_name = participants[message_index % len(participants)]
        else:
            last_response = all_messages[-1][1] if all_messages else ""
            last_speaker = all_messages[-1][0] if all_messages else None
            mentioned = find_mentioned_char(last_response, participants, last_speaker)
            if mentioned:
                char_name = mentioned
            else:
                char_name = get_next_speaker(participants, all_messages, chars)
        
        current += 1
        progress = 10 + int((current / max_messages) * 80)
        
        char = next((c for c in chars if c["name"] == char_name), None)
        if not char:
            break
        
        context = f"Scene: {scene_prompt}\n\n" + "\n".join([f"{s}: {m}" for s, m in all_messages if s != "SCENE"])
        villager = village.villagers[char_name]
        response = villager.respond_to(context)
        
        if not response:
            response = f"{char_name} says something..."
        
        all_messages.append((char_name, response))
        
        chat_text = ""
        for speaker, msg in all_messages:
            if speaker == "SCENE":
                chat_text += f"🎬 **SCENE**: {msg}\n\n---\n\n"
            else:
                chat_text += f"👤 **{speaker}**: {msg}\n\n"
        
        yield chat_text, f"Text: {char_name}...", progress
        
        char_messages = len([m for m in all_messages if m[0] != "SCENE"])
        if char_messages >= num_turns * len(participants):
            break
        
        message_index += 1
    
    # Save messages to a global variable for the audio phase
    global _last_chat_messages
    _last_chat_messages = all_messages
    global _last_chat_chars
    _last_chat_chars = chars
    global _last_output_folder
    _last_output_folder = os.path.join(settings["output_folder"], f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_" + "_".join([c["name"] for c in chars]))
    os.makedirs(_last_output_folder, exist_ok=True)
    
    # Unload LLM to free VRAM
    unload_result = unload_llm(settings["lm_studio_host"])
    
    yield chat_text, f"Text generated! {unload_result}. You can edit above and click 'Generate Audio'.", 100


_last_chat_messages = []
_last_chat_chars = []
_last_output_folder = ""


def generate_audio_from_text(edited_text, status_overrides_text="", auto_playback=True):
    """Generate audio from already-generated text."""
    global _last_chat_messages, _last_chat_chars, _last_output_folder
    
    if not _last_chat_messages:
        yield "No text generated yet. Generate text first.", 0, None, None
        return
    
    settings = get_settings()
    
    # Parse the edited text back into messages
    all_messages = []
    lines = edited_text.split("\n")
    current_speaker = None
    current_msg = []
    
    for line in lines:
        if "🎬 **SCENE**:" in line:
            if current_speaker and current_msg:
                all_messages.append((current_speaker, " ".join(current_msg)))
            scene_text = line.split("**SCENE**:", 1)[-1].strip()
            all_messages.append(("SCENE", scene_text))
            current_speaker = None
            current_msg = []
        elif "👤 **" in line:
            if current_speaker and current_msg:
                all_messages.append((current_speaker, " ".join(current_msg)))
            current_speaker = line.split("**", 2)[1].strip() if "**" in line else None
            if ":" in line:
                current_msg = [line.split(":", 1)[-1].strip()]
            else:
                current_msg = []
        elif current_speaker and line.strip():
            current_msg.append(line.strip())
    
    if current_speaker and current_msg:
        all_messages.append((current_speaker, " ".join(current_msg)))
    
    if not all_messages:
        yield "Could not parse conversation text.", 0, None, None
        return
    
    chars = _last_chat_chars
    settings = get_settings()
    voices_folder = "voices"
    models_folder = "models"
    
    tts = Qwen3TTS(
        voice_mode="clone",
        voice_folder=voices_folder,
        model_folder=models_folder,
    )
    
    yield "Loading TTS...", 0, None, None
    
    for char in chars:
        voice_path = char.get("voice_file")
        if voice_path:
            full_path = os.path.join(voices_folder, voice_path)
            tts.load_voice(char["name"], full_path)
        else:
            tts.load_voice(char["name"])
    
    char_messages = [m for m in all_messages if m[0] != "SCENE"]
    
    for i, (speaker, msg) in enumerate(char_messages):
        char = next((c for c in chars if c["name"] == speaker), None)
        if not char:
            continue
        
        tts.instruct = char.get("emotion", "")
        audio_num = i + 1
        output_path = os.path.join(_last_output_folder, f"{audio_num}_{speaker}.wav")
        
        try:
            tts.speak(msg, wait=auto_playback, voice_name=speaker, save_path=output_path)
        except Exception as e:
            print(f"Audio error: {e}")
        
        progress = int(((i + 1) / len(char_messages)) * 90)
        yield f"Audio: {speaker} ({i+1}/{len(char_messages)})", progress, output_path, None
    
    # Combine audio
    import glob
    import soundfile as sf
    import numpy as np
    
    audio_files = sorted(glob.glob(os.path.join(_last_output_folder, "*.wav")), key=lambda x: int(os.path.basename(x).split("_")[0]))
    
    if audio_files:
        combined = []
        sr = 24000
        
        for filepath in audio_files:
            audio_data, sample_rate = sf.read(filepath)
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            combined.append(audio_data)
            pause_duration = np.random.uniform(0.25, 1.25)
            silence = np.zeros(int(sample_rate * pause_duration))
            combined.append(silence)
        
        final_audio = np.concatenate(combined)
        combined_path = os.path.join(_last_output_folder, "combined.wav")
        sf.write(combined_path, final_audio, sr)
    
    # Unload LLM to free VRAM
    unload_result = unload_llm(settings["lm_studio_host"])
    
    yield f"Done! {unload_result}", 100, combined_path if audio_files else None, combined_path


def main():
    """Launch Gradio UI."""
    
    # Character Management Tab
    with gr.Blocks(title="AI Character Chat") as app:
        gr.Markdown("# AI Character Chat Generator")
        gr.Markdown("Create characters, set up multi-character chats, and generate AI conversations with voice synthesis.")
        
        with gr.Tab("Characters"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Add/Edit Character")
                    char_name = gr.Textbox(label="Character Name", placeholder="e.g., Finn")
                    system_prompt = gr.Textbox(
                        label="System Prompt", 
                        placeholder="You are Finn from Adventure Time...",
                        lines=4
                    )
                    voice_file = gr.Dropdown(choices=get_voice_files(), label="Voice File", value="")
                    transcribe_result = gr.Textbox(label="Transcription Status", interactive=False)
                    transcript_display = gr.Textbox(label="Transcript", lines=4, interactive=False)
                    with gr.Row():
                        refresh_voices_btn = gr.Button("Refresh Voices")
                        transcribe_btn = gr.Button("Transcribe Voice")
                    
                    def load_existing_transcript(voice_filename):
                        if not voice_filename:
                            return "", ""
                        txt_path = os.path.join("voices", voice_filename.replace(".wav", ".txt"))
                        if os.path.exists(txt_path):
                            with open(txt_path, "r", encoding="utf-8") as f:
                                transcript = f.read().strip()
                            return f"Loaded ({len(transcript)} chars)", transcript
                        return "No transcript found", ""
                    
                    voice_file.change(
                        load_existing_transcript,
                        inputs=voice_file,
                        outputs=[transcribe_result, transcript_display]
                    )
                    
                    transcribe_btn.click(
                        transcribe_voice_file,
                        inputs=voice_file,
                        outputs=[transcribe_result, transcript_display]
                    )
                    
                    emotion = gr.Textbox(
                        label="Emotion/Style",
                        placeholder="young, heroic, energetic"
                    )
                    status_effect_dropdown = gr.Dropdown(
                        choices=STATUS_EFFECTS,
                        value="Normal",
                        label="Status Effect",
                    )
                    save_btn = gr.Button("Save Character", variant="primary")
                    save_result = gr.Textbox(label="Status")
                    save_btn.click(
                        save_character,
                        inputs=[char_name, system_prompt, voice_file, emotion, status_effect_dropdown],
                        outputs=save_result
                    )
                
                with gr.Column():
                    gr.Markdown("### Saved Characters")
                    
                    char_checkbox_group = gr.CheckboxGroup(choices=[], label="Select Character to Edit")
                    
                    with gr.Row():
                        edit_btn = gr.Button("Load Character")
                    
                    edit_status = gr.Textbox(label="Edit Status", interactive=False)
                    
                    def load_selected_char(selected_names):
                        if not selected_names:
                            return "", "", "", "", "", "No character selected"
                        return load_character_for_edit(selected_names[0])
                    
                    edit_btn.click(
                        load_selected_char,
                        inputs=char_checkbox_group,
                        outputs=[char_name, system_prompt, voice_file, emotion, status_effect_dropdown, edit_status]
                    )
                    
                    def get_char_list():
                        chars = get_characters()
                        return gr.CheckboxGroup(choices=[c["name"] for c in chars])
                    
                    app.load(get_char_list, outputs=char_checkbox_group)
                    
                    gr.Markdown("---")
                    gr.Markdown("### Delete Character")
                    
                    delete_checkboxes = gr.CheckboxGroup(choices=[], label="Select Characters to Delete")
                    app.load(get_char_list, outputs=delete_checkboxes)
                    
                    with gr.Row():
                        delete_btn = gr.Button("Delete Selected", variant="stop")
                    
                    delete_result = gr.Textbox(label="Status")
                    
                    def delete_selected_chars(selected_names):
                        if not selected_names:
                            return "No characters selected"
                        results = []
                        for name in selected_names:
                            result = delete_character(name)
                            results.append(result)
                        return "\n".join(results)
                    
                    delete_btn.click(
                        delete_selected_chars,
                        inputs=delete_checkboxes,
                        outputs=delete_result
                    )
                    
                    delete_btn.click(get_char_list, outputs=char_checkbox_group)
                    delete_btn.click(get_char_list, outputs=delete_checkboxes)
                    
                    # Refresh checkboxes when character is saved
                    save_btn.click(get_char_list, outputs=char_checkbox_group)
                    save_btn.click(get_char_list, outputs=delete_checkboxes)
                
                # Refresh voices button
                refresh_voices_btn.click(
                    lambda: gr.Dropdown(choices=get_voice_files()),
                    outputs=voice_file
                )
        
        # Combine Voices Tab
        with gr.Tab("Combine Voices"):
            gr.Markdown("### Combine voice clips into a single voice file")
            
            with gr.Row():
                folder_dropdown = gr.Dropdown(choices=get_unrefined_folders(), label="Select Folder", value="")
                refresh_folders_btn = gr.Button("Refresh")
            
            refresh_folders_btn.click(
                lambda: gr.Dropdown(choices=get_unrefined_folders()),
                outputs=folder_dropdown
            )
            
            char_name_for_voice = gr.Textbox(label="Character Name (for filename)", placeholder="e.g., Bender")
            
            combine_btn = gr.Button("Combine Voices", variant="primary")
            combine_result = gr.Textbox(label="Status", interactive=False)
            
            combine_btn.click(
                combine_voice_files,
                inputs=[folder_dropdown, char_name_for_voice],
                outputs=combine_result
            )
            
            gr.Markdown("Or enter a custom folder path:")
            custom_folder = gr.Textbox(label="Custom Folder Path", placeholder="C:\\Users\\...\\voices\\UNREFINED\\Bender")
            
            with gr.Row():
                combine_custom_btn = gr.Button("Combine from Custom Folder")
            
            combine_custom_btn.click(
                combine_voice_files,
                inputs=[custom_folder, char_name_for_voice],
                outputs=combine_result
            )
        
        # Multi Chat Tab
        with gr.Tab("Multi Chat"):
            gr.Markdown("### Generate a multi-character chat")
            
            def get_char_choices():
                chars = get_characters()
                return [c["name"] for c in chars]
            
            char_checkboxes = gr.CheckboxGroup(choices=[], label="Characters")
            
            with gr.Row():
                refresh_btn = gr.Button("Refresh Characters")
            
            def update_checkboxes():
                chars = get_characters()
                return gr.CheckboxGroup(choices=[c["name"] for c in chars])
            
            refresh_btn.click(update_checkboxes, outputs=char_checkboxes)
            app.load(update_checkboxes, outputs=char_checkboxes)
            
            gr.Markdown("#### Status Effects Override")
            gr.Markdown("Set status effects for characters. Leave as 'From Character' to use the character's default status.")
            
            # Dynamic status dropdowns for each selected character
            status_state = gr.State({})  # {character_name: status_effect}
            
            def get_status_dropdowns(selected_chars):
                """Return dropdown choices based on selected characters."""
                if not selected_chars:
                    return gr.Dropdown(visible=False), ""
                return gr.Dropdown(choices=STATUS_EFFECTS, value="From Character", visible=True), ""
            
            with gr.Row():
                override_status_btn = gr.Button("Show Status Overrides")
            
            # Status override area - will be populated based on selection
            status_override_area = gr.Textbox(
                label="Status Overrides (format: Character:Status, one per line)",
                placeholder="Finn: Drunk\nJake: Caffeinated",
                lines=3,
                interactive=True
            )
            
            with gr.Row():
                starter = gr.Textbox(
                    label="Scene Prompt",
                    value="Finn, Jake, and Shrek are sitting around a campfire in the Ooo Swamp. Finn is excited about a new adventure, Jake is being his chill self, and Shrek is grumpy but tolerating them. They are discussing what to do tomorrow.",
                    scale=2
                )
                turns = gr.Slider(1, 20, value=5, step=1, label="Number of Turns")
            
            with gr.Row():
                random_scene_btn = gr.Button("Random Scene")
            
            random_scene_btn.click(
                generate_random_scene_prompt,
                outputs=[starter, char_checkboxes]
            )
            
            chat_state = gr.State([])
            
            with gr.Row():
                auto_playback = gr.Checkbox(label="Auto Playback", value=True)
            
            with gr.Row():
                generate_all_btn = gr.Button("Generate All (Text + Audio)", variant="primary")
                generate_text_btn = gr.Button("Generate Text Only")
                generate_audio_btn = gr.Button("Generate Audio", variant="secondary")
            
            status_text = gr.Textbox(label="Status", interactive=False)
            progress_bar = gr.Slider(0, 100, value=0, step=1, label="Progress", interactive=False)
            
            output = gr.Textbox(label="Conversation (Editable)", lines=15, interactive=True)
            
            latest_audio = gr.Audio(label="Latest Audio", interactive=False)
            combined_audio = gr.Audio(label="Combined Audio", interactive=False)
            
            generate_all_btn.click(
                generate_chat,
                inputs=[char_checkboxes, starter, turns, gr.State(True), status_override_area, auto_playback],
                outputs=[output, status_text, progress_bar, latest_audio, combined_audio]
            )
            
            generate_text_btn.click(
                generate_text_only,
                inputs=[char_checkboxes, starter, turns, status_override_area],
                outputs=[output, status_text, progress_bar]
            )
            
            generate_audio_btn.click(
                generate_audio_from_text,
                inputs=[output, status_override_area],
                outputs=[status_text, progress_bar, latest_audio, combined_audio]
            )
        
        # Chat Tab
        with gr.Tab("Chat"):
            gr.Markdown("### Talk to Characters")
            
            def get_char_choices():
                return [c["name"] for c in get_characters()]
            
            char_checkboxes = gr.CheckboxGroup(choices=[], label="Characters")
            
            with gr.Row():
                refresh_btn = gr.Button("Refresh Characters")
            
            def update_checkboxes():
                chars = get_characters()
                return gr.CheckboxGroup(choices=[c["name"] for c in chars])
            
            refresh_btn.click(update_checkboxes, outputs=char_checkboxes)
            app.load(update_checkboxes, outputs=char_checkboxes)
            
            gr.Markdown("#### Status Overrides")
            chat_status_override = gr.Textbox(
                label="Status Effects (format: Character:Status)",
                placeholder="Finn: Drunk\nBender: Caffeinated",
                lines=2
            )
            
            with gr.Row():
                auto_playback_chat = gr.Checkbox(label="Auto Playback", value=True)
            
            chat_history = gr.State([])
            chat_display = gr.Textbox(label="Chat History", lines=10, interactive=False)
            
            with gr.Row():
                user_input = gr.Textbox(label="Your Message", scale=3)
                send_btn = gr.Button("Send", variant="primary")
            
            chat_audio = gr.Audio(label="Response Audio", interactive=False)
            chat_status = gr.Textbox(label="Status", interactive=False)
            
            def handle_send(char_names, message, history, status_text, auto_play):
                if not char_names or not message:
                    return history, None, "Please select character and enter message", "", ""
                new_history, audio, status = chat_with_character(char_names, message, history, status_text, auto_play)
                # Format for display
                display = ""
                for role, msg in new_history:
                    if role == "user":
                        display += f"You: {msg}\n\n"
                    else:
                        display += f"{role}: {msg}\n\n"
                return new_history, display, audio, status, "", ""
            
            send_btn.click(
                handle_send,
                inputs=[char_checkboxes, user_input, chat_history, chat_status_override, auto_playback_chat],
                outputs=[chat_history, chat_display, chat_audio, chat_status, user_input, chat_status_override]
            )
            
            clear_chat_btn = gr.Button("Clear Chat")
            clear_chat_btn.click(clear_chat, outputs=[chat_history, chat_display, chat_status])
        
        # Settings Tab
        with gr.Tab("Settings"):
            gr.Markdown("### API Settings")
            settings = get_settings()
            
            with gr.Row():
                lm_host = gr.Textbox(
                    label="LM Studio Host",
                    value=settings.get("lm_studio_host", "http://192.168.56.1:6842")
                )
                model = gr.Textbox(
                    label="Model Name",
                    value=settings.get("model_name", "qwen/qwen3.5-9b")
                )
            
            output_folder = gr.Textbox(
                label="Output Folder",
                value=settings.get("output_folder", "output")
            )
            
            save_settings_btn = gr.Button("Save Settings", variant="primary")
            save_settings_btn.click(
                save_settings,
                inputs=[lm_host, model, output_folder],
                outputs=gr.Textbox(label="Status")
            )
    
    app.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
