# Voice Editor Project

## Overview
Building Glyph - a voice-controlled markdown editor that integrates Whisper transcription with GPT-4 for intelligent editing.

## Features
- [x] Local Whisper transcription
- [x] GPT-4 integration
- [x] Rich terminal UI
- [ ] PyPI distribution
- [ ] Docker support
- [ ] Mobile app

## Architecture

### Core Components
1. **Audio Processing** - Handles microphone input and Whisper transcription
2. **AI Integration** - Manages GPT-4 API calls for intelligent editing
3. **UI Layer** - Rich terminal interface with progress indicators
4. **File Management** - Safe file operations with backup system

### Dependencies
- OpenAI Whisper (local transcription)
- OpenAI API (GPT-4 processing)
- Rich (terminal UI)
- SoundDevice (audio capture)

## Development Notes

### Current Status
Working prototype with all core features implemented. Ready for:
- Documentation polish
- Package distribution setup
- Community features

### Known Issues
- Terminal interference with spacebar recording in iTerm (fixed with enter-to-stop)
- Large Whisper models require significant memory
- GPT-4 API costs for heavy usage

### Future Roadmap
1. **Short Term**
   - PyPI packaging
   - Cross-platform testing
   - Performance optimization

2. **Medium Term**
   - Obsidian plugin integration
   - VS Code extension
   - Web interface

3. **Long Term**
   - Mobile applications
   - Offline AI models
   - Team collaboration features

## Usage Examples

### Basic Commands
```bash
# Standard usage
python main.py --file notes.md

# Enter-to-stop recording
python main.py --file notes.md --enter-stop

# Interactive mode
python main.py --interactive
```

### Advanced Features
```bash
# Live transcription
python main.py --live

# Different models
python main.py --whisper-model large --file complex-doc.md

# Dry run mode
python main.py --file notes.md --dry-run
```

---

*Try saying: "Mark the PyPI distribution task as complete" or "Add a new task about creating demo videos under the Short Term roadmap"*