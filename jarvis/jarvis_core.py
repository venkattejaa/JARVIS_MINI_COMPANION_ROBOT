#!/usr/bin/env python3
"""
JARVIS Voice Assistant - Core System

This implements the core JARVIS functionality with continuous wake word detection,
voice activity detection, and interruptible responses as per the reference implementation.
"""

import os
import sys
import time
import json
import queue
import threading
import sqlite3
import re
import random
from pathlib import Path

# Add current directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from jarvis.config import AUDIO_OUTPUT_FILE
from jarvis.audio.recorder import AudioRecorder
from jarvis.stt.deepgram_client import DeepgramClient
from jarvis.llm.groq_client import GroqClient
from jarvis.tts.placeholder import TTSClient


class JARVISCore:
    """
    Core JARVIS system implementing continuous wake word detection,
    voice activity detection, and interruptible responses.
    """
    
    def __init__(self):
        """Initialize JARVIS core components"""
        print("=" * 60)
        print("JARVIS Core System - Initializing...")
        print("=" * 60)
        
        try:
            # Initialize all components
            self.recorder = AudioRecorder()
            self.stt_client = DeepgramClient()
            self.llm_client = GroqClient()
            self.tts_client = TTSClient()
            
            # State management
            self.is_listening_for_wake_word = True
            self.is_interacting = False
            self.should_stop = False
            self.interaction_queue = queue.Queue()
            self.is_speaking = False
            self.self_trigger_disabled_until = 0.0
            
            # Initialize database for conversation history
            self.init_db()
            
            print("\n✓ JARVIS Core components initialized successfully")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ JARVIS Core initialization failed: {e}")
            print("\nPlease check:")
            print("1. API keys are configured in jarvis/config.py")
            print("2. Microphone is connected and working")
            print("3. Internet connection is active")
            sys.exit(1)
    
    def init_db(self):
        """Initialize SQLite database for conversation history"""
        try:
            conn = sqlite3.connect("jarvis_mem.db")
            conn.execute("CREATE TABLE IF NOT EXISTS history (role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DB] Warning: Could not initialize database: {e}")
    
    def save_history(self, role, content):
        """Save conversation history to database"""
        try:
            conn = sqlite3.connect("jarvis_mem.db")
            conn.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))
            conn.commit()
            conn.close()
        except Exception:
            pass  # Don't let DB errors break the system
    
    def get_history(self, limit=6):
        """Get recent conversation history"""
        try:
            conn = sqlite3.connect("jarvis_mem.db")
            rows = conn.execute("SELECT role, content FROM history ORDER BY rowid DESC LIMIT ?", (limit,)).fetchall()
            conn.close()
            out = []
            for r in reversed(rows):
                out.append({"role": r[0], "content": r[1]})
            return out
        except Exception:
            return []
    
    def sanitize_for_speech(self, text: str) -> str:
        """Clean text for speech output"""
        if not isinstance(text, str):
            text = str(text)
        
        # Remove AI identity statements
        forbidden = [
            r"\bas an ai\b", r"\bas an ai model\b", r"\bi am a language model\b",
            r"\bi'?m a language model\b", r"\bi am a text-based ai\b", r"\bi'?m a text-based ai\b",
        ]
        s = text
        for pat in forbidden:
            s = re.sub(pat, "", s, flags=re.I)
        
        # Remove code blocks
        s = re.sub(r"```[\s\S]*?```", "", s, flags=re.DOTALL)
        s = re.sub(r"`[^`]*`", "", s)
        s = re.sub(r"\s{2,}", " ", s).strip()
        
        # Replace jarvis with vocal name
        s = re.sub(r"\bjarvis\b", "jarvis", s, flags=re.I)
        
        # Check if content is substantial
        if len(re.sub(r"[^a-zA-Z0-9]", "", s)) < 2:
            return ""
        
        return s
    
    def get_ai_response(self, prompt):
        """Get response from AI using conversation history"""
        sys_prompt = (
            "You are JARVIS (Just A Rather Very Intelligent System) pronounced as jarvis.\n"
            "Created by the user. Persona: concise, witty, and always in-character. "
            "Address the user as 'Sir'. Do not identify as a language model, or mention limitations.\n"
            "Just speak a little, Even if you are explaining or anything just speak few words, "
            "never break this rule, unless you are teaching or something else but don't speak a lot"
        )
        
        try:
            messages = [{"role":"system","content":sys_prompt}]
            messages.extend(self.get_history(limit=6))
            messages.append({"role":"user","content":prompt})
            
            response = self.llm_client.generate_response_with_messages(messages)
            return response
        except Exception as e:
            print(f"[AI] Error getting response: {e}")
            return "Neural Core error. I cannot fetch that right now, Sir."
    
    def generate_response(self, user_input):
        """Generate response to user input"""
        try:
            response = self.get_ai_response(user_input)
            self.save_history("user", user_input)
            self.save_history("assistant", response)
            return response
        except Exception as e:
            print(f"[JARVIS] Error generating response: {e}")
            return "I'm having trouble processing that request, Sir."
    
    def run_interaction_cycle(self):
        """
        Execute one complete interaction cycle.
        
        Returns:
            bool: True if cycle completed successfully, False otherwise
        """
        try:
            # Step 1: Record user's request
            print("\n" + "─" * 60)
            print("[JARVIS] I'm listening, Sir. Please speak your request...")
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
            response = self.generate_response(transcript)
            
            # Step 4: Output response with interruptible TTS
            print("─" * 60)
            
            # Mark that we're now speaking
            self.is_speaking = True
            self.self_trigger_disabled_until = time.time() + 0.5  # Suppress wake word briefly after TTS
            
            # Use interruptible TTS
            def audio_callback():
                # This would provide audio frames for wake word detection during TTS
                # For now, return None since we don't have continuous audio input during TTS
                return None
            
            success = self.tts_client.speak_with_interruption(response, audio_callback=audio_callback)
            
            # Mark that we're no longer speaking
            self.is_speaking = False
            
            if success:
                print("\n[JARVIS] Response delivered successfully")
            else:
                print("\n[JARVIS] Response interrupted by wake word")
            
            return True
            
        except Exception as e:
            print(f"\n[JARVIS] Error during interaction: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def listen_for_wake_word(self):
        """
        Listen continuously for the wake word in a separate thread.
        This simulates the continuous wake word detection.
        """
        print("\n[JARVIS] Entering wake word listening mode...")
        print("Say 'jarvis' to activate the system.")
        
        while not self.should_stop:
            try:
                # Record a short segment to check for wake word
                # In a real implementation, this would use the wake word detector directly
                audio_file = self.recorder.record("temp_wake_check.wav", use_vad=True)
                
                # For now, we'll just continue the loop
                # In the future, we'd detect the wake word and trigger interaction
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                print(f"[WakeWord] Error: {e}")
                time.sleep(1)  # Wait before retrying
    
    def run(self):
        """
        Run JARVIS in continuous mode.
        
        Continues in listening mode until wake word is detected,
        then enters interaction mode, then returns to listening.
        """
        print("\n" + "=" * 60)
        print("JARVIS Core is now active and listening...")
        print("Say 'jarvis' to activate, or press Ctrl+C to stop")
        print("=" * 60)
        
        interaction_count = 0
        
        try:
            # Start wake word detection in background thread
            wake_word_thread = threading.Thread(target=self.listen_for_wake_word, daemon=True)
            wake_word_thread.start()
            
            while not self.should_stop:
                print(f"\n[Interaction #{interaction_count + 1}]")
                print("Ready for wake word detection...")
                
                # Simulate wake word detection (in real implementation, this would be continuous)
                # For now, we'll just run one interaction cycle
                print("─" * 60)
                print("JARVIS activated! Please speak your request...")
                
                # Enter interaction mode
                success = self.run_interaction_cycle()
                
                if success:
                    interaction_count += 1
                    print(f"\n[JARVIS] Interaction #{interaction_count} completed")
                else:
                    print("\n[JARVIS] Interaction failed")
                
                # Small delay before returning to wake word listening
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("JARVIS shutting down...")
            print(f"Total interactions: {interaction_count}")
            print("Goodbye!")
            print("=" * 60)
            self.should_stop = True


def main():
    """Main entry point for JARVIS Core application"""
    try:
        # Create and run JARVIS Core
        jarvis = JARVISCore()
        jarvis.run()
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()