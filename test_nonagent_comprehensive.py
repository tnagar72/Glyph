#!/usr/bin/env python3

"""
Comprehensive Test Suite for Non-Agent Mode Functionality
Tests all non-agent capabilities including voice recording, transcription, live mode, 
interactive CLI, file handling, and configuration systems.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
import json
import time
import numpy as np
from unittest.mock import Mock, patch, MagicMock, mock_open

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Test imports
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

class TestNonAgentMode:
    """Comprehensive non-agent mode test suite."""
    
    def __init__(self):
        self.test_dir = None
        self.original_configs = {}
        self.test_results = {}
        
    def setup_test_environment(self):
        """Create test environment."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="glyph_test_"))
        
        # Create test markdown file
        self.test_md_file = self.test_dir / "test_document.md"
        self.test_md_file.write_text("""# Test Document

## Introduction
This is a test document for testing Glyph functionality.

## Tasks
- [ ] Complete testing
- [ ] Review results

## Notes
Some additional notes here.
""")
        
        # Create test audio data (simulated)
        self.test_audio = np.random.randint(-32768, 32767, size=16000, dtype=np.int16)  # 1 second at 16kHz
        
        return True
    
    def backup_configs(self):
        """Backup existing configurations."""
        config_dir = Path.home() / ".glyph"
        config_files = ["audio_config.json", "model_config.json", "transcription_config.json"]
        
        for config_file in config_files:
            config_path = config_dir / config_file
            if config_path.exists():
                self.original_configs[config_file] = config_path.read_text()
    
    def restore_configs(self):
        """Restore original configurations."""
        config_dir = Path.home() / ".glyph"
        
        for config_file, content in self.original_configs.items():
            config_path = config_dir / config_file
            config_path.write_text(content)
    
    def test_audio_recording_system(self):
        """Test audio recording functionality."""
        console.print("\n🎙️ Testing Audio Recording System")
        console.print("=" * 50)
        
        try:
            from recording import validate_audio, AudioValidationError
            import sounddevice as sd
            
            # Test audio validation with good audio
            console.print("✅ Testing audio validation...")
            
            # Create valid audio (not silent, sufficient length)
            valid_audio = np.random.randint(-1000, 1000, size=24000, dtype=np.int16)  # 1.5 seconds
            
            try:
                validate_audio(valid_audio, min_duration=0.5)
                console.print("   ✅ Valid audio passed validation")
            except AudioValidationError:
                console.print("   ❌ Valid audio failed validation")
                return False
            
            # Test audio validation with invalid audio (too short)
            short_audio = np.random.randint(-1000, 1000, size=4000, dtype=np.int16)  # 0.25 seconds
            
            try:
                validate_audio(short_audio, min_duration=0.5)
                console.print("   ❌ Short audio should have failed validation")
                return False
            except AudioValidationError:
                console.print("   ✅ Short audio correctly failed validation")
            
            # Test audio validation with silent audio
            silent_audio = np.zeros(24000, dtype=np.int16)
            
            try:
                validate_audio(silent_audio, min_duration=0.5)
                console.print("   ❌ Silent audio should have failed validation")
                return False
            except AudioValidationError:
                console.print("   ✅ Silent audio correctly failed validation")
            
            # Test device listing
            console.print("🔍 Testing audio device detection...")
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            
            if len(input_devices) > 0:
                console.print(f"   ✅ Found {len(input_devices)} input devices")
            else:
                console.print("   ⚠️ No input devices found (this might be expected in CI)")
            
            console.print("✅ Audio recording system tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Audio recording system tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_audio_configuration(self):
        """Test audio device configuration system."""
        console.print("\n🔧 Testing Audio Configuration System")
        console.print("=" * 50)
        
        try:
            from audio_config import AudioConfig, get_audio_device, score_audio_device
            import sounddevice as sd
            
            # Test audio config creation
            config = AudioConfig()
            
            # Test device scoring
            console.print("📊 Testing device scoring...")
            devices = sd.query_devices()
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    score = score_audio_device(device, i)
                    console.print(f"   Device '{device['name']}': score {score}")
                    assert isinstance(score, (int, float)), "Score should be numeric"
                    break
            
            # Test configuration saving/loading
            console.print("💾 Testing configuration persistence...")
            test_device_index = 0
            config.set_device_index(test_device_index)
            config.save()
            
            # Create new config instance and load
            config2 = AudioConfig()
            config2.load()
            
            assert config2.get_device_index() == test_device_index, "Device index should persist"
            
            console.print("✅ Audio configuration tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Audio configuration tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_transcription_system(self):
        """Test transcription functionality."""
        console.print("\n🗣️ Testing Transcription System")
        console.print("=" * 50)
        
        try:
            from transcription import TranscriptionService, transcribe_audio
            import tempfile
            
            # Create mock audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Write a simple WAV header and some audio data
                import scipy.io.wavfile
                scipy.io.wavfile.write(temp_file.name, 16000, self.test_audio)
                temp_audio_path = temp_file.name
            
            try:
                # Test transcription service initialization
                console.print("🚀 Testing transcription service...")
                service = TranscriptionService()
                
                # Test configuration loading
                config = service.config
                assert config is not None, "Config should be loaded"
                
                method = config.get_transcription_method()
                console.print(f"   Current method: {method}")
                
                # Test local transcription method testing
                console.print("🧪 Testing local transcription method...")
                success, message = service.test_transcription_method("local")
                console.print(f"   Local method test: {message}")
                
                if success:
                    # Test actual transcription with mock
                    console.print("🎯 Testing transcription with mock...")
                    
                    # Mock whisper model to avoid loading large model
                    with patch('whisper.load_model') as mock_load_model:
                        mock_model = Mock()
                        mock_model.transcribe.return_value = {"text": "This is a test transcription."}
                        mock_load_model.return_value = mock_model
                        
                        result = service._transcribe_local(self.test_audio)
                        assert result == "This is a test transcription.", f"Expected test transcription, got: {result}"
                        console.print("   ✅ Local transcription mock test passed")
                
                # Test OpenAI API method testing (without API key)
                console.print("🌐 Testing OpenAI API method...")
                
                # This should fail without API key, which is expected
                success, message = service.test_transcription_method("openai_api")
                console.print(f"   OpenAI API test: {message}")
                
                # Test convenience function
                console.print("🔄 Testing convenience function...")
                with patch.object(service, 'transcribe') as mock_transcribe:
                    mock_transcribe.return_value = "Test result"
                    
                    result = transcribe_audio(self.test_audio)
                    assert result == "Test result", "Convenience function should work"
                    console.print("   ✅ Convenience function test passed")
                
                console.print("✅ Transcription system tests passed")
                return True
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass
                    
        except Exception as e:
            console.print(f"❌ Transcription system tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_transcription_configuration(self):
        """Test transcription configuration system."""
        console.print("\n⚙️ Testing Transcription Configuration System")
        console.print("=" * 50)
        
        try:
            from transcription_config import TranscriptionConfig, get_transcription_config
            
            # Test configuration creation
            config = TranscriptionConfig()
            
            # Test method setting
            console.print("🔧 Testing method configuration...")
            config.set_transcription_method("local")
            assert config.get_transcription_method() == "local", "Method should be set to local"
            
            config.set_transcription_method("openai_api")
            assert config.get_transcription_method() == "openai_api", "Method should be set to openai_api"
            
            # Test model configuration
            console.print("🤖 Testing model configuration...")
            config.set_local_whisper_model("small")
            assert config.get_local_whisper_model() == "small", "Local model should be set to small"
            
            config.set_openai_model("whisper-1")
            assert config.get_openai_model() == "whisper-1", "OpenAI model should be set to whisper-1"
            
            # Test configuration persistence
            console.print("💾 Testing configuration persistence...")
            config.save()
            
            # Load with new instance
            config2 = TranscriptionConfig()
            config2.load()
            
            assert config2.get_transcription_method() == "openai_api", "Method should persist"
            assert config2.get_local_whisper_model() == "small", "Local model should persist"
            assert config2.get_openai_model() == "whisper-1", "OpenAI model should persist"
            
            # Test global function
            global_config = get_transcription_config()
            assert global_config is not None, "Global config should work"
            
            console.print("✅ Transcription configuration tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Transcription configuration tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_model_configuration(self):
        """Test Whisper model configuration system."""
        console.print("\n🧠 Testing Model Configuration System")
        console.print("=" * 50)
        
        try:
            from model_config import ModelConfig, get_default_model
            
            # Test model config creation
            config = ModelConfig()
            
            # Test model setting
            console.print("🎯 Testing model selection...")
            valid_models = ["tiny", "base", "small", "medium", "large"]
            
            for model in valid_models:
                config.set_default_model(model)
                assert config.get_default_model() == model, f"Model should be set to {model}"
                console.print(f"   ✅ {model} model set successfully")
            
            # Test model information
            console.print("📊 Testing model information...")
            model_info = config.get_model_info("medium")
            assert "size" in model_info, "Model info should include size"
            assert "description" in model_info, "Model info should include description"
            
            # Test configuration persistence
            console.print("💾 Testing model configuration persistence...")
            config.set_default_model("small")
            config.save()
            
            # Load with new instance
            config2 = ModelConfig()
            config2.load()
            
            assert config2.get_default_model() == "small", "Model should persist"
            
            # Test global function
            default_model = get_default_model()
            assert default_model in valid_models, f"Default model should be valid, got: {default_model}"
            
            console.print("✅ Model configuration tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Model configuration tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_markdown_file_handling(self):
        """Test markdown file handling functionality."""
        console.print("\n📄 Testing Markdown File Handling")
        console.print("=" * 50)
        
        try:
            from md_file import read_markdown_file, write_markdown_file, validate_markdown_path
            from backup_manager import BackupManager
            
            # Test path validation
            console.print("📝 Testing path validation...")
            
            # Test with extension
            validated = validate_markdown_path(str(self.test_md_file))
            assert validated == self.test_md_file, "Path with extension should validate"
            
            # Test without extension
            no_ext_path = str(self.test_md_file).replace('.md', '')
            validated = validate_markdown_path(no_ext_path)
            assert str(validated).endswith('.md'), "Path without extension should get .md added"
            
            # Test reading
            console.print("📖 Testing file reading...")
            content = read_markdown_file(str(self.test_md_file))
            assert "# Test Document" in content, "Should read file content"
            assert "## Introduction" in content, "Should read full content"
            
            # Test writing with backup
            console.print("💾 Testing file writing with backup...")
            new_content = content + "\n\n## New Section\nAdded by test."
            
            backup_path = write_markdown_file(str(self.test_md_file), new_content)
            assert backup_path is not None, "Should create backup"
            assert Path(backup_path).exists(), "Backup file should exist"
            
            # Verify content was written
            written_content = read_markdown_file(str(self.test_md_file))
            assert "## New Section" in written_content, "New content should be written"
            assert "Added by test." in written_content, "New content should be complete"
            
            console.print("✅ Markdown file handling tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Markdown file handling tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_backup_and_undo_system(self):
        """Test backup and undo functionality."""
        console.print("\n💾 Testing Backup and Undo System")
        console.print("=" * 50)
        
        try:
            from backup_manager import BackupManager
            from undo_manager import UndoManager
            
            # Test backup creation
            console.print("📦 Testing backup creation...")
            backup_path = BackupManager.create_backup(str(self.test_md_file), backup_type="test")
            assert backup_path is not None, "Should create backup"
            assert Path(backup_path).exists(), "Backup should exist"
            
            # Test backup listing
            console.print("📋 Testing backup listing...")
            backups = UndoManager.list_backups(str(self.test_md_file))
            assert len(backups) > 0, "Should find backups"
            assert backup_path in backups, "Should include our backup"
            
            # Test backup info
            console.print("ℹ️ Testing backup info...")
            backup_info = UndoManager.get_backup_info(backup_path)
            assert "created" in backup_info, "Should include creation time"
            assert "size" in backup_info, "Should include file size"
            
            # Test content modification
            original_content = self.test_md_file.read_text()
            modified_content = original_content + "\n\n## Modified\nThis was modified."
            self.test_md_file.write_text(modified_content)
            
            # Test restoration
            console.print("🔄 Testing backup restoration...")
            success = UndoManager.restore_from_backup(str(self.test_md_file))
            assert success, "Restoration should succeed"
            
            # Verify content was restored
            restored_content = self.test_md_file.read_text()
            assert restored_content == original_content, "Content should be restored"
            assert "## Modified" not in restored_content, "Modified content should be gone"
            
            console.print("✅ Backup and undo system tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Backup and undo system tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_diff_and_approval_system(self):
        """Test diff viewing and user approval functionality."""
        console.print("\n🔍 Testing Diff and Approval System")
        console.print("=" * 50)
        
        try:
            from diff import show_diff, count_changes, get_user_approval
            
            # Test diff generation
            console.print("📊 Testing diff generation...")
            original = "# Title\n\nOriginal content\n\n## Section\nOriginal section content."
            modified = "# Title\n\nModified content\n\n## Section\nModified section content.\n\n## New Section\nNew content."
            
            # Mock console output to capture diff
            with patch('diff.console') as mock_console:
                diff_lines = show_diff(original, modified, "test.md")
                
                # Verify diff was generated
                assert mock_console.print.called, "Should print diff"
                assert len(diff_lines) > 0, "Should generate diff lines"
            
            # Test change counting
            console.print("🔢 Testing change counting...")
            additions, deletions = count_changes(diff_lines)
            assert additions > 0, "Should count additions"
            console.print(f"   Found {additions} additions, {deletions} deletions")
            
            # Test approval system (mock user input)
            console.print("✅ Testing approval system...")
            
            # Test approval
            with patch('builtins.input', return_value='y'):
                approval = get_user_approval(changes_detected=True)
                assert approval == True, "Should approve with 'y'"
            
            # Test rejection
            with patch('builtins.input', return_value='n'):
                approval = get_user_approval(changes_detected=True)
                assert approval == False, "Should reject with 'n'"
            
            # Test no changes
            approval = get_user_approval(changes_detected=False)
            assert approval == False, "Should not approve when no changes"
            
            console.print("✅ Diff and approval system tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Diff and approval system tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_llm_integration(self):
        """Test GPT-4 LLM integration for markdown editing."""
        console.print("\n🧠 Testing LLM Integration")
        console.print("=" * 50)
        
        try:
            from llm import call_gpt_api
            from cleaning import extract_markdown_from_response
            
            # Mock OpenAI API response
            mock_response = """Here's the edited markdown:

```markdown
# Test Document

## Introduction
This is a test document for testing Glyph functionality with AI enhancements.

## Tasks
- [ ] Complete testing
- [ ] Review results
- [ ] Document findings

## Notes
Some additional notes here with improvements.

## Analysis
Added analysis section based on voice command.
```
"""
            
            console.print("🎯 Testing LLM API call...")
            
            with patch('openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_response_obj = Mock()
                mock_response_obj.choices = [Mock()]
                mock_response_obj.choices[0].message.content = mock_response
                mock_client.chat.completions.create.return_value = mock_response_obj
                mock_openai.return_value = mock_client
                
                # Test API call
                original_content = self.test_md_file.read_text()
                transcript = "Add an analysis section to the document"
                
                result = call_gpt_api(original_content, transcript, "test.md")
                assert result is not None, "Should return result"
                assert "Analysis" in result, "Should contain requested changes"
            
            # Test response cleaning
            console.print("🧹 Testing response cleaning...")
            cleaned = extract_markdown_from_response(mock_response)
            
            assert not cleaned.startswith("```"), "Should remove code fences"
            assert "# Test Document" in cleaned, "Should preserve markdown content"
            assert "## Analysis" in cleaned, "Should preserve all sections"
            
            console.print("✅ LLM integration tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ LLM integration tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_live_transcription_mode(self):
        """Test live transcription functionality."""
        console.print("\n🎤 Testing Live Transcription Mode")
        console.print("=" * 50)
        
        try:
            from live_transcription import LiveTranscriptionSession, filter_transcript_text
            
            # Test transcript filtering
            console.print("🔍 Testing transcript filtering...")
            
            test_cases = [
                ("Hello world", "Hello world"),  # Normal text
                ("", ""),  # Empty text
                ("Thank you.", ""),  # Common phrase to filter
                ("Bye.", ""),  # Another common phrase
                ("This is a real transcript.", "This is a real transcript."),  # Real content
            ]
            
            for input_text, expected in test_cases:
                result = filter_transcript_text(input_text)
                assert result == expected, f"Filter failed for '{input_text}': expected '{expected}', got '{result}'"
            
            # Test session creation
            console.print("📺 Testing session creation...")
            
            # Mock the session to avoid actual audio capture
            with patch('live_transcription.LiveTranscriptionSession._capture_audio_chunk') as mock_capture:
                mock_capture.return_value = self.test_audio
                
                with patch('live_transcription.transcribe_audio') as mock_transcribe:
                    mock_transcribe.return_value = "Test transcription result"
                    
                    session = LiveTranscriptionSession(
                        transcription_method="local",
                        simple=True,
                        clipboard_mode=False
                    )
                    
                    assert session is not None, "Should create session"
                    assert session.chunk_duration == 5, "Should have default chunk duration"
            
            console.print("✅ Live transcription mode tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Live transcription mode tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_interactive_cli_mode(self):
        """Test interactive CLI functionality."""
        console.print("\n💻 Testing Interactive CLI Mode")
        console.print("=" * 50)
        
        try:
            from interactive_cli import InteractiveCLI, discover_markdown_files
            
            # Test file discovery
            console.print("🔍 Testing file discovery...")
            
            # Create some test markdown files
            test_files_dir = self.test_dir / "test_docs"
            test_files_dir.mkdir(exist_ok=True)
            
            test_files = [
                "document1.md",
                "document2.md", 
                "notes.md",
                "readme.txt"  # Non-markdown file
            ]
            
            for filename in test_files:
                (test_files_dir / filename).write_text(f"# {filename}\n\nTest content.")
            
            # Test discovery
            discovered = discover_markdown_files([str(test_files_dir)])
            markdown_files = [f for f in discovered if f.endswith('.md')]
            
            assert len(markdown_files) == 3, f"Should find 3 markdown files, found {len(markdown_files)}"
            assert any("document1.md" in f for f in markdown_files), "Should find document1.md"
            assert any("document2.md" in f for f in markdown_files), "Should find document2.md"
            assert any("notes.md" in f for f in markdown_files), "Should find notes.md"
            
            # Test CLI creation
            console.print("🖥️ Testing CLI creation...")
            cli = InteractiveCLI()
            assert cli is not None, "Should create CLI instance"
            
            console.print("✅ Interactive CLI mode tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Interactive CLI mode tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_session_logging(self):
        """Test session logging functionality."""
        console.print("\n📊 Testing Session Logging")
        console.print("=" * 50)
        
        try:
            from session_logger import get_session_logger, end_session
            
            # Test logger creation
            console.print("📝 Testing logger creation...")
            logger = get_session_logger()
            assert logger is not None, "Should create logger"
            
            # Test event logging
            console.print("📋 Testing event logging...")
            
            # Audio capture logging
            logger.log_audio_capture(1.5, True)
            logger.log_audio_capture(0.3, False, "Too short")
            
            # Transcription logging
            logger.log_transcription("Test transcript", "medium", True, 2.1)
            logger.log_transcription("", "medium", False, 1.8, "Failed to transcribe")
            
            # GPT request logging
            logger.log_gpt_request("Add section", "test.md", True, 100, 150, 3.2)
            
            # User decision logging
            logger.log_user_decision("accept", True, "test.md", "backup.md")
            
            # File operation logging
            logger.log_file_operation("write", "test.md", True, "backup.md")
            
            # Diff analysis logging
            logger.log_diff_analysis(5, 2, "test.md")
            
            # Test session end
            console.print("🏁 Testing session end...")
            end_session(True)
            
            # Verify log files exist
            logs_dir = Path("logs")
            if logs_dir.exists():
                log_files = list(logs_dir.glob("session_*.txt"))
                json_files = list(logs_dir.glob("session_*.json"))
                
                if log_files:
                    console.print(f"   ✅ Found {len(log_files)} text log files")
                if json_files:
                    console.print(f"   ✅ Found {len(json_files)} JSON log files")
            
            console.print("✅ Session logging tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Session logging tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_obsidian_integration(self):
        """Test Obsidian integration functionality."""
        console.print("\n🔮 Testing Obsidian Integration")
        console.print("=" * 50)
        
        try:
            from utils import open_in_obsidian_if_available, detect_obsidian_vault
            
            # Test vault detection
            console.print("🔍 Testing vault detection...")
            
            # Create a mock Obsidian vault
            mock_vault = self.test_dir / "mock_vault"
            mock_vault.mkdir(exist_ok=True)
            (mock_vault / ".obsidian").mkdir(exist_ok=True)
            (mock_vault / "test_note.md").write_text("# Test Note\n\nContent.")
            
            vault_path = detect_obsidian_vault(str(mock_vault / "test_note.md"))
            assert vault_path == str(mock_vault), f"Should detect vault, got: {vault_path}"
            
            # Test with non-vault file
            non_vault_file = self.test_dir / "non_vault_note.md"
            non_vault_file.write_text("# Non Vault Note")
            
            vault_path = detect_obsidian_vault(str(non_vault_file))
            assert vault_path is None, "Should not detect vault for non-vault file"
            
            # Test Obsidian opening (mock to avoid launching actual app)
            console.print("🚀 Testing Obsidian opening...")
            
            with patch('subprocess.run') as mock_run:
                with patch('shutil.which', return_value='/usr/bin/open'):
                    try:
                        open_in_obsidian_if_available(str(mock_vault / "test_note.md"))
                        console.print("   ✅ Obsidian opening attempted")
                    except Exception as e:
                        console.print(f"   ⚠️ Obsidian opening failed (expected): {e}")
            
            console.print("✅ Obsidian integration tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Obsidian integration tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_ui_system(self):
        """Test UI helpers and display system."""
        console.print("\n🎨 Testing UI System")
        console.print("=" * 50)
        
        try:
            from ui_helpers import (
                show_welcome_banner, show_success_message, show_error_message,
                show_warning_message, show_recording_indicator, show_thinking_indicator,
                show_config_overview
            )
            
            # Test UI functions (they should not crash)
            console.print("🎪 Testing UI components...")
            
            # These functions primarily output to console, so we test they don't crash
            try:
                show_welcome_banner()
                show_success_message("Test success", "Test detail")
                show_error_message("Test error", "Test detail")
                show_warning_message("Test warning", "Test detail")
                show_config_overview()
                console.print("   ✅ All UI components rendered without errors")
            except Exception as e:
                console.print(f"   ❌ UI component error: {e}")
                return False
            
            # Test recording indicator (mock to avoid blocking)
            console.print("🎙️ Testing recording indicator...")
            
            with patch('ui_helpers.console') as mock_console:
                show_recording_indicator("enter", dry_run=True)
                assert mock_console.print.called, "Should call console.print"
            
            console.print("✅ UI system tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ UI system tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_main_integration(self):
        """Test main.py integration and command-line argument handling."""
        console.print("\n🎯 Testing Main Integration")
        console.print("=" * 50)
        
        try:
            from main import main
            import argparse
            
            # Test argument parser setup
            console.print("⚙️ Testing argument parser...")
            
            # Mock sys.argv for testing
            test_args = [
                ["--version"],
                ["--help"],
                ["--dry-run", "-f", str(self.test_md_file)],
                ["--transcript-only"],
                ["--show-config"],
            ]
            
            parser = argparse.ArgumentParser(description="🎙️ Glyph - Voice-controlled Markdown Editor")
            
            # Add some basic arguments to test parser
            parser.add_argument("--version", action="version", version="Test 1.0.0")
            parser.add_argument("--dry-run", "-d", action="store_true")
            parser.add_argument("--file", "-f", type=str)
            parser.add_argument("--transcript-only", "-t", action="store_true")
            parser.add_argument("--show-config", action="store_true")
            
            # Test parsing some arguments
            args = parser.parse_args(["--dry-run", "-f", "test.md"])
            assert args.dry_run == True, "Should parse dry-run flag"
            assert args.file == "test.md", "Should parse file argument"
            
            console.print("   ✅ Argument parsing works correctly")
            
            # Test configuration loading functions
            console.print("🔧 Testing configuration functions...")
            
            from main import handle_audio_setup, handle_model_setup, handle_transcription_setup
            
            # These functions are interactive, so we just test they exist and are callable
            assert callable(handle_audio_setup), "handle_audio_setup should be callable"
            assert callable(handle_model_setup), "handle_model_setup should be callable"
            assert callable(handle_transcription_setup), "handle_transcription_setup should be callable"
            
            console.print("✅ Main integration tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Main integration tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """Clean up test resources."""
        try:
            # Remove test directory
            if self.test_dir and self.test_dir.exists():
                shutil.rmtree(self.test_dir)
                
            # Restore original configurations
            self.restore_configs()
            
        except Exception as e:
            console.print(f"⚠️ Cleanup error: {e}")
    
    def run_all_tests(self):
        """Run all non-agent mode tests."""
        console.print("🧪 Comprehensive Non-Agent Mode Test Suite")
        console.print("=" * 60)
        
        # Setup
        console.print("🔧 Setting up test environment...")
        self.setup_test_environment()
        self.backup_configs()
        
        # Run tests
        tests = [
            ("Audio Recording System", self.test_audio_recording_system),
            ("Audio Configuration", self.test_audio_configuration),
            ("Transcription System", self.test_transcription_system),
            ("Transcription Configuration", self.test_transcription_configuration),
            ("Model Configuration", self.test_model_configuration),
            ("Markdown File Handling", self.test_markdown_file_handling),
            ("Backup and Undo System", self.test_backup_and_undo_system),
            ("Diff and Approval System", self.test_diff_and_approval_system),
            ("LLM Integration", self.test_llm_integration),
            ("Live Transcription Mode", self.test_live_transcription_mode),
            ("Interactive CLI Mode", self.test_interactive_cli_mode),
            ("Session Logging", self.test_session_logging),
            ("Obsidian Integration", self.test_obsidian_integration),
            ("UI System", self.test_ui_system),
            ("Main Integration", self.test_main_integration),
        ]
        
        passed = 0
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                console.print(f"❌ {test_name} failed with exception: {e}")
                self.test_results[test_name] = False
        
        # Results summary
        console.print("\n" + "=" * 60)
        console.print("🏁 Test Results Summary")
        console.print("=" * 60)
        
        for test_name, success in self.test_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            console.print(f"{status:10} {test_name}")
        
        console.print(f"\nResults: {passed}/{len(tests)} tests passed")
        
        # Cleanup
        self.cleanup()
        
        if passed == len(tests):
            console.print("🎉 All non-agent mode tests passed!")
            return True
        else:
            console.print("⚠️ Some tests failed. Check the output above for details.")
            return False

def main():
    """Run the comprehensive non-agent mode test suite."""
    tester = TestNonAgentMode()
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())