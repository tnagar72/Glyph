#!/usr/bin/env python3

"""
Live transcription mode for real-time voice-to-text streaming.
Great for debugging and building toward live command streaming.
"""

import threading
import time
import queue
import sys
from datetime import datetime
from typing import Optional

import sounddevice as sd
import numpy as np
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

from transcription import transcribe_audio, save_transcript
from utils import SAMPLE_RATE, CHANNELS, DEVICE_INDEX, WHISPER_MODEL, verbose_print

console = Console()

class LiveTranscriber:
    """Real-time voice transcription with streaming output."""
    
    def __init__(self, model: str = WHISPER_MODEL, chunk_duration: float = 3.0):
        self.model = model
        self.chunk_duration = chunk_duration  # seconds
        self.chunk_size = int(SAMPLE_RATE * chunk_duration)
        
        self.audio_queue = queue.Queue()
        self.transcript_queue = queue.Queue()
        self.running = False
        
        self.total_transcripts = 0
        self.session_start = datetime.now()
        
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio input stream."""
        if status:
            verbose_print(f"Audio status: {status}")
        
        if self.running:
            # Add audio chunk to queue
            self.audio_queue.put(indata.copy())
    
    def transcription_worker(self):
        """Worker thread for processing audio chunks."""
        audio_buffer = []
        
        while self.running:
            try:
                # Get audio chunk with timeout
                chunk = self.audio_queue.get(timeout=0.1)
                audio_buffer.extend(chunk.flatten())
                
                # Process when we have enough audio
                if len(audio_buffer) >= self.chunk_size:
                    # Take chunk and keep remainder
                    audio_chunk = np.array(audio_buffer[:self.chunk_size])
                    audio_buffer = audio_buffer[self.chunk_size // 2:]  # 50% overlap
                    
                    # Transcribe chunk
                    transcript = transcribe_audio(audio_chunk)
                    
                    if transcript and transcript.strip():
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        self.transcript_queue.put((timestamp, transcript.strip()))
                        self.total_transcripts += 1
                        
            except queue.Empty:
                continue
            except Exception as e:
                verbose_print(f"Transcription error: {e}")
    
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
    
    def run_live_mode(self, save_transcripts: bool = True) -> None:
        """Run live transcription mode."""
        
        console.print("🎤 [bold green]Starting Live Transcription Mode[/bold green]")
        console.print("[dim]Speak naturally, transcription will appear in real-time...[/dim]\n")
        
        # Start audio stream
        self.running = True
        
        try:
            with sd.InputStream(
                device=DEVICE_INDEX,
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
                                
                                # Save transcript if enabled
                                if save_transcripts:
                                    save_transcript(f"[{timestamp}] {transcript}")
                                
                                # Output to stdout for piping
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
            console.print("\n🔇 [yellow]Live transcription stopped[/yellow]")
            
            # Session summary
            duration = (datetime.now() - self.session_start).total_seconds()
            console.print(f"📊 Session summary: {self.total_transcripts} transcripts in {duration:.1f}s")
    
    def run_simple_live_mode(self) -> None:
        """Run simple live mode for piping/debugging."""
        
        print("# Live Transcription Stream", file=sys.stderr)
        print("# Format: [HH:MM:SS] transcript", file=sys.stderr)
        print("# Press Ctrl+C to stop", file=sys.stderr)
        
        self.running = True
        
        try:
            with sd.InputStream(
                device=DEVICE_INDEX,
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
                        print(f"[{timestamp}] {transcript}", flush=True)
                        
                    except queue.Empty:
                        continue
                    except KeyboardInterrupt:
                        break
                        
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            print("# Live transcription ended", file=sys.stderr)

def run_live_transcription(model: str = WHISPER_MODEL, simple: bool = False, 
                          chunk_duration: float = 3.0) -> None:
    """
    Run live transcription mode.
    
    Args:
        model: Whisper model to use
        simple: If True, use simple output mode (good for piping)
        chunk_duration: Audio chunk duration in seconds
    """
    
    transcriber = LiveTranscriber(model, chunk_duration)
    
    if simple:
        transcriber.run_simple_live_mode()
    else:
        transcriber.run_live_mode()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Live Voice Transcription")
    parser.add_argument("--model", "-m", choices=["tiny", "base", "small", "medium", "large"], 
                       default=WHISPER_MODEL, help="Whisper model to use")
    parser.add_argument("--simple", "-s", action="store_true", help="Simple output mode (good for piping)")
    parser.add_argument("--chunk", "-c", type=float, default=3.0, help="Audio chunk duration in seconds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        from utils import set_verbose
        set_verbose(True)
    
    run_live_transcription(args.model, args.simple, args.chunk)