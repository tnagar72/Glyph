# Contributing to Glyph

## Development Setup

```bash
git clone https://github.com/tnagar72/Glyph.git
cd Glyph
python -m venv glyph_env
source glyph_env/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"  # Install development dependencies
```

## Testing

Always run tests before submitting:

```bash
# Quick validation
python run_tests_simple.py

# Full test suite
python run_all_tests.py

# Individual components
python test_agent_comprehensive.py
python test_nonagent_comprehensive.py
```

Tests mock external APIs and audio input for reliable CI/CD execution.

## Code Style

- Follow existing patterns and naming conventions
- Use type hints for function parameters and returns
- Add docstrings for new classes and public methods
- Keep functions focused and under 50 lines when possible

## Architecture Overview

**Dual-mode design:**
- `main.py` - Entry point and mode routing
- `agent_*` modules - Conversational AI system
- `transcription*` modules - Audio processing pipeline
- `*_config.py` modules - Persistent configuration

**Key principles:**
- Separation of concerns
- Dependency injection for services
- Comprehensive error handling
- Automatic fallback strategies

## Adding Features

### Agent Tools

New agent tools go in `agent_tools.py`:

```python
def _tool_your_feature(self, arg1: str, arg2: Optional[str] = None) -> ToolCallResult:
    """Brief description of what this tool does."""
    try:
        # Validate inputs
        if not arg1:
            return ToolCallResult(success=False, message="arg1 is required")
        
        # Perform operation
        result = your_operation(arg1, arg2)
        
        # Update memory/context if needed
        self.memory.register_operation("your_feature", {"arg1": arg1})
        
        return ToolCallResult(
            success=True,
            message=f"Operation completed: {result}",
            data={"result": result}
        )
    except Exception as e:
        logger.error(f"Tool your_feature failed: {e}")
        return ToolCallResult(success=False, message=f"Operation failed: {e}")
```

Then register it in `__init__`:
```python
self.tools = {
    # ... existing tools
    'your_feature': self._tool_your_feature,
}
```

### Transcription Providers

New transcription methods go in `transcription.py`:

```python
class YourTranscriptionProvider(TranscriptionProvider):
    def transcribe(self, audio_data, language: str) -> str:
        # Your implementation
        pass
    
    def test_connection(self) -> Tuple[bool, str]:
        # Connection validation
        pass
```

### Configuration

New config modules should follow the pattern:
- Persistent storage in `~/.glyph/`
- Configuration class with load/save methods
- Interactive setup function
- Validation and fallback defaults

## Testing New Features

### Agent Tools
Add tests to `test_agent_comprehensive.py`:

```python
def test_your_tool(self):
    """Test your new tool functionality."""
    # Setup
    tools = AgentTools()
    
    # Test success case
    result = tools.execute_tool_call({
        'tool_call': 'your_feature',
        'arguments': {'arg1': 'test_value'}
    })
    
    assert result.success
    assert 'expected_result' in result.message
    
    # Test error cases
    result = tools.execute_tool_call({
        'tool_call': 'your_feature',
        'arguments': {}  # Missing required arg
    })
    
    assert not result.success
```

### Non-Agent Features
Add tests to `test_nonagent_comprehensive.py` for direct mode features.

## Pull Request Process

1. **Fork and branch**: Create feature branch from `main`
2. **Develop**: Implement feature with tests
3. **Test**: Ensure all tests pass
4. **Document**: Update relevant documentation
5. **Submit**: Create PR with clear description

## PR Requirements

- [ ] All tests pass: `python run_all_tests.py`
- [ ] New features have tests
- [ ] Documentation updated if needed
- [ ] Code follows existing style
- [ ] No API keys or secrets in code

## Common Issues

**Import errors during development:**
```bash
# Ensure you're in the virtual environment
source glyph_env/bin/activate

# Install in development mode
pip install -e .
```

**Tests failing due to missing mocks:**
- All external API calls should be mocked in tests
- Audio input is mocked via `AudioMockProvider`
- File operations use temporary directories

**Agent memory not persisting:**
- Memory is only saved on successful operations
- Check that your tool calls are returning `ToolCallResult(success=True)`
- Memory files are in `~/.glyph/memory/`

## Code Areas

**Audio System** (`recording.py`, `audio_config.py`):
- Cross-platform audio device management
- Recording validation and processing
- Device scoring and selection

**Transcription** (`transcription*.py`):
- Dual-method service architecture
- Automatic fallback logic
- Provider pattern for extensibility

**Agent System** (`agent_*.py`):
- Conversational interface and session management
- Tool execution and error handling
- Memory and learning systems
- Context tracking across conversations

**UI Components** (`*_cli.py`, `ui_helpers.py`):
- Rich terminal interfaces
- Interactive configuration wizards
- Real-time transcription streaming

## Performance Considerations

- Large Whisper models use significant memory
- API calls should have appropriate timeouts
- File operations need backup/rollback mechanisms
- Memory system should handle large reference sets

## Security Guidelines

- Never commit API keys or secrets
- Validate all file paths for traversal attacks
- Sanitize voice command inputs
- Use secure API clients with SSL verification

## Documentation

- Update `FUNCTIONALITY.md` for new features
- Add architecture details to `ARCHITECTURE.md`
- Update `INSTALLATION.md` for new dependencies
- Add examples to `README.md` for major features

## Release Process

1. Update version in `main.py` and `setup.py`
2. Update `CHANGELOG.md` with new features
3. Run full test suite
4. Create release tag
5. Update PyPI package (if applicable)

## Getting Help

- Check existing issues for similar problems
- Review `TESTING_GUIDE.md` for testing patterns
- Look at recent commits for implementation examples
- Open discussion for design questions before major changes

## Design Philosophy

- **Terminal-first**: Built for developers who live in the terminal
- **Voice-optimized**: Natural language over rigid commands
- **Fallback-ready**: Always have a backup plan
- **Learning-capable**: Systems that improve with usage
- **Privacy-conscious**: Local processing by default