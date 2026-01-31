"""
Test script for LAXMANA AI
Demonstrates the basic functionality of the LAXMANA AI system
"""

from laxmana_core import LaxmanaAI

def test_laxmana():
    """
    Test function to demonstrate LAXMANA AI capabilities
    """
    print("Initializing LAXMANA AI...")
    laxmana = LaxmanaAI()
    
    print(f"LAXMANA AI v{laxmana.version} ready!")
    
    # Test various inputs
    test_inputs = [
        "Hello LAXMANA!",
        "What is your name?",
        "Explain quantum computing in simple terms",
        "How are you different from other AIs?",
        "Tell me about machine learning"
    ]
    
    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        response = laxmana.process_input(user_input)
        print(f"Response: {response}")
    
    # Get system info
    info = laxmana.get_system_info()
    print(f"\nSystem Info: {info}")

if __name__ == "__main__":
    test_laxmana()