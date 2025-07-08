# OpenAI API Transcription Feature

## Overview

Glyph now supports both local Whisper models and OpenAI's speech-to-text API for audio transcription, providing users with flexible options based on their needs.

## Features Implemented

### 🔧 **Dual Transcription System**
- **Local Whisper**: Traditional offline transcription using local models
- **OpenAI API**: Cloud-based transcription using OpenAI's speech-to-text endpoint

### ⚙️ **Configuration Management**
- Persistent configuration storage in `~/.glyph/transcription_config.json`
- Default method selection with fallback options
- API key status tracking (without storing the actual key)

### 🎛️ **User Interface**
- Interactive setup wizard (`glyph --setup-transcription`)
- CLI method override (`glyph --transcription-method openai_api`)
- Transcription method testing (`glyph --test-transcription`)
- Interactive CLI integration with method selection

### 🔄 **Dynamic Switching**
- Switch between methods per session using CLI flags
- Configure default method in interactive setup
- Override method for specific transcription calls

## Usage Examples

### Setup and Configuration

```bash
# Run the transcription setup wizard
glyph --setup-transcription

# Test all transcription methods
glyph --test-transcription

# View current configuration
glyph --show-config
```

### Dynamic Method Selection

```bash
# Use OpenAI API for this session (overrides default)
glyph --file myfile.md --transcription-method openai_api

# Force local Whisper for this session
glyph --file myfile.md --transcription-method local

# Use configured default method
glyph --file myfile.md
```

### Interactive Mode

```bash
# Launch interactive mode with transcription config
glyph --interactive
# Then select option 3: "Configure transcription method"
```

## Configuration File

The configuration is stored in `~/.glyph/transcription_config.json`:

```json
{
  "transcription_method": "local",
  "local_whisper": {
    "model": "medium",
    "language": "auto"
  },
  "openai_api": {
    "model": "whisper-1",
    "language": "auto",
    "api_key_set": false
  }
}
```

## OpenAI API Setup

### 1. Get API Key
- Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
- Create a new API key
- Copy the key

### 2. Set Environment Variable
```bash
# For current session
export OPENAI_API_KEY='your-api-key-here'

# For permanent setup (add to ~/.bashrc, ~/.zshrc, etc.)
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### 3. Configure Glyph
```bash
glyph --setup-transcription
# Select option 2: "OpenAI API"
# Follow the setup instructions
```

## Method Comparison

| Feature | Local Whisper | OpenAI API |
|---------|---------------|------------|
| **Cost** | Free | Paid ($0.006/minute) |
| **Privacy** | Fully private | Data sent to OpenAI |
| **Internet** | Not required | Required |
| **Speed** | Slower (CPU intensive) | Faster |
| **Accuracy** | Good | Excellent |
| **Resource Usage** | High CPU/RAM | Minimal |
| **Setup** | Model download | API key required |

## Technical Implementation

### New Modules
- `transcription_config.py`: Configuration management
- Enhanced `transcription.py`: Dual-method support

### Key Classes
- `TranscriptionConfig`: Handles configuration persistence
- `TranscriptionService`: Unified transcription interface

### Error Handling
- Graceful fallback to local method if API fails
- Comprehensive error messages for API issues
- Network timeout handling

### Backward Compatibility
- Existing `transcribe_audio()` function maintained
- Legacy Whisper model loading preserved
- No breaking changes to existing workflows

## Benefits

### For Users
- **Flexibility**: Choose method based on needs
- **Performance**: Faster transcription with API
- **Privacy**: Keep sensitive audio local when needed
- **Reliability**: Fallback options if one method fails

### For Developers
- **Extensible**: Easy to add more transcription services
- **Configurable**: Rich configuration system
- **Testable**: Built-in testing utilities
- **Maintainable**: Clean separation of concerns

## Future Enhancements

- Support for additional OpenAI models
- Integration with other speech-to-text services
- Advanced language detection and switching
- Real-time transcription API support
- Custom API endpoint configuration