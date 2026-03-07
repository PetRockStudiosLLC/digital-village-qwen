"""
Fish Speech TTS Module - High-quality Text-to-Speech

Fish Speech provides:
- Better quality than Chatterbox
- Emotion control markers
- Voice cloning with reference audio
- Faster inference on GPU
"""

import requests
import io
import os
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


class FishSpeechTTS:
    """Text-to-Speech using Fish Speech API."""

    def __init__(
        self,
        api_url: str = "http://localhost:8080",
        voice: str = None,  # Reference audio file or voice ID
        voice_mode: str = "clone",  # "clone" or "preset"
    ):
        """
        Initialize Fish Speech TTS.

        Args:
            api_url: Fish Speech API URL
            voice: Reference audio path or voice ID
            voice_mode: "clone" for voice cloning, "preset" for preset voices
        """
        self.api_url = api_url.rstrip("/")
        self.voice = voice
        self.voice_mode = voice_mode

        # Persistent session
        self.session = requests.Session()

    def speak(self, text: str, wait: bool = True, speed: float = 1.0):
        """
        Speak text with Fish Speech.

        Args:
            text: Text to speak (can include emotion markers)
            wait: Wait for speech to finish
            speed: Speed factor (1.0 = normal)
        """
        # Adjust speed (Fish Speech uses speed_factor)
        speed_factor = 1.0 / speed if speed > 0 else 1.0

        # Build request
        if self.voice_mode == "clone" and self.voice:
            # Voice cloning mode
            data = {
                "text": text,
                "reference_audio": self.voice,  # Base64 encoded audio
                "max_new_tokens": 1024,
                "temperature": 0.7,
                "speed": speed_factor,
            }
        else:
            # Using a voice ID
            data = {
                "text": text,
                "voice_id": self.voice,
                "max_new_tokens": 1024,
                "temperature": 0.7,
                "speed": speed_factor,
            }

        try:
            response = self.session.post(
                f"{self.api_url}/v1/tts", json=data, timeout=60
            )
            response.raise_for_status()

            # Play audio
            self._play_audio(response.content)

        except Exception as e:
            print(f"[Fish TTS] Error: {e}")

    def _play_audio(self, audio_bytes: bytes):
        """Play audio bytes."""
        pg = _get_pygame()
        if not pg:
            print("[Fish TTS] No pygame")
            return

        global _pygame_initialized
        if not _pygame_initialized:
            try:
                # Fish Speech outputs 24kHz typically
                pg.mixer.init(frequency=24000, size=-16, channels=1)
                _pygame_initialized = True
            except Exception as e:
                print(f"[Fish TTS] Init error: {e}")
                pg.mixer.init()
                _pygame_initialized = True

        try:
            audio_data = io.BytesIO(audio_bytes)
            pg.mixer.music.load(audio_data)
            pg.mixer.music.play()
            while pg.mixer.music.get_busy():
                pg.time.wait(10)
        except Exception as e:
            print(f"[Fish TTS] Play error: {e}")

    def speak_async(self, text: str):
        """Speak in background thread."""
        thread = threading.Thread(target=self.speak, args=(text, True), daemon=True)
        thread.start()

    def set_voice(self, voice: str):
        """Set the voice."""
        self.voice = voice

    def use_voice_clone(self, reference_audio_path: str):
        """Use voice cloning with reference audio."""
        # Read and encode reference audio
        try:
            with open(reference_audio_path, "rb") as f:
                import base64

                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
                self.voice = audio_b64
                self.voice_mode = "clone"
        except Exception as e:
            print(f"[Fish TTS] Error loading reference: {e}")

    def use_preset(self, voice_id: str):
        """Use a preset voice."""
        self.voice = voice_id
        self.voice_mode = "preset"


def get_fish_tts(
    api_url: str = "http://localhost:8080", voice: str = None
) -> FishSpeechTTS:
    """Create Fish Speech TTS instance."""
    return FishSpeechTTS(api_url=api_url, voice=voice)
