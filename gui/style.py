"""Blender-inspired dark theme for Digital Village GUI."""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


COLORS = {
    "background": "#1e1e1e",
    "background_alt": "#252526",
    "background_dark": "#181818",
    "surface": "#2d2d2d",
    "surface_hover": "#3d3d3d",
    "surface_active": "#4d4d4d",
    "border": "#3e3e3e",
    "border_focus": "#007fd4",
    "text": "#cccccc",
    "text_disabled": "#666666",
    "text_bright": "#ffffff",
    "accent": "#007fd4",
    "accent_hover": "#1e8ad4",
    "accent_pressed": "#006bb3",
    "success": "#4ec9b0",
    "warning": "#dcdcaa",
    "error": "#f14c4c",
    "character_1": "#4ec9b0",
    "character_2": "#dcdcaa",
    "character_3": "#ce9178",
    "character_4": "#c586c0",
    "character_5": "#9cdcfe",
    "character_6": "#d7ba7d",
}


CHARACTER_COLORS = [
    COLORS["character_1"],
    COLORS["character_2"],
    COLORS["character_3"],
    COLORS["character_4"],
    COLORS["character_5"],
    COLORS["character_6"],
]


def get_character_color(index: int) -> str:
    """Get color for character at index."""
    return CHARACTER_COLORS[index % len(CHARACTER_COLORS)]


def get_stylesheet() -> str:
    """Get the complete stylesheet."""
    return f"""
    QWidget {{
        background-color: {COLORS["background"]};
        color: {COLORS["text"]};
        font-family: "Segoe UI", -apple-system, sans-serif;
        font-size: 12px;
    }}
    
    QMainWindow {{
        background-color: {COLORS["background"]};
    }}
    
    QFrame {{
        background-color: {COLORS["background"]};
    }}
    
    QLabel {{
        background-color: transparent;
        color: {COLORS["text"]};
    }}
    
    QPushButton {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        padding: 6px 16px;
        min-height: 24px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS["surface_hover"]};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS["surface_active"]};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS["background_alt"]};
        color: {COLORS["text_disabled"]};
    }}
    
    QPushButton:focus {{
        border: 1px solid {COLORS["border_focus"]};
    }}
    
    QPushButton.QToolButton {{
        background-color: transparent;
        border: none;
        padding: 4px 8px;
    }}
    
    QPushButton.QToolButton:hover {{
        background-color: {COLORS["surface_hover"]};
        border-radius: 4px;
    }}
    
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {COLORS["background_dark"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        padding: 4px 8px;
        selection-background-color: {COLORS["accent"]};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {COLORS["border_focus"]};
    }}
    
    QComboBox {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        padding: 4px 8px;
        min-height: 24px;
    }}
    
    QComboBox:hover {{
        background-color: {COLORS["surface_hover"]};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {COLORS["text"]};
        margin-right: 8px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        selection-background-color: {COLORS["accent"]};
    }}
    
    QCheckBox {{
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {COLORS["border"]};
        border-radius: 3px;
        background-color: {COLORS["background_dark"]};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS["accent"]};
        border-color: {COLORS["accent"]};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {COLORS["accent"]};
    }}
    
    QProgressBar {{
        background-color: {COLORS["background_dark"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        text-align: center;
        height: 16px;
    }}
    
    QProgressBar::chunk {{
        background-color: {COLORS["accent"]};
        border-radius: 3px;
    }}
    
    QSlider::groove:horizontal {{
        background-color: {COLORS["background_dark"]};
        height: 6px;
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background-color: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background-color: {COLORS["surface_hover"]};
    }}
    
    QSlider::sub-page:horizontal {{
        background-color: {COLORS["accent"]};
        border-radius: 3px;
    }}
    
    QScrollBar:vertical {{
        background-color: {COLORS["background"]};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS["surface"]};
        min-height: 30px;
        border-radius: 6px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS["surface_hover"]};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {COLORS["background"]};
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS["surface"]};
        min-width: 30px;
        border-radius: 6px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS["surface_hover"]};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    QGroupBox {{
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        margin-top: 12px;
        padding-top: 12px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        padding: 0 4px;
    }}
    
    QMenuBar {{
        background-color: {COLORS["background_alt"]};
        border-bottom: 1px solid {COLORS["border"]};
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 4px 12px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS["surface_hover"]};
    }}
    
    QMenu {{
        background-color: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
    }}
    
    QMenu::item {{
        padding: 6px 24px 6px 12px;
    }}
    
    QMenu::item:selected {{
        background-color: {COLORS["accent"]};
    }}
    
    QToolTip {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        padding: 4px 8px;
    }}
    
    QDialog {{
        background-color: {COLORS["background"]};
    }}
    
    QSplitter::handle {{
        background-color: {COLORS["border"]};
    }}
    
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    """


def apply_theme(app: QApplication):
    """Apply the theme to the application."""
    app.setStyle("Fusion")
    app.setStyleSheet(get_stylesheet())
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS["background"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLORS["background_dark"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLORS["background_alt"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(COLORS["surface"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLORS["surface"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(COLORS["text_bright"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS["text_bright"]))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(COLORS["text_disabled"]))
    
    app.setPalette(palette)
