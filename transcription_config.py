#!/usr/bin/env python3

"""
Transcription Configuration Module for Glyph.
Manages configuration for local Whisper vs OpenAI API transcription.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Literal
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box

from ui_helpers import (
    GLYPH_PRIMARY, GLYPH_SUCCESS, GLYPH_ERROR, GLYPH_WARNING, 
    GLYPH_HIGHLIGHT, GLYPH_MUTED, show_success_message, show_error_message
)

console = Console()

# Configuration file path
CONFIG_DIR = Path.home() / ".glyph"
TRANSCRIPTION_CONFIG_FILE = CONFIG_DIR / "transcription_config.json"

# Transcription method types
TranscriptionMethod = Literal["local", "openai_api"]

# Default configuration
DEFAULT_CONFIG = {
    "transcription_method": "local",
    "local_whisper": {
        "model": "medium",
        "language": "auto"
    },
    "openai_api": {
        "model": "whisper-1",
        "language": "auto",
        "api_key_set": False
    }
}

class TranscriptionConfig:
    """Manages transcription configuration settings."""
    
    def __init__(self):
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        try:
            if TRANSCRIPTION_CONFIG_FILE.exists():
                with open(TRANSCRIPTION_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to handle new settings
                return self._merge_config(DEFAULT_CONFIG, config)
            else:
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            console.print(f"[{GLYPH_WARNING}]⚠️ Could not load transcription config: {e}[/{GLYPH_WARNING}]")
            return DEFAULT_CONFIG.copy()
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults to handle missing keys."""
        result = default.copy()
        for key, value in user.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self) -> bool:
        """Save configuration to file."""
        try:
            CONFIG_DIR.mkdir(exist_ok=True)
            with open(TRANSCRIPTION_CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            console.print(f"[{GLYPH_ERROR}]❌ Could not save transcription config: {e}[/{GLYPH_ERROR}]")
            return False
    
    def get_transcription_method(self) -> TranscriptionMethod:
        """Get the current transcription method."""
        return self.config.get("transcription_method", "local")
    
    def set_transcription_method(self, method: TranscriptionMethod) -> bool:
        """Set the transcription method."""
        if method not in ["local", "openai_api"]:
            raise ValueError(f"Invalid transcription method: {method}")
        
        self.config["transcription_method"] = method
        return self._save_config()
    
    def get_local_whisper_model(self) -> str:
        """Get the local Whisper model."""
        return self.config["local_whisper"].get("model", "medium")
    
    def set_local_whisper_model(self, model: str) -> bool:
        """Set the local Whisper model."""
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if model not in valid_models:
            raise ValueError(f"Invalid model: {model}. Must be one of {valid_models}")
        
        self.config["local_whisper"]["model"] = model
        return self._save_config()
    
    def get_openai_model(self) -> str:
        """Get the OpenAI API model."""
        return self.config["openai_api"].get("model", "whisper-1")
    
    def set_openai_model(self, model: str) -> bool:
        """Set the OpenAI API model."""
        # OpenAI currently only supports whisper-1
        valid_models = ["whisper-1"]
        if model not in valid_models:
            raise ValueError(f"Invalid OpenAI model: {model}. Must be one of {valid_models}")
        
        self.config["openai_api"]["model"] = model
        return self._save_config()
    
    def is_openai_api_key_set(self) -> bool:
        """Check if OpenAI API key is configured."""
        # Check environment variable
        if os.getenv("OPENAI_API_KEY"):
            return True
        # Check stored flag (not the actual key for security)
        return self.config["openai_api"].get("api_key_set", False)
    
    def set_openai_api_key_status(self, is_set: bool) -> bool:
        """Set the OpenAI API key status flag."""
        self.config["openai_api"]["api_key_set"] = is_set
        return self._save_config()
    
    def get_language(self, method: Optional[TranscriptionMethod] = None) -> str:
        """Get the language setting for the specified method."""
        if method is None:
            method = self.get_transcription_method()
        
        if method == "local":
            return self.config["local_whisper"].get("language", "auto")
        else:
            return self.config["openai_api"].get("language", "auto")
    
    def set_language(self, language: str, method: Optional[TranscriptionMethod] = None) -> bool:
        """Set the language for the specified method."""
        if method is None:
            method = self.get_transcription_method()
        
        if method == "local":
            self.config["local_whisper"]["language"] = language
        else:
            self.config["openai_api"]["language"] = language
        
        return self._save_config()

def setup_transcription_method() -> Optional[TranscriptionMethod]:
    """Interactive setup for transcription method."""
    config = TranscriptionConfig()
    
    # Show current configuration
    show_current_transcription_config()
    
    # Method selection
    header = Text()
    header.append("◈ ", style=f"bold {GLYPH_PRIMARY}")
    header.append("Choose Transcription Method", style="bold white")
    header.append(" ◈", style=f"bold {GLYPH_PRIMARY}")
    
    panel = Panel(header, style=GLYPH_PRIMARY, box=box.HEAVY)
    console.print(panel)
    
    methods_table = Table(show_header=True, box=box.HEAVY, border_style=GLYPH_PRIMARY)
    methods_table.add_column("Option", style=f"bold {GLYPH_HIGHLIGHT}", width=6)
    methods_table.add_column("Method", style="bold white", width=15)
    methods_table.add_column("Description", style=GLYPH_MUTED, width=50)
    methods_table.add_column("Pros", style=GLYPH_SUCCESS, width=25)
    methods_table.add_column("Cons", style=GLYPH_ERROR, width=25)
    
    methods_table.add_row(
        "1", "Local Whisper", 
        "Use local OpenAI Whisper model",
        "• Free\n• Private\n• Works offline",
        "• Slower\n• Uses more CPU/RAM"
    )
    
    methods_table.add_row(
        "2", "OpenAI API", 
        "Use OpenAI's speech-to-text API",
        "• Faster\n• More accurate\n• Less resource usage",
        "• Requires API key\n• Costs money\n• Needs internet"
    )
    
    console.print(methods_table)
    
    choice = Prompt.ask(
        f"[bold {GLYPH_PRIMARY}]Select transcription method[/bold {GLYPH_PRIMARY}]",
        choices=["1", "2"],
        default="1"
    )
    
    if choice == "1":
        method = "local"
        # Configure local Whisper model
        model = setup_local_whisper_model()
        if model:
            config.set_local_whisper_model(model)
    else:
        method = "openai_api"
        # Configure OpenAI API
        api_configured = setup_openai_api()
        if not api_configured:
            show_error_message(
                "❌ OpenAI API configuration failed",
                "Falling back to local Whisper method"
            )
            method = "local"
    
    # Save the method
    success = config.set_transcription_method(method)
    if success:
        show_success_message(
            f"✅ Transcription method set to: {method}",
            "You can change this anytime with 'glyph --setup-transcription'"
        )
        return method
    else:
        show_error_message("❌ Failed to save transcription configuration")
        return None

def setup_local_whisper_model() -> Optional[str]:
    """Setup local Whisper model selection."""
    models = ["tiny", "base", "small", "medium", "large"]
    model_info = {
        "tiny": ("39 MB", "~32x", "Lower"),
        "base": ("74 MB", "~16x", "Basic"),
        "small": ("244 MB", "~6x", "Good"),
        "medium": ("769 MB", "~2x", "Better"),
        "large": ("1550 MB", "~1x", "Best")
    }
    
    console.print(f"\n🎯 [bold {GLYPH_PRIMARY}]Local Whisper Model Selection[/bold {GLYPH_PRIMARY}]")
    
    model_table = Table(show_header=True, box=box.HEAVY, border_style=GLYPH_PRIMARY)
    model_table.add_column("Option", style=f"bold {GLYPH_HIGHLIGHT}", width=6)
    model_table.add_column("Model", style="bold white", width=8)
    model_table.add_column("Size", style=GLYPH_WARNING, width=8)
    model_table.add_column("Speed", style=GLYPH_SUCCESS, width=8)
    model_table.add_column("Accuracy", style=GLYPH_HIGHLIGHT, width=10)
    
    for i, model in enumerate(models, 1):
        size, speed, accuracy = model_info[model]
        model_table.add_row(str(i), model, size, speed, accuracy)
    
    console.print(model_table)
    
    choice = Prompt.ask(
        f"[bold {GLYPH_PRIMARY}]Select Whisper model[/bold {GLYPH_PRIMARY}]",
        choices=[str(i) for i in range(1, len(models) + 1)],
        default="4"  # medium
    )
    
    return models[int(choice) - 1]

def setup_openai_api() -> bool:
    """Setup OpenAI API configuration."""
    console.print(f"\n🔑 [bold {GLYPH_PRIMARY}]OpenAI API Configuration[/bold {GLYPH_PRIMARY}]")
    
    # Check if API key is already set
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        console.print(f"✅ OpenAI API key found in environment variable")
        config = TranscriptionConfig()
        config.set_openai_api_key_status(True)
        return True
    
    # Guide user to set up API key
    setup_text = Text()
    setup_text.append("To use OpenAI API transcription, you need to:\n\n", style="white")
    setup_text.append("1. ", style=f"bold {GLYPH_HIGHLIGHT}")
    setup_text.append("Get an API key from: ", style="white")
    setup_text.append("https://platform.openai.com/api-keys\n", style=f"bold {GLYPH_SUCCESS}")
    setup_text.append("2. ", style=f"bold {GLYPH_HIGHLIGHT}")
    setup_text.append("Set the environment variable:\n", style="white")
    setup_text.append("   export OPENAI_API_KEY='your-api-key-here'\n\n", style=f"bold {GLYPH_WARNING}")
    setup_text.append("3. ", style=f"bold {GLYPH_HIGHLIGHT}")
    setup_text.append("Or add it to your shell profile (.bashrc, .zshrc, etc.)", style="white")
    
    setup_panel = Panel(
        setup_text,
        title="◈ API Key Setup ◈",
        title_align="center",
        style=GLYPH_PRIMARY,
        box=box.HEAVY
    )
    console.print(setup_panel)
    
    # Ask if they want to continue
    has_key = Confirm.ask(
        f"[bold {GLYPH_PRIMARY}]Have you set the OPENAI_API_KEY environment variable?[/bold {GLYPH_PRIMARY}]",
        default=False
    )
    
    if has_key:
        # Re-check for the API key
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            config = TranscriptionConfig()
            config.set_openai_api_key_status(True)
            show_success_message("✅ OpenAI API key detected!")
            return True
        else:
            show_error_message(
                "❌ API key not found",
                "Please set the OPENAI_API_KEY environment variable and restart"
            )
            return False
    else:
        console.print(f"[{GLYPH_MUTED}]You can set up the API key later and run 'glyph --setup-transcription' again[/{GLYPH_MUTED}]")
        return False

def show_current_transcription_config():
    """Display current transcription configuration."""
    config = TranscriptionConfig()
    
    header = Text()
    header.append("◈ ", style=f"bold {GLYPH_PRIMARY}")
    header.append("Current Transcription Configuration", style="bold white")
    header.append(" ◈", style=f"bold {GLYPH_PRIMARY}")
    
    # Configuration table
    config_table = Table(show_header=True, box=box.HEAVY, border_style=GLYPH_PRIMARY)
    config_table.add_column("Setting", style=f"bold {GLYPH_HIGHLIGHT}", width=20)
    config_table.add_column("Value", style="bold white", width=20)
    config_table.add_column("Status", style=GLYPH_SUCCESS, width=15)
    
    # Current method
    current_method = config.get_transcription_method()
    method_display = "Local Whisper" if current_method == "local" else "OpenAI API"
    config_table.add_row("Method", method_display, "✅ Active")
    
    # Local Whisper settings
    local_model = config.get_local_whisper_model()
    local_status = "✅ Active" if current_method == "local" else "⏸️ Available"
    config_table.add_row("Local Model", local_model, local_status)
    
    # OpenAI API settings
    openai_model = config.get_openai_model()
    api_key_set = config.is_openai_api_key_set()
    
    if current_method == "openai_api":
        api_status = "✅ Active" if api_key_set else "❌ No API Key"
    else:
        api_status = "✅ Available" if api_key_set else "❌ No API Key"
    
    config_table.add_row("OpenAI Model", openai_model, api_status)
    
    # Language settings
    language = config.get_language()
    config_table.add_row("Language", language, "🌍 Global")
    
    # Print header
    header_panel = Panel(
        header,
        style=GLYPH_PRIMARY,
        box=box.HEAVY,
        title="◈ Transcription Config ◈",
        title_align="center"
    )
    console.print(header_panel)
    console.print()
    
    # Print config table
    console.print(config_table)

def get_transcription_config() -> TranscriptionConfig:
    """Get the current transcription configuration instance."""
    return TranscriptionConfig()

if __name__ == "__main__":
    # Test the configuration system
    show_current_transcription_config()
    method = setup_transcription_method()
    if method:
        console.print(f"✅ Configuration complete: {method}")