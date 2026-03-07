"""Web UI for AI Character Chat Generator."""

import os
import json
import gradio as gr
from datetime import datetime

from digital_village.village import Village
from digital_village.qwen_tts import Qwen3TTS


CHARACTERS_FOLDER = "characters"
SETTINGS_FILE = "data/settings.json"


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


def save_character(name, system_prompt, voice_file, emotion):
    """Save a character."""
    ensure_characters_folder()
    
    character = {
        "name": name,
        "system_prompt": system_prompt,
        "voice_file": voice_file,
        "emotion": emotion
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


def save_settings(lm_host, model_name, output_folder):
    """Save settings."""
    save_json(SETTINGS_FILE, {
        "lm_studio_host": lm_host,
        "model_name": model_name,
        "output_folder": output_folder,
    })
    return "Settings saved!"


def generate_chat(selected_characters, starter_message, num_turns, combine_audio):
    """Generate a chat between characters."""
    # Handle string input from textbox
    if isinstance(selected_characters, str):
        if selected_characters:
            selected_characters = [c.strip() for c in selected_characters.split(",")]
        else:
            selected_characters = []
    
    if not selected_characters or len(selected_characters) < 2:
        yield "", "Please select at least 2 characters.", 0
        return
    
    settings = get_settings()
    characters = get_characters()
    
    # Filter to selected characters
    chars = [c for c in characters if c["name"] in selected_characters]
    
    if len(chars) < 2:
        yield "", "Selected characters not found.", 0
        return
    
    # Setup Village
    village = Village(
        model=settings["model_name"],
        api_host=settings["lm_studio_host"],
    )
    
    for char in chars:
        village.add_villager(
            name=char["name"],
            system_prompt=char["system_prompt"],
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
    
            # Load voices
    for char in chars:
        voice_path = char.get("voice_file")
        if voice_path:
            full_path = os.path.join(voices_folder, voice_path)
            tts.load_voice(char["name"], full_path)
        else:
            tts.load_voice(char["name"])
    
    # Generate conversation
    all_messages = []
    participants = [c["name"] for c in chars]
    
    # First message - use starter as scene prompt, not a character message
    scene_prompt = starter_message
    all_messages.append(("SCENE", scene_prompt))
    
    # Generate responses
    total_messages = num_turns * len(participants)
    current = 0
    
    yield "", "Loading...", 0
    
    for turn in range(num_turns):
        for char_name in participants:
            current += 1
            progress = int((current / total_messages) * 100)
            yield "", f"Generating turn {turn+1}/{num_turns} - {char_name}...", progress
            
            char = next((c for c in chars if c["name"] == char_name), None)
            if not char:
                continue
            
            context_parts = [f"{s}: {m}" for s, m in all_messages]
            context = f"Scene: {scene_prompt}\n\nContinue the conversation naturally.\n\n" + "\n".join([f"{s}: {m}" for s, m in all_messages if s != "SCENE"])
            
            villager = village.villagers[char_name]
            response = villager.respond_to(context)
            
            if not response:
                response = f"{char_name} says something..."
            
            all_messages.append((char_name, response))
            
            # Generate audio
            if combine_audio:
                tts.instruct = char.get("emotion", "")
                audio_num = len([m for m in all_messages if m[0] != "SCENE"])
                output_path = os.path.join(output_folder, f"{audio_num}_{char_name}.wav")
                tts.speak(response, wait=False, voice_name=char_name, save_path=output_path)
    
    # Format output
    output = ""
    for speaker, msg in all_messages:
        if speaker == "SCENE":
            output += f"**SCENE**: {msg}\n\n---\n\n"
        else:
            output += f"**{speaker}**: {msg}\n\n"
    
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
            output += f"\n\nAudio saved to: {output_folder}/combined.wav"
        else:
            output += f"\n\nAudio files saved to: {output_folder}"
    
    yield output, "Done!", 100
    return


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
                    refresh_voices_btn = gr.Button("Refresh Voices")
                    emotion = gr.Textbox(
                        label="Emotion/Style",
                        placeholder="young, heroic, energetic"
                    )
                    save_btn = gr.Button("Save Character", variant="primary")
                    save_result = gr.Textbox(label="Status")
                    save_btn.click(
                        save_character,
                        inputs=[char_name, system_prompt, voice_file, emotion],
                        outputs=save_result
                    )
                
                with gr.Column():
                    gr.Markdown("### Saved Characters")
                    char_list = gr.Markdown("No characters yet")
                    
                    def refresh_char_list():
                        chars = get_characters()
                        return "\n".join([f"- **{c['name']}**" for c in chars]) or "No characters yet"
                    
                    save_btn.click(refresh_char_list, outputs=char_list)
                    app.load(refresh_char_list, outputs=char_list)
                    
                    delete_name = gr.Textbox(label="Character to Delete")
                    delete_btn = gr.Button("Delete Character", variant="stop")
                    delete_result = gr.Textbox(label="Status")
                    delete_btn.click(
                        delete_character,
                        inputs=delete_name,
                        outputs=delete_result
                    )
                    delete_btn.click(refresh_char_list, outputs=char_list)
        
        # Chat Tab
        with gr.Tab("Generate Chat"):
            gr.Markdown("### Select Characters for Chat")
            
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
            
            with gr.Row():
                starter = gr.Textbox(
                    label="Starter Message",
                    value="Hey, what's going on?",
                    scale=2
                )
                turns = gr.Slider(1, 20, value=5, step=1, label="Number of Turns")
            
            with gr.Row():
                combine = gr.Checkbox(label="Generate Audio", value=True)
                generate_btn = gr.Button("Generate Chat", variant="primary")
            
            status_text = gr.Textbox(label="Status", interactive=False)
            progress_bar = gr.Slider(0, 100, value=0, step=1, label="Progress", interactive=False)
            
            output = gr.Markdown()
            generate_btn.click(
                generate_chat,
                inputs=[char_checkboxes, starter, turns, combine],
                outputs=[output, status_text, progress_bar]
            )
        
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
