#!/bin/bash
# JARVIS Installation Script for Raspberry Pi

echo "========================================"
echo "JARVIS Voice Assistant - Installation"
echo "========================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry" /proc/device-tree/model 2>/dev/null && ! grep -q "Raspberry" /sys/firmware/devicetree/base/model 2>/dev/null; then
    echo "⚠️  WARNING: This script is designed for Raspberry Pi"
    echo "   Continuing anyway, but results may vary"
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install system dependencies first
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y libatlas-base-dev libopenblas-dev libportaudio2 portaudio19-dev python3-pyaudio python3-numpy python3-scipy

# Create virtual environment with system site packages
echo "Creating virtual environment with system packages..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing..."
    rm -rf venv
fi

python3 -m venv venv --system-site-packages
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo "✓ pip upgraded"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check if config has API keys
echo "Checking configuration..."
if grep -q "your_deepgram_api_key_here\|988be47d91aca476e11aad90ed37e5abf4d34eb9" jarvis/config.py; then
    echo "⚠️  WARNING: Deepgram API key not configured"
    echo "   Please edit jarvis/config.py and add your Deepgram API key"
fi

if grep -q "your_groq_api_key_here\|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" jarvis/config.py; then
    echo "⚠️  WARNING: Groq API key not configured"
    echo "   Please edit jarvis/config.py and add your Groq API key"
fi

if grep -q "YOUR_PORCUPINE_ACCESS_KEY" jarvis/config.py; then
    echo "⚠️  WARNING: Porcupine access key not configured"
    echo "   Wake word detection will be disabled"
    echo "   Get a free key from: https://console.picovoice.ai/"
fi
echo ""

# Test microphone
echo "Testing microphone availability..."
if command -v arecord &> /dev/null; then
    echo "Available audio input devices:"
    arecord -l
else
    echo "⚠️  arecord command not found. Cannot list audio devices."
    echo "   Make sure ALSA utilities are installed: sudo apt-get install alsa-utils"
fi
echo ""

echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit jarvis/config.py and add your API keys (optional for now)"
echo "2. Run JARVIS: python jarvis/main.py"
echo ""
echo "For testing individual components:"
echo "  - Audio: python jarvis/audio/recorder.py"
echo "  - Wake word: python jarvis/wake_word/detector.py"
echo "  - TTS: python jarvis/tts/placeholder.py"
echo ""
echo "To run with VAD (voice activity detection):"
echo "  python jarvis/main.py"
echo ""
echo "Enjoy your JARVIS voice assistant! 🎤🤖"
echo ""
