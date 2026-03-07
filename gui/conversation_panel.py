"""Conversation panel - right side of the GUI."""

import os
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QTextCharFormat, QFont

from .character_panel import CharacterData
from .style import COLORS


class MessageItem:
    """A single message in the conversation."""
    
    def __init__(self, character_name: str, text: str, color: str):
        self.character_name = character_name
        self.text = text
        self.color = color


class ConversationPanel(QWidget):
    """Right panel for displaying conversation."""
    
    generation_progress = Signal(str, float)  # character_name, progress (0-1)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages: List[MessageItem] = []
        self.characters: List[CharacterData] = []
        self.current_speaker: Optional[str] = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        header = QHBoxLayout()
        
        title = QLabel("CONVERSATION LOG")
        title.setStyleSheet("font-weight: bold; color: #888;")
        header.addWidget(title)
        
        header.addStretch()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear)
        header.addWidget(self.clear_btn)
        
        layout.addLayout(header)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"background-color: {COLORS['border']};")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        self.conversation_view = QScrollArea()
        self.conversation_view.setWidgetResizable(True)
        self.conversation_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.conversation_text = QTextEdit()
        self.conversation_text.setReadOnly(True)
        self.conversation_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['background_dark']};
                border: none;
                padding: 8px;
            }}
        """)
        
        self.conversation_view.setWidget(self.conversation_text)
        layout.addWidget(self.conversation_view)
        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #888;")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QFrame()
        progress_layout = QHBoxLayout(self.progress_bar)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_fill = QFrame()
        self.progress_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['accent']};
                border-radius: 2px;
            }}
        """)
        self.progress_fill.setFixedHeight(4)
        self.progress_fill.setMinimumWidth(0)
        self.progress_fill.setMaximumWidth(0)
        
        progress_layout.addWidget(self.progress_fill)
        
        layout.addWidget(self.progress_bar)
    
    def set_characters(self, characters: List[CharacterData]):
        """Set characters for color coding."""
        self.characters = characters
    
    def add_message(self, character_name: str, text: str):
        """Add a message to the conversation."""
        print(f"[DEBUG] add_message called: {character_name}: {text[:50]}...")
        color = "#cccccc"
        for char in self.characters:
            if char.name == character_name:
                color = char.color
                break
        
        print(f"[DEBUG] Using color: {color}, characters: {[(c.name, c.color) for c in self.characters]}")
        
        self.messages.append(MessageItem(character_name, text, color))
        self._update_display()
    
    def add_message_with_progress(self, character_name: str, text: str):
        """Add a message and show progress bar."""
        self.add_message(character_name, text)
        self.current_speaker = character_name
        self._update_progress(0)
    
    def update_progress(self, progress: float):
        """Update generation progress."""
        if self.current_speaker:
            self._update_progress(progress)
    
    def _update_progress(self, progress: float):
        """Update progress bar display."""
        max_width = self.progress_bar.width()
        self.progress_fill.setFixedWidth(int(max_width * progress))
        
        if self.current_speaker:
            self.progress_label.setText(f"Generating: {self.current_speaker} ({int(progress * 100)}%)")
        
        if progress >= 1.0:
            self.current_speaker = None
            self.progress_label.setText("")
            self.progress_fill.setFixedWidth(0)
    
    def _update_display(self):
        """Update the conversation text display."""
        html = ""
        
        for msg in self.messages:
            bubble_color = msg.color
            text_html = msg.text.replace("\n", "<br>")
            
            html += f'''
            <div style="margin-bottom: 12px; display: flex; flex-direction: column;">
                <div style="color: {msg.color}; font-weight: bold; font-size: 13px; margin-bottom: 4px;">
                    {msg.character_name}
                </div>
                <div style="
                    background-color: #2a2a2a;
                    padding: 10px 14px;
                    border-radius: 18px;
                    border-top-left-radius: 4px;
                    max-width: 85%;
                    align-self: flex-start;
                    line-height: 1.4;
                ">
                    {text_html}
                </div>
            </div>
            '''
        
        if not html:
            html = '<div style="color: #666; font-style: italic; text-align: center; padding: 40px;">Add characters and start generating...</div>'
        
        self.conversation_text.setHtml(html)
        
        scroll_bar = self.conversation_view.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())
    
    def clear(self):
        """Clear the conversation."""
        self.messages = []
        self.current_speaker = None
        self._update_display()
        self._update_progress(0)
