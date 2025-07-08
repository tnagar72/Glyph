# Installation Guide

## Quick Install

```bash
git clone https://github.com/tnagar72/Glyph.git
cd Glyph
python -m venv glyph_env
source glyph_env/bin/activate  # On Windows: glyph_env\Scripts\activate
pip install -r requirements.txt
```

Test it works:
```bash
python main.py --test-transcription
```

## Requirements

- **Python 3.8+** (3.9+ recommended)
- **2GB+ RAM** (4GB+ for large Whisper models)
- **Microphone**
- **OpenAI API key** (optional, for faster transcription)

## Platform Notes

### macOS
Works out of the box. If you get permission errors for microphone access, go to System Preferences → Security & Privacy → Privacy → Microphone and enable Terminal/iTerm.

### Linux
Install additional audio dependencies:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
# or on Fedora/RHEL:
sudo dnf install portaudio-devel
```

### Windows
Install Microsoft C++ Build Tools if you get compiler errors:
```bash
# Alternative: use conda instead of pip
conda install pytorch torchaudio -c pytorch
pip install -r requirements.txt
```

## Initial Setup

### 1. Audio Configuration
```bash
python main.py --setup-audio
```
This will detect your microphones and let you choose the best one.

### 2. Choose Transcription Method
```bash
python main.py --setup-transcription
```

**Local Whisper** (recommended):
- Free and private
- Works offline
- Slower but no API costs

**OpenAI API**:
- Faster and more accurate
- Requires API key: `export OPENAI_API_KEY=your_key_here`
- $0.006 per minute

### 3. Model Selection (if using local)
```bash
python main.py --setup-model
```

For most users: **medium** model (769MB, good balance)
For testing: **tiny** model (39MB, fastest)
For best accuracy: **large** model (1550MB, slow)

### 4. Agent Setup (optional)
```bash
python main.py --setup-agent
```
Point it at your Obsidian vault folder for full conversational AI features.

## Basic Usage

### Direct File Editing
```bash
# Edit a specific file
python main.py --file notes.md

# Preview changes first (recommended)
python main.py --file notes.md --dry-run
```

### Agent Mode (Conversational AI)
```bash
# Launch agent
python main.py --agent-mode

# Text-only mode for testing
python main.py --agent-mode --text-only
```

### Live Transcription
```bash
# Stream to terminal
python main.py --live

# Copy to clipboard
python main.py --live --clipboard
```

## Troubleshooting

### Audio Issues
```bash
# Check available devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Reconfigure audio
python main.py --setup-audio
```

### Import Errors
```bash
# Make sure virtual environment is active
source glyph_env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Transcription Problems
```bash
# Test transcription methods
python main.py --test-transcription

# Try different model
python main.py --setup-model
```

### Terminal Conflicts (iTerm users)
```bash
# Use enter-to-stop instead of spacebar
python main.py --agent-mode --enter-stop
```

## Configuration Files

Glyph stores settings in `~/.glyph/`:
- `audio_config.json` - Audio device preferences
- `model_config.json` - Whisper model selection
- `transcription_config.json` - Transcription method
- `agent_config.json` - Agent and vault settings

## Optional: System-wide Installation

```bash
# Install as package
pip install -e .

# Now available as commands
glyph --agent-mode
glyph-test
glyph-cleanup
```

## Getting Help

```bash
# View all options
python main.py --help

# Show current configuration
python main.py --show-config

# Run tests to verify installation
python run_tests_simple.py
```

## Next Steps

1. Try direct editing mode first: `python main.py --file notes.md --dry-run`
2. Set up agent mode for conversational AI: `python main.py --setup-agent`
3. Read [FUNCTIONALITY.md](FUNCTIONALITY.md) for complete feature documentation
4. Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for development setup

The installation is complete when you can successfully run voice commands and see diff outputs or agent responses.