#!/usr/bin/env python3

import argparse
import sounddevice as sd
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich import box

__version__ = "1.0.0"

from recording import run_voice_capture, run_simple_record, run_enter_stop_capture
from transcription import transcribe_audio, save_transcript
from md_file import read_markdown_file, write_markdown_file, validate_markdown_path
from llm import call_gpt_api
from cleaning import extract_markdown_from_response
from diff import show_diff, get_user_approval, show_change_summary, count_changes
from session_logger import get_session_logger, end_session
from undo_manager import UndoManager
from utils import DEVICE_INDEX, WHISPER_MODEL, SAMPLE_RATE

console = Console()

def handle_undo_operation(file_path: str, verbose: bool = False):
    """Handle undo operation for a specific file."""
    if verbose:
        from utils import set_verbose
        set_verbose(True)
    
    try:
        # Validate the file path
        validated_path = validate_markdown_path(file_path)
        
        # Find available backups
        backups = UndoManager.list_backups(str(validated_path))
        
        if not backups:
            error_panel = Panel(
                f"[red]❌ No backups found for {validated_path}[/red]\n\n"
                "No backup files were found. The file may not have been edited yet.",
                title="Undo Error",
                style="red",
                box=box.ROUNDED
            )
            console.print(error_panel)
            return
        
        # Show available backups
        console.print(f"\n📋 Found {len(backups)} backup(s) for [cyan]{validated_path}[/cyan]:")
        
        for i, backup in enumerate(backups[:5], 1):  # Show max 5 backups
            info = UndoManager.get_backup_info(backup)
            console.print(f"  {i}. [dim]{info['created']}[/dim] - {backup}")
        
        # Ask for confirmation
        latest_backup = backups[0]
        info = UndoManager.get_backup_info(latest_backup)
        
        confirm_panel = Panel(
            f"[yellow]⚠️ This will restore {validated_path} from:[/yellow]\n"
            f"[cyan]{latest_backup}[/cyan]\n"
            f"[dim]Created: {info['created']}[/dim]\n\n"
            f"[red]Current content will be backed up before restoration.[/red]",
            title="Confirm Undo",
            style="yellow",
            box=box.ROUNDED
        )
        console.print(confirm_panel)
        
        console.print("🔄 [bold yellow]Restore from backup?[/bold yellow] [dim]\\[y/N][/dim]: ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            success = UndoManager.restore_from_backup(str(validated_path))
            
            if success:
                success_panel = Panel(
                    f"✅ [green]Successfully restored {validated_path}[/green]\n"
                    f"[dim]Restored from: {latest_backup}[/dim]",
                    title="Undo Complete",
                    style="green",
                    box=box.ROUNDED
                )
                console.print(success_panel)
            else:
                console.print("❌ [red]Failed to restore from backup[/red]")
        else:
            console.print("❌ [yellow]Undo operation cancelled[/yellow]")
            
    except Exception as e:
        error_panel = Panel(
            f"[red]❌ Undo operation failed:[/red] {str(e)}",
            style="red",
            box=box.ROUNDED
        )
        console.print(error_panel)

def handle_live_mode(args):
    """Handle live transcription mode."""
    if args.verbose:
        from utils import set_verbose
        set_verbose(True)
    
    from live_transcription import run_live_transcription
    
    model = args.whisper_model if args.whisper_model else WHISPER_MODEL
    
    # Check if we're in a pipeline (stdout is not a terminal)
    import sys
    simple_mode = not sys.stdout.isatty()
    
    try:
        run_live_transcription(model=model, simple=simple_mode)
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Live transcription stopped[/yellow]")

def handle_interactive_mode(args):
    """Handle interactive CLI mode."""
    if args.verbose:
        from utils import set_verbose
        set_verbose(True)
    
    from interactive_cli import InteractiveCLI
    
    cli = InteractiveCLI()
    settings = cli.run_interactive_mode()
    
    if settings is None:
        return  # User quit
    
    if settings.get('mode') == 'live':
        # Switch to live mode
        args.live = True
        handle_live_mode(args)
        return
    
    # Apply settings and run normal mode
    if settings.get('verbose'):
        from utils import set_verbose
        set_verbose(True)
    
    # Override args with interactive settings
    args.file = settings['file']
    args.whisper_model = settings['whisper_model']
    args.dry_run = settings['dry_run']
    args.transcript_only = settings['transcript_only']
    
    # Continue with normal mode using updated args
    run_normal_mode(args)

def run_normal_mode(args):
    """Run the normal voice editing mode."""
    
    # Initialize session logger
    logger = get_session_logger()
    
    # Set verbose mode if specified
    if args.verbose:
        from utils import set_verbose
        set_verbose(True)
    
    # Override default Whisper model if specified
    if args.whisper_model:
        import utils
        utils.WHISPER_MODEL = args.whisper_model
    
    # Beautiful header
    title_text = Text()
    title_text.append("🎙️ ", style="bold yellow")
    title_text.append("Voice-controlled Markdown Editor", style="bold white")
    
    header = Panel(
        title_text,
        style="blue",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    console.print(header)
    
    # Set up audio device
    sd.default.device = [DEVICE_INDEX, None]  # [input, output]
    
    # Recording Phase
    if args.enter_stop:
        instruction_text = "🎤 [bold yellow]Recording Phase[/bold yellow]\nRecording will start automatically. Press ENTER when finished speaking..."
    else:
        instruction_text = "🎤 [bold yellow]Recording Phase[/bold yellow]\nHold SPACEBAR to record your voice command..."
    
    recording_panel = Panel(
        instruction_text,
        style="yellow",
        box=box.ROUNDED
    )
    console.print(recording_panel)
    
    import time
    audio_start_time = time.time()
    
    # Choose recording method based on args
    if args.enter_stop:
        audio = run_enter_stop_capture()
    else:
        audio = run_voice_capture()
    
    audio_duration = time.time() - audio_start_time
    
    if audio is None or len(audio) == 0:
        logger.log_audio_capture(audio_duration, False, "No audio captured or validation failed")
        error_panel = Panel(
            "[red]❌ Audio capture failed[/red]\n\n"
            "Possible issues:\n"
            "• Recording too short (< 0.5 seconds)\n"
            "• No speech detected (silent input)\n" 
            "• Microphone not working\n"
            "• Background noise only\n\n"
            "💡 Try speaking clearly for at least 1 second",
            title="Audio Error",
            style="red",
            box=box.ROUNDED
        )
        console.print(error_panel)
        end_session(False)
        return
    
    logger.log_audio_capture(len(audio) / SAMPLE_RATE, True)
    
    # Transcription with progress indicator
    transcription_start = time.time()
    with console.status("[bold green]🤖 Transcribing audio...", spinner="dots"):
        transcript = transcribe_audio(audio)
    transcription_time = time.time() - transcription_start
    
    if not transcript:
        logger.log_transcription("", WHISPER_MODEL, False, transcription_time, "Transcription returned empty result")
        console.print("⚠️ [red]Transcription failed.[/red]")
        end_session(False)
        return
    
    logger.log_transcription(transcript, WHISPER_MODEL, True, transcription_time)
    
    # Show transcript in a nice panel
    transcript_panel = Panel(
        f"[bold white]📄 Transcript:[/bold white]\n[italic cyan]{transcript}[/italic cyan]",
        style="green",
        box=box.ROUNDED,
        title="Voice Command"
    )
    console.print(transcript_panel)
    
    # Save transcript silently
    transcript_file = save_transcript(transcript)
    if transcript_file:
        console.print(f"[dim]💾 Transcript saved to {transcript_file}[/dim]")
    
    # If transcript-only mode, exit here
    if args.transcript_only:
        console.print("✅ [green]Transcript-only mode - done![/green]")
        return
    
    # Get target markdown file
    if not args.file:
        console.print("\n📁 [bold white]Enter path to markdown file:[/bold white] ", end="")
        file_path = input().strip()
        if not file_path:
            console.print("❌ [red]No file specified.[/red]")
            return
    else:
        file_path = args.file
    
    try:
        # File processing phase
        with console.status("[bold blue]📖 Reading markdown file...", spinner="dots"):
            validated_path = validate_markdown_path(file_path)
            original_content = read_markdown_file(str(validated_path))
        
        # GPT processing with nice progress
        gpt_start = time.time()
        with console.status("[bold magenta]🧠 Processing with GPT-4...", spinner="bouncingBall"):
            modified_content = call_gpt_api(original_content, transcript, validated_path.name)
            cleaned_content = extract_markdown_from_response(modified_content)
        gpt_time = time.time() - gpt_start
        
        logger.log_gpt_request(transcript, validated_path.name, True, 
                              len(original_content), len(cleaned_content), gpt_time)
        
        # Show diff and get user approval
        diff_lines = show_diff(original_content, cleaned_content, validated_path.name)
        
        if not diff_lines:
            console.print("✅ [green]No changes suggested by GPT-4[/green]")
            logger.log_user_decision("no_changes", False, validated_path.name)
            end_session(True)
            return
        
        # Log diff analysis
        additions, deletions = count_changes(diff_lines)
        logger.log_diff_analysis(additions, deletions, validated_path.name)
        
        show_change_summary(diff_lines)
        
        # Apply changes if approved and not in dry-run mode
        if args.dry_run:
            dry_run_panel = Panel(
                "🔍 [bold yellow]Dry-run mode[/bold yellow] - Changes preview only",
                style="yellow",
                box=box.ROUNDED
            )
            console.print(dry_run_panel)
            logger.log_user_decision("dry_run", False, validated_path.name)
            end_session(True)
        elif get_user_approval(changes_detected=True):
            with console.status("[bold green]💾 Applying changes...", spinner="dots"):
                backup_path = write_markdown_file(str(validated_path), cleaned_content)
            
            success_text = Text()
            success_text.append("✅ Changes applied to ", style="bold green")
            success_text.append(str(validated_path), style="bold cyan")
            
            console.print(Panel(success_text, style="green", box=box.ROUNDED))
            
            if backup_path:
                console.print(f"[dim]💾 Original backed up to {backup_path}[/dim]")
            
            logger.log_user_decision("accept", True, validated_path.name, backup_path)
            logger.log_file_operation("write", validated_path.name, True, backup_path)
            end_session(True)
        else:
            console.print("❌ [yellow]Changes rejected by user[/yellow]")
            logger.log_user_decision("reject", False, validated_path.name)
            end_session(True)
            
    except Exception as e:
        error_panel = Panel(
            f"❌ [bold red]Error:[/bold red] {str(e)}",
            style="red",
            box=box.ROUNDED
        )
        console.print(error_panel)
        end_session(False)

def main():
    """Main entry point for the voice-controlled markdown editor."""
    parser = argparse.ArgumentParser(description="🎙️ Voice-controlled Markdown Editor")
    parser.add_argument("--version", action="version", version=f"Voice Markdown Editor {__version__}")
    parser.add_argument("--file", "-f", type=str, help="Path to markdown file to edit")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Preview changes without applying")
    parser.add_argument("--transcript-only", "-t", action="store_true", help="Only transcribe, skip GPT processing")
    parser.add_argument("--whisper-model", "-w", type=str, choices=["tiny", "base", "small", "medium", "large"], 
                       help="Whisper model to use (default: medium)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output for debugging")
    parser.add_argument("--undo", "-u", type=str, help="Undo changes to specified file (restore from latest backup)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive CLI mode")
    parser.add_argument("--live", "-l", action="store_true", help="Live transcription mode (real-time streaming)")
    parser.add_argument("--enter-stop", "-e", action="store_true", help="Use Enter key to stop recording (prevents terminal interference)")
    
    args = parser.parse_args()
    
    # Handle special modes first
    if args.undo:
        handle_undo_operation(args.undo, args.verbose)
        return
    
    if args.live:
        handle_live_mode(args)
        return
    
    if args.interactive:
        handle_interactive_mode(args)
        return
    
    # Run normal mode
    run_normal_mode(args)

if __name__ == "__main__":
    main()