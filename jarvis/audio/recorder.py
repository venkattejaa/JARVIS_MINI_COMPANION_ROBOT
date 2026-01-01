"""
Audio Recorder Module for JARVIS

This module handles microphone input recording for the JARVIS voice assistant.
Records audio from USB microphone with specific parameters required by Deepgram:
- 16 kHz sample rate
- Mono channel
- 16-bit depth
- WAV format

Uses sounddevice for cross-platform audio recording with NumPy arrays.
"""

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent.parent))
from jarvis.config import AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, AUDIO_DTYPE, AUDIO_DURATION


class AudioRecorder:
    """
    Handles audio recording from USB microphone.
    
    Attributes:
        sample_rate (int): Audio sample rate in Hz (16000)
        channels (int): Number of audio channels (1 for mono)
        dtype (str): Data type for audio samples ('int16')
        duration (int): Recording duration in seconds
    """
    
    def __init__(self):
        """Initialize audio recorder with configuration from config.py"""
        self.sample_rate = AUDIO_SAMPLE_RATE
        self.channels = AUDIO_CHANNELS
        self.dtype = AUDIO_DTYPE
        self.duration = AUDIO_DURATION
        
    def record(self, output_file="audio.wav"):
        """
        Record audio from the default microphone and save to WAV file.
        
        Args:
            output_file (str): Path to save the recorded audio file
            
        Returns:
            str: Path to the saved audio file
            
        Raises:
            Exception: If recording fails
        """
        try:
            print(f"[AudioRecorder] Recording for {self.duration} seconds...")
            print("[AudioRecorder] Speak now!")
            
            # Record audio using sounddevice
            # sounddevice.rec() records audio and returns a NumPy array
            audio_data = sd.rec(
                frames=int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype
            )
            
            # Wait for recording to complete
            sd.wait()
            
            print("[AudioRecorder] Recording complete.")
            
            # Save as WAV file using scipy
            write(output_file, self.sample_rate, audio_data)
            print(f"[AudioRecorder] Audio saved to {output_file}")
            
            return output_file
            
        except Exception as e:
            print(f"[AudioRecorder] ERROR: Failed to record audio: {e}")
            raise
            
    def list_devices(self):
        """
        List all available audio input devices.
        Useful for debugging microphone issues.
        
        Returns:
            None (prints device list)
        """
        print("[AudioRecorder] Available audio devices:")
        print(sd.query_devices())


# Test function for standalone testing
if __name__ == "__main__":
    recorder = AudioRecorder()
    
    # List available devices
    print("\n=== Available Audio Devices ===")
    recorder.list_devices()
    
    # Test recording
    print("\n=== Testing Audio Recording ===")
    try:
        output_file = recorder.record("test_audio.wav")
        print(f"✓ Recording test successful: {output_file}")
    except Exception as e:
        print(f"✗ Recording test failed: {e}")
