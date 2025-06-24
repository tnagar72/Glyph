# Contributing to Voice-Controlled Markdown Editor

Thank you for your interest in contributing to the Voice-Controlled Markdown Editor! This document provides guidelines and information for contributors.

## 🎯 **Project Overview**

This project combines local speech recognition (OpenAI Whisper) with GPT-4 to create an intelligent voice-controlled markdown editing system. We welcome contributions that improve functionality, documentation, performance, and user experience.

## 🚀 **Getting Started**

### Prerequisites
- Python 3.8+
- Git
- OpenAI API key
- Microphone for testing

### Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/tnagar72/VoiceMark.git
cd VoiceMark
```

2. **Set up virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. **Test your setup:**
```bash
python main.py --transcript-only --verbose
```

## 🔧 **Development Guidelines**

### Code Style
- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and reasonably sized (< 50 lines when possible)
- Use type hints where beneficial

### Code Organization
```python
# Good: Clear imports and docstrings
import sounddevice as sd
from typing import Optional

def transcribe_audio(audio_data: np.ndarray) -> Optional[str]:
    """Transcribe audio data using Whisper.
    
    Args:
        audio_data: Raw audio data as numpy array
        
    Returns:
        Transcribed text or None if transcription failed
    """
    # Implementation here
```

### Testing
Before submitting changes, test:
- Basic functionality: `python main.py --transcript-only`
- Interactive mode: `python main.py --interactive`
- Live transcription: `python main.py --live`
- Different Whisper models: `python main.py --whisper-model tiny`
- Edge cases: empty files, long recordings, API failures

### Error Handling
- Use descriptive error messages
- Handle API failures gracefully
- Provide helpful user feedback
- Log errors appropriately with verbose mode

## 🐛 **Reporting Issues**

### Bug Reports
When reporting bugs, please include:

**Environment:**
- Operating system and version
- Python version
- Dependencies (pip freeze output)
- Audio device information

**Steps to Reproduce:**
1. Exact command used
2. Input file content (if applicable)
3. Voice command spoken
4. Expected vs actual behavior

**Additional Information:**
- Error messages or stack traces
- Verbose output (--verbose flag)
- Log files from logs/ directory

### Feature Requests
For new features, please describe:
- **Use case**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches
- **Impact**: Who would benefit?

## 🔀 **Pull Request Process**

### Before Submitting
1. **Create feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
- Follow coding guidelines above
- Add tests if applicable
- Update documentation
- Test thoroughly

3. **Commit with clear messages:**
```bash
git commit -m "Add enter-to-stop recording method

- Implement new recording function without keyboard hooks
- Add --enter-stop command line flag
- Update UI to show appropriate instructions
- Fixes terminal interference issues in iTerm"
```

### Pull Request Template
Please include:

**Description:**
- What changes were made?
- Why were they necessary?
- How do they work?

**Testing:**
- What testing was performed?
- Any edge cases considered?
- Performance impact?

**Documentation:**
- README updates needed?
- New features documented?
- Breaking changes noted?

**Checklist:**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

## 🎨 **Areas for Contribution**

### High Priority
- **Cross-platform support**: Windows and Linux compatibility
- **Additional audio codecs**: Support for more audio formats
- **Performance optimization**: Faster transcription, lower memory usage
- **Error recovery**: Better handling of API failures and network issues

### Medium Priority
- **Integration examples**: Obsidian plugins, VS Code extensions
- **Additional Whisper models**: Support for custom models
- **Batch processing**: Multiple file editing capabilities
- **Configuration management**: Better settings organization

### Low Priority
- **UI enhancements**: More terminal themes, better progress indicators
- **Testing framework**: Comprehensive test suite
- **Documentation**: Video tutorials, advanced usage guides
- **Packaging**: PyPI distribution, Docker containers

### Code Quality
- **Type hints**: Add typing throughout codebase
- **Refactoring**: Improve code organization and modularity
- **Documentation**: API docs, inline comments
- **Performance**: Profiling and optimization

## 🏗️ **Architecture Guidelines**

### Module Responsibilities
- **main.py**: Entry point and argument parsing
- **recording.py**: Audio capture and device management
- **transcription.py**: Whisper integration and audio processing
- **llm.py**: GPT-4 API communication
- **interactive_cli.py**: Rich terminal interface
- **diff.py**: Change visualization and user approval

### Design Principles
- **Modularity**: Each module has clear responsibilities
- **Error resilience**: Graceful failure handling
- **User experience**: Clear feedback and intuitive interface
- **Performance**: Efficient resource usage
- **Extensibility**: Easy to add new features

## 🧪 **Testing Guidelines**

### Manual Testing Checklist
- [ ] Basic voice editing workflow
- [ ] Interactive CLI navigation
- [ ] Live transcription streaming
- [ ] Error handling (no API key, no microphone, etc.)
- [ ] Different Whisper models
- [ ] Various markdown file types
- [ ] Backup and undo functionality

### Automated Testing (Future)
We welcome contributions to set up:
- Unit tests for core functions
- Integration tests for API interactions
- Performance benchmarks
- Cross-platform compatibility tests

## 📝 **Documentation Standards**

### Code Documentation
- Docstrings for all public functions
- Inline comments for complex logic
- Type hints for function signatures
- Examples in docstrings when helpful

### User Documentation
- Clear, step-by-step instructions
- Real-world examples
- Troubleshooting sections
- Platform-specific notes

## 🤝 **Community Guidelines**

### Code of Conduct
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and contribute
- Focus on technical discussions

### Communication
- Use clear, descriptive issue titles
- Provide sufficient detail in descriptions
- Be patient with response times
- Ask questions when unsure

## 🎉 **Recognition**

Contributors will be:
- Listed in repository contributors
- Mentioned in release notes for significant contributions
- Credited in documentation for major features

## 📞 **Getting Help**

### Before Asking
1. Check existing issues and documentation
2. Search previous discussions
3. Test with verbose mode enabled
4. Review relevant code sections

### Where to Ask
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Request Comments**: Code-specific questions

Thank you for contributing to Voice-Controlled Markdown Editor! 🎙️