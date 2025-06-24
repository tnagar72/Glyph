# 🎙️ Voice-Controlled Markdown Editor

> Transform your voice into intelligent markdown edits using local Whisper transcription and GPT-4 processing.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ **Key Features**

- 🎤 **Voice-to-Text**: Local Whisper transcription with multiple model options
- 🧠 **AI-Powered Editing**: GPT-4 integration for intelligent markdown modifications  
- 🖥️ **Rich Terminal UI**: Beautiful interface with progress indicators and colored diffs
- 📝 **Safe Editing**: Automatic backups and change previews before applying
- 🔄 **Multiple Modes**: Interactive CLI, live transcription, and command-line interfaces
- 🎯 **Obsidian Ready**: Preserves links, tags, and frontmatter formatting
- ⚡ **Two Recording Methods**: Spacebar press-to-talk or Enter-to-stop (prevents terminal interference)

## 🚀 **Quick Start**

### Prerequisites
- Python 3.8+
- OpenAI API key
- Microphone access

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/voice-markdown-editor.git
cd voice-markdown-editor
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up OpenAI API:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Test your setup:**
```bash
python main.py --transcript-only
```

## 📖 **Usage**

### Basic Voice Editing
```bash
# Edit a specific file
python main.py --file notes.md

# Use Enter-to-stop recording (recommended for iTerm)
python main.py --file notes.md --enter-stop

# Preview changes without applying
python main.py --file notes.md --dry-run
```

### Interactive Mode
```bash
# Launch rich menu interface
python main.py --interactive
```
Features file browsing, model selection, and integrated options management.

### Live Transcription
```bash
# Real-time voice-to-text streaming
python main.py --live

# Simple output for piping
python main.py --live | tee transcript.log
```

### Advanced Options
```bash
# Use different Whisper models
python main.py --whisper-model large --file notes.md

# Enable verbose debugging
python main.py --verbose --file notes.md

# Transcript only (no GPT processing)
python main.py --transcript-only

# Undo recent changes
python main.py --undo notes.md
```

## 🎯 **Voice Command Examples**

### Task Management
- *"Mark task 2 as complete"*
- *"Add a new task about grocery shopping"*
- *"Move the bike repair task under Personal section"*

### Content Editing
- *"Change the heading from TODO to DONE"*
- *"Add a bullet point about meeting preparation"*
- *"Remove the completed tasks section"*

### Structure Modifications
- *"Create a new section called Ideas"*
- *"Move all incomplete tasks to the top"*
- *"Reorder the sections alphabetically"*

## ⚙️ **Configuration**

### Whisper Models
| Model | Size | Speed | Accuracy | Use Case |
|-------|------|--------|----------|----------|
| tiny | 39MB | Fastest | Basic | Quick testing |
| base | 74MB | Fast | Good | Simple commands |
| small | 244MB | Medium | Better | Balanced use |
| **medium** | 769MB | Slow | High | **Default** |
| large | 1550MB | Slowest | Highest | Complex commands |

### Audio Device Setup
The system is configured for MacBook Pro Microphone (device index 2). To change:
1. List available devices: `python -c "import sounddevice as sd; print(sd.query_devices())"`
2. Update `DEVICE_INDEX` in `utils.py`

### Environment Variables
```bash
# Optional environment variables
export WHISPER_MODEL=large        # Override default model
export VERBOSE=1                  # Enable verbose output
export OPENAI_API_KEY=your_key    # OpenAI API key
```

## 🛠️ **Advanced Features**

### Developer Tools
- **Interactive CLI**: Rich menu system with file browsing and model selection
- **Live Transcription**: Real-time streaming for testing and integration
- **Session Logging**: Comprehensive audit trails with JSON and text formats
- **Undo Management**: Automatic backup discovery and restoration

### Integration Ready
- **Piping Support**: `python main.py --live | your_processor.py`
- **Batch Processing**: Loop through multiple files with interactive mode
- **Remote Usage**: SSH-compatible for remote voice control

## 🔧 **Troubleshooting**

### Common Issues

**Audio capture failed:**
- Check microphone permissions in System Preferences
- Verify correct audio device index in `utils.py`
- Test with: `python -c "import sounddevice as sd; sd.rec(1000, samplerate=44100)"`

**OpenAI API errors:**
- Verify API key in `.env` file
- Check API usage limits and billing
- Test with: `python -c "import openai; print(openai.api_key)"`

**Terminal interference (iTerm):**
- Use `--enter-stop` flag instead of spacebar recording
- Update iTerm preferences to disable bell sounds

**Transcription accuracy:**
- Use larger Whisper models (`--whisper-model large`)
- Ensure quiet environment and clear speech
- Check microphone positioning and levels

## 📁 **Project Structure**

```
voice-markdown-editor/
├── main.py                 # Main entry point
├── recording.py            # Audio capture system
├── transcription.py        # Whisper integration
├── llm.py                 # GPT-4 API integration
├── interactive_cli.py     # Rich menu interface
├── live_transcription.py  # Real-time streaming
├── diff.py                # Change visualization
├── session_logger.py      # Audit logging
├── undo_manager.py        # Backup management
├── prompts/               # GPT-4 prompt templates
├── docs/                  # Extended documentation
└── examples/              # Sample markdown files
```

## 🎥 **Examples & Demos**

> **📝 TODO for Repository Owner:**
> - [ ] Add demo video showing voice editing workflow
> - [ ] Create screenshots of Rich terminal UI
> - [ ] Record voice command examples
> - [ ] Show before/after markdown comparisons

## 🤝 **Contributing**

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://github.com/your-username/voice-markdown-editor.git
cd voice-markdown-editor
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
```

### Running Tests
```bash
# Test audio system
python main.py --transcript-only --verbose

# Test interactive mode
python main.py --interactive

# Test live transcription
python main.py --live
```

## 📚 **Documentation**

- [**FUNCTIONALITY.md**](FUNCTIONALITY.md) - Complete feature documentation
- [**DEVELOPER_TOOLS.md**](DEVELOPER_TOOLS.md) - Interactive and live modes guide
- [**WHISPER_MODELS.md**](WHISPER_MODELS.md) - Model selection guide
- [**CONTRIBUTING.md**](CONTRIBUTING.md) - Development guidelines

## 🚀 **Future Roadmap**

### Planned Features
- macOS menu bar integration
- Obsidian plugin development
- VS Code extension
- Web interface
- Mobile app support

### Integration Possibilities
- GitHub Actions for automated testing
- PyPI package distribution
- Docker containerization
- Cloud deployment options

## 📋 **TODO List for Repository Enhancement**

### **High Priority** (User Action Required)
- [ ] **Record demo video** showing complete workflow
- [ ] **Create screenshots** of Rich UI, interactive menus, and diffs
- [ ] **Set up OpenAI API key** and verify all functionality
- [ ] **Test on different systems** (various macOS versions, microphones)
- [ ] **Create sample markdown files** in examples/ directory

### **Medium Priority**
- [ ] **Record voice command examples** for different use cases
- [ ] **Create Obsidian vault integration** examples
- [ ] **Write blog post** about voice-driven productivity workflows
- [ ] **Set up GitHub repository** with proper name and description
- [ ] **Add repository topics/tags** for discoverability

### **Low Priority**
- [ ] **GitHub Actions setup** for automated testing
- [ ] **PyPI package preparation** for pip installation
- [ ] **Documentation website** with GitHub Pages
- [ ] **Community features** (Discord server, GitHub Discussions)
- [ ] **Performance benchmarking** across different Whisper models

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- [OpenAI Whisper](https://github.com/openai/whisper) for local speech recognition
- [Rich](https://github.com/Textualize/rich) for beautiful terminal interfaces
- [OpenAI GPT-4](https://openai.com/) for intelligent text processing

---

**Made with ❤️ for voice-driven productivity**

*Transform your voice into intelligent markdown edits - because typing is so 2023!*