# utils/stt.py

import os
import tempfile
import speech_recognition as sr
import platform
import threading
import time
import streamlit as st
from typing import Optional, Dict, Any

class STTEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.temp_dir = tempfile.mkdtemp()
        self.language_settings = {
            "en": "en-US",  # English
            "hi": "hi-IN"   # Hindi
        }
    
    def process_audio(self, audio_data: bytes, language: str = "en") -> Optional[str]:
        """Process audio data and convert to text"""
        try:
            # Save audio data to temporary file
            filename = "temp_audio.wav"
            filepath = os.path.join(self.temp_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(audio_data)
            
            # Process audio file
            with sr.AudioFile(filepath) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.language_settings.get(language, "en-US")
                )
            
            return text
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Speech Recognition service; {e}")
            return None
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            return None
    
    def process_microphone_input(self, language: str = "en") -> Optional[str]:
        """Process audio from microphone and convert to text"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.language_settings.get(language, "en-US")
                )
                return text
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Speech Recognition service; {e}")
            return None
        except Exception as e:
            print(f"Error processing microphone input: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            for filename in os.listdir(self.temp_dir):
                filepath = os.path.join(self.temp_dir, filename)
                os.remove(filepath)
            os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up STT files: {str(e)}")
    
    def set_language_code(self, language: str, code: str):
        """Set language code for a specific language"""
        self.language_settings[language] = code
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages for STT"""
        return {
            "en": "English",
            "hi": "Hindi"
        }

# ------------------ Convenience Functions ------------------ #

# Initialize the engine globally
stt_engine = STTEngine()

def recognize_speech(language="en", timeout=5):
    """Record and recognize speech from microphone."""
    return stt_engine.recognize_from_microphone(language, timeout)

def recognize_from_file(file_path, language="en"):
    """Recognize speech from an audio file."""
    return stt_engine.recognize_from_file(file_path, language)

def start_listening(callback_fn, language="en"):
    """Start live continuous listening."""
    return stt_engine.start_continuous_listening(callback_fn, language)

def stop_listening():
    """Stop live continuous listening."""
    return stt_engine.stop_continuous_listening()

def cleanup():
    """Clean temporary files."""
    return stt_engine.cleanup()
