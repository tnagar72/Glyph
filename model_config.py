"""
Smart Whisper model configuration and management for Glyph.

This module provides intelligent model selection, configuration, and management
that allows users to set their preferred default model.
"""

import os
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt
from typing import Optional, Dict, List

console = Console()

class ModelManager:
    """Manages Whisper model configuration and persistence."""
    
    def __init__(self):
        self.config_dir = Path.home() / '.glyph'
        self.config_file = self.config_dir / 'model_config.json'
        self.config_dir.mkdir(exist_ok=True)
        
        self.available_models = {
            'tiny': {
                'size': '39MB',
                'speed': 'Fastest',
                'accuracy': 'Basic',
                'description': 'Ultra-fast for testing and demos',
                'use_case': 'Quick testing, real-time demos'
            },
            'base': {
                'size': '74MB', 
                'speed': 'Fast',
                'accuracy': 'Good',
                'description': 'Good balance for simple commands',
                'use_case': 'Simple voice commands, development'
            },
            'small': {
                'size': '244MB',
                'speed': 'Medium', 
                'accuracy': 'Better',
                'description': 'Balanced performance and accuracy',
                'use_case': 'General purpose, balanced use'
            },
            'medium': {
                'size': '769MB',
                'speed': 'Slow',
                'accuracy': 'High', 
                'description': 'High accuracy for production use',
                'use_case': 'Production, complex commands (default)'
            },
            'large': {
                'size': '1550MB',
                'speed': 'Slowest',
                'accuracy': 'Highest',
                'description': 'Maximum accuracy for critical applications',
                'use_case': 'Maximum accuracy, batch processing'
            }
        }
        
    def save_model_config(self, model: str) -> None:
        """Save the selected model to configuration file."""
        config = {
            'default_model': model,
            'configured_at': str(Path.cwd()),
            'version': '1.0.0'
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            console.print(f"✅ [green]Model configuration saved: {model}[/green]")
        except Exception as e:
            console.print(f"❌ [red]Failed to save model config: {e}[/red]")
    
    def load_model_config(self) -> Optional[str]:
        """Load the configured default model."""
        if not self.config_file.exists():
            return None
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config.get('default_model')
        except Exception as e:
            console.print(f"⚠️ [yellow]Could not load model config: {e}[/yellow]")
            return None
    
    def show_model_selection_table(self) -> None:
        """Display a beautiful table of available models."""
        table = Table(title="🤖 Available Whisper Models", show_header=True, header_style="bold magenta")
        
        table.add_column("Option", style="cyan", justify="center", width=6)
        table.add_column("Model", style="bold white", width=8)
        table.add_column("Size", style="blue", justify="center", width=8)
        table.add_column("Speed", style="green", justify="center", width=10)
        table.add_column("Accuracy", style="yellow", justify="center", width=12)
        table.add_column("Best Use Case", style="dim white", width=25)
        table.add_column("Current", style="bold green", justify="center", width=8)
        
        current_model = self.load_model_config()
        
        for i, (model, info) in enumerate(self.available_models.items(), 1):
            is_current = "✓" if model == current_model else ""
            is_default = " (default)" if model == "medium" else ""
            
            table.add_row(
                str(i),
                f"{model}{is_default}",
                info['size'],
                info['speed'],
                info['accuracy'],
                info['use_case'],
                is_current
            )
        
        console.print(table)
    
    def show_model_selection_wizard(self) -> Optional[str]:
        """Interactive wizard for selecting default Whisper model."""
        
        # Header
        header_panel = Panel(
            "[bold cyan]🤖 Glyph Model Configuration Wizard[/bold cyan]\n\n"
            "Choose your preferred default Whisper model for voice transcription.\n"
            "This will be used when no specific model is specified in commands.\n\n"
            "[dim]You can always override this with --whisper-model flag[/dim]",
            title="Model Setup",
            border_style="cyan"
        )
        console.print(header_panel)
        console.print()
        
        # Show available models
        self.show_model_selection_table()
        console.print()
        
        # Model selection
        try:
            choice = IntPrompt.ask(
                "Select your preferred default model",
                choices=[str(i) for i in range(1, len(self.available_models) + 1)],
                default="4"  # medium is default
            )
            
            model_names = list(self.available_models.keys())
            selected_model = model_names[choice - 1]
            
            # Show selection details
            model_info = self.available_models[selected_model]
            details_panel = Panel(
                f"[bold white]Selected Model: {selected_model}[/bold white]\n\n"
                f"📦 Size: {model_info['size']}\n"
                f"⚡ Speed: {model_info['speed']}\n"
                f"🎯 Accuracy: {model_info['accuracy']}\n"
                f"💡 Description: {model_info['description']}\n\n"
                f"[dim]Use case: {model_info['use_case']}[/dim]",
                title="Model Details",
                border_style="green"
            )
            console.print(details_panel)
            console.print()
            
            # Confirmation
            if Confirm.ask(f"Set '{selected_model}' as your default model?", default=True):
                self.save_model_config(selected_model)
                return selected_model
            else:
                console.print("❌ [yellow]Model configuration cancelled[/yellow]")
                return None
                
        except KeyboardInterrupt:
            console.print("\n❌ [yellow]Model configuration cancelled[/yellow]")
            return None
        except Exception as e:
            console.print(f"❌ [red]Error during model selection: {e}[/red]")
            return None

def get_default_model() -> str:
    """Get the configured default model or fallback to medium."""
    manager = ModelManager()
    configured_model = manager.load_model_config()
    
    if configured_model:
        console.print(f"✅ Using configured default model: {configured_model}")
        return configured_model
    else:
        # Fallback to medium model
        return "medium"

def setup_default_model() -> Optional[str]:
    """Run the model configuration wizard."""
    manager = ModelManager()
    return manager.show_model_selection_wizard()

def show_current_model_config() -> None:
    """Display current model configuration."""
    manager = ModelManager()
    current_model = manager.load_model_config()
    
    if current_model:
        model_info = manager.available_models.get(current_model, {})
        panel = Panel(
            f"[bold green]Current Default Model: {current_model}[/bold green]\n\n"
            f"📦 Size: {model_info.get('size', 'Unknown')}\n"
            f"⚡ Speed: {model_info.get('speed', 'Unknown')}\n"
            f"🎯 Accuracy: {model_info.get('accuracy', 'Unknown')}\n\n"
            f"[dim]Run 'glyph --setup-model' to change[/dim]",
            title="Model Configuration",
            border_style="green"
        )
        console.print(panel)
    else:
        panel = Panel(
            "[yellow]No default model configured[/yellow]\n\n"
            f"Using fallback: medium model\n\n"
            f"[dim]Run 'glyph --setup-model' to configure[/dim]",
            title="Model Configuration", 
            border_style="yellow"
        )
        console.print(panel)

def show_all_configurations() -> None:
    """Display all current Glyph configurations and defaults."""
    from pathlib import Path
    import platform
    import sounddevice as sd
    from utils import WHISPER_MODEL, SAMPLE_RATE, CHANNELS, DURATION_LIMIT, DEVICE_INDEX
    from audio_config import audio_manager
    
    console.print("\n[bold cyan]🔧 Glyph Configuration Overview[/bold cyan]\n")
    
    # === Model Configuration ===
    manager = ModelManager()
    current_model = manager.load_model_config()
    
    model_panel = Panel(
        f"[bold white]🤖 Whisper Model Configuration[/bold white]\n\n"
        f"📁 Config Directory: [cyan]{manager.config_dir}[/cyan]\n"
        f"📄 Config File: [cyan]{manager.config_file}[/cyan]\n"
        f"✅ Config Exists: [green]{'Yes' if manager.config_file.exists() else 'No'}[/green]\n\n"
        f"🎯 Current Model: [bold green]{current_model or 'Not configured'}[/bold green]\n"
        f"🔄 Fallback Model: [yellow]{WHISPER_MODEL}[/yellow]\n"
        f"📊 Available Models: [dim]{', '.join(manager.available_models.keys())}[/dim]",
        title="Model Settings",
        border_style="blue"
    )
    console.print(model_panel)
    
    # === Audio Configuration ===
    audio_config = audio_manager.load_saved_config()
    
    try:
        devices = sd.query_devices()
        current_audio_device = audio_config['device_id'] if audio_config else None
        current_device_name = audio_config['device_name'] if audio_config else "Not configured"
        device_exists = (current_audio_device is not None and 
                        current_audio_device < len(devices) and 
                        devices[current_audio_device]['max_input_channels'] >= 1)
    except Exception:
        device_exists = False
        current_device_name = "Error detecting devices"
    
    audio_panel = Panel(
        f"[bold white]🎙️ Audio Device Configuration[/bold white]\n\n"
        f"📁 Config Directory: [cyan]{audio_manager.config_dir}[/cyan]\n"
        f"📄 Config File: [cyan]{audio_manager.config_file}[/cyan]\n"
        f"✅ Config Exists: [green]{'Yes' if audio_manager.config_file.exists() else 'No'}[/green]\n\n"
        f"🎤 Current Device: [bold green]{current_device_name}[/bold green]\n"
        f"🔢 Device ID: [yellow]{current_audio_device if current_audio_device is not None else 'Not set'}[/yellow]\n"
        f"✅ Device Available: [green]{'Yes' if device_exists else 'No'}[/green]\n"
        f"🔄 Fallback Device: [yellow]{DEVICE_INDEX}[/yellow]",
        title="Audio Settings",
        border_style="magenta"
    )
    console.print(audio_panel)
    
    # === Audio Parameters ===
    audio_params_panel = Panel(
        f"[bold white]🔊 Audio Parameters[/bold white]\n\n"
        f"📊 Sample Rate: [cyan]{SAMPLE_RATE} Hz[/cyan]\n"
        f"🎵 Channels: [cyan]{CHANNELS}[/cyan]\n"
        f"⏱️ Duration Limit: [cyan]{DURATION_LIMIT} seconds[/cyan]\n"
        f"💾 Format: [cyan]16-bit PCM[/cyan]",
        title="Audio Processing",
        border_style="green"
    )
    console.print(audio_params_panel)
    
    # === System Information ===
    system_panel = Panel(
        f"[bold white]💻 System Information[/bold white]\n\n"
        f"🖥️ Platform: [cyan]{platform.system()}[/cyan]\n"
        f"📦 Platform Release: [cyan]{platform.release()}[/cyan]\n"
        f"🏠 Home Directory: [cyan]{Path.home()}[/cyan]\n"
        f"📂 Working Directory: [cyan]{Path.cwd()}[/cyan]\n"
        f"🔧 Glyph Config Dir: [cyan]{manager.config_dir}[/cyan]",
        title="System Info",
        border_style="yellow"
    )
    console.print(system_panel)
    
    # === Application Settings ===
    from utils import VERBOSE_MODE
    
    app_panel = Panel(
        f"[bold white]⚙️ Application Settings[/bold white]\n\n"
        f"🔍 Verbose Mode: [cyan]{'Enabled' if VERBOSE_MODE else 'Disabled'}[/cyan]\n"
        f"🎨 Rich Console Width: [cyan]120 chars[/cyan]\n"
        f"📝 Logging: [cyan]Session-based[/cyan]\n"
        f"💾 Backup System: [cyan]Enabled[/cyan]",
        title="App Configuration",
        border_style="cyan"
    )
    console.print(app_panel)
    
    # === Configuration Commands ===
    commands_panel = Panel(
        f"[bold white]🛠️ Configuration Commands[/bold white]\n\n"
        f"🤖 Setup Model: [cyan]glyph --setup-model[/cyan]\n"
        f"🎙️ Setup Audio: [cyan]glyph --setup-audio[/cyan]\n"
        f"🔍 Show Config: [cyan]glyph --show-config[/cyan]\n"
        f"📋 Interactive Mode: [cyan]glyph --interactive[/cyan]\n"
        f"🔄 Live Mode: [cyan]glyph --live[/cyan]",
        title="Configuration Options",
        border_style="white"
    )
    console.print(commands_panel)
    
    console.print("\n[dim]💡 Tip: Use --setup-model or --setup-audio to configure specific components[/dim]\n")