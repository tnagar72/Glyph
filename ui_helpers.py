#!/usr/bin/env python3

"""
UI Helper module for Glyph - Unique voice-first terminal interface.
Provides reusable UI components with distinctive Glyph styling.
Glyph Color Scheme: Purple/Violet primary, Gold accents, Teal highlights
"""

import shutil
import textwrap
import asyncio
import time
from typing import Optional, List, Dict, Any
from pathlib import Path

import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.syntax import Syntax
from rich import box
from rich.live import Live
from rich.spinner import Spinner
from rich.theme import Theme

# ═══════════════════════════════════════════════════════════════════════════════════
# CATPPUCCIN MOCHACCINO COLOR SCHEME - Futuristic CLI
# ═══════════════════════════════════════════════════════════════════════════════════

# Catppuccin Mochaccino Core Colors (Dark Mode)
GLYPH_BASE = "#1e1e2e"              # Deep dark background
GLYPH_SURFACE = "#313244"           # Surface elements
GLYPH_OVERLAY = "#6c7086"           # Overlay text
GLYPH_MUTED = "#6c7086"             # Muted/secondary text
GLYPH_TEXT = "#cdd6f4"              # Primary text
GLYPH_SUBTEXT = "#a6adc8"           # Secondary text

# Accent Colors (Mochaccino Palette)
GLYPH_LAVENDER = "#b4befe"          # Soft purple - primary brand
GLYPH_BLUE = "#89b4fa"              # Cool blue - info/links
GLYPH_SAPPHIRE = "#74c7ec"          # Bright cyan - highlights
GLYPH_SKY = "#89dceb"               # Light cyan - voice/interactive
GLYPH_TEAL = "#94e2d5"              # Mint green - success
GLYPH_GREEN = "#a6e3a1"             # Green - confirmations
GLYPH_YELLOW = "#f9e2af"            # Warm yellow - warnings
GLYPH_PEACH = "#fab387"             # Orange - accents
GLYPH_MAROON = "#eba0ac"            # Soft red - errors
GLYPH_RED = "#f38ba8"               # Error states
GLYPH_MAUVE = "#cba6f7"             # Purple - secondary brand
GLYPH_PINK = "#f5c2e7"              # Pink - special highlights

# Semantic Color Mapping (Rich-compatible)
GLYPH_PRIMARY = GLYPH_LAVENDER         # Main brand color - soft purple
GLYPH_SECONDARY = GLYPH_MAUVE          # Secondary brand - deeper purple  
GLYPH_ACCENT = GLYPH_PEACH             # Warm accents - soft orange
GLYPH_HIGHLIGHT = GLYPH_SAPPHIRE       # Interactive highlights - bright cyan
GLYPH_SUCCESS = GLYPH_TEAL             # Success states - mint green
GLYPH_ERROR = GLYPH_MAROON             # Error states - soft red
GLYPH_WARNING = GLYPH_YELLOW           # Warning states - warm yellow
GLYPH_INFO = GLYPH_BLUE                # Info states - cool blue
GLYPH_VOICE = GLYPH_SKY                # Voice-related UI - light cyan

# Create Catppuccin Mochaccino theme for Rich
catppuccin_theme = Theme({
    "primary": GLYPH_PRIMARY,
    "secondary": GLYPH_SECONDARY, 
    "accent": GLYPH_ACCENT,
    "highlight": GLYPH_HIGHLIGHT,
    "success": GLYPH_SUCCESS,
    "error": GLYPH_ERROR,
    "warning": GLYPH_WARNING,
    "info": GLYPH_INFO,
    "voice": GLYPH_VOICE,
    "muted": GLYPH_MUTED,
    "text": GLYPH_TEXT,
    "subtext": GLYPH_SUBTEXT,
})

console = Console(theme=catppuccin_theme, force_terminal=True, color_system="truecolor")

# ═══════════════════════════════════════════════════════════════════════════════════
# CORE UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════════

def get_terminal_width() -> int:
    """Get current terminal width for responsive design."""
    return shutil.get_terminal_size().columns

def center_text(text: str, width: Optional[int] = None) -> str:
    """Center text within terminal width."""
    if width is None:
        width = get_terminal_width()
    return text.center(width)

def wrap_text(text: str, width: Optional[int] = None) -> str:
    """Wrap text to fit terminal width."""
    if width is None:
        width = get_terminal_width() - 4  # Leave margin
    return textwrap.fill(text, width=width)

# ═══════════════════════════════════════════════════════════════════════════════════
# WELCOME BANNER & LOGO
# ═══════════════════════════════════════════════════════════════════════════════════

def show_welcome_banner():
    """Display stylized welcome banner with unique Glyph branding."""
    width = get_terminal_width()
    
    # Create banner with distinctive Glyph styling
    banner_text = Text()
    banner_text.append("◈ ", style=f"bold {GLYPH_ACCENT}")
    banner_text.append("Welcome to ", style="bold white")
    banner_text.append("Glyph", style=f"bold {GLYPH_PRIMARY}")
    banner_text.append(" ◈", style=f"bold {GLYPH_ACCENT}")
    
    banner = Panel(
        Align.center(banner_text),
        style=GLYPH_PRIMARY,
        box=box.HEAVY,
        width=min(width, 40)
    )
    
    console.print(Align.center(banner))
    console.print()

def show_ascii_logo():
    """Display ASCII art logo with unique Glyph styling."""
    try:
        # Generate ASCII art
        logo = pyfiglet.figlet_format("GLYPH", font="slant")
        
        # Style the logo with Glyph colors
        logo_text = Text(logo, style=f"bold {GLYPH_PRIMARY}")
        
        # Add distinctive subtitle with voice emphasis
        subtitle = Text()
        subtitle.append("◈ ", style=f"bold {GLYPH_ACCENT}")
        subtitle.append("Voice-native interface for structured thought and knowledge workflows", style=f"italic {GLYPH_HIGHLIGHT}")
        subtitle.append(" ◈", style=f"bold {GLYPH_ACCENT}")
        
        # Create panel with Glyph styling
        logo_panel = Panel(
            Align.center(logo_text) + "\n" + Align.center(subtitle),
            style=GLYPH_SECONDARY,
            box=box.HEAVY,
            padding=(1, 2)
        )
        
        console.print(Align.center(logo_panel))
        console.print()
        
        # Interactive prompt with voice emphasis
        prompt_text = Text()
        prompt_text.append("Press Enter or say ", style=GLYPH_MUTED)
        prompt_text.append("\"Continue\"", style=f"bold {GLYPH_VOICE}")
        prompt_text.append(" to start", style=GLYPH_MUTED)
        
        console.print(Align.center(prompt_text))
        
        # Wait for input
        input()
        
    except Exception:
        # Fallback simple logo with Glyph branding
        fallback_logo = """
    ╔══════════════════════════════════════╗
    ║               GLYPH                  ║
    ║   ◈ Voice-powered knowledge tool ◈   ║
    ╚══════════════════════════════════════╝
        """
        console.print(Align.center(Text(fallback_logo, style=f"bold {GLYPH_PRIMARY}")))
        console.print()

# ═══════════════════════════════════════════════════════════════════════════════════
# VOICE INTERACTION INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════════

def show_recording_indicator(recording_method="spacebar", dry_run=False):
    """Display recording indicator with Glyph voice theme."""
    if recording_method == "enter":
        message = "🎙️ Listening... (Say your command or press Enter to stop)"
    else:
        message = "🎙️ Listening... (Hold SPACEBAR to record, release to stop)"
    
    # Add dry-run indicator
    if dry_run:
        message += "\n🔍 DRY-RUN MODE: Changes will be previewed only"
    
    title = "◈ Recording ◈" if not dry_run else "◈ Recording (Preview Mode) ◈"
    
    indicator = Panel(
        Text(message, style=f"bold {GLYPH_VOICE}"),
        style=GLYPH_VOICE,
        box=box.HEAVY,
        title=title,
        title_align="center"
    )
    console.print(indicator)

def show_thinking_indicator():
    """Display processing indicator with Glyph AI theme."""
    indicator = Panel(
        Text("🧠 Thinking... (AI is parsing your intent)", style=f"bold {GLYPH_SECONDARY}"),
        style=GLYPH_SECONDARY,
        box=box.HEAVY,
        title="◈ Processing ◈",
        title_align="center"
    )
    console.print(indicator)

def show_animated_status(message: str, style: str = GLYPH_HIGHLIGHT):
    """Show animated status with spinner using Glyph colors."""
    with console.status(f"[bold {style}]{message}[/bold {style}]", spinner="dots"):
        time.sleep(0.5)  # Brief pause for visual effect

# ═══════════════════════════════════════════════════════════════════════════════════
# PROPOSAL & CONFIRMATION PANELS
# ═══════════════════════════════════════════════════════════════════════════════════

def show_edit_proposal(filename: str, old_content: str, new_content: str) -> bool:
    """Show edit proposal with unique Glyph styling."""
    
    # Create proposal header with Glyph branding
    header = Text()
    header.append("◈ ", style=f"bold {GLYPH_ACCENT}")
    header.append("Proposed Edit to ", style="bold white")
    header.append(filename, style=f"bold {GLYPH_HIGHLIGHT}")
    header.append(" ◈", style=f"bold {GLYPH_ACCENT}")
    
    # Create diff view with Glyph colors
    diff_text = ""
    old_lines = old_content.split('\n')
    new_lines = new_content.split('\n')
    
    # Simple diff visualization
    for i, (old, new) in enumerate(zip(old_lines, new_lines)):
        if old != new:
            diff_text += f"- {old}\n"
            diff_text += f"+ {new}\n"
        else:
            diff_text += f"  {old}\n"
    
    # Create panel with distinctive Glyph styling
    proposal_panel = Panel(
        header + "\n" + Text("◈" * 40, style=GLYPH_MUTED) + "\n" + 
        Text(diff_text, style="white") + "\n" + 
        Text("Do you want to apply this change?", style=f"bold {GLYPH_PRIMARY}") + "\n" +
        Text("1. ✅ Yes", style=GLYPH_SUCCESS) + "\n" +
        Text("2. ❌ No, rephrase", style=GLYPH_ERROR) + "\n" +
        Text("3. 🔁 Regenerate", style=GLYPH_WARNING),
        style=GLYPH_PRIMARY,
        box=box.HEAVY,
        title="◈ Edit Proposal ◈",
        title_align="center"
    )
    
    console.print(proposal_panel)
    
    # Get user choice
    choice = Prompt.ask(
        "Choose option",
        choices=["1", "2", "3"],
        default="1"
    )
    
    if choice == "1":
        console.print(f"✅ [{GLYPH_SUCCESS}]Changes accepted![/{GLYPH_SUCCESS}]")
        return True
    elif choice == "2":
        console.print(f"❌ [{GLYPH_ERROR}]Changes rejected - please rephrase your request[/{GLYPH_ERROR}]")
        return False
    else:
        console.print(f"🔁 [{GLYPH_WARNING}]Regenerating response...[/{GLYPH_WARNING}]")
        return False

# ═══════════════════════════════════════════════════════════════════════════════════
# ENHANCED DIFF DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════════

def show_enhanced_diff(original: str, modified: str, filename: str) -> List[str]:
    """Show enhanced diff with Glyph styling and voice-oriented design."""
    
    # Header with file info using Glyph branding
    header = Text()
    header.append("◈ ", style=f"bold {GLYPH_ACCENT}")
    header.append("Changes Preview: ", style="bold white")
    header.append(filename, style=f"bold {GLYPH_HIGHLIGHT}")
    header.append(" ◈", style=f"bold {GLYPH_ACCENT}")
    
    # Create diff table with Glyph styling
    table = Table(
        show_header=True,
        box=box.HEAVY,
        title=header,
        title_style=f"bold {GLYPH_PRIMARY}",
        border_style=GLYPH_SECONDARY
    )
    
    table.add_column("Type", style="bold", width=8)
    table.add_column("Content", style="", min_width=60)
    
    # Process diff line by line
    original_lines = original.splitlines()
    modified_lines = modified.splitlines()
    
    # Simple diff algorithm
    import difflib
    diff = list(difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        lineterm=''
    ))
    
    # Process diff lines with Glyph colors
    for line in diff:
        if line.startswith('---') or line.startswith('+++'):
            continue
        elif line.startswith('@@'):
            continue
        elif line.startswith('+'):
            # Addition with success color
            content = line[1:].strip()
            if content:
                table.add_row(
                    Text("+ ADD", style=f"bold {GLYPH_SUCCESS}"),
                    Text(content, style=GLYPH_SUCCESS)
                )
        elif line.startswith('-'):
            # Deletion with error color
            content = line[1:].strip()
            if content:
                table.add_row(
                    Text("- DEL", style=f"bold {GLYPH_ERROR}"),
                    Text(content, style=GLYPH_ERROR)
                )
        elif line.startswith(' '):
            # Context line
            content = line[1:].strip()
            if content:
                table.add_row(
                    Text("", style=GLYPH_MUTED),
                    Text(content, style=GLYPH_MUTED)
                )
    
    console.print(table)
    return diff

# ═══════════════════════════════════════════════════════════════════════════════════
# FILE SELECTION UI
# ═══════════════════════════════════════════════════════════════════════════════════

def show_file_selector() -> Optional[str]:
    """Modern file browser with distinctive Glyph styling."""
    
    # Header with Glyph branding
    header_text = Text()
    header_text.append("◈ ", style=f"bold {GLYPH_ACCENT}")
    header_text.append("Select a file to edit:", style="bold white")
    header_text.append(" ◈", style=f"bold {GLYPH_ACCENT}")
    
    header = Panel(
        header_text,
        style=GLYPH_PRIMARY,
        box=box.HEAVY
    )
    console.print(header)
    
    # Search common directories
    search_dirs = [
        Path.home() / "Documents",
        Path.home() / "Desktop",
        Path.home() / "Notes",
        Path.home() / "Obsidian",
        Path.cwd()
    ]
    
    # Find markdown files
    md_files = []
    for directory in search_dirs:
        if directory.exists():
            md_files.extend(directory.glob("*.md"))
    
    if not md_files:
        console.print(f"❌ [{GLYPH_ERROR}]No markdown files found in common locations[/{GLYPH_ERROR}]")
        return None
    
    # Create file selection table with Glyph styling
    table = Table(
        show_header=True,
        box=box.HEAVY,
        title="◈ Available Files ◈",
        title_style=f"bold {GLYPH_PRIMARY}",
        border_style=GLYPH_SECONDARY
    )
    
    table.add_column("Option", style=f"bold {GLYPH_HIGHLIGHT}", width=6)
    table.add_column("File", style="bold white", width=30)
    table.add_column("Location", style=GLYPH_MUTED, width=30)
    table.add_column("Size", style=f"bold {GLYPH_ACCENT}", width=10)
    
    # Sort by modification time
    md_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Show top 10 files
    display_files = md_files[:10]
    for i, file_path in enumerate(display_files, 1):
        size = file_path.stat().st_size
        size_str = f"{size:,} bytes" if size < 1024 else f"{size//1024:,} KB"
        
        table.add_row(
            str(i),
            file_path.name,
            str(file_path.parent),
            size_str
        )
    
    # Add option to specify custom file
    table.add_row("c", "Custom file path", "Enter manually", "—")
    
    console.print(table)
    
    # Get user choice
    choices = [str(i) for i in range(1, len(display_files) + 1)] + ["c"]
    choice = Prompt.ask(
        "Select file",
        choices=choices,
        default="1"
    )
    
    if choice == "c":
        return Prompt.ask("Enter file path")
    else:
        return str(display_files[int(choice) - 1])

# ═══════════════════════════════════════════════════════════════════════════════════
# FEEDBACK & SUCCESS INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════════

def show_clipboard_success():
    """Show clipboard copy success message with Glyph branding."""
    content = Text()
    content.append("✅ Copied result to clipboard.\n", style=f"bold {GLYPH_SUCCESS}")
    content.append("🧠 Your thoughts are now structured and saved.", style=f"italic {GLYPH_HIGHLIGHT}")
    
    success_panel = Panel(
        content,
        style=GLYPH_SUCCESS,
        box=box.HEAVY,
        title="◈ Success ◈",
        title_align="center"
    )
    console.print(success_panel)

def show_success_message(message: str, subtitle: str = ""):
    """Show generic success message with Glyph styling."""
    content = Text(message, style=f"bold {GLYPH_SUCCESS}")
    if subtitle:
        content.append(f"\n{subtitle}", style=GLYPH_MUTED)
    
    success_panel = Panel(
        content,
        style=GLYPH_SUCCESS,
        box=box.HEAVY,
        title="◈ Success ◈",
        title_align="center"
    )
    console.print(success_panel)

def show_error_message(message: str, subtitle: str = ""):
    """Show error message with Glyph styling."""
    content = Text(message, style=f"bold {GLYPH_ERROR}")
    if subtitle:
        content.append(f"\n{subtitle}", style=GLYPH_MUTED)
    
    error_panel = Panel(
        content,
        style=GLYPH_ERROR,
        box=box.HEAVY,
        title="◈ Error ◈",
        title_align="center"
    )
    console.print(error_panel)

def show_warning_message(message: str, subtitle: str = ""):
    """Show warning message with Glyph styling."""
    content = Text(message, style=f"bold {GLYPH_WARNING}")
    if subtitle:
        content.append(f"\n{subtitle}", style=GLYPH_MUTED)
    
    warning_panel = Panel(
        content,
        style=GLYPH_WARNING,
        box=box.HEAVY,
        title="◈ Warning ◈",
        title_align="center"
    )
    console.print(warning_panel)

# ═══════════════════════════════════════════════════════════════════════════════════
# PROGRESS & LOADING INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════════

def show_progress_bar(description: str, total: int = 100):
    """Show progress bar for long operations."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(description, total=total)
        for i in range(total):
            progress.update(task, advance=1)
            time.sleep(0.02)  # Simulate work

def show_loading_spinner(message: str, duration: float = 2.0):
    """Show loading spinner for operations."""
    with Live(
        Spinner("dots", text=Text(message, style="bold cyan")),
        console=console,
        transient=True
    ) as live:
        time.sleep(duration)

# ═══════════════════════════════════════════════════════════════════════════════════
# RESPONSIVE LAYOUT HELPERS
# ═══════════════════════════════════════════════════════════════════════════════════

def create_responsive_columns(items: List[Any], min_width: int = 20) -> Columns:
    """Create responsive columns based on terminal width."""
    terminal_width = get_terminal_width()
    num_columns = max(1, terminal_width // min_width)
    
    return Columns(items, equal=True, expand=True, column_first=True)

def create_adaptive_panel(content: Any, title: str = "", style: str = "blue") -> Panel:
    """Create panel that adapts to terminal width."""
    terminal_width = get_terminal_width()
    
    # Adjust padding based on terminal width
    padding = (1, 2) if terminal_width > 80 else (0, 1)
    
    return Panel(
        content,
        title=title,
        style=style,
        box=box.ROUNDED,
        padding=padding,
        width=min(terminal_width - 4, 120)
    )

# ═══════════════════════════════════════════════════════════════════════════════════
# INTERACTIVE MENUS
# ═══════════════════════════════════════════════════════════════════════════════════

def show_main_menu(current_file: Optional[str] = None) -> str:
    """Show main menu with distinctive Glyph styling."""
    
    # Header with Glyph branding
    header = Text()
    header.append("◈ ", style=f"bold {GLYPH_ACCENT}")
    header.append("Glyph", style=f"bold {GLYPH_PRIMARY}")
    header.append(" - Main Menu", style=f"bold {GLYPH_HIGHLIGHT}")
    header.append(" ◈", style=f"bold {GLYPH_ACCENT}")
    
    # Create menu table with Glyph styling
    table = Table(
        show_header=False,
        box=box.HEAVY,
        title=header,
        title_style=f"bold {GLYPH_PRIMARY}",
        border_style=GLYPH_SECONDARY
    )
    
    table.add_column("Option", style=f"bold {GLYPH_HIGHLIGHT}", width=6)
    table.add_column("Action", style="bold white", width=25)
    table.add_column("Status", style=GLYPH_MUTED, width=20)
    
    # Menu items with Glyph colors
    file_status = current_file if current_file else f"[{GLYPH_ERROR}]Not selected[/{GLYPH_ERROR}]"
    table.add_row("1", "📝 Edit markdown file", file_status)
    table.add_row("2", "🎤 Live transcription", f"[{GLYPH_VOICE}]Real-time[/{GLYPH_VOICE}]")
    table.add_row("3", "⚙️ Settings", f"[{GLYPH_MUTED}]Configure[/{GLYPH_MUTED}]")
    table.add_row("4", "🔄 Undo changes", f"[{GLYPH_WARNING}]Restore[/{GLYPH_WARNING}]")
    table.add_row("5", "📊 View session logs", f"[{GLYPH_SECONDARY}]History[/{GLYPH_SECONDARY}]")
    table.add_row("q", "🚪 Quit", f"[{GLYPH_ERROR}]Exit[/{GLYPH_ERROR}]")
    
    console.print(table)
    
    return Prompt.ask(
        "Choose option",
        choices=["1", "2", "3", "4", "5", "q"],
        default="1"
    )

# ═══════════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════════

def show_config_overview():
    """Display configuration overview with unique Glyph styling."""
    
    # Header with Glyph branding
    header_text = Text()
    header_text.append("◈ ", style=f"bold {GLYPH_ACCENT}")
    header_text.append("Configuration Overview", style="bold white")
    header_text.append(" ◈", style=f"bold {GLYPH_ACCENT}")
    
    header = Panel(
        header_text,
        style=GLYPH_PRIMARY,
        box=box.HEAVY
    )
    console.print(header)
    
    # Get dynamic configuration data
    try:
        from audio_config import get_audio_device
        from model_config import get_default_model
        from transcription_config import get_transcription_config
        from agent_config import get_agent_config
        
        # Get current configurations
        audio_device = get_audio_device()
        default_model = get_default_model()
        transcription_config = get_transcription_config()
        agent_config = get_agent_config()
        
        # Audio configuration
        audio_info = [
            f"Device: {audio_device if audio_device else 'Not configured'}",
            "Sample Rate: 44.1kHz",
            "Channels: Mono"
        ]
        
        # Model configuration
        current_method = transcription_config.get_transcription_method()
        method_display = "Local Whisper" if current_method == "local" else "OpenAI API"
        model_info = [
            f"Transcription: {method_display}",
            f"Whisper Model: {default_model}",
            "GPT Model: gpt-4"
        ]
        
        # Agent configuration
        vault_path = agent_config.get_vault_path()
        if vault_path:
            from pathlib import Path
            vault_display = f"Configured: {Path(vault_path).name}"
        else:
            vault_display = "Not configured"
        agent_info = [
            f"Vault: {vault_display}",
            f"Auto-accept: {'On' if agent_config.get_auto_accept() else 'Off'}",
            f"Backups: {'On' if agent_config.get_backup_before_edits() else 'Off'}"
        ]
        
        # File configuration  
        file_info = [
            "Backup: Centralized",
            "Auto-save: Enabled",
            "Format: Markdown"
        ]
        
    except Exception:
        # Fallback to static info if imports fail
        audio_info = ["Device: Built-in Microphone", "Sample Rate: 44.1kHz", "Channels: Mono"]
        model_info = ["Transcription: Local Whisper", "Whisper: medium", "GPT: gpt-4"]
        agent_info = ["Vault: Not configured", "Auto-accept: Off", "Backups: On"]
        file_info = ["Backup: Enabled", "Auto-save: On", "Format: Markdown"]
    
    # Configuration sections with Glyph colors
    sections = [
        ("🎙️ Audio", audio_info),
        ("🤖 Models", model_info),
        ("🤖 Agent", agent_info),
        ("📁 Files", file_info)
    ]
    
    # Create columns for each section with Glyph styling
    columns = []
    for title, items in sections:
        
        section_table = Table(
            show_header=False,
            box=box.HEAVY,
            title=title,
            title_style=f"bold {GLYPH_HIGHLIGHT}",
            border_style=GLYPH_SECONDARY
        )
        section_table.add_column("Setting", style=GLYPH_MUTED, width=15)
        
        for item in items:
            section_table.add_row(item)
        
        columns.append(section_table)
    
    # Display in responsive columns
    console.print(create_responsive_columns(columns))