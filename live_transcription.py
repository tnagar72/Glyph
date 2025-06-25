#!/usr/bin/env python3

"""
Live transcription mode for real-time voice-to-text streaming.
Great for debugging and building toward live command streaming.
"""

import threading
import time
import queue
import sys
import string
from datetime import datetime
from typing import Optional
from pathlib import Path

import sounddevice as sd
import numpy as np
import pyperclip
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

import whisper
import scipy.io.wavfile
import tempfile
import os
from transcription import save_transcript
from utils import SAMPLE_RATE, CHANNELS, DEVICE_INDEX, WHISPER_MODEL, verbose_print
from audio_config import get_audio_device

console = Console()

class LiveTranscriber:
    """Real-time voice transcription with streaming output."""
    
    def __init__(self, model: str = WHISPER_MODEL, chunk_duration: float = 5.0):
        self.model = model
        self.chunk_duration = chunk_duration  # seconds
        self.chunk_size = int(SAMPLE_RATE * chunk_duration)
        
        self.audio_queue = queue.Queue()
        self.transcript_queue = queue.Queue()
        self.running = False
        
        self.total_transcripts = 0
        self.session_start = datetime.now()
        self.chunk_start_time = None  # Track when chunk recording started
        self.session_transcript_file = None  # Single file for entire session
        self.clipboard_text = ""  # Accumulated text for clipboard mode
        self._whisper_model = None  # Cache for the whisper model
        
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio input stream."""
        if status:
            verbose_print(f"Audio status: {status}")
        
        if self.running:
            # Add audio chunk to queue with timestamp
            current_time = datetime.now()
            self.audio_queue.put((indata.copy(), current_time))
    
    def load_whisper_model(self):
        """Load and cache the Whisper model for this transcriber."""
        if self._whisper_model is None:
            verbose_print(f"Loading Whisper model '{self.model}' (this may take a moment)...")
            self._whisper_model = whisper.load_model(self.model)
            verbose_print(f"Whisper model '{self.model}' loaded successfully")
        return self._whisper_model
    
    def transcribe_audio_with_model(self, audio_data):
        """Transcribe audio data using this transcriber's configured model."""
        if audio_data is None or len(audio_data) == 0:
            return None
        
        try:
            # Load the model (cached after first use)
            model = self.load_whisper_model()
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                scipy.io.wavfile.write(tmpfile.name, SAMPLE_RATE, audio_data)
                verbose_print(f"Saved audio to temporary file: {tmpfile.name}")
                
                # Transcribe with better parameters for accuracy
                verbose_print("Starting Whisper transcription with optimized parameters...")
                result = model.transcribe(
                    tmpfile.name,
                    language="en",  # Specify English for better accuracy
                    task="transcribe",  # Explicit task specification
                    temperature=0.0,  # Lower temperature for more consistent results
                    best_of=2,  # Try multiple decoding attempts for better accuracy
                    beam_size=5,  # Use beam search for better quality
                    fp16=False  # Use fp32 for better accuracy on CPU
                )
                verbose_print("Whisper transcription completed")
                
                # Clean up temporary file
                try:
                    os.unlink(tmpfile.name)
                    verbose_print(f"Cleaned up temporary file: {tmpfile.name}")
                except:
                    pass  # Ignore cleanup errors
                    
                return result['text'].strip()
                
        except Exception as e:
            verbose_print(f"Transcription error: {e}")
            return None
    
    def transcription_worker(self):
        """Worker thread for processing audio chunks."""
        audio_buffer = []
        chunk_start_time = None
        last_transcript = ""  # Track to avoid duplicates
        recent_transcripts = {}  # Track recent transcripts with timestamps
        
        while self.running:
            try:
                # Get audio chunk with timeout
                chunk_data, chunk_time = self.audio_queue.get(timeout=0.1)
                audio_buffer.extend(chunk_data.flatten())
                
                # Set chunk start time when we start collecting audio
                if chunk_start_time is None:
                    chunk_start_time = chunk_time
                
                # Process when we have enough audio
                if len(audio_buffer) >= self.chunk_size:
                    # Take chunk and keep remainder
                    audio_chunk = np.array(audio_buffer[:self.chunk_size])
                    audio_buffer = audio_buffer[self.chunk_size // 2:]  # 50% overlap
                    
                    # Use the timestamp from when this chunk started
                    timestamp_to_use = chunk_start_time if chunk_start_time else datetime.now()
                    # Reset for next chunk
                    chunk_start_time = None
                    
                    # Check if chunk has enough volume to be speech
                    volume = np.sqrt(np.mean(audio_chunk**2))
                    verbose_print(f"Audio volume: {volume:.4f}")
                    if volume < 0.005:  # Lowered threshold to be more sensitive to speech
                        verbose_print(f"Volume too low ({volume:.4f}), skipping chunk")
                        continue
                    
                    # Transcribe chunk using the configured model
                    transcript = self.transcribe_audio_with_model(audio_chunk)
                    
                    # Debug: Always show what was transcribed
                    if transcript and transcript.strip():
                        verbose_print(f"Raw transcript: '{transcript.strip()}'")
                    
                    if transcript and transcript.strip() and len(transcript.strip()) > 2:
                        clean_transcript = transcript.strip()
                        clean_lower = clean_transcript.lower()
                        
                        # Remove punctuation for better noise detection
                        clean_no_punct = clean_lower.translate(str.maketrans('', '', string.punctuation))
                        
                        # Enhanced filtering for common noise/artifacts
                        exact_noise_phrases = [
                            'thanks for watching', 'thank you for watching',
                            'thanks for listening', 'thank you for listening',
                            'you', 'yeah', 'uh', 'um', 'hmm', 'ah',
                            'bye', 'goodbye', 'see you later'
                        ]
                        
                        partial_noise_phrases = [
                            'subscribe', 'like and subscribe'
                        ]
                        
                        # Skip if it's noise, duplicate, or too recent
                        is_exact_noise = clean_no_punct in exact_noise_phrases
                        is_partial_noise = any(noise in clean_no_punct for noise in partial_noise_phrases)
                        is_duplicate = clean_transcript == last_transcript
                        
                        # Check if this transcript appeared recently (within 10 seconds)
                        current_time = timestamp_to_use
                        is_too_recent = False
                        if clean_transcript in recent_transcripts:
                            time_diff = (current_time - recent_transcripts[clean_transcript]).total_seconds()
                            if time_diff < 10:  # Same transcript within 10 seconds
                                is_too_recent = True
                        
                        # Debug: Show filtering decision
                        verbose_print(f"Transcript: '{clean_transcript}' -> No punct: '{clean_no_punct}'")
                        verbose_print(f"Exact noise: {is_exact_noise}, Partial noise: {is_partial_noise}, Duplicate: {is_duplicate}, Too recent: {is_too_recent}")
                        
                        if is_exact_noise or is_partial_noise or is_duplicate or is_too_recent:
                            verbose_print(f"🚫 FILTERED: '{clean_transcript}' (noise:{is_exact_noise}, partial:{is_partial_noise}, dup:{is_duplicate}, recent:{is_too_recent})")
                            continue
                        else:
                            verbose_print(f"✅ KEEPING: '{clean_transcript}'")
                        
                        # Calculate session-relative timestamp
                        elapsed_seconds = (timestamp_to_use - self.session_start).total_seconds()
                        minutes = int(elapsed_seconds // 60)
                        seconds = int(elapsed_seconds % 60)
                        session_timestamp = f"{minutes:02d}:{seconds:02d}"
                        
                        self.transcript_queue.put((session_timestamp, clean_transcript))
                        self.total_transcripts += 1
                        last_transcript = clean_transcript
                        
                        # Update recent transcripts tracking
                        recent_transcripts[clean_transcript] = current_time
                        
                        # Add to clipboard text (for clipboard mode)
                        if self.clipboard_text:
                            self.clipboard_text += " " + clean_transcript
                        else:
                            self.clipboard_text = clean_transcript
                        
            except queue.Empty:
                continue
            except Exception as e:
                verbose_print(f"Transcription error: {e}")
    
    def initialize_session_transcript_file(self):
        """Initialize a single transcript file for this live session."""
        if self.session_transcript_file is None:
            Path("transcripts").mkdir(exist_ok=True)
            timestamp = self.session_start.strftime('%Y-%m-%d_%H-%M-%S')
            self.session_transcript_file = f"transcripts/live_session_{timestamp}.txt"
            
            # Write session header
            with open(self.session_transcript_file, "w") as f:
                f.write(f"# Live Transcription Session\n")
                f.write(f"# Started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Model: {self.model}\n")
                f.write(f"# Chunk Duration: {self.chunk_duration}s\n")
                f.write(f"#\n\n")
    
    def append_to_session_transcript(self, timestamp: str, transcript: str):
        """Append a single transcript to the session file."""
        if self.session_transcript_file:
            with open(self.session_transcript_file, "a") as f:
                f.write(f"[{timestamp}] {transcript}\n")
    
    def finalize_session_transcript(self):
        """Finalize the session transcript file with summary."""
        if self.session_transcript_file:
            duration = (datetime.now() - self.session_start).total_seconds()
            with open(self.session_transcript_file, "a") as f:
                f.write(f"\n# Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Duration: {duration:.1f}s\n")
                f.write(f"# Total transcripts: {self.total_transcripts}\n")
    
    def create_live_display(self, transcripts: list) -> Panel:
        """Create the live display panel."""
        
        # Header with session info
        duration = (datetime.now() - self.session_start).total_seconds()
        header = Text()
        header.append("🎤 ", style="bold red")
        header.append("LIVE TRANSCRIPTION", style="bold white")
        header.append(f" • {duration:.0f}s • {self.total_transcripts} transcripts", style="dim")
        
        # Recent transcripts (last 10)
        recent_transcripts = transcripts[-10:] if transcripts else []
        
        if not recent_transcripts:
            content = Text("🔇 Waiting for speech...", style="dim italic")
        else:
            content = Text()
            for i, (timestamp, text) in enumerate(recent_transcripts):
                if i > 0:
                    content.append("\n")
                content.append(f"[{timestamp}] ", style="dim cyan")
                content.append(text, style="white")
        
        # Instructions
        footer = Text()
        footer.append("💡 ", style="yellow")
        footer.append("Speak normally • Press Ctrl+C to stop • Transcripts auto-saved", style="dim")
        
        full_content = Text()
        full_content.append(content)
        full_content.append("\n\n")
        full_content.append(footer)
        
        return Panel(
            full_content,
            title=header,
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2)
        )
    
    def run_live_mode(self, save_transcripts: bool = True, output_to_stdout: bool = False, clipboard_mode: bool = False) -> None:
        """Run live transcription mode."""
        
        # Check if verbose mode is enabled - if so, fall back to simple mode
        from utils import is_verbose
        if is_verbose():
            console.print("🎤 [bold green]Starting Live Transcription Mode (Verbose)[/bold green]")
            console.print("[dim]Using simple mode due to verbose output...[/dim]\n")
            return self.run_simple_live_mode(save_transcripts, clipboard_mode)
        
        mode_text = "Clipboard Mode" if clipboard_mode else "Live Transcription Mode"
        console.print(f"🎤 [bold green]Starting {mode_text}[/bold green]")
        if clipboard_mode:
            console.print("[dim]Speak naturally, transcripts will be copied to clipboard...[/dim]\n")
        else:
            console.print("[dim]Speak naturally, transcription will appear in real-time...[/dim]\n")
        
        # Initialize session transcript file if saving is enabled (not in clipboard mode)
        if save_transcripts and not clipboard_mode:
            self.initialize_session_transcript_file()
        
        # Get configured audio device
        audio_device = get_audio_device()
        if audio_device is None:
            console.print("[red]❌ No audio device configured. Run 'glyph --setup-audio' first.[/red]")
            return
        
        # Start audio stream
        self.running = True
        
        try:
            with sd.InputStream(
                device=audio_device,
                callback=self.audio_callback,
                channels=CHANNELS,
                samplerate=SAMPLE_RATE,
                blocksize=1024
            ):
                # Start transcription worker thread
                transcription_thread = threading.Thread(target=self.transcription_worker)
                transcription_thread.daemon = True
                transcription_thread.start()
                
                transcripts = []
                
                # Live display loop
                with Live(self.create_live_display(transcripts), refresh_per_second=2) as live:
                    while self.running:
                        try:
                            # Check for new transcripts
                            while not self.transcript_queue.empty():
                                timestamp, transcript = self.transcript_queue.get_nowait()
                                transcripts.append((timestamp, transcript))
                                
                                # Save transcript to session file if enabled (not in clipboard mode)
                                if save_transcripts and not clipboard_mode:
                                    self.append_to_session_transcript(timestamp, transcript)
                                
                                # Output to stdout for piping if enabled
                                if output_to_stdout:
                                    print(f"[{timestamp}] {transcript}", file=sys.stdout, flush=True)
                            
                            # Update display
                            live.update(self.create_live_display(transcripts))
                            time.sleep(0.1)
                            
                        except KeyboardInterrupt:
                            break
                        except Exception as e:
                            verbose_print(f"Display error: {e}")
                            
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            
            # Finalize session transcript file or copy to clipboard
            if clipboard_mode and self.clipboard_text:
                pyperclip.copy(self.clipboard_text)
                console.print(f"📋 [green]Transcription copied to clipboard ({len(self.clipboard_text)} characters)[/green]")
            elif save_transcripts and not clipboard_mode:
                self.finalize_session_transcript()
                if self.session_transcript_file:
                    console.print(f"💾 [green]Session transcript saved: {self.session_transcript_file}[/green]")
            
            console.print("\n🔇 [yellow]Live transcription stopped[/yellow]")
            
            # Session summary
            duration = (datetime.now() - self.session_start).total_seconds()
            console.print(f"📊 Session summary: {self.total_transcripts} transcripts in {duration:.1f}s")
    
    def run_simple_live_mode(self, save_transcripts: bool = True, clipboard_mode: bool = False) -> None:
        """Run simple live mode for piping/debugging."""
        
        mode_text = "Clipboard Mode" if clipboard_mode else "Live Transcription Stream"
        print(f"# {mode_text}", file=sys.stderr)
        if clipboard_mode:
            print("# Transcripts will be copied to clipboard on exit", file=sys.stderr)
        else:
            print("# Format: [HH:MM:SS] transcript", file=sys.stderr)
        print("# Press Ctrl+C to stop", file=sys.stderr)
        
        # Initialize session transcript file if saving is enabled (not in clipboard mode)
        if save_transcripts and not clipboard_mode:
            self.initialize_session_transcript_file()
            print(f"# Saving to: {self.session_transcript_file}", file=sys.stderr)
        
        # Get configured audio device
        audio_device = get_audio_device()
        if audio_device is None:
            print("❌ No audio device configured. Run 'glyph --setup-audio' first.", file=sys.stderr)
            return
        
        self.running = True
        
        try:
            with sd.InputStream(
                device=audio_device,
                callback=self.audio_callback,
                channels=CHANNELS,
                samplerate=SAMPLE_RATE,
                blocksize=1024
            ):
                # Start transcription worker
                transcription_thread = threading.Thread(target=self.transcription_worker)
                transcription_thread.daemon = True
                transcription_thread.start()
                
                # Simple output loop
                while self.running:
                    try:
                        timestamp, transcript = self.transcript_queue.get(timeout=0.1)
                        if clipboard_mode:
                            # In clipboard mode, only output the raw transcript text (no timestamp)
                            print(transcript, flush=True)
                        else:
                            print(f"[{timestamp}] {transcript}", flush=True)
                        
                        # Save to session file if enabled (not in clipboard mode)
                        if save_transcripts and not clipboard_mode:
                            self.append_to_session_transcript(timestamp, transcript)
                        
                    except queue.Empty:
                        continue
                    except KeyboardInterrupt:
                        break
                        
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            
            # Finalize session transcript file or copy to clipboard
            if clipboard_mode and self.clipboard_text:
                pyperclip.copy(self.clipboard_text)
                print(f"# Transcription copied to clipboard ({len(self.clipboard_text)} characters)", file=sys.stderr)
            elif save_transcripts and not clipboard_mode:
                self.finalize_session_transcript()
                if self.session_transcript_file:
                    print(f"# Session transcript saved: {self.session_transcript_file}", file=sys.stderr)
            
            print("# Live transcription ended", file=sys.stderr)

def run_live_transcription(model: str = WHISPER_MODEL, simple: bool = False, 
                          chunk_duration: float = 5.0, clipboard_mode: bool = False) -> None:
    """
    Run live transcription mode.
    
    Args:
        model: Whisper model to use
        simple: If True, use simple output mode (good for piping)
        chunk_duration: Audio chunk duration in seconds
        clipboard_mode: If True, copy transcripts to clipboard instead of saving
    """
    
    transcriber = LiveTranscriber(model, chunk_duration)
    
    if simple:
        transcriber.run_simple_live_mode(save_transcripts=not clipboard_mode, clipboard_mode=clipboard_mode)
    else:
        transcriber.run_live_mode(save_transcripts=not clipboard_mode, clipboard_mode=clipboard_mode)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Live Voice Transcription")
    parser.add_argument("--model", "-m", choices=["tiny", "base", "small", "medium", "large"], 
                       default=WHISPER_MODEL, help="Whisper model to use")
    parser.add_argument("--simple", "-s", action="store_true", help="Simple output mode (good for piping)")
    parser.add_argument("--chunk", "-c", type=float, default=5.0, help="Audio chunk duration in seconds")
    parser.add_argument("--clipboard", action="store_true", help="Copy transcripts to clipboard instead of saving")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        from utils import set_verbose
        set_verbose(True)
    
    run_live_transcription(args.model, args.simple, args.chunk, args.clipboard)