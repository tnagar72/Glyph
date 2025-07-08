# Glyph Testing Guide

This document provides a comprehensive guide to testing all functionality of the Glyph Voice-Controlled Markdown Editor.

## Overview

Glyph has two main operational modes, each with extensive testing coverage:

1. **Agent Mode** - Conversational AI for Obsidian vault management
2. **Non-Agent Mode** - Voice-to-text markdown editing, live transcription, and interactive CLI

## Test Structure

### Comprehensive Test Suites

#### 1. Agent Mode Tests (`test_agent_comprehensive.py`)
Tests all agent functionality including:

- **Agent Configuration System**
  - Vault path validation and setup
  - Configuration persistence and loading
  - Auto-accept and session memory settings

- **Agent Memory System**
  - Note reference registration and resolution
  - Typo tolerance and fuzzy matching
  - Entity tracking (people, projects, concepts)
  - Learning from user interactions

- **Conversation Context**
  - Multi-turn conversation tracking
  - Reference resolution ("it", "that note", "the one I created")
  - Working context and current focus management

- **Agent Tools**
  - File operations (create, read, delete, rename, move)
  - Section management (insert, append, replace, edit, delete)
  - Note discovery and similarity matching
  - Folder operations and organization
  - Obsidian integration and note opening

- **LLM Integration**
  - GPT-4 command processing
  - Tool call generation and validation
  - Context-aware prompting
  - Multi-turn conversation handling

- **CLI Integration**
  - Session management and state tracking
  - Command processing workflow
  - Error handling and recovery

- **End-to-End Workflows**
  - Complete multi-turn conversations
  - Reference learning and resolution
  - Context propagation across turns

#### 2. Non-Agent Mode Tests (`test_nonagent_comprehensive.py`)
Tests all traditional functionality including:

- **Audio Recording System**
  - Audio validation (duration, silence detection)
  - Recording methods (spacebar, enter-to-stop)
  - Device detection and scoring

- **Audio Configuration**
  - Device selection and scoring
  - Configuration persistence
  - Smart device detection

- **Transcription System**
  - Local Whisper model support (tiny → large)
  - OpenAI API transcription
  - Fallback mechanisms
  - Method testing and validation

- **Transcription Configuration**
  - Method selection (local vs API)
  - Model configuration
  - Environment variable management

- **Model Configuration**
  - Whisper model selection and info
  - Performance vs accuracy trade-offs
  - Configuration persistence

- **Markdown File Handling**
  - Path validation and extension handling
  - File reading and writing
  - Backup creation before modifications

- **Backup and Undo System**
  - Automatic backup creation
  - Backup listing and metadata
  - Restoration from backups
  - Undo operations

- **Diff and Approval System**
  - Diff generation and display
  - Change counting and statistics
  - User approval workflow

- **LLM Integration**
  - GPT-4 API integration for editing
  - Response cleaning and processing
  - Context-aware prompting

- **Live Transcription Mode**
  - Real-time audio processing
  - Transcript filtering and cleaning
  - Session management
  - Clipboard integration

- **Interactive CLI Mode**
  - File discovery in common locations
  - Interactive menus and selection
  - Configuration through UI

- **Session Logging**
  - Event logging (audio, transcription, GPT, user decisions)
  - Performance metrics tracking
  - Dual format (text + JSON) logging

- **Obsidian Integration**
  - Vault detection and validation
  - URI generation and file opening
  - Cross-platform support

- **UI System**
  - Rich terminal interface components
  - Recording indicators and progress
  - Error/success/warning messages
  - Configuration overview displays

### Existing Test Files

#### 3. Enhanced Agent Tests (`test_enhanced_agent.py`)
Focuses on advanced agent architecture:
- Memory system integration
- Conversation context management
- Enhanced note resolution
- Learning system validation
- Agent CLI integration

#### 4. Direct Agent Tests (`test_agent_directly.py`)
Tests agent functionality without interactive input:
- Command processing simulation
- File finding capabilities
- Similarity matching algorithms
- Tool execution validation

#### 5. Agent Commands Tests (`test_agent_commands.py`)
Comprehensive command testing scenarios:
- Test vault creation with realistic note structure
- Spelling mistake tolerance
- Word rearrangement handling
- Partial match resolution
- Folder reference handling
- Conversational reference testing
- Complex scenario validation
- Error handling verification

## Running Tests

### Prerequisites

Install required dependencies:
```bash
pip install numpy scipy sounddevice openai-whisper openai rich pytest
```

### Virtual Environment Setup

Always activate the Glyph virtual environment before testing:
```bash
source obsidian_voice/bin/activate
```

### Running All Tests

Use the master test runner:
```bash
python run_all_tests.py
```

This will:
1. Check all dependencies
2. Run comprehensive agent mode tests
3. Run comprehensive non-agent mode tests
4. Run existing specialized test files
5. Generate a detailed test report

### Running Individual Test Suites

**Agent Mode Tests:**
```bash
python test_agent_comprehensive.py
```

**Non-Agent Mode Tests:**
```bash
python test_nonagent_comprehensive.py
```

**Enhanced Agent Tests:**
```bash
python test_enhanced_agent.py
```

**Direct Agent Tests:**
```bash
python test_agent_directly.py
```

**Agent Commands Tests:**
```bash
python test_agent_commands.py
```

### Agent Setup for Testing

Before running agent tests, configure a test vault:
```bash
python test_agent_commands.py  # Creates test vault
python main.py --setup-agent   # Configure agent with test vault path
```

## Test Coverage

### Agent Mode Coverage
- ✅ Configuration management and persistence
- ✅ Memory system and learning capabilities
- ✅ Conversation context and reference resolution
- ✅ All 15+ agent tools and operations
- ✅ LLM integration and command processing
- ✅ Multi-turn conversation workflows
- ✅ Error handling and recovery
- ✅ CLI session management
- ✅ Obsidian integration

### Non-Agent Mode Coverage
- ✅ Audio capture and validation
- ✅ Device configuration and management
- ✅ Dual transcription methods (local + API)
- ✅ Model selection and configuration
- ✅ File handling and validation
- ✅ Backup and undo systems
- ✅ Diff generation and user approval
- ✅ GPT-4 integration for editing
- ✅ Live transcription with real-time processing
- ✅ Interactive CLI with rich interface
- ✅ Session logging and analytics
- ✅ Obsidian vault integration
- ✅ Rich terminal UI components
- ✅ Main application integration

## Test Features

### Mocking and Simulation
- Audio data simulation for consistent testing
- OpenAI API mocking to avoid API costs
- File system mocking for isolated testing
- User input simulation for interactive components

### Environment Management
- Automatic test environment setup and teardown
- Configuration backup and restoration
- Temporary file and directory management
- Virtual environment isolation

### Error Handling
- Comprehensive exception testing
- Graceful degradation validation
- Error recovery mechanism testing
- User-friendly error message validation

### Performance Testing
- Audio processing latency validation
- Transcription speed measurement
- Memory usage monitoring
- File operation performance testing

## Continuous Integration

The test suite is designed to run in CI environments:

### GitHub Actions Example
```yaml
name: Test Glyph
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: python run_all_tests.py
```

### Local Development
For local development, run tests before committing:
```bash
# Quick smoke test
python test_agent_directly.py

# Full test suite
python run_all_tests.py

# Specific functionality
python test_nonagent_comprehensive.py
```

## Test Data and Fixtures

### Test Vault Structure
The agent tests create a realistic Obsidian vault with:
- **Daily Notes/** - Daily standup and planning notes
- **Projects/** - Project documentation and tracking
- **Work/** - Meeting notes and sprint planning
- **Personal/** - Shopping lists and personal notes
- **Templates/** - Note templates for consistency

### Test Audio Data
- Simulated 16kHz audio data for consistent testing
- Various durations for validation testing
- Silent audio for error condition testing
- Noisy audio for filtering algorithm testing

### Test Markdown Files
- Well-structured markdown with headers and sections
- Task lists and checkboxes
- Links and references
- Various content types for comprehensive testing

## Debugging Tests

### Verbose Mode
Most tests support verbose output for debugging:
```bash
python test_agent_comprehensive.py --verbose
```

### Individual Test Methods
You can run specific test methods by modifying the test files:
```python
# In test file, comment out unwanted tests
def run_all_tests(self):
    tests = [
        # ("Test Name", self.test_method),  # Commented out
        ("Specific Test", self.test_specific_functionality),  # Run only this
    ]
```

### Log Analysis
Check generated logs for detailed execution information:
- `logs/session_*.txt` - Human-readable session logs
- `logs/session_*.json` - Structured session data
- `transcripts/` - Audio transcription outputs

## Contributing Tests

When adding new functionality:

1. **Add unit tests** to the appropriate comprehensive test file
2. **Update this guide** with new test coverage information
3. **Ensure mocking** for external dependencies (APIs, hardware)
4. **Test error conditions** and edge cases
5. **Validate cleanup** to avoid test interference

### Test Naming Convention
- Use descriptive test method names: `test_agent_memory_system()`
- Group related tests in logical sections
- Include both positive and negative test cases
- Test edge cases and error conditions

### Test Documentation
- Add docstrings explaining what each test validates
- Include examples of expected behavior
- Document any special setup or teardown requirements
- Note any dependencies or prerequisites

## Troubleshooting

### Common Issues

**Audio device errors:**
- Tests may skip audio tests in CI environments
- Local testing requires working microphone
- Mock audio device for headless testing

**API key requirements:**
- OpenAI tests will fail without API key
- Set `OPENAI_API_KEY` environment variable for full testing
- API tests gracefully degrade when key unavailable

**Permission errors:**
- Ensure write permissions to test directories
- Check Obsidian app permissions for file opening tests
- Verify microphone permissions for audio tests

**Memory issues:**
- Large Whisper models require significant RAM
- Use smaller models or mocking for constrained environments
- Monitor memory usage during test execution

### Test Environment Reset
If tests become inconsistent:
```bash
# Clean all test artifacts
rm -rf ~/.glyph/test_*
rm -rf logs/test_*
rm -rf transcripts/test_*

# Reset configurations
python main.py --setup-audio
python main.py --setup-model
python main.py --setup-transcription
python main.py --setup-agent
```

This comprehensive testing framework ensures Glyph maintains high quality and reliability across all features and use cases.