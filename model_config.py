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