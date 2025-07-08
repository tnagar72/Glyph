#!/usr/bin/env python3

import argparse
import sounddevice as sd
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

__version__ = "1.0.0"

from recording import run_voice_capture, run_enter_stop_capture
from transcription import transcribe_audio, save_transcript
from md_file import read_markdown_file, write_markdown_file, validate_markdown_path
from llm import call_gpt_api
from cleaning import extract_markdown_from_response
from diff import show_diff, get_user_approval, show_change_summary, count_changes
from session_logger import get_session_logger, end_session
from undo_manager import UndoManager
from utils import DEVICE_INDEX, WHISPER_MODEL, SAMPLE_RATE, open_in_obsidian_if_available
from audio_config import setup_audio_device, get_audio_device
from model_config import setup_default_model, get_default_model, show_current_model_config, show_all_configurations
from transcription_config import setup_transcription_method, show_current_transcription_config
from transcription import test_all_transcription_methods
from ui_helpers import (
    show_welcome_banner, show_ascii_logo, show_recording_indicator, 
    show_thinking_indicator, show_success_message, show_error_message,
    show_warning_message, show_config_overview, GLYPH_PRIMARY, GLYPH_SUCCESS, 
    GLYPH_ERROR, GLYPH_WARNING, GLYPH_VOICE, GLYPH_HIGHLIGHT
)

console = Console()

def handle_audio_setup():
    """Handle audio device configuration wizard."""
    device = setup_audio_device()
    if device is not None:
        show_success_message(
            f"🎉 Audio setup complete! Device {device} is ready for use.",
            "You can now use Glyph normally. Run 'glyph --setup-audio' again to change devices."
        )
    else:
        show_error_message(
            "❌ Audio setup cancelled or failed.",
            "You may need to check your microphone permissions or try again."
        )

def handle_model_setup():
    """Handle Whisper model configuration wizard."""
    model = setup_default_model()
    if model is not None:
        show_success_message(
            f"🎉 Model setup complete! '{model}' is now your default model.",
            "You can now use Glyph normally. Run 'glyph --setup-model' again to change models."
        )
    else:
        show_error_message(
            "❌ Model setup cancelled or failed.",
            "The system will continue using 'medium' as the default model."
        )

def handle_transcription_setup():
    """Handle transcription method configuration wizard."""
    method = setup_transcription_method()
    if method is not None:
        show_success_message(
            f"🎉 Transcription setup complete! Using '{method}' method.",
            "You can now use Glyph normally. Run 'glyph --setup-transcription' again to change methods."
        )
    else:
        show_error_message(
            "❌ Transcription setup cancelled or failed.",
            "The system will continue using the current configuration."
        )

def handle_transcription_test():
    """Handle transcription method testing."""
    console.print(f"\n🧪 [bold {GLYPH_PRIMARY}]Testing All Transcription Methods[/bold {GLYPH_PRIMARY}]")
    test_all_transcription_methods()

def handle_agent_setup():
    """Handle agent configuration wizard."""
    from agent_config import setup_agent_configuration
    vault_path = setup_agent_configuration()
    if vault_path:
        show_success_message(
            f"🎉 Agent setup complete! Vault configured: {vault_path}",
            "You can now use 'glyph --agent-mode' to start voice-controlled Obsidian management."
        )
    else:
        show_error_message(
            "❌ Agent setup incomplete.",
            "You need to configure a vault path to use agent mode."
        )

def handle_agent_mode(args):
    """Handle agent mode session."""
    if args.verbose:
        from utils import set_verbose
        set_verbose(True)
    
    try:
        from agent_cli import run_agent_mode
        
        # Check if agent is configured
        from agent_config import get_agent_config
        config = get_agent_config()
        if not config.is_vault_configured():
            show_error_message(
                "❌ Agent not configured. Run 'glyph --setup-agent' first.",
                "Agent mode requires an Obsidian vault to be configured."
            )
            return
        
        # Show current agent configuration
        if args.verbose:
            console.print(f"\n🤖 [bold {GLYPH_PRIMARY}]Agent Configuration:[/bold {GLYPH_PRIMARY}]")
            config.show_current_config()
        
        # Start agent mode
        transcription_method = getattr(args, 'transcription_method', None)
        text_only = getattr(args, 'text_only', False)
        # Default to enter-stop mode for agent mode (more reliable for interactive use)
        # Only use spacebar mode if user explicitly requests it with a hypothetical --spacebar flag
        enter_stop = True  # Default to enter-stop for agent mode
        run_agent_mode(enter_stop, transcription_method, text_only)
        
    except KeyboardInterrupt:
        console.print(f"\n👋 [yellow]Agent mode interrupted[/yellow]")
    except Exception as e:
        show_error_message(f"❌ Agent mode error: {e}")

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
    
    # Use specified transcription method or default from config
    transcription_method = getattr(args, 'transcription_method', None)
    
    # Check if we're in a pipeline (stdout is not a terminal)
    import sys
    simple_mode = not sys.stdout.isatty()
    
    # Check for clipboard mode
    clipboard_mode = getattr(args, 'clipboard', False)
    
    # Show current transcription method
    if transcription_method:
        console.print(f"✅ Using specified transcription method: {transcription_method}")
    else:
        from transcription_config import get_transcription_config
        config = get_transcription_config()
        current_method = config.get_transcription_method()
        method_display = "Local Whisper" if current_method == "local" else "OpenAI API"
        console.print(f"✅ Using configured transcription method: {method_display}")
    
    try:
        run_live_transcription(transcription_method=transcription_method, simple=simple_mode, clipboard_mode=clipboard_mode)
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
    
    if settings.get('mode') == 'agent':
        # Switch to agent mode
        args.agent_mode = True
        handle_agent_mode(args)
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
    args.no_obsidian = settings['no_obsidian']
    
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
    
    # Override default Whisper model if specified, otherwise use configured default
    if args.whisper_model:
        import utils
        utils.WHISPER_MODEL = args.whisper_model
    else:
        import utils
        utils.WHISPER_MODEL = get_default_model()
    
    # Show welcome banner with Glyph branding
    show_welcome_banner()
    
    # Set up audio device with smart detection
    audio_device = get_audio_device()
    if audio_device is not None:
        sd.default.device = [audio_device, None]  # [input, output]
        if args.verbose:
            from utils import set_verbose, verbose_print
            set_verbose(True)
            devices = sd.query_devices()
            verbose_print(f"Using audio device {audio_device}: {devices[audio_device]['name']}")
    else:
        show_error_message(
            "❌ No suitable audio device found!",
            "💡 Run 'glyph --setup-audio' to configure your microphone."
        )
        return
    
    # Recording Phase with Glyph styling
    import time
    audio_start_time = time.time()
    
    # Choose recording method based on args
    if args.enter_stop:
        show_recording_indicator("enter", args.dry_run)
        audio = run_enter_stop_capture()
    else:
        show_recording_indicator("spacebar", args.dry_run)
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
    
    # Transcription with progress indicator (with optional method override)
    transcription_start = time.time()
    transcription_method = getattr(args, 'transcription_method', None)
    
    with console.status(f"[bold {GLYPH_VOICE}]🤖 Transcribing audio...", spinner="dots"):
        transcript = transcribe_audio(audio, method=transcription_method)
    transcription_time = time.time() - transcription_start
    
    if not transcript:
        logger.log_transcription("", WHISPER_MODEL, False, transcription_time, "Transcription returned empty result")
        show_error_message("⚠️ Transcription failed.")
        end_session(False)
        return
    
    logger.log_transcription(transcript, WHISPER_MODEL, True, transcription_time)
    
    # Show transcript in a nice panel with Glyph styling
    transcript_text = Text()
    transcript_text.append("📄 Transcript:\n", style="bold white")
    transcript_text.append(transcript, style=f"italic {GLYPH_HIGHLIGHT}")
    
    transcript_panel = Panel(
        transcript_text,
        style=GLYPH_SUCCESS,
        box=box.HEAVY,
        title="◈ Voice Command ◈",
        title_align="center"
    )
    console.print(transcript_panel)
    
    # Save transcript silently
    transcript_file = save_transcript(transcript)
    if transcript_file:
        console.print(f"[dim]💾 Transcript saved to {transcript_file}[/dim]")
    
    # If transcript-only mode, exit here
    if args.transcript_only:
        show_success_message("✅ Transcript-only mode - done!")
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
        with console.status(f"[bold {GLYPH_PRIMARY}]🧠 Processing with GPT-4...", spinner="bouncingBall"):
            modified_content = call_gpt_api(original_content, transcript, validated_path.name)
            cleaned_content = extract_markdown_from_response(modified_content)
        gpt_time = time.time() - gpt_start
        
        logger.log_gpt_request(transcript, validated_path.name, True, 
                              len(original_content), len(cleaned_content), gpt_time)
        
        # Show diff and get user approval
        diff_lines = show_diff(original_content, cleaned_content, validated_path.name)
        
        if not diff_lines:
            show_success_message("✅ No changes suggested by GPT-4")
            logger.log_user_decision("no_changes", False, validated_path.name)
            end_session(True)
            return
        
        # Log diff analysis
        additions, deletions = count_changes(diff_lines)
        logger.log_diff_analysis(additions, deletions, validated_path.name)
        
        show_change_summary(diff_lines)
        
        # Apply changes if approved and not in dry-run mode
        if args.dry_run:
            show_warning_message("🔍 Dry-run mode - Changes preview only")
            logger.log_user_decision("dry_run", False, validated_path.name)
            end_session(True)
        elif get_user_approval(changes_detected=True):
            with console.status(f"[bold {GLYPH_SUCCESS}]💾 Applying changes...", spinner="dots"):
                backup_path = write_markdown_file(str(validated_path), cleaned_content)
            
            show_success_message(
                f"✅ Changes applied to {validated_path}",
                f"💾 Original backed up to {backup_path}" if backup_path else ""
            )
            
            # Attempt to open the modified file in Obsidian (unless disabled)
            if not args.no_obsidian:
                try:
                    open_in_obsidian_if_available(str(validated_path))
                except Exception as e:
                    # Don't fail the whole operation if Obsidian opening fails
                    console.print(f"[dim yellow]⚠️ Could not open in Obsidian: {e}[/dim yellow]")
            
            logger.log_user_decision("accept", True, validated_path.name, backup_path)
            logger.log_file_operation("write", validated_path.name, True, backup_path)
            end_session(True)
        else:
            show_warning_message("❌ Changes rejected by user")
            logger.log_user_decision("reject", False, validated_path.name)
            end_session(True)
            
    except Exception as e:
        show_error_message(f"❌ Error: {str(e)}")
        end_session(False)

def main():
    """Main entry point for Glyph."""
    parser = argparse.ArgumentParser(description="🎙️ Glyph - Voice-controlled Markdown Editor")
    parser.add_argument("--version", action="version", version=f"Glyph {__version__}")
    parser.add_argument("--file", "-f", type=str, help="Path to markdown file to edit")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Preview changes without applying")
    parser.add_argument("--transcript-only", "-t", action="store_true", help="Only transcribe, skip GPT processing")
    parser.add_argument("--whisper-model", "-w", type=str, choices=["tiny", "base", "small", "medium", "large"], 
                       help="Whisper model to use (default: medium)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output for debugging")
    parser.add_argument("--undo", "-u", type=str, help="Undo changes to specified file (restore from latest backup)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive CLI mode")
    parser.add_argument("--live", "-l", action="store_true", help="Live transcription mode (real-time streaming)")
    parser.add_argument("--clipboard", action="store_true", help="Copy live transcripts to clipboard (use with --live)")
    parser.add_argument("--enter-stop", "-e", action="store_true", help="Use Enter key to stop recording (prevents terminal interference)")
    parser.add_argument("--setup-audio", action="store_true", help="Run audio device configuration wizard")
    parser.add_argument("--setup-model", action="store_true", help="Run Whisper model configuration wizard")
    parser.add_argument("--setup-transcription", action="store_true", help="Run transcription method configuration wizard")
    parser.add_argument("--transcription-method", choices=["local", "openai_api"], help="Force specific transcription method for this session")
    parser.add_argument("--test-transcription", action="store_true", help="Test all transcription methods")
    parser.add_argument("--show-config", action="store_true", help="Display all current configurations and defaults")
    parser.add_argument("--logo", action="store_true", help="Show ASCII logo on startup")
    parser.add_argument("--no-obsidian", action="store_true", help="Don't automatically open files in Obsidian after changes")
    parser.add_argument("--agent-mode", "-a", action="store_true", help="Start agent mode for voice-controlled Obsidian management")
    parser.add_argument("--text-only", action="store_true", help="Use text input instead of voice (for testing agent logic)")
    parser.add_argument("--setup-agent", action="store_true", help="Run agent configuration wizard")
    
    args = parser.parse_args()
    
    # Handle logo display first
    if args.logo:
        show_ascii_logo()
        return
    
    # Handle special modes first
    if args.setup_audio:
        handle_audio_setup()
        return
    
    if args.setup_model:
        handle_model_setup()
        return
    
    if args.setup_transcription:
        handle_transcription_setup()
        return
    
    if args.setup_agent:
        handle_agent_setup()
        return
    
    if args.test_transcription:
        handle_transcription_test()
        return
    
    if args.show_config:
        show_config_overview()
        return
        
    if args.undo:
        handle_undo_operation(args.undo, args.verbose)
        return
    
    if args.live:
        handle_live_mode(args)
        return
    
    if args.agent_mode:
        handle_agent_mode(args)
        return
    
    if args.interactive:
        handle_interactive_mode(args)
        return
    
    # Run normal mode
    run_normal_mode(args)

if __name__ == "__main__":
    main()