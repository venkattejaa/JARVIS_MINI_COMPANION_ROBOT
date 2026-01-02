"""
Wake Word Detection Module for JARVIS

This module handles wake word detection using Picovoice Porcupine.
It listens for the wake word 'jarvis' and signals when detected.

Note: This requires a Picovoice Porcupine license key.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent.parent))

from jarvis.config import WAKE_WORD_ENABLED, WAKE_WORD_PORCUPINE_ACCESS_KEY, WAKE_WORD_KEYWORD, WAKE_WORD_SENSITIVITY


class WakeWordDetector:
    """
    Handles wake word detection using Picovoice Porcupine.
    
    Attributes:
        enabled (bool): Whether wake word detection is enabled
        porcupine (pvporcupine.Porcupine): Porcupine wake word engine
        keyword_path (str): Path to wake word file
        sensitivity (float): Wake word detection sensitivity
    """
    
    def __init__(self):
        """Initialize wake word detector with configuration from config.py"""
        self.enabled = WAKE_WORD_ENABLED
        
        if not self.enabled:
            print("[WakeWord] Wake word detection disabled")
            self.porcupine = None
            return
        
        # Check if access key is configured
        if not WAKE_WORD_PORCUPINE_ACCESS_KEY or WAKE_WORD_PORCUPINE_ACCESS_KEY == "YOUR_PORCUPINE_ACCESS_KEY":
            print("[WakeWord] WARNING: Porcupine access key not configured")
            print("[WakeWord] To enable wake word detection, get a free key from:")
            print("[WakeWord] https://console.picovoice.ai/")
            print("[WakeWord] Wake word detection will be disabled")
            self.enabled = False
            self.porcupine = None
            return
        
        try:
            import pvporcupine
            
            # Initialize Porcupine with the 'jarvis' keyword
            self.porcupine = pvporcupine.create(
                access_key=WAKE_WORD_PORCUPINE_ACCESS_KEY,
                keywords=[WAKE_WORD_KEYWORD],
                sensitivities=[WAKE_WORD_SENSITIVITY]
            )
            
            print(f"[WakeWord] Initialized with keyword: '{WAKE_WORD_KEYWORD}'")
            print(f"[WakeWord] Sensitivity: {WAKE_WORD_SENSITIVITY}")
            
        except ImportError:
            print("[WakeWord] ERROR: pvporcupine not installed")
            print("[WakeWord] Install with: pip install pvporcupine")
            print("[WakeWord] Wake word detection will be disabled")
            self.enabled = False
            self.porcupine = None
        except Exception as e:
            print(f"[WakeWord] ERROR: Failed to initialize Porcupine: {e}")
            print("[WakeWord] Wake word detection will be disabled")
            self.enabled = False
            self.porcupine = None
    
    def detect_wake_word(self, audio_frame):
        """
        Detect wake word in audio frame.
        
        Args:
            audio_frame (bytes): Audio frame to analyze (16-bit, mono, 16kHz)
            
        Returns:
            bool: True if wake word detected, False otherwise
        """
        if not self.enabled or not self.porcupine:
            return False
        
        try:
            # Process audio frame with Porcupine
            result = self.porcupine.process(audio_frame)
            return result > 0  # True if wake word detected
        except Exception:
            return False  # Don't let errors break the system
    
    def get_frame_length(self):
        """
        Get required audio frame length for Porcupine.
        
        Returns:
            int: Required frame length in samples
        """
        if self.porcupine:
            return self.porcupine.frame_length
        else:
            # Default frame length if Porcupine not available
            return 512
    
    def get_sample_rate(self):
        """
        Get required sample rate for Porcupine.
        
        Returns:
            int: Required sample rate in Hz
        """
        if self.porcupine:
            return self.porcupine.sample_rate
        else:
            # Default sample rate if Porcupine not available
            return 16000
    
    def __del__(self):
        """Clean up Porcupine resources"""
        if hasattr(self, 'porcupine') and self.porcupine:
            try:
                self.porcupine.delete()
            except:
                pass


# Test function for standalone testing
if __name__ == "__main__":
    detector = WakeWordDetector()
    
    print("\n=== Testing Wake Word Detector ===")
    
    if detector.enabled:
        print("✓ Wake word detector initialized successfully")
        print(f"  Frame length: {detector.get_frame_length()}")
        print(f"  Sample rate: {detector.get_sample_rate()}")
    else:
        print("✗ Wake word detector not enabled")
        print("  This is expected if Porcupine access key is not configured")