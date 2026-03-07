"""Toolbar widget - top toolbar."""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QToolButton, QFrame
)
from PySide6.QtCore import Signal, Qt

from .style import COLORS


class Toolbar(QWidget):
    """Top toolbar with settings and preset buttons."""
    
    settings_clicked = Signal()
    load_preset_clicked = Signal()
    save_preset_clicked = Signal()
    export_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background_alt']};
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self.settings_btn)
        
        layout.addStretch()
        
        self.load_preset_btn = QPushButton("📂 Load Preset")
        self.load_preset_btn.clicked.connect(self.load_preset_clicked.emit)
        layout.addWidget(self.load_preset_btn)
        
        self.save_preset_btn = QPushButton("💾 Save Preset")
        self.save_preset_btn.clicked.connect(self.save_preset_clicked.emit)
        layout.addWidget(self.save_preset_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_clicked.emit)
        layout.addWidget(self.export_btn)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"background-color: {COLORS['border']};")
        layout.addWidget(separator)
