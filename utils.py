import itertools
import sounddevice as sd
import subprocess
import platform
import os
from pathlib import Path
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

def is_obsidian_running() -> bool:
    """Check if Obsidian is currently running."""
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            result = subprocess.run(
                ["pgrep", "-f", "Obsidian"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        elif system == "Windows":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Obsidian.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "Obsidian.exe" in result.stdout
        elif system == "Linux":
            result = subprocess.run(
                ["pgrep", "-f", "obsidian"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        else:
            verbose_print(f"⚠️ Unsupported platform: {system}")
            return False
    except Exception as e:
        verbose_print(f"❌ Failed to check if Obsidian is running: {e}")
        return False

def open_obsidian_with_file(file_path: str) -> bool:
    """
    Open Obsidian and navigate to the specified file.
    
    Args:
        file_path: Path to the markdown file to open
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        file_path = Path(file_path).resolve()
        
        # Check if file exists
        if not file_path.exists():
            verbose_print(f"❌ File does not exist: {file_path}")
            return False
        
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # Try multiple URI formats for better compatibility
            import urllib.parse
            
            # Method 1: Try with vault and file parameters (most reliable)
            # First, try to detect if this is in an Obsidian vault
            vault_root = None
            current_path = file_path.parent
            
            # Look for .obsidian folder to identify vault root
            while current_path.parent != current_path:  # Not at filesystem root
                if (current_path / ".obsidian").exists():
                    vault_root = current_path
                    break
                current_path = current_path.parent
            
            if vault_root:
                # Use vault + file format for nested files (Obsidian's preferred method)
                vault_name = vault_root.name
                relative_path = file_path.relative_to(vault_root)
                # Encode spaces and special chars but keep forward slashes
                encoded_file = urllib.parse.quote(str(relative_path), safe='/')
                encoded_vault = urllib.parse.quote(vault_name)
                obsidian_uri = f"obsidian://open?vault={encoded_vault}&file={encoded_file}"
                verbose_print(f"Trying vault+file URI: {obsidian_uri}")
            else:
                # Fallback to absolute path
                encoded_path = urllib.parse.quote(str(file_path), safe='/:')
                obsidian_uri = f"obsidian://open?path={encoded_path}"
                verbose_print(f"Trying absolute path URI: {obsidian_uri}")
            
            # First try to open with the URI scheme
            result = subprocess.run(
                ["open", obsidian_uri],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                verbose_print(f"✅ Opened file in Obsidian: {file_path.name}")
                return True
            else:
                # Fallback: Open Obsidian app first, then try to open the file
                subprocess.run(["open", "-a", "Obsidian"], timeout=10)
                # Give Obsidian a moment to start
                import time
                time.sleep(2)
                # Try the URI again with proper encoding
                result = subprocess.run(
                    ["open", obsidian_uri],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    verbose_print(f"✅ Opened file in Obsidian (after launching app): {file_path.name}")
                    return True
                    
        elif system == "Windows":
            # Try obsidian:// URI scheme on Windows with vault detection
            import urllib.parse
            
            # Look for .obsidian folder to identify vault root
            vault_root = None
            current_path = file_path.parent
            
            while current_path.parent != current_path:  # Not at filesystem root
                if (current_path / ".obsidian").exists():
                    vault_root = current_path
                    break
                current_path = current_path.parent
            
            if vault_root:
                # Use vault + file format for nested files
                vault_name = vault_root.name
                relative_path = file_path.relative_to(vault_root)
                encoded_file = urllib.parse.quote(str(relative_path), safe='/')
                obsidian_uri = f"obsidian://open?vault={urllib.parse.quote(vault_name)}&file={encoded_file}"
            else:
                # Fallback to absolute path
                encoded_path = urllib.parse.quote(str(file_path), safe='/:')
                obsidian_uri = f"obsidian://open?path={encoded_path}"
            result = subprocess.run(
                ["start", "", obsidian_uri],
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                verbose_print(f"✅ Opened file in Obsidian: {file_path.name}")
                return True
                
        elif system == "Linux":
            # Try obsidian:// URI scheme on Linux
            obsidian_uri = f"obsidian://open?path={file_path}"
            result = subprocess.run(
                ["xdg-open", obsidian_uri],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                verbose_print(f"✅ Opened file in Obsidian: {file_path.name}")
                return True
        
        # If we get here, the URI method failed
        verbose_print(f"⚠️ Could not open file in Obsidian using URI scheme")
        return False
        
    except subprocess.TimeoutExpired:
        verbose_print("⚠️ Timeout while trying to open Obsidian")
        return False
    except Exception as e:
        verbose_print(f"❌ Failed to open Obsidian with file: {e}")
        return False

def open_in_obsidian_if_available(file_path: str) -> None:
    """
    Attempt to open the file in Obsidian with user feedback.
    This is a high-level function that provides user-friendly messaging.
    
    Args:
        file_path: Path to the markdown file to open
    """
    from ui_helpers import show_success_message, show_warning_message
    
    try:
        file_path = Path(file_path).resolve()
        
        # Check if Obsidian is running
        obsidian_running = is_obsidian_running()
        
        if obsidian_running:
            verbose_print("📱 Obsidian is already running")
        else:
            verbose_print("📱 Obsidian is not running, will attempt to launch it")
        
        # Attempt to open the file
        success = open_obsidian_with_file(str(file_path))
        
        if success:
            if obsidian_running:
                show_success_message(
                    f"📱 File opened in Obsidian: {file_path.name}",
                    "The modified file is now ready for review in Obsidian."
                )
            else:
                show_success_message(
                    f"📱 Obsidian launched with file: {file_path.name}",
                    "The modified file is now ready for review."
                )
        else:
            show_warning_message(
                "📱 Could not open file in Obsidian automatically",
                f"Please manually open: {file_path}"
            )
            
    except Exception as e:
        verbose_print(f"❌ Error in open_in_obsidian_if_available: {e}")
        show_warning_message(
            "📱 Could not open file in Obsidian",
            f"Please manually open: {file_path}"
        )