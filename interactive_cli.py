#!/usr/bin/env python3

"""
Interactive CLI mode for Glyph.
Provides rich menus for file selection, model configuration, and options.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box

from md_file import validate_markdown_path
from utils import WHISPER_MODEL, verbose_print
from ui_helpers import (
    GLYPH_PRIMARY, GLYPH_SECONDARY, GLYPH_ACCENT, GLYPH_HIGHLIGHT,
    GLYPH_SUCCESS, GLYPH_ERROR, GLYPH_WARNING, GLYPH_MUTED, GLYPH_VOICE
)

console = Console()

class InteractiveCLI:
    """Interactive command-line interface for voice markdown editing."""
    
    def __init__(self):
        self.settings = {
            'file': None,
            'whisper_model': WHISPER_MODEL,
            'dry_run': False,
            'verbose': False,
            'transcript_only': False,
            'no_obsidian': False,
            'transcription_method': None
        }
    
    def show_banner(self):
        """Display the application banner with Glyph styling."""
        banner_text = Text()
        banner_text.append("◈ ", style=f"bold {GLYPH_ACCENT}")
        banner_text.append("Glyph", style=f"bold {GLYPH_PRIMARY}")
        banner_text.append(" - Interactive Mode", style=f"bold {GLYPH_HIGHLIGHT}")
        banner_text.append(" ◈", style=f"bold {GLYPH_ACCENT}")
        
        banner = Panel(
            banner_text,
            style=GLYPH_PRIMARY,
            box=box.HEAVY,
            padding=(1, 2)
        )
        console.print(banner)
    
    def show_main_menu(self) -> str:
        """Display main menu with Glyph styling."""
        console.print(f"\n◈ [bold {GLYPH_PRIMARY}]Main Menu[/bold {GLYPH_PRIMARY}] ◈")
        
        # Create menu table with Glyph styling
        table = Table(
            show_header=False, 
            box=box.HEAVY, 
            padding=(0, 1),
            border_style=GLYPH_SECONDARY
        )
        table.add_column("Option", style=f"bold {GLYPH_HIGHLIGHT}", width=3)
        table.add_column("Description", style="white")
        table.add_column("Current", style=GLYPH_MUTED)
        
        # Add menu options with Glyph colors
        file_status = str(self.settings['file']) if self.settings['file'] else f"[{GLYPH_ERROR}]Not set[/{GLYPH_ERROR}]"
        # Get current transcription method for display
        from transcription_config import get_transcription_config
        config = get_transcription_config()
        current_method = config.get_transcription_method()
        method_display = "Local Whisper" if current_method == "local" else "OpenAI API"
        
        table.add_row("1", "Select markdown file to edit", file_status)
        table.add_row("2", "Configure Whisper model", f"[{GLYPH_SUCCESS}]{self.settings['whisper_model']}[/{GLYPH_SUCCESS}]")
        table.add_row("3", "Configure transcription method", f"[{GLYPH_HIGHLIGHT}]{method_display}[/{GLYPH_HIGHLIGHT}]")
        table.add_row("4", "Toggle options", self._get_options_summary())
        table.add_row("5", "Start voice editing", f"[{GLYPH_WARNING}]Ready[/{GLYPH_WARNING}]" if self.settings['file'] else f"[{GLYPH_ERROR}]Need file[/{GLYPH_ERROR}]")
        table.add_row("6", "Agent mode (Obsidian)", f"[{GLYPH_VOICE}]🤖 Assistant[/{GLYPH_VOICE}]")
        table.add_row("7", "Live transcription mode", f"[{GLYPH_VOICE}]Real-time[/{GLYPH_VOICE}]")
        table.add_row("8", "Undo recent changes", f"[{GLYPH_SECONDARY}]Restore[/{GLYPH_SECONDARY}]")
        table.add_row("q", "Quit", f"[{GLYPH_MUTED}]Exit[/{GLYPH_MUTED}]")
        
        console.print(table)
        
        choice = Prompt.ask(
            f"\n◈ [bold {GLYPH_PRIMARY}]Choose an option[/bold {GLYPH_PRIMARY}] ◈",
            choices=["1", "2", "3", "4", "5", "6", "7", "8", "q"],
            default="1" if not self.settings['file'] else "5"
        )
        
        return choice
    
    def _get_options_summary(self) -> str:
        """Get a summary of current option settings with Glyph colors."""
        options = []
        if self.settings['dry_run']:
            options.append(f"[{GLYPH_WARNING}]dry-run[/{GLYPH_WARNING}]")
        if self.settings['verbose']:
            options.append(f"[{GLYPH_HIGHLIGHT}]verbose[/{GLYPH_HIGHLIGHT}]")
        if self.settings['transcript_only']:
            options.append(f"[{GLYPH_SUCCESS}]transcript-only[/{GLYPH_SUCCESS}]")
        if self.settings['no_obsidian']:
            options.append(f"[{GLYPH_MUTED}]no-obsidian[/{GLYPH_MUTED}]")
        
        return ", ".join(options) if options else f"[{GLYPH_MUTED}]none[/{GLYPH_MUTED}]"
    
    def select_file(self):
        """Interactive file selection with Glyph styling."""
        console.print(f"\n◈ [bold {GLYPH_PRIMARY}]File Selection[/bold {GLYPH_PRIMARY}] ◈")
        
        # Option 1: Enter file path manually
        console.print(f"\n[{GLYPH_HIGHLIGHT}]Option 1:[/{GLYPH_HIGHLIGHT}] Enter file path directly")
        file_path = Prompt.ask(
            "📝 File path (or Enter to browse)",
            default=""
        )
        
        if file_path:
            try:
                validated_path = validate_markdown_path(file_path)
                self.settings['file'] = str(validated_path)
                console.print(f"✅ Selected: [{GLYPH_SUCCESS}]{self.settings['file']}[/{GLYPH_SUCCESS}]")
                return
            except Exception as e:
                console.print(f"❌ [{GLYPH_ERROR}]Error: {e}[/{GLYPH_ERROR}]")
        
        # Option 2: Browse common locations
        self._browse_files()
    
    def _browse_files(self):
        """Browse for markdown files in common locations."""
        console.print("\n[cyan]Option 2:[/cyan] Browse common locations")
        
        # Common markdown locations
        search_dirs = [
            Path.home() / "Documents",
            Path.home() / "Desktop", 
            Path.home() / "Notes",
            Path.home() / "Obsidian",
            Path.cwd()
        ]
        
        # Find existing directories
        existing_dirs = [d for d in search_dirs if d.exists()]
        
        if not existing_dirs:
            console.print("❌ [red]No common directories found[/red]")
            return
        
        # Show directory options
        console.print("\n📂 [bold white]Select directory to browse:[/bold white]")
        for i, directory in enumerate(existing_dirs, 1):
            file_count = len(list(directory.glob("*.md")))
            console.print(f"  {i}. [cyan]{directory}[/cyan] [dim]({file_count} .md files)[/dim]")
        
        try:
            choice = IntPrompt.ask(
                "Choose directory",
                choices=[str(i) for i in range(1, len(existing_dirs) + 1)]
            )
            selected_dir = existing_dirs[choice - 1]
            self._browse_directory(selected_dir)
        except Exception:
            console.print("❌ [red]Invalid selection[/red]")
    
    def _browse_directory(self, directory: Path):
        """Browse markdown files in a specific directory."""
        md_files = list(directory.glob("*.md"))
        
        if not md_files:
            console.print(f"❌ [red]No .md files found in {directory}[/red]")
            return
        
        # Sort by modification time (newest first)
        md_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        console.print(f"\n📄 [bold white]Markdown files in {directory}:[/bold white]")
        
        # Show max 10 files
        display_files = md_files[:10]
        for i, file_path in enumerate(display_files, 1):
            size = file_path.stat().st_size
            modified = file_path.stat().st_mtime
            from datetime import datetime
            mod_time = datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M')
            
            console.print(f"  {i}. [green]{file_path.name}[/green] [dim]({size} bytes, {mod_time})[/dim]")
        
        if len(md_files) > 10:
            console.print(f"  [dim]... and {len(md_files) - 10} more files[/dim]")
        
        try:
            choice = IntPrompt.ask(
                "Select file",
                choices=[str(i) for i in range(1, len(display_files) + 1)]
            )
            selected_file = display_files[choice - 1]
            self.settings['file'] = str(selected_file)
            console.print(f"✅ Selected: [green]{selected_file}[/green]")
        except Exception:
            console.print("❌ [red]Invalid selection[/red]")
    
    def configure_model(self):
        """Configure Whisper model settings."""
        console.print("\n🤖 [bold white]Whisper Model Configuration[/bold white]")
        
        models = ["tiny", "base", "small", "medium", "large"]
        model_info = {
            "tiny": ("39MB", "Fastest", "Basic accuracy"),
            "base": ("74MB", "Fast", "Good accuracy"), 
            "small": ("244MB", "Medium", "Better accuracy"),
            "medium": ("769MB", "Slow", "High accuracy"),
            "large": ("1550MB", "Slowest", "Highest accuracy")
        }
        
        # Create model selection table
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("Option", style="bold cyan", width=6)
        table.add_column("Model", style="bold white", width=8)
        table.add_column("Size", style="yellow", width=8)
        table.add_column("Speed", style="green", width=8)
        table.add_column("Accuracy", style="blue", width=15)
        table.add_column("Current", style="magenta", width=8)
        
        for i, model in enumerate(models, 1):
            size, speed, accuracy = model_info[model]
            current = "✓" if model == self.settings['whisper_model'] else ""
            table.add_row(str(i), model, size, speed, accuracy, current)
        
        console.print(table)
        
        choice = Prompt.ask(
            "\n🎯 [bold white]Select model[/bold white]",
            choices=[str(i) for i in range(1, len(models) + 1)],
            default=str(models.index(self.settings['whisper_model']) + 1)
        )
        
        selected_model = models[int(choice) - 1]
        self.settings['whisper_model'] = selected_model
        console.print(f"✅ Model set to: [green]{selected_model}[/green]")
    
    def configure_transcription(self):
        """Configure transcription method."""
        from transcription_config import setup_transcription_method
        
        console.print(f"\n🎯 [bold {GLYPH_PRIMARY}]Transcription Method Configuration[/bold {GLYPH_PRIMARY}]")
        method = setup_transcription_method()
        
        if method:
            console.print(f"✅ Transcription method set to: [{GLYPH_SUCCESS}]{method}[/{GLYPH_SUCCESS}]")
        else:
            console.print(f"❌ [{GLYPH_ERROR}]Transcription configuration cancelled[/{GLYPH_ERROR}]")
    
    def toggle_options(self):
        """Toggle various options."""
        console.print("\n⚙️ [bold white]Options Configuration[/bold white]")
        
        options = [
            ("dry_run", "Dry Run", "Preview changes without applying"),
            ("verbose", "Verbose", "Show detailed debug output"),
            ("transcript_only", "Transcript Only", "Voice-to-text without GPT processing"),
            ("no_obsidian", "No Obsidian", "Don't automatically open files in Obsidian")
        ]
        
        while True:
            # Show current options
            table = Table(show_header=True, box=box.ROUNDED)
            table.add_column("Option", style="bold cyan", width=3)
            table.add_column("Setting", style="bold white", width=15)
            table.add_column("Description", style="dim", width=35)
            table.add_column("Status", style="magenta", width=10)
            
            for i, (key, name, desc) in enumerate(options, 1):
                status = "[green]ON[/green]" if self.settings[key] else "[red]OFF[/red]"
                table.add_row(str(i), name, desc, status)
            
            table.add_row("4", "Done", "Return to main menu", "[yellow]←[/yellow]")
            
            console.print(table)
            
            choice = Prompt.ask(
                "\n🎯 [bold white]Toggle option[/bold white]",
                choices=["1", "2", "3", "4"],
                default="4"
            )
            
            if choice == "4":
                break
            
            option_key = options[int(choice) - 1][0]
            self.settings[option_key] = not self.settings[option_key]
            status = "enabled" if self.settings[option_key] else "disabled"
            console.print(f"✅ {options[int(choice) - 1][1]} {status}")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings as dictionary."""
        return self.settings.copy()
    
    def run_interactive_mode(self) -> Optional[Dict[str, Any]]:
        """Run the interactive CLI mode."""
        self.show_banner()
        
        while True:
            choice = self.show_main_menu()
            
            if choice == "1":
                self.select_file()
            elif choice == "2":
                self.configure_model()
            elif choice == "3":
                self.configure_transcription()
            elif choice == "4":
                self.toggle_options()
            elif choice == "5":
                if not self.settings['file']:
                    console.print("❌ [red]Please select a file first[/red]")
                    continue
                console.print("🚀 [green]Starting voice editing...[/green]")
                return self.get_settings()
            elif choice == "6":
                console.print("🤖 [cyan]Starting agent mode...[/cyan]")
                return {'mode': 'agent'}
            elif choice == "7":
                console.print("🎤 [cyan]Starting live transcription mode...[/cyan]")
                return {'mode': 'live'}
            elif choice == "8":
                self._handle_undo_menu()
            elif choice == "q":
                console.print("👋 [yellow]Goodbye![/yellow]")
                return None
    
    def _handle_undo_menu(self):
        """Handle undo operation from interactive menu."""
        if not self.settings['file']:
            file_path = Prompt.ask("📁 [bold white]Enter file path to undo[/bold white]")
            if not file_path:
                return
        else:
            file_path = self.settings['file']
        
        # Import here to avoid circular imports
        from undo_manager import UndoManager
        
        try:
            validated_path = validate_markdown_path(file_path)
            backups = UndoManager.list_backups(str(validated_path))
            
            if not backups:
                console.print(f"❌ [red]No backups found for {validated_path}[/red]")
                return
            
            console.print(f"\n📋 Found {len(backups)} backup(s)")
            
            if Confirm.ask("🔄 Restore from latest backup?"):
                success = UndoManager.restore_from_backup(str(validated_path))
                if success:
                    console.print("✅ [green]File restored successfully[/green]")
                else:
                    console.print("❌ [red]Failed to restore file[/red]")
            
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")