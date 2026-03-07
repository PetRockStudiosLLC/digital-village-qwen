"""Main window - central GUI application."""

import os
import sys
import json
import threading
import time
import random
from typing import List, Optional, Dict, Any

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMessageBox
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut

from .character_panel import CharacterPanel, CharacterData
from .conversation_panel import ConversationPanel
from .timeline import Timeline
from .toolbar import Toolbar
from .settings_dialog import SettingsDialog
from .control_bar import ControlBar
from .preset_manager import PresetManager
from .style import apply_theme


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Village - AI Conversation Generator")
        self.setMinimumSize(1000, 700)
        
        self.settings: Dict[str, Any] = self._default_settings()
        self.output_files: List[str] = []
        self.is_generating = False
        self.generation_thread: Optional[threading.Thread] = None
        
        self.init_ui()
        self._apply_theme()
        self._setup_shortcuts()
    
    def _default_settings(self) -> dict:
        """Get default settings."""
        return {
            "lm_studio_host": "http://192.168.56.1:6842",
            "model_name": "qwen2.5-0.5b-instruct",
            "output_folder": "output",
            "pause_min": 0.5,
            "pause_max": 1.5,
            "preview_phrase": "Hello, this is a test of the voice.",
            "default_emotion": "neutral",
            "num_turns": 5,
            "starter_message": "Hey, how are you doing?",
        }
    
    def _apply_theme(self):
        """Apply theme to the application."""
        app = self.application()
        if app:
            apply_theme(app)
    
    def application(self):
        """Get the QApplication instance."""
        from PySide6.QtWidgets import QApplication
        return QApplication.instance()
    
    def init_ui(self):
        """Initialize the UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.toolbar = Toolbar()
        self.toolbar.settings_clicked.connect(self._show_settings)
        self.toolbar.load_preset_clicked.connect(self._load_preset)
        self.toolbar.save_preset_clicked.connect(self._save_preset)
        self.toolbar.export_clicked.connect(self._export_conversation)
        main_layout.addWidget(self.toolbar)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.character_panel = CharacterPanel()
        self.character_panel.character_changed.connect(self._on_character_changed)
        self.character_panel.preview_requested.connect(self._preview_character)
        self.character_panel.remove_requested.connect(self._remove_character)
        
        splitter.addWidget(self.character_panel)
        
        self.conversation_panel = ConversationPanel()
        splitter.addWidget(self.conversation_panel)
        
        splitter.setSizes([300, 600])
        main_layout.addWidget(splitter)
        
        self.timeline = Timeline()
        self.timeline.play_clicked.connect(self._on_play_audio)
        self.timeline.stop_clicked.connect(self._on_stop_audio)
        main_layout.addWidget(self.timeline)
        
        self.control_bar = ControlBar()
        self.control_bar.generate_clicked.connect(self._start_generation)
        main_layout.addWidget(self.control_bar)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        QShortcut(QKeySequence("Ctrl+G"), self, self._start_generation)
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_preset)
        QShortcut(QKeySequence("Ctrl+O"), self, self._load_preset)
        QShortcut(QKeySequence("Ctrl+E"), self, self._export_conversation)
        QShortcut(QKeySequence("Space"), self, self._toggle_playback)
        QShortcut(QKeySequence("Esc"), self, self._stop_generation)
    
    def _on_character_changed(self, index: int, data: CharacterData):
        """Handle character data change."""
        self.conversation_panel.set_characters(self.character_panel.get_characters())
    
    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.settings, self)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()
    
    def _apply_settings(self, settings: dict):
        """Apply new settings."""
        self.settings.update(settings)
    
    def _load_preset(self):
        """Load preset from file."""
        file_path = PresetManager.show_load_dialog(self)
        if not file_path:
            return
        
        data = PresetManager.load_preset(file_path)
        if data is None:
            PresetManager.show_error(self, "Failed to load preset file.")
            return
        
        characters = PresetManager.get_characters_from_preset(data)
        preset_settings = PresetManager.get_settings_from_preset(data)
        
        self.character_panel.clear()
        for char in characters:
            self.character_panel.add_character(char)
        
        if preset_settings:
            self.settings.update(preset_settings)
        
        self.conversation_panel.set_characters(characters)
        PresetManager.show_success(self, f"Loaded preset: {data.get('name', 'Unknown')}")
    
    def _save_preset(self):
        """Save preset to file."""
        characters = self.character_panel.get_characters()
        if not characters:
            PresetManager.show_error(self, "No characters to save.")
            return
        
        file_path = PresetManager.show_save_dialog(self, "shrek_donkey.json")
        if not file_path:
            return
        
        if PresetManager.save_preset(file_path, characters, self.settings):
            PresetManager.show_success(self, "Preset saved successfully!")
        else:
            PresetManager.show_error(self, "Failed to save preset.")
    
    def _export_conversation(self):
        """Export conversation."""
        if not self.output_files:
            QMessageBox.information(self, "Export", "No audio files to export.")
            return
        
        output_folder = self.settings.get("output_folder", "output")
        os.makedirs(output_folder, exist_ok=True)
        
        QMessageBox.information(
            self, 
            "Export", 
            f"Conversation exported to {output_folder} folder."
        )
    
    def _preview_character(self, index: int):
        """Preview character voice."""
        characters = self.character_panel.get_characters()
        if index >= len(characters):
            return
        
        char = characters[index]
        preview_text = self.settings.get("preview_phrase", "Hello, this is a test.")
        
        self._generate_audio(char, preview_text, f"preview_{char.name}")
    
    def _remove_character(self, index: int):
        """Remove character."""
        self.character_panel.remove_character(index)
        self.conversation_panel.set_characters(self.character_panel.get_characters())
    
    def _start_generation(self):
        """Start conversation generation."""
        if self.is_generating:
            return
        
        characters = self.character_panel.get_characters()
        if len(characters) < 2:
            QMessageBox.warning(
                self, 
                "Warning", 
                "Please add at least 2 characters to generate a conversation."
            )
            return
        
        self.is_generating = True
        self.control_bar.set_generating(True)
        self.conversation_panel.clear()
        self.conversation_panel.set_characters(characters)
        
        options = self.control_bar.get_options()
        
        self.generation_thread = threading.Thread(
            target=self._generation_worker,
            args=(characters, options),
            daemon=True
        )
        self.generation_thread.start()
    
    def _generation_worker(self, characters: List[CharacterData], options: dict):
        """Worker thread for generation."""
        try:
            output_folder = self.settings.get("output_folder", "output")
            os.makedirs(output_folder, exist_ok=True)
            
            starter = self.settings.get("starter_message", "Hey, how are you doing?")
            num_turns = self.settings.get("num_turns", 5)
            model_name = self.settings.get("model_name", "qwen/qwen3.5-9b")
            lm_host = self.settings.get("lm_studio_host", "http://192.168.56.1:6842")
            
            self.output_files = []
            
            from digital_village.village import Village
            
            village = Village(model=model_name, api_host=lm_host)
            
            for char in characters:
                prompt = char.system_prompt or f"You are {char.name}. Keep responses short - 1-2 sentences max."
                village.add_villager(
                    name=char.name,
                    system_prompt=prompt,
                    description=f"Character: {char.name}",
                )
            
            all_messages = []
            participants = [c.name for c in characters]
            
            starter_speaker = participants[0]
            message = starter
            print(f"[{starter_speaker}]: {message}")
            all_messages.append((starter_speaker, message))
            
            QTimer.singleShot(0, lambda: self.control_bar.set_status(f"Starting: {starter_speaker}"))
            QTimer.singleShot(0, lambda c=starter_speaker, m=message: 
                self.conversation_panel.add_message_with_progress(c, m))
            
            char_data = next((c for c in characters if c.name == starter_speaker), characters[0])
            self._generate_audio(char_data, message, f"turn0_{starter_speaker}")
            
            turn = 0
            while turn < num_turns and self.is_generating:
                for idx, char_name in enumerate(participants):
                    if not self.is_generating:
                        break
                    
                    char_data = next((c for c in characters if c.name == char_name), characters[idx])
                    
                    context_parts = [f"{s}: {m}" for s, m in all_messages]
                    context = "Continue the conversation naturally.\n\n" + "\n".join(context_parts)
                    
                    QTimer.singleShot(0, lambda c=char_name: self.control_bar.set_status(f"AI thinking: {c}"))
                    
                    villager = village.villagers[char_name]
                    response = villager.respond_to(context)
                    
                    if not response:
                        response = f"{char_name} says something..."
                    
                    print(f"[{char_name}]: {response}")
                    all_messages.append((char_name, response))
                    
                    QTimer.singleShot(0, lambda c=char_name, m=response: 
                        self.conversation_panel.add_message_with_progress(c, m))
                    
                    QTimer.singleShot(0, lambda c=char_name: self.control_bar.set_status(f"Generating voice: {c}"))
                    
                    self._generate_audio(char_data, response, f"turn{turn+1}_{char_name}")
                    
                    for p in range(10):
                        if not self.is_generating:
                            break
                        time.sleep(0.05)
                        progress = (p + 1) / 10
                        QTimer.singleShot(0, lambda p=progress:
                            self.conversation_panel.update_progress(p))
                
                turn += 1
            
            if options.get("combine") and self.output_files:
                self._combine_audio_files()
            
        except Exception as e:
            print(f"Generation error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.is_generating = False
            QTimer.singleShot(0, lambda: self.control_bar.set_generating(False))
            QTimer.singleShot(0, lambda: self.control_bar.set_status(f"Done! Generated {len(self.output_files)} files"))
    
    def _generate_audio(self, char: CharacterData, text: str, filename: str):
        """Generate audio for a character."""
        try:
            from digital_village.qwen_tts import Qwen3TTS
            
            output_folder = self.settings.get("output_folder", "output")
            output_path = os.path.join(output_folder, f"{filename}.wav")
            
            models_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
            voices_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "voices")
            
            tts = Qwen3TTS(
                voice_mode="clone",
                speaker=char.preset_speaker,
                voice_folder=voices_folder,
                model_folder=models_folder,
                instruct=char.emotion if char.emotion else None,
            )
            
            tts.load_voice(char.name)
            tts.speak(text, wait=False, voice_name=char.name, save_path=output_path)
            self.output_files.append(output_path)
            
        except Exception as e:
            print(f"TTS Error: {e}")
            import traceback
            traceback.print_exc()
    
    def _combine_audio_files(self):
        """Combine audio files into one."""
        pass
    
    def _stop_generation(self):
        """Stop generation."""
        self.is_generating = False
    
    def _on_play_audio(self):
        """Play audio."""
        pass
    
    def _on_stop_audio(self):
        """Stop audio playback."""
        self.timeline.stop()
    
    def _toggle_playback(self):
        """Toggle playback."""
        if self.timeline.is_playing:
            self.timeline.pause()
        else:
            self.timeline.play()


def run():
    """Run the application."""
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    apply_theme(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
