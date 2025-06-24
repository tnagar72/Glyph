#!/usr/bin/env python3
"""
Basic tests for voice markdown editor functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path

# Import modules to test
from md_file import read_markdown_file, write_markdown_file, validate_markdown_path
from utils import SAMPLE_RATE, CHANNELS, WHISPER_MODEL
from cleaning import extract_markdown_from_response


class TestMarkdownFile:
    """Test markdown file operations."""
    
    def test_validate_markdown_path_valid(self):
        """Test validation of valid markdown file paths."""
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp:
            tmp.write(b"# Test\nContent")
            tmp_path = tmp.name
        
        try:
            validated = validate_markdown_path(tmp_path)
            assert validated.exists()
            assert validated.suffix == '.md'
        finally:
            os.unlink(tmp_path)
    
    def test_validate_markdown_path_invalid(self):
        """Test validation rejects non-markdown files."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b"Not markdown")
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValueError):
                validate_markdown_path(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_read_write_markdown_file(self):
        """Test reading and writing markdown files."""
        test_content = "# Test File\n\n- Item 1\n- Item 2\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
            tmp.write(test_content)
            tmp_path = tmp.name
        
        try:
            # Test reading
            content = read_markdown_file(tmp_path)
            assert content == test_content
            
            # Test writing
            new_content = "# Updated\n\n- New item\n"
            backup_path = write_markdown_file(tmp_path, new_content)
            
            # Verify write
            updated_content = read_markdown_file(tmp_path)
            assert updated_content == new_content
            
            # Verify backup exists
            assert backup_path is not None
            assert os.path.exists(backup_path)
            
        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            if 'backup_path' in locals() and backup_path and os.path.exists(backup_path):
                os.unlink(backup_path)


class TestCleaning:
    """Test response cleaning functionality."""
    
    def test_extract_markdown_simple(self):
        """Test extracting markdown from simple response."""
        response = "Here's the updated markdown:\n\n# Title\n\n- Item 1\n- Item 2"
        result = extract_markdown_from_response(response)
        assert "# Title" in result
        assert "- Item 1" in result
    
    def test_extract_markdown_with_code_blocks(self):
        """Test extracting markdown from response with code blocks."""
        response = """Here's your updated file:

```markdown
# Updated Title

## Section
- Task 1
- Task 2
```

The changes look good!"""
        
        result = extract_markdown_from_response(response)
        assert "# Updated Title" in result
        assert "- Task 1" in result
        assert "The changes look good!" not in result


class TestUtils:
    """Test utility functions and constants."""
    
    def test_constants_valid(self):
        """Test that utility constants are valid."""
        assert SAMPLE_RATE > 0
        assert CHANNELS in [1, 2]  # Mono or stereo
        assert WHISPER_MODEL in ["tiny", "base", "small", "medium", "large"]
    
    def test_sample_rate_reasonable(self):
        """Test that sample rate is reasonable for audio."""
        assert SAMPLE_RATE >= 16000  # Minimum for decent quality
        assert SAMPLE_RATE <= 48000  # Maximum reasonable for this use case


class TestImports:
    """Test that all modules can be imported."""
    
    def test_core_imports(self):
        """Test importing core modules."""
        import main
        import recording
        import transcription
        import llm
        import utils
        
        # Check version is available
        assert hasattr(main, '__version__')
        assert isinstance(main.__version__, str)
    
    def test_ui_imports(self):
        """Test importing UI modules."""
        import interactive_cli
        import live_transcription
        import diff
        
        # Basic functionality check
        assert hasattr(interactive_cli, 'InteractiveCLI')
        assert hasattr(live_transcription, 'LiveTranscriber')
    
    def test_data_imports(self):
        """Test importing data handling modules."""
        import session_logger
        import undo_manager
        import md_file
        
        # Check key classes exist
        assert hasattr(undo_manager, 'UndoManager')


class TestCLI:
    """Test command-line interface."""
    
    def test_help_output(self):
        """Test that help can be displayed."""
        import subprocess
        result = subprocess.run(['python', 'main.py', '--help'], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert "Voice-controlled Markdown Editor" in result.stdout
    
    def test_version_output(self):
        """Test that version can be displayed."""
        import subprocess
        result = subprocess.run(['python', 'main.py', '--version'], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert "Voice Markdown Editor" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])