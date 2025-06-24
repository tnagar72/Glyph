import itertools
from rich.console import Console
from rich.theme import Theme

# === Audio Configuration ===
SAMPLE_RATE = 44100
CHANNELS = 1
DURATION_LIMIT = 60
DEVICE_INDEX = 2  # MacBook Pro Microphone

# === Whisper Configuration ===
# Available models: tiny, base, small, medium, large
# Trade-off: accuracy vs speed vs memory usage
# - tiny/base: Fast but less accurate
# - small: Good balance 
# - medium: Better accuracy, slower
# - large: Best accuracy, slowest
WHISPER_MODEL = "medium"  # Upgraded from "base" for better accuracy

# === UI Elements ===
SPINNER_FRAMES = itertools.cycle(["|", "/", "-", "\\"])

# === Rich Theme Configuration ===
CUSTOM_THEME = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "green",
    "file": "bold cyan",
    "transcript": "italic bright_cyan",
    "diff.addition": "bold green",
    "diff.deletion": "bold red",
    "diff.context": "dim white",
    "diff.header": "bold magenta"
})

# Create a console instance with custom theme
rich_console = Console(theme=CUSTOM_THEME, width=120)

# === Verbose Logging ===
VERBOSE_MODE = False

def set_verbose(enabled: bool):
    """Enable or disable verbose output globally."""
    global VERBOSE_MODE
    VERBOSE_MODE = enabled

def verbose_print(message: str, style: str = "dim"):
    """Print message only if verbose mode is enabled."""
    if VERBOSE_MODE:
        rich_console.print(f"[{style}][VERBOSE] {message}[/{style}]")