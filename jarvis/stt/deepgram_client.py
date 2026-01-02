"""
Deepgram Speech-to-Text Client for JARVIS

This module handles speech-to-text conversion using Deepgram's REST API.

WHY REST API INSTEAD OF SDK:
- Direct control over HTTP requests for better debugging and transparency
- No dependency on SDK version compatibility issues
- Simpler for educational purposes and custom error handling
- Works reliably across different Python versions and platforms
- Easier to adapt if API changes or custom headers are needed

The Deepgram REST API accepts audio files and returns JSON transcription results.
Authentication is done via Authorization header with API token.
"""

import requests
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent.parent))
from jarvis.config import DEEPGRAM_API_KEY, DEEPGRAM_API_URL, DEEPGRAM_MODEL, DEEPGRAM_LANGUAGE


class DeepgramClient:
    """
    Handles speech-to-text conversion using Deepgram REST API.
    
    Attributes:
        api_key (str): Deepgram API authentication key
        api_url (str): Deepgram API endpoint URL
        model (str): Deepgram model to use for transcription
        language (str): Language code for transcription
    """
    
    def __init__(self):
        """Initialize Deepgram client with configuration from config.py"""
        self.api_key = DEEPGRAM_API_KEY
        self.api_url = DEEPGRAM_API_URL
        self.model = DEEPGRAM_MODEL
        self.language = DEEPGRAM_LANGUAGE
        
        if not self.api_key or self.api_key == "your_deepgram_api_key_here":
            raise ValueError("Deepgram API key not configured. Please update config.py")
    
    def transcribe(self, audio_file_path):
        """
        Transcribe audio file to text using Deepgram REST API.
        
        Args:
            audio_file_path (str): Path to the audio WAV file
            
        Returns:
            str: Transcribed text from the audio
            
        Raises:
            Exception: If transcription fails
        """
        try:
            print(f"[Deepgram] Transcribing audio file: {audio_file_path}")
            
            # Prepare headers with authentication
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav"
            }
            
            # Prepare query parameters
            params = {
                "model": self.model,
                "language": self.language,
                "punctuate": "true",
                "utterances": "false"
            }
            
            # Read audio file as binary
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            print(f"[Deepgram] Sending {len(audio_data)} bytes to Deepgram API...")
            
            # Make POST request to Deepgram API
            response = requests.post(
                self.api_url,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code != 200:
                raise Exception(
                    f"Deepgram API request failed with status {response.status_code}: "
                    f"{response.text}"
                )
            
            # Parse JSON response
            result = response.json()
            
            # Extract transcript from response
            # Response structure: results.channels[0].alternatives[0].transcript
            transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
            
            if not transcript or transcript.strip() == "":
                print("[Deepgram] WARNING: Empty transcript received")
                return ""
            
            print(f"[Deepgram] Transcription successful: '{transcript}'")
            return transcript.strip()
            
        except FileNotFoundError:
            print(f"[Deepgram] ERROR: Audio file not found: {audio_file_path}")
            raise
        except KeyError as e:
            print(f"[Deepgram] ERROR: Unexpected API response format: {e}")
            print(f"[Deepgram] Response: {response.text if 'response' in locals() else 'N/A'}")
            raise
        except requests.exceptions.Timeout:
            print("[Deepgram] ERROR: Request timed out")
            raise
        except requests.exceptions.RequestException as e:
            print(f"[Deepgram] ERROR: Network error: {e}")
            raise
        except Exception as e:
            print(f"[Deepgram] ERROR: Transcription failed: {e}")
            raise


# Test function for standalone testing
if __name__ == "__main__":
    # Test with a sample audio file
    client = DeepgramClient()
    
    print("\n=== Testing Deepgram STT ===")
    print("Note: This test requires a valid audio.wav file and API key")
    
    try:
        # Test transcription (assumes audio.wav exists)
        transcript = client.transcribe("audio.wav")
        print(f"✓ Transcription test successful")
        print(f"  Transcript: {transcript}")
    except Exception as e:
        print(f"✗ Transcription test failed: {e}")
