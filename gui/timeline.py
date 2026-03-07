"""Timeline widget - audio playback timeline."""

import os
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QPen

from .style import COLORS


class WaveformWidget(QWidget):
    """Simple waveform visualization widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = []
        self.playhead_position = 0.0  # 0-1
        self.setMinimumHeight(40)
    
    def set_audio_data(self, data):
        """Set audio samples for visualization."""
        self.audio_data = data
        self.update()
    
    def set_playhead(self, position: float):
        """Set playhead position (0-1)."""
        self.playhead_position = max(0, min(1, position))
        self.update()
    
    def paintEvent(self, event):
        """Paint the waveform."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        painter.fillRect(0, 0, width, height, QColor(COLORS["background_dark"]))
        
        if not self.audio_data:
            pen = QPen(QColor(COLORS["border"]))
            painter.setPen(pen)
            painter.drawLine(0, height // 2, width, height // 2)
            return
        
        bar_width = 3
        bar_spacing = 1
        total_width = bar_width + bar_spacing
        num_bars = width // total_width
        
        step = len(self.audio_data) // max(num_bars, 1)
        if step == 0:
            step = 1
        
        center_y = height // 2
        max_height = height * 0.8
        
        for i in range(0, len(self.audio_data), step):
            sample = self.audio_data[i]
            bar_height = int(abs(sample) * max_height)
            if bar_height < 1:
                bar_height = 1
            
            x = (i // step) * total_width
            if x + bar_width > width:
                break
            
            if x / width <= self.playhead_position:
                painter.fillRect(x, center_y - bar_height // 2, bar_width, bar_height, QColor(COLORS["accent"]))
            else:
                painter.fillRect(x, center_y - bar_height // 2, bar_width, bar_height, QColor(COLORS["surface"]))
        
        playhead_x = int(self.playhead_position * width)
        painter.fillRect(playhead_x - 1, 0, 2, height, QColor(COLORS["text_bright"]))


class Timeline(QWidget):
    """Bottom timeline panel for audio playback."""
    
    play_clicked = Signal()
    stop_clicked = Signal()
    seek_signal = Signal(float)  # position 0-1
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_playing = False
        self.duration_ms = 0
        self.current_position_ms = 0
        self.audio_data = []
        self._playback_timer: Optional[QTimer] = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"background-color: {COLORS['border']};")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        header = QLabel("TIMELINE")
        header.setStyleSheet("font-weight: bold; color: #888;")
        layout.addWidget(header)
        
        self.waveform = WaveformWidget()
        layout.addWidget(self.waveform)
        
        controls = QHBoxLayout()
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedWidth(40)
        self.play_btn.clicked.connect(self._on_play_clicked)
        controls.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedWidth(40)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        controls.addWidget(self.stop_btn)
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("font-family: monospace;")
        controls.addWidget(self.time_label)
        
        controls.addStretch()
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setToolTip("Volume")
        controls.addWidget(QLabel("🔊"))
        controls.addWidget(self.volume_slider)
        
        layout.addLayout(controls)
    
    def set_audio_data(self, data):
        """Set audio data for waveform."""
        self.audio_data = data
        self.waveform.set_audio_data(data)
    
    def set_duration(self, duration_ms: int):
        """Set total duration in milliseconds."""
        self.duration_ms = duration_ms
        self._update_time_label()
    
    def set_position(self, position_ms: int):
        """Set current position in milliseconds."""
        self.current_position_ms = position_ms
        self._update_time_label()
        
        if self.duration_ms > 0:
            position = position_ms / self.duration_ms
            self.waveform.set_playhead(position)
    
    def _update_time_label(self):
        """Update the time label."""
        current = self._format_time(self.current_position_ms)
        total = self._format_time(self.duration_ms)
        self.time_label.setText(f"{current} / {total}")
    
    def _format_time(self, ms: int) -> str:
        """Format milliseconds to MM:SS."""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def _on_play_clicked(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def _on_stop_clicked(self):
        self.stop()
        self.stop_clicked.emit()
    
    def play(self):
        """Start playback."""
        self.is_playing = True
        self.play_btn.setText("⏸")
        
        if not self._playback_timer:
            self._playback_timer = QTimer()
            self._playback_timer.timeout.connect(self._on_playback_tick)
        
        self._playback_timer.start(50)
        self.play_clicked.emit()
    
    def pause(self):
        """Pause playback."""
        self.is_playing = False
        self.play_btn.setText("▶")
        
        if self._playback_timer:
            self._playback_timer.stop()
    
    def stop(self):
        """Stop playback."""
        self.pause()
        self.set_position(0)
        self.stop_clicked.emit()
    
    def _on_playback_tick(self):
        """Handle playback timer tick."""
        self.current_position_ms += 50
        
        if self.current_position_ms >= self.duration_ms:
            self.stop()
            return
        
        self._update_time_label()
        
        if self.duration_ms > 0:
            position = self.current_position_ms / self.duration_ms
            self.waveform.set_playhead(position)
    
    def load_audio_file(self, file_path: str):
        """Load audio file for display."""
        if not os.path.exists(file_path):
            return
        
        try:
            import soundfile as sf
            data, samplerate = sf.read(file_path, dtype='float32')
            
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            
            max_samples = 1000
            if len(data) > max_samples:
                step = len(data) // max_samples
                data = data[::step]
            
            self.audio_data = data
            self.waveform.set_audio_data(data)
            
            duration = len(data) / samplerate * 1000
            self.set_duration(int(duration))
            
        except Exception as e:
            print(f"Error loading audio: {e}")
    
    def get_volume(self) -> float:
        """Get volume (0-1)."""
        return self.volume_slider.value() / 100.0
