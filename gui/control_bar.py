"""Control bar - bottom controls for generation."""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Signal, Qt

from .style import COLORS


class ControlBar(QWidget):
    """Bottom control bar for generation controls."""
    
    generate_clicked = Signal()
    mode_changed = Signal(str)  # "stream" or "generate"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background_alt']};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        options_label = QLabel("Options:")
        options_label.setStyleSheet("color: #888;")
        layout.addWidget(options_label)
        
        self.individual_check = QCheckBox("Individual")
        self.individual_check.setToolTip("Save each clip separately")
        layout.addWidget(self.individual_check)
        
        self.combine_check = QCheckBox("Combine")
        self.combine_check.setToolTip("Create combined audio file")
        self.combine_check.setChecked(True)
        layout.addWidget(self.combine_check)
        
        self.play_final_check = QCheckBox("Play Final")
        self.play_final_check.setToolTip("Play combined audio after generation")
        layout.addWidget(self.play_final_check)
        
        layout.addSpacing(20)
        
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("color: #888;")
        layout.addWidget(mode_label)
        
        self.mode_group = QButtonGroup(self)
        
        self.stream_radio = QRadioButton("Stream")
        self.stream_radio.setToolTip("Generate → Play → Continue")
        self.stream_radio.setChecked(True)
        self.stream_radio.toggled.connect(lambda checked: self._on_mode_changed("stream") if checked else None)
        self.mode_group.addButton(self.stream_radio)
        layout.addWidget(self.stream_radio)
        
        self.generate_only_radio = QRadioButton("Gen Only")
        self.generate_only_radio.setToolTip("Generate all → Save → Optional Play")
        self.generate_only_radio.toggled.connect(lambda checked: self._on_mode_changed("generate") if checked else None)
        self.mode_group.addButton(self.generate_only_radio)
        layout.addWidget(self.generate_only_radio)
        
        layout.addStretch()
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        self.generate_btn = QPushButton("▶ Generate")
        self.generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['text_bright']};
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_disabled']};
            }}
        """)
        self.generate_btn.clicked.connect(self.generate_clicked.emit)
        layout.addWidget(self.generate_btn)
    
    def _on_mode_changed(self, mode: str):
        """Handle mode change."""
        self.mode_changed.emit(mode)
    
    def set_generating(self, generating: bool):
        """Set generating state."""
        self.generate_btn.setEnabled(not generating)
        self.generate_btn.setText("⏳ Generating..." if generating else "▶ Generate")
        if not generating:
            self.status_label.setText("")
    
    def set_status(self, text: str):
        """Set status text."""
        self.status_label.setText(text)
    
    def get_options(self) -> dict:
        """Get current options."""
        return {
            "individual": self.individual_check.isChecked(),
            "combine": self.combine_check.isChecked(),
            "play_final": self.play_final_check.isChecked(),
            "mode": "stream" if self.stream_radio.isChecked() else "generate",
        }
    
    def set_options(self, options: dict):
        """Set options."""
        self.individual_check.setChecked(options.get("individual", False))
        self.combine_check.setChecked(options.get("combine", True))
        self.play_final_check.setChecked(options.get("play_final", False))
        
        mode = options.get("mode", "stream")
        if mode == "stream":
            self.stream_radio.setChecked(True)
        else:
            self.generate_only_radio.setChecked(True)
