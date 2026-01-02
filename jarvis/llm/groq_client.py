"""
Groq Language Model Client for JARVIS

This module handles natural language processing using Groq's LLM API.

CORRECT GROQ SDK USAGE:
- Initialize client with: client = Groq(api_key=...)
- Model name is passed INSIDE the chat.completions.create() call, NOT during init
- This is different from some other LLM APIs where model is set at client level

The Groq SDK provides a clean interface to state-of-the-art language models
with fast inference speeds, perfect for real-time voice assistant responses.
"""

from groq import Groq
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent.parent))
from jarvis.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_TEMPERATURE,
    GROQ_MAX_TOKENS,
    SYSTEM_PROMPT
)


class GroqClient:
    """
    Handles natural language understanding and response generation using Groq LLM.
    
    Attributes:
        client (Groq): Groq API client instance
        model (str): Model name to use for completions
        temperature (float): Sampling temperature for response generation
        max_tokens (int): Maximum tokens in response
        system_prompt (str): System instruction defining JARVIS personality
    """
    
    def __init__(self):
        """
        Initialize Groq client with configuration from config.py.
        
        IMPORTANT: The Groq() constructor takes the API key, but NOT the model.
        The model is specified later in the chat.completions.create() call.
        """
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            raise ValueError("Groq API key not configured. Please update config.py")
        
        # Initialize Groq client with API key only
        # Model is NOT passed here - it's passed in the generate() method
        self.client = Groq(api_key=GROQ_API_KEY)
        
        # Store configuration
        self.model = GROQ_MODEL
        self.temperature = GROQ_TEMPERATURE
        self.max_tokens = GROQ_MAX_TOKENS
        self.system_prompt = SYSTEM_PROMPT
        
        print(f"[Groq] Initialized with model: {self.model}")
    
    def generate_response(self, user_input):
        """
        Generate a response to user input using Groq LLM.
        
        Args:
            user_input (str): The user's transcribed speech text
            
        Returns:
            str: JARVIS's response text
            
        Raises:
            Exception: If response generation fails
        """
        try:
            print(f"[Groq] Generating response for: '{user_input}'")
            
            # Prepare messages for chat completion
            # Messages format: list of dicts with 'role' and 'content'
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
            
            # Call Groq API with model specified HERE, not in __init__
            # This is the correct way to use the Groq SDK
            chat_completion = self.client.chat.completions.create(
                model=self.model,  # Model name goes HERE in the request
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1,
                stream=False
            )
            
            # Extract response from completion
            response = chat_completion.choices[0].message.content
            
            if not response or response.strip() == "":
                print("[Groq] WARNING: Empty response received")
                return "I apologize, but I couldn't generate a response."
            
            print(f"[Groq] Response generated successfully")
            return response.strip()
            
        except Exception as e:
            print(f"[Groq] ERROR: Failed to generate response: {e}")
            raise
    
    def generate_response_with_messages(self, messages):
        """
        Generate a response using a list of messages (for conversation history).
        
        Args:
            messages (list): List of message dicts with 'role' and 'content'
            
        Returns:
            str: JARVIS's response text
            
        Raises:
            Exception: If response generation fails
        """
        try:
            print(f"[Groq] Generating response with {len(messages)} messages")
            
            # Call Groq API with the provided messages
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1,
                stream=False
            )
            
            # Extract response from completion
            response = chat_completion.choices[0].message.content
            
            if not response or response.strip() == "":
                print("[Groq] WARNING: Empty response received")
                return "I apologize, but I couldn't generate a response."
            
            print(f"[Groq] Response generated successfully")
            return response.strip()
            
        except Exception as e:
            print(f"[Groq] ERROR: Failed to generate response: {e}")
            raise


# Test function for standalone testing
if __name__ == "__main__":
    client = GroqClient()
    
    print("\n=== Testing Groq LLM ===")
    
    # Test with sample inputs
    test_inputs = [
        "Hello, who are you?",
        "What is the capital of France?",
        "Explain quantum computing in simple terms."
    ]
    
    for test_input in test_inputs:
        try:
            print(f"\nUser: {test_input}")
            response = client.generate_response(test_input)
            print(f"JARVIS: {response}")
            print("✓ Test successful")
        except Exception as e:
            print(f"✗ Test failed: {e}")
            break
