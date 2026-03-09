"""
Qwen3-TTS Module - Text-to-Speech (Local GPU)

Supports both preset speakers and custom voice cloning from reference audio.
"""

import os
import io
import threading
import soundfile as sf
import numpy as np

os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

_pygame = None
_pygame_initialized = False
_model_loaded = False
_model = None


def _get_pygame():
    global _pygame
    if _pygame is None:
        try:
            import pygame as pg
            _pygame = pg
        except ImportError:
            return None
    return _pygame


def _load_model(voice_mode="preset", model_folder="models"):
    """Load Qwen3TTSModel on GPU."""
    global _model, _model_loaded, _current_mode, _model_id
    if _model_loaded and getattr(_current_mode, 'voice_mode', None) == voice_mode:
        return _model
    
    from qwen_tts import Qwen3TTSModel
    import torch
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[Qwen3-TTS] Loading model on {device}...")
    
    # Use appropriate model based on mode
    if voice_mode == "clone":
        model_name = "Qwen3-TTS-12Hz-0.6B-Base"
    elif voice_mode == "design":
        model_name = "Qwen3-TTS-12Hz-0.6B-Base"
    else:
        model_name = "Qwen3-TTS-12Hz-0.6B-CustomVoice"
    
    model_path = os.path.join(model_folder, model_name)
    
    # Check if local model exists and has config.json
    config_path = os.path.join(model_path, "config.json")
    if os.path.exists(config_path):
        print(f"[Qwen3-TTS] Loading from local: {model_path}")
        _model = Qwen3TTSModel.from_pretrained(model_path, device_map=device)
    else:
        print(f"[Qwen3-TTS] Downloading: {model_name}")
        _model = Qwen3TTSModel.from_pretrained(f"Qwen/{model_name}", device_map=device)
    
    _model_loaded = True
    _model_id = model_name
    _current_mode = type('obj', (object,), {'voice_mode': voice_mode})()
    print(f"[Qwen3-TTS] Model loaded on {device}")
    return _model

_model_id = None

_current_mode = type('obj', (object,), {'voice_mode': None})()


class Qwen3TTS:
    """Text-to-Speech using Qwen3-TTS local model."""

    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
        device: str = "auto",
        voice_mode: str = "preset",  # "preset", "clone", or "design"
        speaker: str = "ryan",
        language: str = "English",
        voice_folder: str = "voices",
        model_folder: str = "models",
        instruct: str = None,  # Emotion/style instruction for VoiceDesign
    ):
        """
        Initialize Qwen3-TTS.

        Args:
            model_name: HuggingFace model name
            device: "auto", "cuda", or "cpu"
            voice_mode: "preset" for built-in speakers, "clone" for voice cloning, "design" for emotional voices
            speaker: Preset speaker name (if voice_mode="preset")
            language: Language for TTS
            voice_folder: Folder containing reference audio files for cloning
            instruct: Emotion/style instruction (e.g., "angry", "happy", "sad", "excited")
        """
        self.model_name = model_name
        self.device = device
        self.voice_mode = voice_mode
        self.speaker = speaker.lower()
        self.language = language
        self.voice_folder = voice_folder
        self.model_folder = model_folder
        self.instruct = instruct  # Emotion/style instruction
        self._model = None
        self._speaker_embeddings = {}

    def _ensure_model(self):
        if self._model is None:
            self._model = _load_model(self.voice_mode, self.model_folder)

    def set_speaker(self, speaker: str):
        """Set the preset speaker."""
        self.speaker = speaker.lower()

    def set_emotion(self, emotion: str):
        """Set emotion for VoiceDesign mode."""
        self.instruct = emotion

    def set_language(self, language: str):
        """Set the language."""
        self.language = language

    def _smooth_audio(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply smoothing to audio for more natural output.
        Reduces robotic harshness between words.
        """
        # Apply light fade in/out to remove clicks
        fade_samples = int(sample_rate * 0.01)  # 10ms fade
        if len(audio) > fade_samples * 2:
            audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
            audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        # Light smoothing to reduce harsh transitions
        window_size = int(sample_rate * 0.005)  # 5ms window
        if window_size > 1 and len(audio) > window_size:
            smoothed = np.convolve(audio, np.ones(window_size)/window_size, mode='same')
            # Blend original with smoothed (80% original, 20% smoothed)
            audio = audio * 0.85 + smoothed * 0.15
        
        # Normalize to prevent clipping
        max_val = np.abs(audio).max()
        if max_val > 0.95:
            audio = audio * (0.95 / max_val)
        
        return audio

    def load_voice(self, name: str, audio_path: str = None, transcript: str = None):
        """
        Load a custom voice from reference audio.
        
        Args:
            name: Name to save the voice as
            audio_path: Path to reference audio file. If None, looks in voice_folder/{name}.wav
            transcript: Transcript text for the reference audio. If None, looks for voice_folder/{name}.txt
        """
        if audio_path is None:
            audio_path = os.path.join(self.voice_folder, f"{name}.wav")
        
        if not os.path.exists(audio_path):
            print(f"[Qwen3-TTS] Voice file not found: {audio_path}")
            return False
        
        # Try to load transcript from .txt file if not provided
        if transcript is None:
            txt_path = os.path.join(self.voice_folder, f"{name}.txt")
            if os.path.exists(txt_path):
                with open(txt_path, "r", encoding="utf-8") as f:
                    transcript = f.read().strip()
                print(f"[Qwen3-TTS] Loaded transcript for {name}")
        
        self._ensure_model()
        
        try:
            import librosa
            
            ref_audio, sr = librosa.load(audio_path, sr=24000)
            # Create prompt with transcript for better voice cloning
            prompt = self._model.create_voice_clone_prompt(
                ref_audio=(ref_audio, sr),
                ref_text=transcript,
                x_vector_only_mode=(transcript is None)
            )
            self._speaker_embeddings[name] = prompt
            print(f"[Qwen3-TTS] Loaded voice: {name} from {audio_path}")
            return True
        except Exception as e:
            print(f"[Qwen3-TTS] Error loading voice: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_speakers(self):
        """Get available preset speakers."""
        self._ensure_model()
        return self._model.get_supported_speakers()

    def _play_audio(self, wav_data, sample_rate: int = 24000):
        """Play numpy audio data."""
        pg = _get_pygame()
        if not pg:
            return

        global _pygame_initialized
        if not _pygame_initialized:
            try:
                pg.mixer.init(frequency=sample_rate, size=-16, channels=1)
                _pygame_initialized = True
            except Exception:
                pg.mixer.init()
                _pygame_initialized = True

        try:
            int16_data = (wav_data * 32767).astype(np.int16)
            audio_io = io.BytesIO()
            sf.write(audio_io, int16_data, sample_rate, format="WAV")
            audio_io.seek(0)
            pg.mixer.music.load(audio_io)
            pg.mixer.music.play()
            while pg.mixer.music.get_busy():
                pg.time.wait(10)
        except Exception as e:
            print(f"[Qwen3-TTS] Play error: {e}")

    def speak(self, text: str, wait: bool = True, show_progress: bool = True, voice_name: str = None, save_path: str = None, non_streaming: bool = False):
        """
        Speak text.

        Args:
            text: Text to speak
            wait: Wait for completion
            show_progress: Show progress
            voice_name: Use custom voice (if loaded) instead of preset speaker
            save_path: Optional path to save audio file
            non_streaming: Use non-streaming mode for better quality
        """
        self._ensure_model()
        
        if show_progress:
            print(f"[Qwen3-TTS] Generating: {text[:50]}...")
        
        try:
            import time
            start = time.time()
            
            if self.voice_mode == "clone" and voice_name and voice_name in self._speaker_embeddings:
                # Use voice cloning with prompt + emotion (Base model)
                prompt = self._speaker_embeddings[voice_name]
                wavs, sr = self._model.generate_voice_clone(
                    text=text,
                    language=self.language,
                    voice_clone_prompt=prompt,
                    instruct=self.instruct,  # Add emotion
                    non_streaming_mode=non_streaming,
                )
            elif self.voice_mode == "design":
                # Use VoiceDesign with emotion instruction
                wavs, sr = self._model.generate_voice_design(
                    text=text,
                    language=self.language,
                    instruct=self.instruct,
                )
            else:
                # Use preset speaker (CustomVoice model)
                wavs, sr = self._model.generate_custom_voice(
                    text=text,
                    language=self.language,
                    speaker=self.speaker,
                    instruct=self.instruct,  # Can also use with CustomVoice
                )
            
            # Apply audio smoothing for more natural output
            wavs[0] = self._smooth_audio(wavs[0], sr)
            
            # Save to file if path provided
            if save_path:
                import os
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                sf.write(save_path, wavs[0], sr)
                print(f"[Qwen3-TTS] Saved: {save_path}")
            
            elapsed = time.time() - start
            audio_len = len(wavs[0]) / sr
            rtf = elapsed / audio_len if audio_len > 0 else 0
            
            if show_progress:
                print(f"[Qwen3-TTS] Generated {audio_len:.1f}s in {elapsed:.1f}s (RTF: {rtf:.2f}x)")
            
            if wait:
                self._play_audio(wavs[0], sr)
                
        except Exception as e:
            print(f"[Qwen3-TTS] Error: {e}")
            import traceback
            traceback.print_exc()

    def speak_async(self, text: str, show_progress: bool = False, voice_name: str = None):
        """Speak in background thread."""
        thread = threading.Thread(target=self.speak, args=(text, True, show_progress, voice_name), daemon=True)
        thread.start()

    def speak_to_file(self, text: str, output_file: str, voice_name: str = None):
        """Generate speech and save to file."""
        self._ensure_model()
        
        try:
            if self.voice_mode == "clone" and voice_name and voice_name in self._speaker_embeddings:
                speaker_embed = self._speaker_embeddings[voice_name]
                wavs, sr = self._model.generate_voice_clone(
                    text=text,
                    language=self.language,
                    speaker_embedding=speaker_embed,
                )
            else:
                wavs, sr = self._model.generate_custom_voice(
                    text=text,
                    language=self.language,
                    speaker=self.speaker,
                )
            sf.write(output_file, wavs[0], sr)
            print(f"[Qwen3-TTS] Saved to {output_file}")
        except Exception as e:
            print(f"[Qwen3-TTS] Error: {e}")


def get_qwen_tts(
    model_name: str = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
    device: str = "auto",
    voice_mode: str = "preset",
    speaker: str = "ryan",
    language: str = "English",
    voice_folder: str = "voices",
    model_folder: str = "models",
) -> Qwen3TTS:
    """Create Qwen3-TTS instance."""
    return Qwen3TTS(
        model_name=model_name,
        device=device,
        voice_mode=voice_mode,
        speaker=speaker,
        language=language,
        voice_folder=voice_folder,
        model_folder=model_folder,
    )
