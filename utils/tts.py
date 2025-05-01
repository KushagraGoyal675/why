# utils/tts.py

import os
import tempfile
from typing import Dict, Any, Optional
from gtts import gTTS
import base64
import time
import pygame

# pip install gtts requests

class TTSEngine:
    def __init__(self):
        try:
            self.temp_dir = tempfile.mkdtemp()
            self.voice_settings = {
                "judge": {"language": "en", "slow": False},
                "plaintiff": {"language": "en", "slow": False},
                "defendant": {"language": "en", "slow": False},
                "witness": {"language": "en", "slow": False}
            }
            pygame.mixer.init()
            print("TTSEngine initialized successfully")
        except Exception as e:
            print(f"Error initializing TTSEngine: {str(e)}")
            raise

    def generate_tts(self, text: str, role: str = "judge", language: str = "en") -> str:
        """Generate TTS audio for the given text"""
        try:
            print(f"Generating TTS for role: {role}, language: {language}")
            print(f"Text length: {len(text)}")
            
            settings = self.voice_settings.get(role, {"language": language, "slow": False})
            print(f"Using settings: {settings}")
            
            tts = gTTS(text=text, lang=settings["language"], slow=settings["slow"])
            
            # Save to temporary file
            filename = f"tts_{role}_{hash(text)}.mp3"
            filepath = os.path.join(self.temp_dir, filename)
            print(f"Saving to: {filepath}")
            
            tts.save(filepath)
            print("TTS file saved successfully")
            
            return filepath
        except Exception as e:
            print(f"Error generating TTS: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def play_audio(self, filepath: str) -> bool:
        """Play the generated audio file"""
        try:
            print(f"Playing audio from: {filepath}")
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            print("Audio playback completed")
            return True
        except Exception as e:
            print(f"Error playing audio: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

    def speak(self, text: str, role: str = "judge", language: str = "en") -> bool:
        """Generate and play TTS audio for the given text."""
        try:
            print(f"Speaking text for role: {role}")
            print(f"Text: {text[:100]}...")  # Print first 100 chars
            
            filepath = self.generate_tts(text, role=role, language=language)
            if filepath:
                return self.play_audio(filepath)
            return False
        except Exception as e:
            print(f"Error in speak method: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

    def cleanup(self):
        """Clean up temporary files"""
        try:
            for filename in os.listdir(self.temp_dir):
                filepath = os.path.join(self.temp_dir, filename)
                os.remove(filepath)
            os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up TTS files: {str(e)}")

    def set_voice_settings(self, role: str, settings: Dict[str, Any]):
        """Set voice settings for a specific role"""
        self.voice_settings[role] = settings

    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages for TTS"""
        return {
            "en": "English",
            "hi": "Hindi"
        }

# ------------------ Convenience Functions ------------------ #

tts_engine = TTSEngine()

def generate_tts(text, language="en", voice="default"):
    """Generate speech audio file from text."""
    return tts_engine.generate_tts(text, language, voice)

def cleanup():
    """Delete temporary audio files."""
    tts_engine.cleanup()
