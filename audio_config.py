"""
Smart audio device configuration and management for Glyph.

This module provides intelligent audio device detection, configuration, and management
that works across different systems and setups.
"""

import os
import json
import platform
import sounddevice as sd
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt
from typing import Optional, Dict, List, Tuple

console = Console()

class AudioDeviceManager:
    """Manages audio device detection, configuration, and persistence."""
    
    def __init__(self):
        self.config_dir = Path.home() / '.glyph'
        self.config_file = self.config_dir / 'audio_config.json'
        self.config_dir.mkdir(exist_ok=True)
        
    def get_suitable_input_devices(self) -> List[Tuple[int, Dict]]:
        """Get all devices suitable for microphone input."""
        devices = sd.query_devices()
        suitable_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] >= 1:
                suitable_devices.append((i, device))
        
        return suitable_devices
    
    def score_device_suitability(self, device_info: Dict) -> int:
        """Score how suitable a device is for voice recording (higher = better)."""
        score = 0
        name = device_info['name'].lower()
        
        # Prefer built-in microphones
        if any(keyword in name for keyword in ['microphone', 'mic', 'built-in']):
            score += 50
            
        # Prefer specific device types
        if 'macbook' in name and 'microphone' in name:
            score += 100  # MacBook Pro/Air Microphone
        elif 'imac' in name and 'microphone' in name:
            score += 100  # iMac Microphone
        elif 'default' in name:
            score += 80   # System default
        elif 'realtek' in name and 'microphone' in name:
            score += 90   # Windows built-in
        elif 'usb' in name and 'microphone' in name:
            score += 70   # USB microphones
        elif 'headset' in name or 'headphone' in name:
            score += 60   # Headset microphones
            
        # Avoid problematic devices
        if any(avoid in name for avoid in ['speaker', 'output', 'hdmi', 'display']):
            score -= 100
        if any(avoid in name for avoid in ['virtual', 'null', 'dummy']):
            score -= 50
        if any(avoid in name for avoid in ['zoom', 'teams', 'skype', 'discord']):
            score -= 30  # App-specific devices (lower priority)
            
        # Prefer devices with exactly 1 channel for voice
        if device_info['max_input_channels'] == 1:
            score += 20
        elif device_info['max_input_channels'] == 2:
            score += 10
            
        return max(0, score)  # Don't go negative
    
    def auto_detect_best_device(self) -> Optional[int]:
        """Automatically detect the best microphone device."""
        suitable_devices = self.get_suitable_input_devices()
        
        if not suitable_devices:
            return None
            
        # Score all devices and pick the best one
        best_device = None
        best_score = -1
        
        for device_id, device_info in suitable_devices:
            score = self.score_device_suitability(device_info)
            if score > best_score:
                best_score = score
                best_device = device_id
                
        return best_device
    
    def test_device(self, device_id: int, duration: float = 1.0) -> bool:
        """Test if a device can record audio successfully."""
        try:
            # Quick recording test
            with sd.InputStream(device=device_id, channels=1, samplerate=44100) as stream:
                data, _ = stream.read(int(44100 * duration))
                return len(data) > 0 and data.max() > 0.001  # Check for actual audio
        except Exception:
            return False
    
    def load_saved_config(self) -> Optional[Dict]:
        """Load saved audio configuration."""
        if not self.config_file.exists():
            return None
            
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def save_config(self, device_id: int, device_name: str):
        """Save audio device configuration."""
        config = {
            'device_id': device_id,
            'device_name': device_name,
            'platform': platform.system(),
            'version': '1.0'
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not save audio config: {e}[/yellow]")
    
    def show_device_selection_wizard(self) -> Optional[int]:
        """Interactive wizard to help user select the best audio device."""
        console.print("\n[bold blue]🎙️ Audio Device Configuration Wizard[/bold blue]")
        console.print("Let's find the best microphone for Glyph!\n")
        
        suitable_devices = self.get_suitable_input_devices()
        
        if not suitable_devices:
            console.print("[red]❌ No audio input devices found![/red]")
            return None
        
        # Show available devices in a nice table
        table = Table(title="Available Audio Input Devices")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Device Name", style="magenta")
        table.add_column("Channels", justify="center")
        table.add_column("Suitability", justify="center")
        
        for device_id, device_info in suitable_devices:
            score = self.score_device_suitability(device_info)
            suitability = "🟢 Excellent" if score >= 80 else "🟡 Good" if score >= 50 else "🔴 Poor"
            table.add_row(
                str(device_id),
                device_info['name'],
                str(device_info['max_input_channels']),
                suitability
            )
        
        console.print(table)
        
        # Auto-recommend the best device
        best_device = self.auto_detect_best_device()
        if best_device is not None:
            best_name = suitable_devices[[i for i, (id, _) in enumerate(suitable_devices) if id == best_device][0]][1]['name']
            console.print(f"\n[green]🎯 Recommended: Device {best_device} ({best_name})[/green]")
            
            if Confirm.ask("Use the recommended device?", default=True):
                return best_device
        
        # Manual selection
        console.print("\n[yellow]Manual Selection:[/yellow]")
        while True:
            try:
                choice = IntPrompt.ask("Enter device ID", 
                                     choices=[str(id) for id, _ in suitable_devices])
                return choice
            except KeyboardInterrupt:
                return None
    
    def get_configured_device(self, force_setup: bool = False) -> Optional[int]:
        """Get the configured audio device, with setup if needed."""
        
        # Try to load saved configuration first
        if not force_setup:
            saved_config = self.load_saved_config()
            if saved_config:
                device_id = saved_config['device_id']
                device_name = saved_config['device_name']
                
                # Verify the saved device still exists and works
                try:
                    devices = sd.query_devices()
                    if (device_id < len(devices) and 
                        devices[device_id]['max_input_channels'] >= 1 and
                        self.test_device(device_id, 0.5)):
                        
                        console.print(f"[green]✅ Using saved audio device: {device_name}[/green]")
                        return device_id
                    else:
                        console.print(f"[yellow]⚠️ Saved device '{device_name}' no longer available[/yellow]")
                except Exception:
                    console.print("[yellow]⚠️ Saved audio configuration is invalid[/yellow]")
        
        # Auto-detect if no saved config or saved device failed
        console.print("[blue]🔍 Auto-detecting audio device...[/blue]")
        best_device = self.auto_detect_best_device()
        
        if best_device is not None:
            devices = sd.query_devices()
            device_name = devices[best_device]['name']
            
            # Test the auto-detected device
            if self.test_device(best_device, 0.5):
                console.print(f"[green]✅ Auto-detected device: {device_name}[/green]")
                self.save_config(best_device, device_name)
                return best_device
            else:
                console.print(f"[yellow]⚠️ Auto-detected device '{device_name}' failed test[/yellow]")
        
        # Fall back to interactive wizard
        console.print("[yellow]🛠️ Manual device selection required[/yellow]")
        selected_device = self.show_device_selection_wizard()
        
        if selected_device is not None:
            devices = sd.query_devices()
            device_name = devices[selected_device]['name']
            self.save_config(selected_device, device_name)
            console.print(f"[green]✅ Audio device configured: {device_name}[/green]")
        
        return selected_device

# Global instance
audio_manager = AudioDeviceManager()

def get_audio_device(force_setup: bool = False) -> Optional[int]:
    """Get the best audio device for recording."""
    return audio_manager.get_configured_device(force_setup)

def setup_audio_device() -> Optional[int]:
    """Force audio device setup wizard."""
    return audio_manager.show_device_selection_wizard()