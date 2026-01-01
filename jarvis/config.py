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
AUDIO_SAMPLE_RATE = 16000  # Hz
AUDIO_CHANNELS = 1  # Mono
AUDIO_DTYPE = 'int16'  # 16-bit
AUDIO_DURATION = 5  # seconds - duration of each recording

# Deepgram Configuration
DEEPGRAM_API_URL = "https://api.deepgram.com/v1/listen"
DEEPGRAM_MODEL = "nova-2"  # Latest general model
DEEPGRAM_LANGUAGE = "en-US"

# Groq Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.7
GROQ_MAX_TOKENS = 1024

# System Prompt for JARVIS
SYSTEM_PROMPT = "You are JARVIS, an intelligent, polite college assistant robot. Answer clearly and concisely."

# File paths
AUDIO_OUTPUT_FILE = "audio.wav"
