"""Character panel - left side of the GUI."""

import os
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFileDialog, QScrollArea, QFrame,
    QListWidget, QListWidgetItem, QSlider, QGroupBox
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QColor, QIcon

from .style import get_character_color, COLORS


@dataclass
class CharacterData:
    """Data for a conversation character."""
    
    name: str = "New Character"
    system_prompt: str = "You are a character in a conversation. Keep responses short - 1-2 sentences max."
    voice_mode: str = "clone"  # clone, preset, design
    voice_file: Optional[str] = None
    preset_speaker: str = "ryan"
    emotion: str = ""
    color: str = "#4ec9b0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "voice_mode": self.voice_mode,
            "voice_file": self.voice_file,
            "preset_speaker": self.preset_speaker,
            "emotion": self.emotion,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], color: str = "#4ec9b0") -> "CharacterData":
        """Create from dictionary."""
        return cls(
            name=data.get("name", "New Character"),
            system_prompt=data.get("system_prompt", "You are a character in a conversation. Keep responses short - 1-2 sentences max."),
            voice_mode=data.get("voice_mode", "clone"),
            voice_file=data.get("voice_file"),
            preset_speaker=data.get("preset_speaker", "ryan"),
            emotion=data.get("emotion", ""),
            color=color,
        )


class CharacterItem(QFrame):
    """Single character card widget."""
    
    changed = Signal()
    preview_requested = Signal(int)  # character index
    remove_requested = Signal(int)  # character index
    
    def __init__(self, index: int, data: CharacterData, parent=None):
        super().__init__(parent)
        self.index = index
        self.data = data
        self.init_ui()
    
    def init_ui(self):
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setMinimumHeight(180)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        header = QHBoxLayout()
        
        self.color_indicator = QLabel("●")
        self.color_indicator.setStyleSheet(f"color: {self.data.color}; font-size: 18px;")
        header.addWidget(self.color_indicator)
        
        self.name_edit = QLineEdit(self.data.name)
        self.name_edit.setPlaceholderText("Character name")
        self.name_edit.textChanged.connect(self._on_name_changed)
        header.addWidget(self.name_edit, 1)
        
        self.preview_btn = QPushButton()
        self.preview_btn.setIcon(QIcon.fromTheme("audio-x-generic", QIcon(":/icons/media-playback-start")))
        self.preview_btn.setToolTip("Preview voice")
        self.preview_btn.setFixedWidth(32)
        self.preview_btn.clicked.connect(lambda: self.preview_requested.emit(self.index))
        header.addWidget(self.preview_btn)
        
        self.remove_btn = QPushButton()
        self.remove_btn.setIcon(QIcon.fromTheme("list-remove", QIcon(":/icons/edit-delete")))
        self.remove_btn.setToolTip("Remove character")
        self.remove_btn.setFixedWidth(32)
        self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.index))
        header.addWidget(self.remove_btn)
        
        layout.addLayout(header)
        
        prompt_layout = QHBoxLayout()
        prompt_layout.addWidget(QLabel("System Prompt:"))
        
        self.prompt_edit = QLineEdit(self.data.system_prompt)
        self.prompt_edit.setPlaceholderText("You are a character in a conversation...")
        self.prompt_edit.textChanged.connect(self._on_prompt_changed)
        prompt_layout.addWidget(self.prompt_edit, 1)
        
        layout.addLayout(prompt_layout)
        
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        
        self.voice_mode_combo = QComboBox()
        self.voice_mode_combo.addItems(["Clone", "Preset", "Design"])
        voice_modes = {"Clone": "clone", "Preset": "preset", "Design": "design"}
        current_mode = self.data.voice_mode
        for key, value in voice_modes.items():
            if value == current_mode:
                self.voice_mode_combo.setCurrentText(key)
                break
        self.voice_mode_combo.currentTextChanged.connect(self._on_voice_mode_changed)
        voice_layout.addWidget(self.voice_mode_combo)
        
        layout.addLayout(voice_layout)
        
        self.voice_file_container = QWidget()
        self.voice_file_layout = QHBoxLayout(self.voice_file_container)
        self.voice_file_layout.setContentsMargins(0, 0, 0, 0)
        self.voice_file_layout.addWidget(QLabel("File:"))
        
        self.voice_file_edit = QLineEdit(self.data.voice_file or "")
        self.voice_file_edit.setPlaceholderText("Path to voice reference audio")
        self.voice_file_edit.textChanged.connect(self._on_voice_file_changed)
        self.voice_file_layout.addWidget(self.voice_file_edit, 1)
        
        self.browse_btn = QPushButton()
        self.browse_btn.setIcon(QIcon.fromTheme("folder-open", QIcon(":/icons/document-open")))
        self.browse_btn.setToolTip("Browse for voice file")
        self.browse_btn.setFixedWidth(32)
        self.browse_btn.clicked.connect(self._browse_voice_file)
        self.voice_file_layout.addWidget(self.browse_btn)
        
        layout.addWidget(self.voice_file_container)
        
        self.preset_container = QWidget()
        self.preset_layout = QHBoxLayout(self.preset_container)
        self.preset_layout.setContentsMargins(0, 0, 0, 0)
        self.preset_layout.addWidget(QLabel("Preset:"))
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "alex", "anna", "beth", "daniel", "david", "emma", 
            "george", "jenny", "john", "katherine", "lily", 
            "matthew", "michael", "olivia", "ryan", "sarah"
        ])
        self.preset_combo.setCurrentText(self.data.preset_speaker)
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        self.preset_layout.addWidget(self.preset_combo)
        
        layout.addWidget(self.preset_container)
        
        emotion_layout = QHBoxLayout()
        emotion_layout.addWidget(QLabel("Emotion:"))
        
        self.emotion_edit = QLineEdit(self.data.emotion)
        self.emotion_edit.setPlaceholderText("e.g., grumpy, angry, happy")
        self.emotion_edit.textChanged.connect(self._on_emotion_changed)
        emotion_layout.addWidget(self.emotion_edit, 1)
        
        layout.addLayout(emotion_layout)
        
        self._update_voice_file_visibility()
    
    def _update_voice_file_visibility(self):
        mode = self.voice_mode_combo.currentText().lower()
        self.voice_file_container.setVisible(mode == "clone")
        self.preset_container.setVisible(mode == "preset")
    
    def _on_name_changed(self, text: str):
        self.data.name = text
        self.changed.emit()
    
    def _on_prompt_changed(self, text: str):
        self.data.system_prompt = text
        self.changed.emit()
    
    def _on_voice_mode_changed(self, text: str):
        mode_map = {"Clone": "clone", "Preset": "preset", "Design": "design"}
        self.data.voice_mode = mode_map.get(text, "clone")
        self._update_voice_file_visibility()
        self.changed.emit()
    
    def _on_voice_file_changed(self, text: str):
        self.data.voice_file = text if text else None
        self.changed.emit()
    
    def _on_preset_changed(self, text: str):
        self.data.preset_speaker = text
        self.changed.emit()
    
    def _on_emotion_changed(self, text: str):
        self.data.emotion = text
        self.changed.emit()
    
    def _browse_voice_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Voice Reference Audio",
            "",
            "Audio Files (*.wav *.mp3 *.ogg);;All Files (*)"
        )
        if file_path:
            self.voice_file_edit.setText(file_path)
    
    def update_data(self, data: CharacterData):
        """Update character data."""
        self.data = data
        self.name_edit.setText(data.name)
        self.voice_mode_combo.setCurrentText(data.voice_mode.capitalize())
        self.voice_file_edit.setText(data.voice_file or "")
        self.preset_combo.setCurrentText(data.preset_speaker)
        self.emotion_edit.setText(data.emotion)
        self.color_indicator.setStyleSheet(f"color: {data.color}; font-size: 18px;")
        self._update_voice_file_visibility()


class CharacterPanel(QWidget):
    """Left panel for managing characters."""
    
    character_changed = Signal(int, CharacterData)
    preview_requested = Signal(int)
    remove_requested = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.characters: List[CharacterData] = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        header = QHBoxLayout()
        
        title = QLabel("CHARACTERS")
        title.setStyleSheet("font-weight: bold; color: #888;")
        header.addWidget(title)
        
        header.addStretch()
        
        self.add_btn = QPushButton("+ Add")
        self.add_btn.clicked.connect(lambda: self.add_character())
        header.addWidget(self.add_btn)
        
        layout.addLayout(header)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"background-color: {COLORS['border']};")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        self.character_list = QScrollArea()
        self.character_list.setWidgetResizable(True)
        self.character_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.character_container = QWidget()
        self.character_layout = QVBoxLayout(self.character_container)
        self.character_layout.setContentsMargins(0, 0, 0, 0)
        self.character_layout.setSpacing(8)
        self.character_layout.addStretch()
        
        self.character_list.setWidget(self.character_container)
        layout.addWidget(self.character_list)
    
    def add_character(self, data: Optional[CharacterData] = None):
        """Add a new character."""
        if data is None:
            color = get_character_color(len(self.characters))
            data = CharacterData(
                name=f"Character {len(self.characters) + 1}",
                voice_mode="clone",
                voice_file="",
                emotion="",
                color=color
            )
        
        self.characters.append(data)
        self._rebuild_character_widgets()
        self.character_changed.emit(len(self.characters) - 1, data)
    
    def remove_character(self, index: int):
        """Remove character at index."""
        if 0 <= index < len(self.characters):
            self.characters.pop(index)
            for i, char in enumerate(self.characters):
                char.color = get_character_color(i)
            self._rebuild_character_widgets()
    
    def get_characters(self) -> List[CharacterData]:
        """Get all characters."""
        return self.characters
    
    def set_characters(self, characters: List[CharacterData]):
        """Set all characters."""
        for i, char in enumerate(characters):
            char.color = get_character_color(i)
        self.characters = characters
        self._rebuild_character_widgets()
    
    def _rebuild_character_widgets(self):
        """Rebuild character widgets."""
        while self.character_layout.count() > 0:
            item = self.character_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for i, char in enumerate(self.characters):
            char.color = get_character_color(i)
            item = CharacterItem(i, char)
            item.changed.connect(lambda idx=i: self._on_character_changed(idx))
            item.preview_requested.connect(self.preview_requested.emit)
            item.remove_requested.connect(self.remove_requested.emit)
            self.character_layout.insertWidget(i, item)
        
        self.character_layout.addStretch()
    
    def _on_character_changed(self, index: int):
        """Handle character data change."""
        if 0 <= index < len(self.characters):
            self.character_changed.emit(index, self.characters[index])
    
    def clear(self):
        """Clear all characters."""
        self.characters = []
        self._rebuild_character_widgets()
