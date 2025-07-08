# 🛠️ Developer Tools - Interactive & Live Modes

## 🎯 **Overview**

Advanced tools for developers and power users to enhance the Glyph experience.

---

## 🖥️ **Interactive CLI Mode**

### **Launch Interactive Mode**
```bash
python main.py --interactive
```

### **Features**
- **Rich menu system** with beautiful terminal UI
- **File browser** for easy markdown file selection
- **Model configuration** with performance details
- **Options toggle** for dry-run, verbose, transcript-only
- **Undo management** with backup selection
- **Live mode launcher** from within menus

### **Menu Options**

#### **1. File Selection**
- **Manual entry**: Type file path directly
- **Smart browsing**: Auto-discover markdown files in:
  - `~/Documents`
  - `~/Desktop` 
  - `~/Notes`
  - `~/Obsidian`
  - Current directory
- **File details**: Shows file size, modification date
- **Recent files**: Sorted by modification time

#### **2. Model Configuration**
```
┌───────┬─────────┬─────────┬─────────┬────────────────┬─────────┐
│ Option│ Model   │ Size    │ Speed   │ Accuracy       │ Current │
├───────┼─────────┼─────────┼─────────┼────────────────┼─────────┤
│ 1     │ tiny    │ 39MB    │ Fastest │ Basic accuracy │         │
│ 2     │ base    │ 74MB    │ Fast    │ Good accuracy  │         │
│ 3     │ small   │ 244MB   │ Medium  │ Better accuracy│         │
│ 4     │ medium  │ 769MB   │ Slow    │ High accuracy  │ ✓       │
│ 5     │ large   │ 1550MB  │ Slowest │ Highest accuracy│        │
└───────┴─────────┴─────────┴─────────┴────────────────┴─────────┘
```

**Set Default Model:**
- Configure your preferred model with the wizard
- All future commands will use this model unless overridden
- Access via main menu or `glyph --setup-model`

#### **3. Transcription Configuration**
- **Method Selection**: Choose between Local Whisper and OpenAI API
- **API Setup**: Configure OpenAI API key and test connectivity
- **Method Testing**: Test all available transcription methods
- **Performance Comparison**: Compare speed and accuracy

#### **4. Options Toggle**
- **Dry Run**: Preview changes without applying
- **Verbose**: Show detailed debug output  
- **Transcript Only**: Voice-to-text without GPT processing
- **Enter-Stop Recording**: Use ENTER key instead of spacebar (prevents terminal interference)

#### **5. Voice Editing**
- Starts normal voice editing with configured settings
- Only available when file is selected

#### **6. Live Transcription**
- Switches to real-time voice streaming mode
- Uses configured transcription method
- Great for testing and debugging

#### **7. Undo Management**
- Lists available backups for selected file
- One-click restoration with confirmation

---

## 🎤 **Live Transcription Mode**

### **Basic Live Mode**
```bash
python main.py --live
```
**Features:**
- Beautiful real-time display with Rich UI
- Uses configured transcription method (local or OpenAI API)
- Shows last 10 transcripts
- Session statistics (duration, transcript count)
- Auto-saves transcripts to `transcripts/` folder
- Ctrl+C to stop

### **Live Mode with Method Override**
```bash
# Force OpenAI API for this session
python main.py --live --transcription-method openai_api

# Force local Whisper for this session
python main.py --live --transcription-method local
```

### **Simple Live Mode (for Piping)**
```bash
python main.py --live | tee transcript.log
```
**Features:**
- Clean stdout output for piping
- Format: `[HH:MM:SS] transcript text`
- No Rich UI interference
- Perfect for logging or further processing

### **Clipboard Mode**
```bash
python main.py --live --clipboard
```
**Features:**
- Copies all transcripts to clipboard instead of saving files
- Raw transcript text only (no timestamps)
- Perfect for quick text input into other applications
- Works with both rich UI and simple modes

### **Standalone Live Transcription**
```bash
python live_transcription.py [OPTIONS]
```

**Options:**
- `--transcription-method {local,openai_api}` - Force transcription method
- `--model {tiny,base,small,medium,large}` - Whisper model selection (local only)
- `--simple` - Simple output mode (good for piping)
- `--clipboard` - Copy transcripts to clipboard instead of saving
- `--chunk CHUNK` - Audio chunk duration in seconds (default: 3.0)
- `--verbose` - Enable verbose debug output

### **Live Mode Use Cases**

#### **1. Development & Debugging**
```bash
# Test different transcription methods
python live_transcription.py --transcription-method openai_api --verbose
python live_transcription.py --transcription-method local --model large --verbose

# Quick transcription testing
python live_transcription.py --model tiny --chunk 2.0
```

#### **2. Data Collection**
```bash
# Collect training data
python main.py --live | tee training_data.txt

# Log all transcriptions with timestamps
python main.py --live >> voice_log.txt
```

#### **3. Integration Testing**
```bash
# Test pipeline integration
python main.py --live | python your_processor.py

# Monitor transcription quality
python main.py --live --verbose 2>&1 | grep "RMS\|amplitude"
```

#### **4. Live Streaming**
```bash
# Stream to external services
python main.py --live | curl -X POST -d @- https://your-api.com/transcriptions

# Real-time processing
python main.py --live | while read line; do echo "Processed: $line"; done
```

---

## ⚙️ **Configuration & Customization**

### **Chunk Duration Tuning**
```bash
# Faster response (less accurate)
python live_transcription.py --chunk 1.0

# Better accuracy (slower response)  
python live_transcription.py --chunk 5.0
```

### **Transcription Method Selection for Live Mode**
- **OpenAI API**: Fastest, requires internet and API key
- **Local Whisper**: Private, works offline, uses more CPU

Configure your preferred default with `glyph --setup-transcription`

### **Model Selection for Live Mode (Local Whisper)**
- **tiny**: Ultra-fast for real-time demos
- **base**: Good balance for development  
- **medium**: Production quality (default)
- **large**: Maximum accuracy for data collection

Configure your preferred default with `glyph --setup-model`

### **Environment Variables**
```bash
# Override default model
export WHISPER_MODEL=large
python main.py --live

# Verbose by default
export VERBOSE=1
python main.py --interactive
```

---

## 🔧 **Integration Examples**

### **1. Voice Command Development**
```bash
# Test commands in real-time
python main.py --live | grep -i "mark\|complete\|add\|move"
```

### **2. Accuracy Testing**
```python
# Process live transcripts
import sys
for line in sys.stdin:
    timestamp, transcript = line.strip().split('] ', 1)
    timestamp = timestamp[1:]  # Remove [
    # Process transcript...
```

### **3. Voice-Controlled Applications**
```bash
# Voice control for other apps
python main.py --live | python voice_controller.py
```

### **4. Meeting Transcription**
```bash
# Live meeting notes
python main.py --live --whisper-model large | \
  python format_meeting_notes.py > meeting_$(date +%Y%m%d).md

# Quick clipboard transcription
python main.py --live --clipboard --whisper-model large
```

---

## 🎨 **UI Features**

### **Interactive Mode UI**
- **Rich tables** with colored headers and borders
- **Progress indicators** for long operations
- **Context-sensitive menus** based on current state
- **File size/date display** for informed selection
- **Status indicators** showing current configuration

### **Live Mode UI**
- **Real-time updates** with animated display
- **Session statistics** showing duration and counts
- **Recent transcript history** (scrolling window)
- **Visual indicators** for recording state
- **Graceful shutdown** with session summary

---

## 🚀 **Advanced Usage**

### **Batch Processing**
```bash
# Process multiple files interactively
for file in *.md; do
  echo "Processing $file"
  python main.py --interactive --file "$file"
done
```

### **Quality Monitoring**
```bash
# Monitor transcription quality metrics
python main.py --live --verbose 2>&1 | \
  grep "RMS\|amplitude\|duration" | \
  python quality_monitor.py
```

### **Remote Voice Control**
```bash
# SSH + voice control
ssh remote-server "python main.py --live" | \
  python local_voice_processor.py
```

---

## 💡 **Tips & Best Practices**

### **For Development**
1. **Start with interactive mode** to familiarize yourself with options
2. **Use live mode** to test voice command phrasing
3. **Enable verbose mode** when debugging issues
4. **Use smaller models** (tiny/base) for rapid iteration

### **For Production**
1. **Use medium/large models** for accuracy
2. **Enable session logging** for audit trails
3. **Test with dry-run mode** before applying changes
4. **Keep backups enabled** for safety

### **For Integration**
1. **Use simple live mode** for clean piping
2. **Parse timestamps** for chronological processing
3. **Handle Ctrl+C gracefully** in downstream processes
4. **Monitor stderr** for status messages

**The developer tools provide a complete toolkit for Glyph development and production use!**