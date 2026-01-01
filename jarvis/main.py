#!/usr/bin/env python3
"""
JARVIS Voice Assistant - Main Application

This is the main entry point for JARVIS voice assistant system.
It orchestrates all components in a continuous loop:
1. Record audio from microphone
2. Transcribe speech to text using Deepgram
3. Generate response using Groq LLM
4. Output response (currently text, will support TTS later)

The system runs continuously until interrupted by the user (Ctrl+C).

SYSTEM REQUIREMENTS:
- Python 3.13
- Virtual environment (venv)
- Raspberry Pi OS 32-bit
- USB microphone
- Internet connection for API calls

SETUP INSTRUCTIONS:
1. Install dependencies: pip install -r requirements.txt
2. Update API keys in jarvis/config.py
3. Run: python jarvis/main.py
"""

import sys
import time
from pathlib import Path
import threading
import queue

# Add current directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from jarvis.config import AUDIO_OUTPUT_FILE
from jarvis.audio.recorder import AudioRecorder
from jarvis.stt.deepgram_client import DeepgramClient
from jarvis.llm.groq_client import GroqClient
from jarvis.tts.placeholder import TTSClient


class JarvisAssistant:
    """
    Main JARVIS voice assistant coordinator.
    
    Integrates all components (audio, STT, LLM, TTS) and manages
    the main conversation loop.
    """
    
    def __init__(self):
        """Initialize all JARVIS components"""
        print("=" * 60)
        print("JARVIS Voice Assistant - Initializing...")
        print("=" * 60)
        
        try:
            # Initialize all components
            self.recorder = AudioRecorder()
            self.stt_client = DeepgramClient()
            self.llm_client = GroqClient()
            self.tts_client = TTSClient()
            
            print("\n✓ All components initialized successfully")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Initialization failed: {e}")
            print("\nPlease check:")
            print("1. API keys are configured in jarvis/config.py")
            print("2. Microphone is connected and working")
            print("3. Internet connection is active")
            sys.exit(1)
    
    def run_once(self):
        """
        Execute one complete interaction cycle.
        
        Returns:
            bool: True if cycle completed successfully, False otherwise
        """
        try:
            # Step 1: Record audio from microphone
            print("\n" + "─" * 60)
            audio_file = self.recorder.record(AUDIO_OUTPUT_FILE, use_vad=True)
            
            # Step 2: Transcribe speech to text
            print("─" * 60)
            transcript = self.stt_client.transcribe(audio_file)
            
            # Check if we got any speech
            if not transcript or transcript.strip() == "":
                print("[JARVIS] No speech detected. Please try again.")
                return False
            
            print(f"\n[YOU SAID]: {transcript}")
            
            # Step 3: Generate LLM response
            print("─" * 60)
            response = self.llm_client.generate_response(transcript)
            
            # Step 4: Output response (currently text only)
            print("─" * 60)
            # Use simple callback that returns None for now (no interruption during TTS)
            self.tts_client.speak_with_interruption(response, audio_callback=lambda: None)
            
            return True
            
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by main loop
        except Exception as e:
            print(f"\n[JARVIS] Error during interaction: {e}")
            print("[JARVIS] Continuing to next cycle...")
            return False
    
    def run(self):
        """
        Run JARVIS in continuous loop mode.
        
        Continues listening and responding until user interrupts (Ctrl+C).
        """
        print("\n" + "=" * 60)
        print("JARVIS is now active and listening...")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        interaction_count = 0
        
        try:
            while True:
                interaction_count += 1
                print(f"\n[Interaction #{interaction_count}]")
                
                self.run_once()
                
                # Small delay between interactions
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("JARVIS shutting down...")
            print(f"Total interactions: {interaction_count}")
            print("Goodbye!")
            print("=" * 60)


def main():
    """Main entry point for JARVIS application"""
    try:
        # Create and run JARVIS
        jarvis = JarvisAssistant()
        jarvis.run()
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
