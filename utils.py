import itertools
import sounddevice as sd
from rich.console import Console
from rich.theme import Theme

# === Audio Configuration ===
SAMPLE_RATE = 44100
CHANNELS = 1
DURATION_LIMIT = 60
DEVICE_INDEX = 2  # MacBook Pro Microphone (device 2 based on current system)

# === Whisper Configuration ===
# Available models: tiny, base, small, medium, large
# Trade-off: accuracy vs speed vs memory usage
# - tiny/base: Fast but less accurate
# - small: Good balance 
# - medium: Better accuracy, slower
# - large: Best accuracy, slowest
WHISPER_MODEL = "medium"  # Default fallback, can be overridden by configured model

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

def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return VERBOSE_MODE

def verbose_print(message: str, style: str = "dim"):
    """Print message only if verbose mode is enabled."""
    if VERBOSE_MODE:
        rich_console.print(f"[{style}][VERBOSE] {message}[/{style}]")

def get_configured_model() -> str:
    """Get the configured default model or fallback to WHISPER_MODEL."""
    try:
        from model_config import get_default_model
        return get_default_model()
    except ImportError:
        return WHISPER_MODEL

def validate_audio_device():
    """Validate and auto-correct audio device configuration."""
    global DEVICE_INDEX
    
    try:
        devices = sd.query_devices()
        current_device = devices[DEVICE_INDEX]
        
        # Check if the current device supports input
        if current_device['max_input_channels'] < 1:
            verbose_print(f"⚠️ Device {DEVICE_INDEX} ({current_device['name']}) has no input channels")
            
            # Prefer MacBook Pro Microphone if available
            for i, device in enumerate(devices):
                if device['max_input_channels'] >= 1 and "MacBook Pro Microphone" in device['name']:
                    verbose_print(f"🔧 Switching to preferred device {i}: {device['name']}")
                    DEVICE_INDEX = i
                    break
            else:
                # Fall back to any device with input channels
                for i, device in enumerate(devices):
                    if device['max_input_channels'] >= 1:
                        verbose_print(f"🔧 Switching to device {i}: {device['name']}")
                        DEVICE_INDEX = i
                        break
                else:
                    raise RuntimeError("No audio input devices found")
        
        verbose_print(f"✅ Using audio device {DEVICE_INDEX}: {devices[DEVICE_INDEX]['name']}")
        return DEVICE_INDEX
        
    except Exception as e:
        verbose_print(f"❌ Audio device validation failed: {e}")
        return None