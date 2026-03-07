"""
TTS Module - Optimized Real-time Text-to-Speech using Chatterbox
"""

import requests
import io
import os
import sys
import threading

# Lazy pygame loading
_pygame = None
_pygame_initialized = False


def _get_pygame():
    global _pygame
    if _pygame is None:
        try:
            import pygame as pg

            _pygame = pg
        except ImportError:
            return None
    return _pygame


class ChatterboxTTS:
    """Optimized Text-to-Speech using Chatterbox API."""

    def __init__(
        self,
        api_url: str = "http://localhost:8004",
        voice: str = "Alice",
        voice_mode: str = "predefined",
    ):
        self.api_url = api_url.rstrip("/")
        self.voice = voice
        self.voice_mode = voice_mode

        # Persistent session for warm connections
        self.session = requests.Session()

    def speak(self, text: str, wait: bool = True, speed: float = 1.0):
        """Speak text - optimized for speed."""

        # Fast inference params
        if self.voice_mode == "clone":
            data = {
                "text": text,
                "voice_mode": "clone",
                "reference_audio_filename": self.voice,
                "output_format": "wav",
                "speed_factor": speed,
                "cfg_weight": 0.4,
                "exaggeration": 0.7,
            }
        else:
            data = {
                "text": text,
                "voice_mode": "predefined",
                "predefined_voice_id": self.voice,
                "output_format": "wav",
                "speed_factor": speed,
                "cfg_weight": 0.4,
                "exaggeration": 0.7,
            }

        try:
            # Use persistent session
            response = self.session.post(f"{self.api_url}/tts", json=data, timeout=30)
            response.raise_for_status()

            # Play audio
            self._play_audio(response.content)

        except Exception as e:
            print(f"[TTS] Error: {e}")

    def _play_audio(self, audio_bytes: bytes):
        """Play audio bytes."""
        pg = _get_pygame()
        if not pg:
            print(f"[TTS] No pygame")
            return

        global _pygame_initialized
        if not _pygame_initialized:
            try:
                pg.mixer.init(frequency=24000, size=-16, channels=1)
                _pygame_initialized = True
            except Exception as e:
                print(f"[TTS] Init error: {e}")
                pg.mixer.init()
                _pygame_initialized = True

        try:
            audio_data = io.BytesIO(audio_bytes)
            pg.mixer.music.load(audio_data)
            pg.mixer.music.play()
            while pg.mixer.music.get_busy():
                pg.time.wait(10)
        except Exception as e:
            print(f"[TTS] Play error: {e}")

    def speak_async(self, text: str):
        """Speak in background."""
        thread = threading.Thread(target=self.speak, args=(text, True), daemon=True)
        thread.start()

    def set_voice(self, voice: str):
        self.voice = voice

    def use_cloned_voice(self, ref: str):
        self.voice_mode = "clone"
        self.voice = ref

    def use_predefined_voice(self, voice: str):
        self.voice_mode = "predefined"
        self.voice = voice


def get_tts(
    api_url: str = "http://localhost:8004", voice: str = "Alice"
) -> ChatterboxTTS:
    return ChatterboxTTS(api_url=api_url, voice=voice)
