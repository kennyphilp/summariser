"""
Simplified Text-to-Speech utilities for the AI Summarizer application.

This module provides essential TTS functionality with a focus on browser-based
speech synthesis and Google TTS as fallback.
"""

import os
import logging
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)


class TTSManager:
    """Simplified TTS manager focusing on essential functionality."""

    def __init__(self):
        self._gtts_available = self._check_gtts_availability()

    def _check_gtts_availability(self) -> bool:
        """Check if Google TTS is available."""
        try:
            import gtts
            return True
        except ImportError:
            logger.warning("Google TTS not available. Install with: pip install gtts")
            return False

    def speak_text(self, text: str) -> bool:
        """Speak text using available TTS engine."""
        if not text or not text.strip():
            return False

        # Try Google TTS first (better quality)
        if self._gtts_available:
            return self._speak_with_google_tts(text)

        # Fallback to system TTS
        return self._speak_with_system_tts(text)

    def generate_audio_file(self, text: str) -> Optional[str]:
        """Generate audio file for download."""
        if not text or not text.strip():
            return None

        if not self._gtts_available:
            logger.warning("Audio file generation requires Google TTS")
            return None

        try:
            from gtts import gTTS

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name

            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_path)
            return temp_path

        except Exception as e:
            logger.error(f"Audio file generation error: {e}")
            return None

    def _speak_with_google_tts(self, text: str) -> bool:
        """Speak text using Google TTS."""
        try:
            from gtts import gTTS
            import subprocess
            import platform

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name

            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_path)

            # Play the audio
            success = self._play_audio_file(temp_path)

            # Clean up
            os.unlink(temp_path)
            return success

        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            return False

    def _speak_with_system_tts(self, text: str) -> bool:
        """Speak text using system TTS (pyttsx3)."""
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 0.9)

            engine.say(text)
            engine.runAndWait()
            return True

        except ImportError:
            logger.warning("System TTS not available. Install with: pip install pyttsx3")
            return False
        except Exception as e:
            logger.error(f"System TTS error: {e}")
            return False

    def _play_audio_file(self, file_path: str) -> bool:
        """Play audio file using system default player."""
        try:
            import subprocess
            import platform

            system = platform.system().lower()
            if system == 'darwin':  # macOS
                subprocess.run(['afplay', file_path], check=True, capture_output=True)
            elif system == 'linux':
                subprocess.run(['mpg123', file_path], check=True, capture_output=True)
            elif system == 'windows':
                os.startfile(file_path)
            else:
                logger.warning(f"Audio playback not supported on {system}")
                return False

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to play audio: {e}")
            return False
        except FileNotFoundError:
            logger.warning("Audio player not found on system")
            return False

    def get_available_engines(self) -> list:
        """Get list of available TTS engines."""
        engines = []

        # Browser TTS (always available in modern browsers)
        engines.append({
            'name': 'browser',
            'available': True,
            'description': 'Browser-based speech synthesis'
        })

        # Google TTS
        engines.append({
            'name': 'google',
            'available': self._gtts_available,
            'description': 'Google Text-to-Speech'
        })

        # System TTS
        try:
            import pyttsx3
            engines.append({
                'name': 'system',
                'available': True,
                'description': 'System text-to-speech'
            })
        except ImportError:
            engines.append({
                'name': 'system',
                'available': False,
                'description': 'System text-to-speech (requires pyttsx3)'
            })

        return engines


# Global TTS manager instance
tts_manager = TTSManager()


class BrowserTTSTTS:
    """Browser-based TTS utility class."""

    @staticmethod
    def get_javascript() -> str:
        """Return JavaScript code for browser-based TTS."""
        return """
        function speakText(text) {
            if ('speechSynthesis' in window) {
                speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.9;
                utterance.pitch = 1;
                utterance.volume = 0.8;

                const voices = speechSynthesis.getVoices();
                const englishVoice = voices.find(voice =>
                    voice.lang.startsWith('en') &&
                    (voice.name.toLowerCase().includes('female') ||
                     voice.name.toLowerCase().includes('samantha'))
                );

                if (englishVoice) {
                    utterance.voice = englishVoice;
                }

                speechSynthesis.speak(utterance);
                return true;
            } else {
                console.warn('Speech synthesis not supported');
                return false;
            }
        }

        function stopSpeech() {
            if ('speechSynthesis' in window) {
                speechSynthesis.cancel();
            }
        }
        """


# Backward compatibility functions
def speak_summary(text: str) -> bool:
    """Backward compatibility function."""
    return tts_manager.speak_text(text)


def get_summary_audio_file(text: str) -> Optional[str]:
    """Backward compatibility function."""
    return tts_manager.generate_audio_file(text)


def speak_summary(text: str, engine: str = 'pyttsx3') -> bool:
    """
    Convenience function to speak summary text.

    Args:
        text: The text to speak
        engine: TTS engine to use ('pyttsx3', 'google', 'browser')

    Returns:
        bool: True if successful
    """
    return tts_manager.speak(text, engine)


def get_summary_audio_file(text: str, engine: str = 'google') -> Optional[str]:
    """
    Generate audio file for summary text.

    Args:
        text: The text to convert to audio
        engine: TTS engine to use ('pyttsx3', 'google', 'browser')

    Returns:
        str or None: Path to audio file, or None if failed
    """
    return tts_manager.get_audio_file(text, engine)