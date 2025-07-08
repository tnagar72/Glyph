#!/usr/bin/env python3

"""
Agent Configuration Module for Glyph.
Manages configuration for Agent mode including vault path and agent preferences.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box

from ui_helpers import (
    GLYPH_PRIMARY, GLYPH_SECONDARY, GLYPH_SUCCESS, GLYPH_ERROR, GLYPH_WARNING, 
    GLYPH_HIGHLIGHT, GLYPH_MUTED, show_success_message, show_error_message
)

console = Console()

# Configuration file path
CONFIG_DIR = Path.home() / ".glyph"
AGENT_CONFIG_FILE = CONFIG_DIR / "agent_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "vault_path": None,
    "auto_accept": False,
    "default_tool_confirmation": True,
    "session_memory": True,
    "backup_before_agent_edits": True,
    "max_tool_calls_per_session": 50
}

class AgentConfig:
    """Manages agent configuration settings."""
    
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = AGENT_CONFIG_FILE
        self.config_dir.mkdir(exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to handle new config keys
                merged_config = DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
            except (json.JSONDecodeError, IOError) as e:
                console.print(f"[yellow]⚠️ Error loading agent config: {e}[/yellow]")
                console.print("[yellow]Using default configuration...[/yellow]")
                return DEFAULT_CONFIG.copy()
        else:
            return DEFAULT_CONFIG.copy()
    
    def _save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError as e:
            console.print(f"[red]❌ Error saving agent config: {e}[/red]")
            return False
    
    def get_vault_path(self) -> Optional[str]:
        """Get the configured Obsidian vault path."""
        return self.config.get("vault_path")
    
    def set_vault_path(self, path: str) -> bool:
        """Set the Obsidian vault path with validation."""
        vault_path = Path(path).expanduser().resolve()
        
        # Validate path exists and is a directory
        if not vault_path.exists():
            console.print(f"[red]❌ Path does not exist: {vault_path}[/red]")
            return False
        
        if not vault_path.is_dir():
            console.print(f"[red]❌ Path is not a directory: {vault_path}[/red]")
            return False
        
        # Check if it looks like an Obsidian vault (has .obsidian folder or .md files)
        has_obsidian_folder = (vault_path / ".obsidian").exists()
        has_md_files = any(vault_path.rglob("*.md"))
        
        if not has_obsidian_folder and not has_md_files:
            if not Confirm.ask(f"[yellow]⚠️ Directory doesn't appear to be an Obsidian vault. Continue anyway?[/yellow]"):
                return False
        
        self.config["vault_path"] = str(vault_path)
        return self._save_config()
    
    def get_auto_accept(self) -> bool:
        """Get auto-accept setting for tool calls."""
        return self.config.get("auto_accept", False)
    
    def set_auto_accept(self, auto_accept: bool) -> bool:
        """Set auto-accept setting."""
        self.config["auto_accept"] = auto_accept
        return self._save_config()
    
    def get_tool_confirmation(self) -> bool:
        """Get default tool confirmation setting."""
        return self.config.get("default_tool_confirmation", True)
    
    def set_tool_confirmation(self, confirm: bool) -> bool:
        """Set default tool confirmation setting."""
        self.config["default_tool_confirmation"] = confirm
        return self._save_config()
    
    def get_session_memory(self) -> bool:
        """Get session memory setting."""
        return self.config.get("session_memory", True)
    
    def set_session_memory(self, enabled: bool) -> bool:
        """Set session memory setting."""
        self.config["session_memory"] = enabled
        return self._save_config()
    
    def get_backup_before_edits(self) -> bool:
        """Get backup before agent edits setting."""
        return self.config.get("backup_before_agent_edits", True)
    
    def set_backup_before_edits(self, enabled: bool) -> bool:
        """Set backup before agent edits setting."""
        self.config["backup_before_agent_edits"] = enabled
        return self._save_config()
    
    def get_max_tool_calls(self) -> int:
        """Get maximum tool calls per session."""
        return self.config.get("max_tool_calls_per_session", 50)
    
    def set_max_tool_calls(self, max_calls: int) -> bool:
        """Set maximum tool calls per session."""
        if max_calls < 1 or max_calls > 1000:
            console.print("[red]❌ Max tool calls must be between 1 and 1000[/red]")
            return False
        
        self.config["max_tool_calls_per_session"] = max_calls
        return self._save_config()
    
    def is_vault_configured(self) -> bool:
        """Check if a vault path is configured and valid."""
        vault_path = self.get_vault_path()
        if not vault_path:
            return False
        
        path = Path(vault_path)
        return path.exists() and path.is_dir()
    
    def show_current_config(self):
        """Display current agent configuration."""
        vault_path = self.get_vault_path()
        vault_status = f"[{GLYPH_SUCCESS}]{vault_path}[/{GLYPH_SUCCESS}]" if self.is_vault_configured() else f"[{GLYPH_ERROR}]Not configured[/{GLYPH_ERROR}]"
        
        table = Table(title=f"🤖 Agent Configuration", box=box.ROUNDED, border_style=GLYPH_PRIMARY)
        table.add_column("Setting", style=GLYPH_HIGHLIGHT)
        table.add_column("Value", style="white")
        table.add_column("Description", style=GLYPH_MUTED)
        
        table.add_row("Vault Path", vault_status, "Obsidian vault directory")
        table.add_row("Auto Accept", 
                     f"[{GLYPH_SUCCESS}]Enabled[/{GLYPH_SUCCESS}]" if self.get_auto_accept() else f"[{GLYPH_WARNING}]Disabled[/{GLYPH_WARNING}]",
                     "Skip confirmation for tool calls")
        table.add_row("Tool Confirmation", 
                     f"[{GLYPH_SUCCESS}]Enabled[/{GLYPH_SUCCESS}]" if self.get_tool_confirmation() else f"[{GLYPH_WARNING}]Disabled[/{GLYPH_WARNING}]",
                     "Ask before executing tools")
        table.add_row("Session Memory", 
                     f"[{GLYPH_SUCCESS}]Enabled[/{GLYPH_SUCCESS}]" if self.get_session_memory() else f"[{GLYPH_WARNING}]Disabled[/{GLYPH_WARNING}]",
                     "Remember context during session")
        table.add_row("Auto Backup", 
                     f"[{GLYPH_SUCCESS}]Enabled[/{GLYPH_SUCCESS}]" if self.get_backup_before_edits() else f"[{GLYPH_WARNING}]Disabled[/{GLYPH_WARNING}]",
                     "Backup files before agent edits")
        table.add_row("Max Tool Calls", 
                     f"[{GLYPH_HIGHLIGHT}]{self.get_max_tool_calls()}[/{GLYPH_HIGHLIGHT}]",
                     "Maximum tool calls per session")
        
        console.print(table)

def setup_agent_configuration() -> Optional[str]:
    """Interactive agent configuration wizard."""
    console.print(f"\n🤖 [bold {GLYPH_PRIMARY}]Agent Configuration Wizard[/bold {GLYPH_PRIMARY}]")
    
    config = AgentConfig()
    
    # Show current configuration
    config.show_current_config()
    
    console.print(f"\n[bold {GLYPH_HIGHLIGHT}]Configuration Options:[/bold {GLYPH_HIGHLIGHT}]")
    
    options_table = Table(box=box.SIMPLE, show_header=False, border_style=GLYPH_SECONDARY)
    options_table.add_column("Option", style=f"bold {GLYPH_HIGHLIGHT}", width=3)
    options_table.add_column("Description", style="white")
    
    options_table.add_row("1", "Set Obsidian vault path")
    options_table.add_row("2", "Configure auto-accept mode")
    options_table.add_row("3", "Configure tool confirmation")
    options_table.add_row("4", "Configure session memory")
    options_table.add_row("5", "Configure auto backup")
    options_table.add_row("6", "Set max tool calls per session")
    options_table.add_row("7", "Test vault configuration")
    options_table.add_row("q", "Quit configuration")
    
    console.print(options_table)
    
    while True:
        choice = Prompt.ask(
            f"\n🤖 [bold {GLYPH_PRIMARY}]Choose option[/bold {GLYPH_PRIMARY}]",
            choices=["1", "2", "3", "4", "5", "6", "7", "q"],
            default="1" if not config.is_vault_configured() else "q"
        )
        
        if choice == "q":
            break
        elif choice == "1":
            setup_vault_path(config)
        elif choice == "2":
            setup_auto_accept(config)
        elif choice == "3":
            setup_tool_confirmation(config)
        elif choice == "4":
            setup_session_memory(config)
        elif choice == "5":
            setup_auto_backup(config)
        elif choice == "6":
            setup_max_tool_calls(config)
        elif choice == "7":
            test_vault_configuration(config)
        
        # Show updated configuration
        console.print()
        config.show_current_config()
    
    if config.is_vault_configured():
        return config.get_vault_path()
    else:
        return None

def setup_vault_path(config: AgentConfig):
    """Setup Obsidian vault path."""
    console.print(f"\n📁 [bold {GLYPH_HIGHLIGHT}]Obsidian Vault Configuration[/bold {GLYPH_HIGHLIGHT}]")
    
    current_path = config.get_vault_path()
    if current_path:
        console.print(f"Current vault path: [cyan]{current_path}[/cyan]")
    
    console.print("\n💡 [dim]Tips:[/dim]")
    console.print("• [dim]Enter the full path to your Obsidian vault directory[/dim]")
    console.print("• [dim]Example: /Users/yourname/Documents/MyVault[/dim]")
    console.print("• [dim]Use ~ for home directory: ~/Documents/MyVault[/dim]")
    
    while True:
        vault_path = Prompt.ask(
            f"\n📁 [bold {GLYPH_PRIMARY}]Enter vault path[/bold {GLYPH_PRIMARY}]",
            default=current_path or ""
        )
        
        if not vault_path:
            console.print("[yellow]⚠️ No path entered. Vault configuration cancelled.[/yellow]")
            return
        
        if config.set_vault_path(vault_path):
            show_success_message(f"✅ Vault path configured: {config.get_vault_path()}")
            break
        else:
            if not Confirm.ask("[yellow]Try again?[/yellow]"):
                break

def setup_auto_accept(config: AgentConfig):
    """Setup auto-accept mode."""
    console.print(f"\n🤖 [bold {GLYPH_HIGHLIGHT}]Auto-Accept Configuration[/bold {GLYPH_HIGHLIGHT}]")
    
    console.print("\n[yellow]⚠️ Auto-accept mode will execute tool calls without confirmation![/yellow]")
    console.print("[dim]• Faster workflow but less control[/dim]")
    console.print("[dim]• Recommended only for trusted environments[/dim]")
    console.print("[dim]• You can always override per session[/dim]")
    
    auto_accept = Confirm.ask(
        f"\n🤖 Enable auto-accept mode?",
        default=config.get_auto_accept()
    )
    
    if config.set_auto_accept(auto_accept):
        status = "enabled" if auto_accept else "disabled"
        show_success_message(f"✅ Auto-accept mode {status}")

def setup_tool_confirmation(config: AgentConfig):
    """Setup tool confirmation."""
    console.print(f"\n🛠️ [bold {GLYPH_HIGHLIGHT}]Tool Confirmation Configuration[/bold {GLYPH_HIGHLIGHT}]")
    
    console.print("\n[dim]Tool confirmation shows you what will happen before execution[/dim]")
    
    confirm = Confirm.ask(
        f"\n🛠️ Enable tool confirmation by default?",
        default=config.get_tool_confirmation()
    )
    
    if config.set_tool_confirmation(confirm):
        status = "enabled" if confirm else "disabled"
        show_success_message(f"✅ Tool confirmation {status}")

def setup_session_memory(config: AgentConfig):
    """Setup session memory."""
    console.print(f"\n🧠 [bold {GLYPH_HIGHLIGHT}]Session Memory Configuration[/bold {GLYPH_HIGHLIGHT}]")
    
    console.print("\n[dim]Session memory helps the agent remember context during conversations[/dim]")
    
    memory = Confirm.ask(
        f"\n🧠 Enable session memory?",
        default=config.get_session_memory()
    )
    
    if config.set_session_memory(memory):
        status = "enabled" if memory else "disabled"
        show_success_message(f"✅ Session memory {status}")

def setup_auto_backup(config: AgentConfig):
    """Setup auto backup."""
    console.print(f"\n💾 [bold {GLYPH_HIGHLIGHT}]Auto Backup Configuration[/bold {GLYPH_HIGHLIGHT}]")
    
    console.print("\n[dim]Auto backup creates backups before agent modifications[/dim]")
    console.print("[dim]Highly recommended for safety[/dim]")
    
    backup = Confirm.ask(
        f"\n💾 Enable auto backup before agent edits?",
        default=config.get_backup_before_edits()
    )
    
    if config.set_backup_before_edits(backup):
        status = "enabled" if backup else "disabled"
        show_success_message(f"✅ Auto backup {status}")

def setup_max_tool_calls(config: AgentConfig):
    """Setup maximum tool calls per session."""
    console.print(f"\n🔢 [bold {GLYPH_HIGHLIGHT}]Max Tool Calls Configuration[/bold {GLYPH_HIGHLIGHT}]")
    
    console.print(f"\nCurrent limit: [cyan]{config.get_max_tool_calls()}[/cyan] tool calls per session")
    console.print("[dim]This prevents runaway agent behavior[/dim]")
    
    max_calls = Prompt.ask(
        f"\n🔢 Enter maximum tool calls per session",
        default=str(config.get_max_tool_calls())
    )
    
    try:
        max_calls_int = int(max_calls)
        if config.set_max_tool_calls(max_calls_int):
            show_success_message(f"✅ Max tool calls set to {max_calls_int}")
    except ValueError:
        show_error_message("❌ Please enter a valid number")

def test_vault_configuration(config: AgentConfig):
    """Test vault configuration."""
    console.print(f"\n🧪 [bold {GLYPH_HIGHLIGHT}]Testing Vault Configuration[/bold {GLYPH_HIGHLIGHT}]")
    
    if not config.is_vault_configured():
        show_error_message("❌ No vault configured. Please set vault path first.")
        return
    
    vault_path = Path(config.get_vault_path())
    
    console.print(f"Testing vault: [cyan]{vault_path}[/cyan]")
    
    # Test basic access
    if not vault_path.exists():
        show_error_message("❌ Vault path does not exist")
        return
    
    if not vault_path.is_dir():
        show_error_message("❌ Vault path is not a directory")
        return
    
    # Test read/write permissions
    try:
        test_file = vault_path / ".glyph_test"
        test_file.write_text("test")
        test_file.unlink()
        console.print("✅ [green]Read/write permissions: OK[/green]")
    except Exception as e:
        show_error_message(f"❌ Permission error: {e}")
        return
    
    # Check for Obsidian features
    obsidian_folder = vault_path / ".obsidian"
    if obsidian_folder.exists():
        console.print("✅ [green]Obsidian configuration found[/green]")
    else:
        console.print("⚠️ [yellow]No .obsidian folder found[/yellow]")
    
    # Count markdown files
    md_files = list(vault_path.rglob("*.md"))
    console.print(f"📄 [cyan]Found {len(md_files)} markdown files[/cyan]")
    
    if len(md_files) == 0:
        console.print("⚠️ [yellow]No markdown files found in vault[/yellow]")
    
    show_success_message("🧪 Vault configuration test completed")

def get_agent_config() -> AgentConfig:
    """Get the global agent configuration instance."""
    return AgentConfig()

if __name__ == "__main__":
    # Test the configuration system
    setup_agent_configuration()