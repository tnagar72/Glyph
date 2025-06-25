# Glyph - Complete Functionality

## 🎯 **Core Purpose**
Transform voice commands into intelligent markdown file edits using local Whisper transcription and GPT-4 processing.

---

## 🏗️ **System Architecture**

### **Pipeline Flow**
```
Voice Input → Audio Recording → Whisper Transcription → GPT-4 Processing → Diff Preview → User Approval → File Update
```

### **Module Structure**
```
📦 Glyph
├── 🎤 Audio Layer (recording.py, utils.py)
├── 🤖 Transcription Layer (transcription.py)  
├── 🧠 AI Processing Layer (llm.py, prompts.py)
├── 📝 File Management Layer (md_file.py, cleaning.py)
├── 👀 UI Layer (diff.py, main.py)
└── 📋 Configuration (utils.py, .env)
```

---

## ✨ **Key Features**

### **1. Voice Input System**
- **Press-to-talk interface**: Hold spacebar to record, release to stop (default)
- **Enter-to-stop interface**: Auto-start recording, press ENTER when finished (avoids terminal interference)
- **Real-time feedback**: Animated spinner with elapsed time counter
- **Audio device management**: Configured for MacBook Pro Microphone (device 2)
- **High-quality recording**: 44.1kHz, mono channel audio capture

### **2. Advanced Transcription**
- **Whisper AI models**: Configurable from tiny to large (default: medium)
- **Optimized parameters**: 
  - English language specification
  - Temperature 0.0 for consistency
  - Beam search (beam_size=5)
  - Multiple attempts (best_of=2)
  - FP32 precision for accuracy
- **Model caching**: One-time loading per session
- **Automatic cleanup**: Temporary files properly managed

### **3. Intelligent Markdown Processing**
- **GPT-4 integration**: Smart markdown editing based on voice commands
- **Context-aware**: Understands existing document structure
- **Obsidian compatibility**: Preserves links, tags, frontmatter
- **Safe editing**: Maintains formatting and indentation

### **4. Rich Visual Interface**
- **GitHub-style diffs**: Professional colored diff visualization
- **Syntax highlighting**: Markdown-aware code display
- **Progress indicators**: Animated spinners for long operations
- **Themed UI**: Consistent color scheme throughout
- **Informative panels**: Clean, organized information display

### **5. File Management**
- **Automatic backups**: Timestamped backup creation before edits
- **Path validation**: Smart markdown file detection (.md/.markdown)
- **Safe writing**: Atomic file operations with error handling
- **Transcript logging**: All voice commands saved with timestamps

---

## 🚀 **Usage Modes**

### **Basic Usage**
```bash
python main.py
# Interactive mode: prompts for file path
```

### **Direct File Editing**
```bash
python main.py --file ~/Documents/notes/todo.md
# Direct editing of specified file
```

### **Preview Mode**
```bash
python main.py --file notes.md --dry-run
# Show changes without applying them
```

### **Transcription Only**
```bash
python main.py --transcript-only
# Voice-to-text without GPT processing
```

### **Model Selection**
```bash
python main.py --whisper-model large --file notes.md
# Use specific Whisper model for better accuracy

python main.py --setup-model
# Configure default model for all future commands
```

### **Verbose Debugging**
```bash
python main.py --verbose --file notes.md
# Enable comprehensive debug output
```

### **Enter-to-Stop Recording**
```bash
python main.py --enter-stop --file notes.md
# Use ENTER key to stop recording (prevents terminal interference)
```

### **Undo Changes**
```bash
python main.py --undo notes.md
# Restore file from latest backup
```

### **Interactive Mode**
```bash
python main.py --interactive
# Launch rich menu-driven interface
```

### **Live Transcription**
```bash
python main.py --live
# Real-time voice-to-text streaming

# For piping/debugging
python main.py --live | tee transcript.log

# Copy transcripts to clipboard
python main.py --live --clipboard
```

---

## 🎙️ **Voice Command Examples**

### **Task Management**
- "Mark task 2 as complete"
- "Add a new task about grocery shopping"
- "Move the bike repair task under Personal section"

### **Content Editing**
- "Change the heading from TODO to DONE"
- "Add a bullet point about meeting preparation"
- "Remove the completed tasks section"

### **Structure Modifications**
- "Create a new section called Ideas"
- "Move all incomplete tasks to the top"
- "Reorder the sections alphabetically"

---

## 📊 **Technical Capabilities**

### **Audio Processing**
- **Sample Rate**: 44.1kHz professional quality
- **Real-time capture**: Stream-based recording with callback
- **Device flexibility**: Configurable audio input device
- **Noise handling**: Robust capture in various environments

### **AI Integration**
- **Whisper Models**: 5 accuracy levels (tiny→large)
- **GPT-4 API**: Professional-grade language understanding
- **Error handling**: Graceful fallbacks and recovery
- **Rate limiting**: Respectful API usage

### **File Operations**
- **Backup system**: Automatic versioning before changes
- **Encoding**: UTF-8 with proper line ending normalization
- **Path handling**: Cross-platform file path resolution
- **Safety checks**: Validation before file operations

### **User Experience**
- **Zero configuration**: Works out of box
- **Rich terminal UI**: Professional appearance
- **Progress feedback**: Clear operation status
- **Error messages**: Helpful, actionable guidance

---

## 🔧 **Configuration Options**

### **Whisper Models**
| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 39MB | Fastest | Basic | Quick testing |
| base | 74MB | Fast | Good | Simple commands |
| small | 244MB | Medium | Better | Balanced use |
| **medium** | 769MB | Slow | High | **Default** |
| large | 1550MB | Slowest | Highest | Complex commands |

Configure your preferred default model with `python main.py --setup-model`

### **Audio Settings**
```python
SAMPLE_RATE = 44100      # Audio quality
CHANNELS = 1             # Mono recording
DEVICE_INDEX = 2         # Input device (configurable with --setup-audio)
```

### **GPT Settings**
```python
model = "gpt-4"          # AI model
temperature = 0.1        # Consistency level
max_tokens = 4000        # Response length
```

---

## 📁 **File Structure**

### **Core Modules**
- **`main.py`**: Entry point and user interface orchestration
- **`recording.py`**: Audio capture and press-to-talk functionality
- **`transcription.py`**: Whisper integration and audio-to-text conversion
- **`llm.py`**: GPT-4 API integration and response handling
- **`md_file.py`**: Markdown file I/O with backup and validation
- **`prompts.py`**: System prompts for GPT-4 markdown editing
- **`cleaning.py`**: GPT output sanitization and formatting
- **`diff.py`**: Rich diff visualization and user approval interface
- **`utils.py`**: Configuration constants and shared utilities

### **Generated Directories**
- **`transcripts/`**: Voice command history with timestamps
- **`*_backup_*`**: Automatic file backups before edits

### **Configuration Files**
- **`.env`**: OpenAI API key (copy from `.env.example`)
- **`WHISPER_MODELS.md`**: Model selection guide
- **`FUNCTIONALITY.md`**: This documentation

---

## 🛡️ **Safety Features**

### **Data Protection**
- **Automatic backups**: Never lose original content
- **Validation checks**: Ensure file integrity before operations
- **Error recovery**: Graceful handling of API failures
- **Rollback capability**: Easy reversion of unwanted changes

### **User Control**
- **Change preview**: See exactly what will be modified
- **Approval required**: No automatic file changes
- **Dry-run mode**: Test without applying changes
- **Selective application**: Choose which changes to accept

---

## 🎯 **Perfect For**

### **Use Cases**
- **Quick task updates**: Voice-driven todo list management
- **Meeting notes**: Rapid note-taking and organization
- **Content creation**: Hands-free markdown editing
- **Documentation**: Voice-driven technical writing
- **Journal entries**: Natural language diary updates

### **Workflows**
- **Mobile editing**: When typing is inconvenient
- **Accessibility**: Alternative input method
- **Rapid prototyping**: Quick idea capture and organization
- **Batch processing**: Multiple quick edits in succession

---

## 🚀 **Future Integration Ready**

The modular architecture supports easy extension to:
- **macOS menu bar app**: System-wide voice commands
- **Obsidian plugin**: Direct vault integration
- **VS Code extension**: Editor integration
- **Web interface**: Browser-based editing
- **Mobile app**: Cross-platform voice editing

Current codebase provides the foundation for any of these implementations.