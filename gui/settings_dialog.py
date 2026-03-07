"""Settings dialog - modal for configuration."""

import os
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QGroupBox, QFormLayout, QSlider,
    QFileDialog, QCheckBox, QSpinBox, QDialogButtonBox
)
from PySide6.QtCore import Signal

from .style import COLORS


class SettingsDialog(QDialog):
    """Settings configuration dialog."""
    
    settings_changed = Signal(dict)
    
    def __init__(self, current_settings: Optional[dict] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(450)
        
        self.settings = current_settings or self._default_settings()
        
        self.init_ui()
        self._load_settings()
    
    def _default_settings(self) -> dict:
        """Get default settings."""
        return {
            "lm_studio_host": "http://192.168.56.1:6842",
            "model_name": "qwen/qwen3.5-9b",
            "output_folder": "output",
            "pause_min": 0.5,
            "pause_max": 1.5,
            "preview_phrase": "Hello, this is a test of the voice.",
            "default_emotion": "neutral",
            "num_turns": 5,
            "starter_message": "Hey, how are you doing?",
        }
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()
        
        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("http://192.168.56.1:6842")
        api_layout.addRow("LM Studio Host:", self.host_edit)
        
        self.model_combo = QComboBox()
        self._refresh_models()
        api_layout.addRow("Model:", self.model_combo)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_models)
        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(self.model_combo, 1)
        refresh_layout.addWidget(self.refresh_btn)
        api_layout.addRow("", refresh_layout)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        output_group = QGroupBox("Output")
        output_layout = QFormLayout()
        
        self.output_folder_edit = QLineEdit()
        output_layout.addRow("Output Folder:", self.output_folder_edit)
        
        self.output_folder_btn = QPushButton("Browse...")
        self.output_folder_btn.clicked.connect(self._browse_output_folder)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.output_folder_edit, 1)
        folder_layout.addWidget(self.output_folder_btn)
        output_layout.addRow("", folder_layout)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        generation_group = QGroupBox("Generation")
        gen_layout = QFormLayout()
        
        self.num_turns_spin = QSpinBox()
        self.num_turns_spin.setRange(1, 50)
        self.num_turns_spin.setValue(5)
        gen_layout.addRow("Number of Turns:", self.num_turns_spin)
        
        self.starter_edit = QLineEdit()
        self.starter_edit.setPlaceholderText("Hey, how are you doing?")
        gen_layout.addRow("Starter Message:", self.starter_edit)
        
        self.pause_min_spin = QSpinBox()
        self.pause_min_spin.setRange(0, 10)
        self.pause_min_spin.setValue(1)
        self.pause_min_spin.setSuffix(" s")
        gen_layout.addRow("Min Pause:", self.pause_min_spin)
        
        self.pause_max_spin = QSpinBox()
        self.pause_max_spin.setRange(0, 10)
        self.pause_max_spin.setValue(2)
        self.pause_max_spin.setSuffix(" s")
        gen_layout.addRow("Max Pause:", self.pause_max_spin)
        
        self.preview_edit = QLineEdit()
        self.preview_edit.setPlaceholderText("Hello, this is a test.")
        gen_layout.addRow("Preview Phrase:", self.preview_edit)
        
        generation_group.setLayout(gen_layout)
        layout.addWidget(generation_group)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _load_settings(self):
        """Load current settings into UI."""
        self.host_edit.setText(self.settings.get("lm_studio_host", ""))
        
        model = self.settings.get("model_name", "")
        index = self.model_combo.findText(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        
        self.output_folder_edit.setText(self.settings.get("output_folder", "output"))
        self.num_turns_spin.setValue(self.settings.get("num_turns", 5))
        self.starter_edit.setText(self.settings.get("starter_message", ""))
        self.pause_min_spin.setValue(int(self.settings.get("pause_min", 0.5)))
        self.pause_max_spin.setValue(int(self.settings.get("pause_max", 1.5)))
        self.preview_edit.setText(self.settings.get("preview_phrase", ""))
    
    def _refresh_models(self):
        """Fetch available models from LM Studio."""
        import requests
        host = self.host_edit.text() or "http://192.168.56.1:6842"
        self.model_combo.clear()
        
        default_models = [
            "qwen/qwen3.5-9b",
            "qwen/qwen3.5-14b",
            "qwen/qwen3.5-32b",
            "llama-3.1-8b-instruct",
            "mistral-7b-instruct",
        ]
        
        try:
            resp = requests.get(f"{host}/v1/models", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("id", "") for m in data.get("data", [])]
                if models:
                    for m in models:
                        self.model_combo.addItem(m)
                    return
        except Exception as e:
            print(f"Could not fetch LM Studio models: {e}")
        
        for m in default_models:
            self.model_combo.addItem(m)
    
    def _browse_output_folder(self):
        """Browse for output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.output_folder_edit.text() or "output"
        )
        if folder:
            self.output_folder_edit.setText(folder)
    
    def _on_ok(self):
        """Save settings and close."""
        self.settings = {
            "lm_studio_host": self.host_edit.text(),
            "model_name": self.model_combo.currentText(),
            "output_folder": self.output_folder_edit.text(),
            "num_turns": self.num_turns_spin.value(),
            "starter_message": self.starter_edit.text(),
            "pause_min": self.pause_min_spin.value(),
            "pause_max": self.pause_max_spin.value(),
            "preview_phrase": self.preview_edit.text(),
        }
        
        self.settings_changed.emit(self.settings)
        self.accept()
    
    def get_settings(self) -> dict:
        """Get current settings."""
        return self.settings
