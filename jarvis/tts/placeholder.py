"""Text-to-Speech Placeholder Module for JARVIS

This is a placeholder stub for future Murf TTS integration.
Currently, JARVIS outputs responses as text to console only.

FUTURE INTEGRATION:
When Murf TTS is added, this module will:
- Accept text input
- Convert text to speech using Murf API
- Play audio through speakers/audio output device
- Handle audio playback errors gracefully

For now, this module provides a simple interface that can be
extended without refactoring the main system.
"""

import sys
import time
import threading
import queue
from pathlib import Path

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent.parent))
from jarvis.config import WAKE_WORD_ENABLED

# Import wake word detector if available
if WAKE_WORD_ENABLED:
    try:
        from jarvis.wake_word.detector import WakeWordDetector
    except ImportError:
        WakeWordDetector = None
        WAKE_WORD_ENABLED = False


class TTSClient:
    """
    Placeholder Text-to-Speech client with interrupt capability.
    
    This class provides a stub interface for TTS functionality.
    Currently just prints text to console. Will be extended with
    actual text-to-speech using Murf API in future versions.
    """
    
    def __init__(self):
        """Initialize TTS client placeholder"""
        print("[TTS] Placeholder initialized (text output only)")
        
        # Initialize wake word detector for interruption if enabled
        self.wake_word_detector = None
        if WAKE_WORD_ENABLED:
            try:
                self.wake_word_detector = WakeWordDetector()
                print("[TTS] Wake word detector initialized for interruption")
            except Exception as e:
                print(f"[TTS] Warning: Could not initialize wake word detector: {e}")
                self.wake_word_detector = None
        
        # Audio queue for processing audio during TTS
        self.audio_queue = queue.Queue()
        self.interrupted = False
        
        # Thread for monitoring wake word during TTS
        self.monitoring_thread = None
        self.monitoring_active = False
    
    def speak(self, text):
        """
        Output text as speech (placeholder implementation).
        
        Currently just prints to console. Will be replaced with
        actual text-to-speech using Murf API in future versions.
        
        Args:
            text (str): The text to convert to speech
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"\n[JARVIS SPEAKS]: {text}\n")
            
            # Simulate speaking with interrupt monitoring if wake word detection is enabled
            if self.wake_word_detector and self.wake_word_detector.enabled:
                print("[TTS] Speak function can be made interruptible in future")
            
            return True
        except Exception as e:
            print(f"[TTS] ERROR: Failed to output text: {e}")
            return False
    
    def speak_with_interruption(self, text, audio_callback=None):
        """
        Speak text with ability to be interrupted by wake word.
        
        Args:
            text (str): The text to convert to speech
            audio_callback: Function to provide audio frames for wake word detection
            
        Returns:
            bool: True if completed normally, False if interrupted
        """
        if not self.wake_word_detector or not self.wake_word_detector.enabled:
            # Just speak normally if no wake word detection
            self.speak(text)
            return True
        
        self.interrupted = False
        
        # Start monitoring for wake word in a separate thread
        self._start_wake_word_monitoring(audio_callback)
        
        try:
            # Simulate speaking with interruption capability
            words = text.split()
            for i, word in enumerate(words):
                if self.interrupted:
                    print("\n[JARVIS] Speech interrupted by wake word!")
                    break
                
                # Print word by word to simulate speech
                print(f"{word} ", end="", flush=True)
                
                # Small delay to simulate speech timing
                time.sleep(0.1)
            
            if not self.interrupted:
                print()  # New line at end
                print(f"\n[JARVIS SPEAKS]: {text}")
                
        finally:
            self._stop_wake_word_monitoring()
        
        return not self.interrupted
    
    def _start_wake_word_monitoring(self, audio_callback):
        """Start monitoring for wake word in a separate thread."""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_wake_word,
            args=(audio_callback,)
        )
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def _stop_wake_word_monitoring(self):
        """Stop monitoring for wake word."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
    
    def _monitor_wake_word(self, audio_callback):
        """Monitor audio for wake word in background thread."""
        if not audio_callback:
            return
        
        while self.monitoring_active and not self.interrupted:
            try:
                # Get audio frame from callback
                audio_frame = audio_callback()
                if audio_frame and self.wake_word_detector.detect_wake_word(audio_frame):
                    self.interrupted = True
                    print("\n[INTERRUPT] Wake word 'jarvis' detected!")
                    break
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.05)
            except Exception:
                # Continue monitoring even if there are errors
                time.sleep(0.1)


# Test function for standalone testing
if __name__ == "__main__":
    client = TTSClient()
    
    print("\n=== Testing TTS Placeholder ===")
    
    test_messages = [
        "Hello! I am JARVIS, your intelligent assistant.",
        "The weather today is sunny and pleasant.",
        "How may I assist you further?"
    ]
    
    for message in test_messages:
        success = client.speak(message)
        if success:
            print("✓ TTS test successful")
        else:
            print("✗ TTS test failed")
