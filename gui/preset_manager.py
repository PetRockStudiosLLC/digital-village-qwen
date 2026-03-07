"""Preset manager - save/load character configurations."""

import json
import os
from typing import List, Optional, Dict, Any
from PySide6.QtWidgets import QFileDialog, QMessageBox

from .character_panel import CharacterData


class PresetManager:
    """Manage save/load of character presets."""
    
    PRESET_FILTER = "JSON Files (*.json);;All Files (*)"
    
    @staticmethod
    def save_preset(
        file_path: str,
        characters: List[CharacterData],
        settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save preset to file."""
        try:
            preset_data = {
                "name": os.path.splitext(os.path.basename(file_path))[0],
                "characters": [char.to_dict() for char in characters],
                "settings": settings or {},
            }
            
            os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving preset: {e}")
            return False
    
    @staticmethod
    def load_preset(file_path: str) -> Optional[Dict[str, Any]]:
        """Load preset from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            print(f"Error loading preset: {e}")
            return None
    
    @staticmethod
    def get_characters_from_preset(data: Dict[str, Any]) -> List[CharacterData]:
        """Extract characters from preset data."""
        characters = []
        
        for i, char_dict in enumerate(data.get("characters", [])):
            from .style import get_character_color
            color = get_character_color(i)
            char = CharacterData.from_dict(char_dict, color)
            characters.append(char)
        
        return characters
    
    @staticmethod
    def get_settings_from_preset(data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract settings from preset data."""
        return data.get("settings", {})
    
    @staticmethod
    def show_save_dialog(
        parent,
        default_name: str = "preset.json"
    ) -> Optional[str]:
        """Show save file dialog."""
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Save Preset",
            default_name,
            PresetManager.PRESET_FILTER
        )
        return file_path
    
    @staticmethod
    def show_load_dialog(parent) -> Optional[str]:
        """Show load file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Load Preset",
            "",
            PresetManager.PRESET_FILTER
        )
        return file_path
    
    @staticmethod
    def show_error(parent, message: str):
        """Show error message."""
        QMessageBox.critical(parent, "Error", message)
    
    @staticmethod
    def show_success(parent, message: str):
        """Show success message."""
        QMessageBox.information(parent, "Success", message)
