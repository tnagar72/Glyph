# Frequently Asked Questions (FAQ)

## 🚀 **Getting Started**

### Q: How do I get started with Glyph?
**A:** Follow these steps:
1. Install Python 3.8+ and clone the repository
2. Run `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your OpenAI API key
4. Test with `python main.py --transcript-only`

### Q: Where do I get an OpenAI API key?
**A:** Visit [OpenAI's API Keys page](https://platform.openai.com/api-keys), create an account, and generate a new API key. You'll need billing set up to use GPT-4.

### Q: What's the difference between the recording methods?
**A:** 
- **Spacebar method** (default): Hold spacebar to record, release to stop
- **Enter-to-stop method** (`--enter-stop`): Auto-starts recording, press Enter when finished
- Use enter-to-stop if you experience terminal interference in iTerm

## 🎤 **Transcription & Audio**

### Q: What's the difference between local and OpenAI API transcription?
**A:** 

| Feature | Local Whisper | OpenAI API |
|---------|---------------|------------|
| **Cost** | Free | $0.006/minute |
| **Privacy** | Fully private | Data sent to OpenAI |
| **Internet** | Not required | Required |
| **Speed** | Slower (CPU intensive) | Faster |
| **Accuracy** | Good | Excellent |
| **Setup** | Model download | API key required |

### Q: How do I set up OpenAI API transcription?
**A:** 
1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Set environment variable: `export OPENAI_API_KEY='your-key'`
3. Run setup wizard: `glyph --setup-transcription`
4. Choose option 2: "OpenAI API"

### Q: Can I switch transcription methods per session?
**A:** Yes! Use CLI flags:
```bash
# Force OpenAI API for this session
glyph --file notes.md --transcription-method openai_api

# Force local Whisper for this session  
glyph --file notes.md --transcription-method local
```

### Q: How do I test which transcription method works better?
**A:** Use the testing feature:
```bash
glyph --test-transcription
```
This will test both methods with the same audio sample.

## 🎤 **Audio & Recording Issues**

### Q: "Audio capture failed" - what's wrong?
**A:** Common solutions:
1. **Check microphone permissions**: Go to System Preferences → Security & Privacy → Privacy → Microphone
2. **Verify audio device**: Run `python -c "import sounddevice as sd; print(sd.query_devices())"` and update `DEVICE_INDEX` in `utils.py`
3. **Test microphone**: Try `python -c "import sounddevice as sd; sd.rec(1000, samplerate=44100)"`
4. **Speak longer**: Recordings under 0.5 seconds are rejected
5. **Check volume**: Ensure you're speaking clearly and microphone isn't muted

### Q: Why does my terminal make bell sounds during recording?
**A:** This happens in some terminal applications (like iTerm) with the spacebar method. Use the enter-to-stop method instead:
```bash
python main.py --enter-stop --file your-file.md
```

### Q: The transcription is inaccurate. How can I improve it?
**A:** Try these approaches:
1. **Switch to OpenAI API**: `--transcription-method openai_api` (more accurate)
2. **Use a larger local model**: `--whisper-model large` (slower but more accurate)
3. **Speak clearly** in a quiet environment
4. **Position microphone** closer to your mouth
5. **Check audio levels** - too quiet or too loud affects accuracy
6. **Avoid background noise** and echo

### Q: Which transcription method should I use?
**A:** Choose based on your needs:
- **OpenAI API**: Faster, more accurate, requires internet and API key ($0.006/minute)
- **Local Whisper**: Free, private, works offline, slower

Configure with `glyph --setup-transcription`

### Q: Which Whisper model should I use (for local transcription)?
**A:** 
- **tiny/base**: Fast testing, simple commands
- **small**: Good balance for regular use
- **medium** (default): Best balance of speed and accuracy
- **large**: Maximum accuracy for complex commands (slower)

## 🧠 **GPT-4 & AI Processing**

### Q: "OpenAI API errors" - how do I fix this?
**A:** Check these common issues:
1. **API key**: Verify it's correctly set in `.env` file
2. **Billing**: Ensure your OpenAI account has billing enabled
3. **Rate limits**: Wait a moment and try again if hitting limits
4. **Network**: Check internet connection
5. **Test manually**: `python -c "import openai; print('API key loaded')" `

### Q: The AI edits aren't what I expected. How can I improve them?
**A:** 
1. **Be specific**: "Mark task 2 as complete" vs "complete something"
2. **Use context**: Mention section names or specific content
3. **Try rephrasing**: Different wording can yield better results
4. **Use dry-run mode**: `--dry-run` to preview without applying
5. **Check existing content**: AI works better with well-structured markdown

### Q: Can I use different AI models besides GPT-4?
**A:** Currently, the system is optimized for GPT-4. You can modify `llm.py` to use other OpenAI models (GPT-3.5) or adapt it for other APIs, but GPT-4 provides the best results for markdown editing.

## 📝 **File & Content Issues**

### Q: "No changes suggested by GPT-4" - why?
**A:** This can happen when:
1. **Command unclear**: AI couldn't understand what to change
2. **Already done**: The requested change already exists
3. **Context missing**: File content doesn't match your command
4. **Try rewording**: Be more specific about the desired change

### Q: How do I undo changes I don't like?
**A:** Use the undo feature:
```bash
python main.py --undo your-file.md
```
This restores from the latest backup created before changes.

### Q: Are my files safe? What about backups?
**A:** Yes, the system is designed for safety:
- **Centralized backups** stored in `backups/` directory with organized structure
- **Automatic backups** created before every edit with timestamps
- **Change preview** shows exactly what will change
- **User approval** required for all modifications
- **Undo functionality** available via `--undo`
- **Dry-run mode** for testing without changes
- **Backup cleanup** tools to manage storage space

### Q: Where are backup files stored?
**A:** Backups are stored in a centralized `backups/` directory structure:
```
backups/
├── parent_directory/
│   └── filename/
│       ├── filename_auto_20250624_120000.md
│       └── filename_pre_restore_20250624_130000.md
```
This prevents filename conflicts and organizes backups by file location.

### Q: Can I use this with Obsidian vaults?
**A:** Absolutely! The editor preserves:
- Internal links `[[note]]`
- Tags `#important`
- Frontmatter metadata
- Markdown formatting

Just point it to files in your Obsidian vault directory.

### Q: How do I manage backup files and storage space?
**A:** Use the built-in backup management tools:

**View backup statistics:**
```bash
python cleanup_backups.py --stats
# or
make backup-stats
```

**List old backup files:**
```bash
python cleanup_backups.py --list --days 30
```

**Clean up old backups:**
```bash
# Interactive cleanup (recommended)
python cleanup_backups.py --days 30

# Dry run to see what would be deleted
python cleanup_backups.py --dry-run --days 30

# Force cleanup without confirmation
python cleanup_backups.py --force --days 30
```

**Automated cleanup:**
Set up a cron job to automatically clean backups older than 30 days:
```bash
# Add to crontab (runs daily at 3 AM)
0 3 * * * cd /path/to/glyph && python cleanup_backups.py --force --days 30
```

### Q: Can I restore from a specific backup?
**A:** Yes, you can choose from multiple backups:
```bash
# List available backups for a file
python main.py --undo your-file.md
# This shows all available backups and lets you choose

# Or use the backup manager directly
python -c "
from backup_manager import get_backup_manager
bm = get_backup_manager()
backups = bm.list_backups('your-file.md')
for i, backup in enumerate(backups):
    print(f'{i}: {backup[\"filename\"]} ({backup[\"created_str\"]})')
"
```

## 🖥️ **Interface & Usage**

### Q: What's the difference between normal and interactive mode?
**A:**
- **Normal mode**: Direct command-line usage with flags
- **Interactive mode** (`--interactive`): Rich menu interface with file browsing, model selection, and options management

### Q: How do I use live transcription mode?
**A:** 
```bash
# Rich UI mode
python main.py --live

# Simple output for piping
python main.py --live | tee transcript.log
```
Live mode streams voice-to-text in real-time without GPT processing.

### Q: Can I use this in scripts or automation?
**A:** Yes! Use these patterns:
```bash
# Batch processing
for file in *.md; do python main.py --file "$file" --transcript-only; done

# Piping live transcription
python main.py --live | your_processing_script.py

# Dry-run for testing
python main.py --file notes.md --dry-run --verbose
```

## 🔧 **Technical Issues**

### Q: "ModuleNotFoundError" errors during installation?
**A:** 
1. **Check Python version**: Requires Python 3.8+
2. **Use virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Update pip**: `pip install --upgrade pip`

### Q: Performance is slow. How can I speed it up?
**A:**
1. **Use smaller Whisper models**: `--whisper-model tiny` or `base`
2. **Close other applications** to free up memory
3. **Use SSD storage** for faster file operations
4. **Check system resources** during transcription

### Q: Can I run this on Windows or Linux?
**A:** The code is designed to be cross-platform, but it's primarily tested on macOS. You may need to:
- Adjust audio device configuration in `utils.py`
- Install platform-specific audio dependencies
- Test microphone permissions and access

### Q: How much does it cost to run?
**A:** Costs depend on OpenAI API usage:
- **Local Whisper transcription**: Free (runs locally)
- **OpenAI API transcription**: $0.006 per minute of audio
- **GPT-4 API calls**: ~$0.03 per 1K tokens (varies by usage)
- **Typical session**: $0.10-0.50 for moderate editing (plus transcription costs if using API)

## 🤝 **Contributing & Development**

### Q: How can I contribute to the project?
**A:** See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines. Common contributions:
- Bug reports and feature requests
- Code improvements and optimizations
- Documentation and examples
- Cross-platform testing

### Q: How do I set up a development environment?
**A:**
```bash
git clone https://github.com/tnagar72/Glyph.git
cd Glyph
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
```

### Q: Where can I get help or ask questions?
**A:**
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community help
- **Documentation**: Check FUNCTIONALITY.md and DEVELOPER_TOOLS.md

## 🎯 **Best Practices**

### Q: What are some effective voice commands?
**A:** Be specific and contextual:
- ✅ **Good**: "Mark the third task in the Work section as complete"
- ❌ **Vague**: "Mark something as done"
- ✅ **Good**: "Add a new bullet point about the quarterly report under Personal Tasks"
- ❌ **Vague**: "Add something to the list"

### Q: How should I structure my markdown files for best results?
**A:**
- Use clear headings and sections
- Keep consistent formatting
- Include context in task descriptions
- Use meaningful names for sections and items

---

**Still have questions?** Check the [documentation](docs/) or [open an issue](https://github.com/tnagar72/Glyph/issues) on GitHub!