"""Digital Village GUI Module."""

__version__ = "1.0.0"

from .main_window import MainWindow
from .character_panel import CharacterPanel, CharacterData
from .conversation_panel import ConversationPanel
from .timeline import Timeline
from .toolbar import Toolbar
from .settings_dialog import SettingsDialog
from .control_bar import ControlBar
from .preset_manager import PresetManager

__all__ = [
    "MainWindow",
    "CharacterPanel",
    "CharacterData", 
    "ConversationPanel",
    "Timeline",
    "Toolbar",
    "SettingsDialog",
    "ControlBar",
    "PresetManager",
]
