"""
Configuration module for JARVIS Voice Assistant

This module manages API keys and configuration settings.
Currently uses hard-coded values for simplicity.

TODO: In production, migrate to environment variables using python-dotenv:
    from dotenv import load_dotenv
    load_dotenv()
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
"""

# API Keys - Replace these with your actual keys
DEEPGRAM_API_KEY = "988be47d91aca476e11aad90ed37e5abf4d34eb9"
GROQ_API_KEY = "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"

# Audio Configuration
AUDIO_SAMPLE_RATE = 16000  # Hz (preferred, will auto-detect if not supported)
AUDIO_CHANNELS = 1  # Mono (changed from default to ensure compatibility)
AUDIO_DTYPE = 'int16'  # 16-bit
AUDIO_DURATION = 5  # seconds - max duration of each recording
AUDIO_DEVICE = None  # USB microphone device index (None for default)

# Voice Activity Detection (VAD)
VAD_ENABLED = True  # Enable VAD for dynamic recording
VAD_AGGRESSIVENESS = 3  # 0-3, higher = more aggressive filtering (3 recommended)
VAD_FRAME_DURATION = 30  # ms per frame (10, 20, or 30)
VAD_SILENCE_DURATION = 1.5  # seconds of silence before stopping recording
VAD_MAX_RECORDING_TIME = 30  # seconds - maximum recording duration

# Deepgram Configuration
DEEPGRAM_API_URL = "https://api.deepgram.com/v1/listen"
DEEPGRAM_MODEL = "nova-2"  # Latest general model
DEEPGRAM_LANGUAGE = "en-US"

# Groq Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.7
GROQ_MAX_TOKENS = 1024

# Wake Word Detection
WAKE_WORD_ENABLED = True  # Enable wake word detection
WAKE_WORD_PORCUPINE_ACCESS_KEY = "YOUR_PORCUPINE_ACCESS_KEY"  # Get from Picovoice Console
WAKE_WORD_KEYWORD = "jarvis"  # Wake word to listen for
WAKE_WORD_SENSITIVITY = 0.5  # 0.0-1.0, higher = more sensitive

# System Prompt for JARVIS
SYSTEM_PROMPT = "You are JARVIS, an intelligent, polite college assistant robot. Answer clearly and concisely."

# File paths
AUDIO_OUTPUT_FILE = "audio.wav"
