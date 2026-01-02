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
from jarvis.config import AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, AUDIO_DTYPE, AUDIO_DURATION, AUDIO_DEVICE, VAD_ENABLED, VAD_AGGRESSIVENESS, VAD_FRAME_DURATION, VAD_SILENCE_DURATION, VAD_MAX_RECORDING_TIME, WAKE_WORD_ENABLED


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
        self.channels = AUDIO_CHANNELS
        self.dtype = AUDIO_DTYPE
        self.duration = AUDIO_DURATION
        self.device = AUDIO_DEVICE
        self.vad_enabled = VAD_ENABLED
        self.vad_aggressiveness = VAD_AGGRESSIVENESS
        self.vad_frame_duration = VAD_FRAME_DURATION
        self.vad_silence_duration = VAD_SILENCE_DURATION
        self.vad_max_recording_time = VAD_MAX_RECORDING_TIME
        
        # Initialize VAD if enabled
        self.vad = None
        if self.vad_enabled:
            try:
                import webrtcvad
                self.vad = webrtcvad.Vad(self.vad_aggressiveness)
                print(f"[AudioRecorder] VAD initialized (aggressiveness: {self.vad_aggressiveness})")
            except ImportError:
                print("[AudioRecorder] Warning: webrtcvad not available, disabling VAD")
                self.vad_enabled = False
        
        # Initialize wake word detector if available
        self.wake_word_detector = None
        if WAKE_WORD_ENABLED:
            try:
                from jarvis.wake_word.detector import WakeWordDetector
                self.wake_word_detector = WakeWordDetector()
                if self.wake_word_detector.enabled:
                    print(f"[AudioRecorder] Wake word detector initialized")
                else:
                    print(f"[AudioRecorder] Wake word detector not enabled")
            except ImportError:
                print("[AudioRecorder] Warning: Wake word detector not available")
                self.wake_word_detector = None
        
        # Auto-detect supported sample rate
        self.sample_rate = self._get_supported_sample_rate(AUDIO_SAMPLE_RATE)
        
    def _get_supported_sample_rate(self, preferred_rate=16000):
        """
        Find a supported sample rate for the default input device.
        Tries preferred rate first, then common alternatives.
        
        Args:
            preferred_rate (int): Preferred sample rate (default 16000)
            
        Returns:
            int: A supported sample rate
        """
        # Common sample rates to try, in order of preference
        rates_to_try = [preferred_rate, 44100, 48000, 22050, 32000, 8000]
        
        try:
            device_info = sd.query_devices(kind='input')
            default_rate = int(device_info['default_samplerate'])
            
            # Add device's default rate to the list if not already there
            if default_rate not in rates_to_try:
                rates_to_try.insert(1, default_rate)
            
            print(f"[AudioRecorder] Device: {device_info['name']}")
            print(f"[AudioRecorder] Device default sample rate: {default_rate} Hz")
            
        except Exception as e:
            print(f"[AudioRecorder] Warning: Could not query device info: {e}")
        
        # Try each sample rate
        for rate in rates_to_try:
            try:
                # Test if this rate is supported by attempting to open a stream
                sd.check_input_settings(device=self.device, samplerate=rate, channels=1, dtype=self.dtype)
                print(f"[AudioRecorder] Using sample rate: {rate} Hz")
                return rate
            except Exception:
                try:
                    # Try with 2 channels if 1 doesn't work
                    sd.check_input_settings(device=self.device, samplerate=rate, channels=2, dtype=self.dtype)
                    print(f"[AudioRecorder] Using sample rate: {rate} Hz with 2 channels")
                    self.channels = 2  # Update channels to 2
                    return rate
                except Exception:
                    continue
        
        # Fallback to 44100 if nothing else works (most universally supported)
        print(f"[AudioRecorder] Warning: Using fallback sample rate 44100 Hz with 1 channel")
        return 44100
    
    def record(self, output_file="audio.wav", use_vad=None):
        """
        Record audio from the default microphone and save to WAV file.
        With VAD enabled, records until silence is detected.
        
        Args:
            output_file (str): Path to save the recorded audio file
            use_vad (bool): Override config setting for VAD (None to use config)
            
        Returns:
            str: Path to the saved audio file
            
        Raises:
            Exception: If recording fails
        """
        if use_vad is None:
            use_vad = self.vad_enabled
        
        try:
            print(f"[AudioRecorder] Recording... Speak now!")
            
            if use_vad and self.vad:
                # Use VAD for dynamic recording
                audio_data = self._record_with_vad()
            else:
                # Use fixed duration recording with dynamic channel support
                original_channels = self.channels
                try:
                    audio_data = sd.rec(
                        frames=int(self.duration * self.sample_rate),
                        samplerate=self.sample_rate,
                        channels=self.channels,  # Use dynamically determined channels
                        dtype=self.dtype,
                        device=self.device  # Use specified device
                    )
                    sd.wait()  # Wait for fixed duration
                except Exception as e:
                    # If it fails with current channels, try with 1 channel
                    print(f"[AudioRecorder] Retrying with 1 channel due to: {e}")
                    audio_data = sd.rec(
                        frames=int(self.duration * self.sample_rate),
                        samplerate=self.sample_rate,
                        channels=1,  # Fallback to 1 channel
                        dtype=self.dtype,
                        device=self.device  # Use specified device
                    )
                    sd.wait()  # Wait for fixed duration
                    self.channels = 1  # Update to 1 channel for consistency
                    
                    # Also update the WAV file sample to use correct channels
                    if audio_data.shape[1] != self.channels:
                        if self.channels == 1:
                            audio_data = audio_data[:, 0:1]  # Take first channel only
                        else:
                            # Expand to match expected channels
                            audio_data = np.tile(audio_data, (1, self.channels))[:audio_data.shape[0], :self.channels]
            
            print("[AudioRecorder] Recording complete.")
            
            # Save as WAV file using scipy
            write(output_file, self.sample_rate, audio_data)
            print(f"[AudioRecorder] Audio saved to {output_file}")
            
            return output_file
            
        except Exception as e:
            print(f"[AudioRecorder] ERROR: Failed to record audio: {e}")
            raise
    
    def _record_with_vad(self):
        """
        Record audio using Voice Activity Detection (VAD).
        Continues recording until silence is detected for VAD_SILENCE_DURATION seconds.
        """
        import time
        import threading
        import queue
        
        # Calculate frame size for VAD
        frame_duration_ms = self.vad_frame_duration
        frame_size = int(self.sample_rate * frame_duration_ms / 1000)
        
        # Audio buffer
        audio_buffer = []
        silence_frames = 0
        max_silence_frames = int(self.vad_silence_duration / (frame_duration_ms / 1000))
        max_frames = int(self.vad_max_recording_time / (frame_duration_ms / 1000))
        
        # Queue for audio data
        audio_queue = queue.Queue()
        
        def audio_callback(indata, frames, time, status):
            # Convert to bytes for VAD - use first channel if multi-channel
            if indata.shape[1] > 1:  # Multi-channel input
                audio_data = indata[:, 0]  # Use first channel (left)
            else:
                audio_data = indata[:, 0]  # Single channel
            audio_bytes = (audio_data * 32767).astype('int16').tobytes()
            audio_queue.put(audio_bytes)
        
        # Start audio stream
        stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=frame_size,
            device=self.device,
            channels=1,  # Use 1 channel for VAD processing
            dtype='int16',
            callback=audio_callback
        )
        
        print(f"[AudioRecorder] VAD recording started (max {self.vad_max_recording_time}s, silence threshold: {self.vad_silence_duration}s)")
        
        start_time = time.time()
        stream.start()
        
        try:
            while True:
                # Check for timeout
                if time.time() - start_time > self.vad_max_recording_time:
                    print(f"[AudioRecorder] Max recording time reached ({self.vad_max_recording_time}s)")
                    break
                
                try:
                    # Get audio frame
                    audio_frame = audio_queue.get(timeout=0.1)
                    
                    # Check for wake word if detector is available
                    if self.wake_word_detector and self.wake_word_detector.enabled:
                        if self.wake_word_detector.detect_wake_word(audio_frame):
                            print(f"[AudioRecorder] Wake word '{self.wake_word_detector.porcupine.keywords[0]}' detected during recording!")
                            print("[AudioRecorder] Recording interrupted by wake word")
                            # Return immediately with the audio recorded so far
                            break
                    
                    # Check for voice activity
                    is_speech = self.vad.is_speech(audio_frame, self.sample_rate)
                    
                    if is_speech:
                        # Add frame to buffer and reset silence counter
                        audio_buffer.append(audio_frame)
                        silence_frames = 0
                    else:
                        # Add frame to buffer but increment silence counter
                        audio_buffer.append(audio_frame)
                        silence_frames += 1
                        
                        # Stop if enough silence frames detected
                        if silence_frames >= max_silence_frames:
                            print(f"[AudioRecorder] Silence detected, stopping recording after {silence_frames * frame_duration_ms / 1000:.1f}s of silence")
                            break
                except queue.Empty:
                    continue
        finally:
            stream.stop()
            stream.close()
        
        # Convert audio buffer to numpy array
        if audio_buffer:
            # Combine all audio frames
            combined_audio = b''.join(audio_buffer)
            # Convert bytes back to numpy array
            audio_array = np.frombuffer(combined_audio, dtype=np.int16)
            # Reshape to match expected format (samples, channels)
            if self.channels == 1:
                audio_array = audio_array.reshape(-1, 1)
            else:
                # For multi-channel, reshape appropriately
                audio_array = audio_array.reshape(-1, self.channels)
            return audio_array
        else:
            # Return empty array if no audio was recorded
            return np.zeros((1, self.channels), dtype=np.int16)
            
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
