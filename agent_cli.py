#!/usr/bin/env python3

"""
Agent CLI Module for Glyph.
Interactive agent session for voice-controlled Obsidian management.
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich import box

from agent_config import get_agent_config
from agent_tools import create_agent_tools, ToolCallResult
from agent_llm import create_agent_llm, AgentResponse
from recording import run_voice_capture, run_enter_stop_capture
from transcription import transcribe_audio
from session_logger import get_session_logger
from audio_config import get_audio_device
from ui_helpers import (
    show_success_message, show_error_message, show_recording_indicator, console
)

import sounddevice as sd

class AgentSession:
    """Manages an interactive agent session."""
    
    def __init__(self, enter_stop: bool = False, transcription_method: Optional[str] = None, text_only: bool = False):
        self.config = get_agent_config()
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.enter_stop = enter_stop
        self.transcription_method = transcription_method
        self.text_only = text_only
        
        # Initialize components
        self.tools = create_agent_tools(self.session_id)
        self.llm = create_agent_llm(self.session_id)
        self.logger = get_session_logger()
        
        # Import context for memory and multi-turn support
        from agent_context import get_conversation_context
        self.context = get_conversation_context()
        
        # Session state
        self.session_active = False
        self.commands_processed = 0
        self.successful_operations = 0
        self.session_start = None
        self.last_command_results = []  # Track results of last command
        
        # Load vault context
        if self.config.is_vault_configured():
            vault_context = self.llm.get_vault_context(self.config.get_vault_path())
            console.print(f"[dim]Loaded context: {vault_context.get('total_notes', 0)} notes in vault[/dim]")
    
    def show_banner(self):
        """Display clean, professional agent session banner."""
        # Professional header - like modern CLI tools
        console.print()
        
        # Simple, clean title
        title = Text()
        title.append("glyph", style="bold primary")
        title.append(" agent", style="muted")
        console.print(title)
        
        # Essential session info - minimal and clean
        vault_path = self.config.get_vault_path()
        vault_name = Path(vault_path).name if vault_path else "not configured"
        
        info_table = Table.grid(padding=(0, 2))
        info_table.add_column(style="muted", justify="right")
        info_table.add_column(style="text")
        
        info_table.add_row("session", self.session_id)
        info_table.add_row("vault", vault_name)
        info_table.add_row("model", "gpt-4-turbo")
        
        console.print(info_table)
        console.print()
    
    def show_session_status(self):
        """Display minimal session status like modern CLI tools."""
        if not self.session_active:
            return
        
        duration = time.time() - self.session_start if self.session_start else 0
        
        # Clean, minimal status - like GitHub CLI or Docker
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        success_rate = (self.successful_operations / max(self.commands_processed, 1)) * 100
        
        # Simple status table
        status_table = Table.grid(padding=(0, 2))
        status_table.add_column(style="muted", justify="right")
        status_table.add_column(style="text")
        
        status_table.add_row("uptime", time_str)
        status_table.add_row("commands", str(self.commands_processed))
        status_table.add_row("success", f"{success_rate:.0f}%")
        status_table.add_row("operations", str(self.tools.tool_call_count))
        
        console.print(status_table)
        console.print()
    
    def capture_voice_command(self) -> Optional[str]:
        """Capture and transcribe a voice command."""
        try:
            # Set up audio device
            audio_device = get_audio_device()
            if audio_device is not None:
                sd.default.device = [audio_device, None]
            else:
                show_error_message("❌ No audio device configured")
                return None
            
            # Show recording indicator
            if self.enter_stop:
                show_recording_indicator("enter", dry_run=False)
                audio = run_enter_stop_capture()
            else:
                show_recording_indicator("spacebar", dry_run=False)
                audio = run_voice_capture()
            
            if audio is None or len(audio) == 0:
                show_error_message("❌ No audio captured")
                return None
            
            # Transcribe audio
            with console.status("[bold voice]🎤 Transcribing...", spinner="dots"):
                transcript = transcribe_audio(audio, method=self.transcription_method)
            
            if not transcript:
                show_error_message("❌ Transcription failed")
                return None
            
            return transcript.strip()
            
        except KeyboardInterrupt:
            # Re-raise KeyboardInterrupt so it can be caught by the main loop
            raise
        except Exception as e:
            show_error_message(f"❌ Voice capture error: {e}")
            return None
    
    def capture_text_command(self) -> Optional[str]:
        """Capture a text command (for testing without voice)."""
        try:
            console.print("\n💬 [bold primary]Enter command (or 'quit' to exit):[/bold primary]")
            console.print("[muted]Examples:[/muted]")
            console.print("[muted]  • Create a note about today's meeting[/muted]")
            console.print("[muted]  • Open project notes[/muted]")
            console.print("[muted]  • Add action items to meeting note[/muted]")
            console.print()
            
            command = input("📝 Command: ").strip()
            
            if not command:
                show_error_message("❌ Empty command")
                return None
                
            if command.lower() in ['quit', 'exit', 'q']:
                return None
                
            return command
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            show_error_message(f"❌ Text input error: {e}")
            return None
    
    def show_transcript_panel(self, transcript: str):
        """Display transcript like modern CLI tools."""
        # Simple, clean transcript display
        console.print(f"[muted]transcript:[/muted] {transcript}")
        console.print()
    
    def show_tool_calls_preview(self, tool_calls: List[Dict[str, Any]]) -> bool:
        """Show tool calls preview like modern dev tools."""
        # Clean header - like kubectl or docker
        console.print(f"[muted]planned operations ({len(tool_calls)}):[/muted]")
        console.print()
        
        # Show operations cleanly
        for i, tool_call in enumerate(tool_calls, 1):
            console.print(f"[muted]{i}.[/muted]")
            preview_panel = self.tools.show_tool_call_preview(tool_call)
            console.print(preview_panel)
        
        # Check auto-accept setting
        if self.config.get_auto_accept():
            console.print("[warning]auto-execution enabled[/warning]")
            return True
        
        # Simple prompt - like modern CLI tools
        console.print("[muted]execute? (y/N/auto):[/muted] ", end="")
        choice = input().strip().lower()
        
        if choice in ['n', 'no', '']:
            console.print("[error]cancelled[/error]")
            return False
        elif choice == 'auto':
            console.print("[warning]executing all operations...[/warning]")
            return True
        else:
            return True  # Step-by-step execution
    
    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]], step_by_step: bool = True) -> bool:
        """Execute a list of tool calls."""
        successful_operations = 0
        self.last_command_results = []  # Reset results for new command
        
        for i, tool_call in enumerate(tool_calls, 1):
            console.print(f"\n🔄 [bold primary]Operation {i}/{len(tool_calls)}[/bold primary]")
            
            # Show individual confirmation if step-by-step mode
            if step_by_step and not self.config.get_auto_accept():
                preview_panel = self.tools.show_tool_call_preview(tool_call)
                console.print(preview_panel)
                
                if not Confirm.ask(f"🤖 Execute this operation?", default=True):
                    console.print(f"[warning]⏭️ Skipped operation {i}[/warning]")
                    continue
            
            # Execute the tool call
            with console.status("[bold primary]Executing...", spinner="dots"):
                result = self.tools.execute_tool_call(tool_call)
            
            # Store result for summary
            self.last_command_results.append(result)
            
            # Show result
            if result.success:
                console.print(f"✅ [green]{result.message}[/green]")
                if result.backup_created:
                    console.print(f"[dim]💾 Backup: {result.backup_created}[/dim]")
                successful_operations += 1
            else:
                console.print(f"❌ [red]{result.message}[/red]")
                
                # Ask if user wants to continue on error
                if len(tool_calls) > 1 and i < len(tool_calls):
                    if not Confirm.ask(f"[yellow]Continue with remaining operations?[/yellow]", default=True):
                        break
        
        # Update session stats
        self.successful_operations += successful_operations
        
        # Show summary
        if len(tool_calls) > 1:
            console.print(f"\n📊 [bold success]Summary: {successful_operations}/{len(tool_calls)} operations successful[/bold success]")
        
        return successful_operations > 0
    
    def handle_clarification(self, clarification: str, suggestions: List[str]) -> Optional[str]:
        """Handle clarification requests from the agent."""
        console.print("\n🤔 [bold warning]Clarification Needed[/bold warning]")
        
        clarification_panel = Panel(
            clarification,
            style="warning",
            box=box.ROUNDED,
            title="❓ Question"
        )
        console.print(clarification_panel)
        
        # Show suggestions if available
        if suggestions:
            console.print("\n💡 [bold highlight]Suggestions:[/bold highlight]")
            for i, suggestion in enumerate(suggestions, 1):
                console.print(f"  {i}. {suggestion}")
            
            # Add option to select from suggestions or type manually
            console.print(f"\n[muted]Select a number (1-{len(suggestions)}) or type the exact note name:[/muted]")
        
        # Get user response
        response = Prompt.ask(
            "\n🗣️ [bold primary]Your response[/bold primary]",
            default=""
        )
        
        # Check if user selected a number
        if suggestions and response.strip().isdigit():
            try:
                index = int(response.strip()) - 1
                if 0 <= index < len(suggestions):
                    response = suggestions[index]
                    console.print(f"[success]Selected:[/success] {response}")
            except (ValueError, IndexError):
                pass
        
        return response if response.strip() else None
    
    def show_command_summary(self):
        """Show clean command summary like modern CLI tools."""
        if not self.last_command_results:
            return
        
        # Count successful operations
        successful_ops = sum(1 for result in self.last_command_results if result.success)
        total_ops = len(self.last_command_results)
        
        # Simple summary - like git or docker
        console.print(f"[success]✓[/success] completed {successful_ops}/{total_ops} operations")
        
        # Show operation details briefly
        for i, result in enumerate(self.last_command_results, 1):
            if result.success:
                console.print(f"  [muted]{i}.[/muted] {result.message}")
                
                # Show key details inline
                if result.data and 'note_path' in result.data:
                    console.print(f"     [muted]→ {result.data['note_path']}[/muted]")
        
        console.print()
        
        # Don't clear results here - they're needed for working context tracking
        # Results will be cleared at the start of process_command instead
    
    def process_command(self, transcript: str) -> bool:
        """Process a voice command through the agent pipeline with enhanced memory and context."""
        self.commands_processed += 1
        
        # Clear previous command results at start of new command
        self.last_command_results = []
        
        # Get enhanced context for LLM
        enhanced_context = self.context.get_context_for_llm()
        
        # Get agent response with enhanced context
        with console.status("[bold primary]🧠 Processing command...", spinner="bouncingBall"):
            agent_response = self.llm.process_voice_command(transcript, enhanced_context)
        
        if not agent_response.success:
            show_error_message(f"❌ Agent processing failed: {agent_response.error_message}")
            # Add failed command to conversation history
            self.llm.add_conversation_turn(transcript, f"Error: {agent_response.error_message}")
            return False
        
        # Handle clarification request
        if agent_response.clarification:
            clarification_response = self.handle_clarification(
                agent_response.clarification, 
                agent_response.suggested_completions or []
            )
            
            if not clarification_response:
                console.print("[warning]⏭️ Command cancelled[/warning]")
                self.llm.add_conversation_turn(transcript, "Clarification cancelled")
                return False
            
            # Process clarification response
            with console.status("[bold primary]🧠 Processing clarification...", spinner="bouncingBall"):
                agent_response = self.llm.process_clarification_response(transcript, clarification_response)
            
            if not agent_response.success or not agent_response.tool_calls:
                show_error_message(f"❌ Clarification processing failed")
                self.llm.add_conversation_turn(transcript, "Clarification processing failed")
                return False
        
        # Show tool calls and get confirmation
        if not agent_response.tool_calls:
            show_error_message("❌ No operations planned")
            self.llm.add_conversation_turn(transcript, "No operations planned")
            return False
        
        if not self.show_tool_calls_preview(agent_response.tool_calls):
            console.print("[warning]⏭️ Operations cancelled[/warning]")
            self.llm.add_conversation_turn(transcript, "Operations cancelled by user")
            return False
        
        # Execute tool calls
        step_by_step = not self.config.get_auto_accept()
        success = self.execute_tool_calls(agent_response.tool_calls, step_by_step)
        
        # Learn from successful interactions and update context
        if success:
            resolved_notes = []
            for i, tool_call in enumerate(agent_response.tool_calls):
                if i < len(self.last_command_results):
                    result = self.last_command_results[i]
                    if result.success:
                        # Learn from this interaction
                        self.tools.learn_from_interaction(transcript, tool_call, result)
                        
                        # Update legacy working context
                        self.llm.update_working_context(
                            tool_call["tool_call"], 
                            result.data or {"note_name": "unknown"}
                        )
                        
                        # Track resolved notes for conversation history
                        if result.data and isinstance(result.data, dict):
                            note_name = (result.data.get("note_name") or 
                                       result.data.get("note_path") or 
                                       result.data.get("note"))
                            if note_name:
                                resolved_notes.append(note_name)
        
        # Generate response summary for conversation history
        operation_summary = self._generate_operation_summary(agent_response.tool_calls, success)
        
        # Add to conversation history (both legacy and new system)
        self.llm.add_conversation_turn(transcript, operation_summary, agent_response.tool_calls)
        self.context.add_conversation_turn(
            user_input=transcript,
            assistant_response=operation_summary,
            tool_calls=agent_response.tool_calls,
            resolved_notes=resolved_notes if success else []
        )
        
        # Log the session
        self.logger.log_event("AGENT_COMMAND", {
            "transcript": transcript,
            "tool_calls": len(agent_response.tool_calls),
            "success": success,
            "session_id": self.session_id
        })
        
        return success
    
    def _generate_operation_summary(self, tool_calls: List[Dict[str, Any]], success: bool) -> str:
        """Generate a summary of operations for conversation history."""
        if not success:
            return "Operations failed"
        
        summaries = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool_call", "unknown")
            args = tool_call.get("arguments", {})
            
            if tool_name == "create_note":
                summaries.append(f"Created note '{args.get('name', 'unknown')}'")
            elif tool_name == "open_note":
                summaries.append(f"Opened note '{args.get('name', 'unknown')}'")
            elif tool_name == "list_notes":
                summaries.append(f"Listed notes matching '{args.get('query', 'all')}'")
            elif tool_name.startswith("insert_") or tool_name.startswith("append_"):
                summaries.append(f"Added content to '{args.get('note', 'unknown')}'")
            else:
                summaries.append(f"Executed {tool_name}")
        
        return "; ".join(summaries)
    
    def run_session(self):
        """Run the interactive agent session."""
        try:
            # Validate configuration
            if not self.config.is_vault_configured():
                show_error_message("❌ No vault configured. Run 'glyph --setup-agent' first.")
                return
            
            # Show banner
            self.show_banner()
            
            # Session instructions
            if self.text_only:
                console.print("\n💡 [bold highlight]How to use Text-Only Agent Mode:[/bold highlight]")
                console.print("• Type commands naturally")
                console.print("• Examples: 'Create a note about today's meeting', 'Add ideas section to project plan'")
                console.print("• Type 'quit', 'exit', or press Ctrl+C to end session")
                console.print("• Perfect for testing agent logic without voice recognition")
            else:
                console.print("\n💡 [bold highlight]How to use Agent Mode:[/bold highlight]")
                console.print("• Speak naturally about what you want to do")
                console.print("• Examples: 'Create a note about today's meeting', 'Add ideas section to project plan'")
                console.print("• Say 'quit', 'exit', or press Ctrl+C to end session")
                recording_method = "Enter" if self.enter_stop else "Spacebar"
                console.print(f"• Recording method: {recording_method}")
            
            # Start session
            self.session_active = True
            self.session_start = time.time()
            
            if self.text_only:
                console.print("\n📝 [bold success]Text-only agent session started! Ready for commands...[/bold success]")
            else:
                console.print("\n🎤 [bold success]Agent session started! Ready for voice commands...[/bold success]")
            
            while self.session_active:
                try:
                    # Capture command (voice or text)
                    if self.text_only:
                        transcript = self.capture_text_command()
                    else:
                        transcript = self.capture_voice_command()
                    
                    if not transcript:
                        continue
                    
                    # Show transcript/command
                    if not self.text_only:
                        self.show_transcript_panel(transcript)
                    else:
                        console.print(f"[muted]command:[/muted] {transcript}")
                        console.print()
                    
                    # Check for exit commands
                    if transcript.lower().strip() in ['quit', 'exit', 'stop', 'end session']:
                        console.print("[success]👋 Ending agent session...[/success]")
                        break
                    
                    # Process the command
                    self.process_command(transcript)
                    
                    # Show command summary
                    console.print()
                    self.show_command_summary()
                    
                    # Show session status
                    console.print()
                    self.show_session_status()
                    
                    # Check session limits
                    max_calls = self.config.get_max_tool_calls()
                    if self.tools.tool_call_count >= max_calls:
                        console.print(f"[warning]⚠️ Maximum tool calls reached ({max_calls}). Ending session.[/warning]")
                        break
                    
                    if self.text_only:
                        console.print("\n📝 [bold success]Ready for next command...[/bold success]")
                    else:
                        console.print("\n🎤 [bold success]Ready for next command...[/bold success]")
                    
                except KeyboardInterrupt:
                    console.print("\n[warning]👋 Session interrupted by user[/warning]")
                    break
                except Exception as e:
                    show_error_message(f"❌ Session error: {e}")
                    continue
            
        except Exception as e:
            show_error_message(f"❌ Failed to start agent session: {e}")
        finally:
            self.session_active = False
            self.show_session_summary()
    
    def show_session_summary(self):
        """Show final session summary."""
        if not self.session_start:
            return
        
        duration = time.time() - self.session_start
        
        summary_table = Table(title="🏁 Session Summary", box=box.ROUNDED, border_style="primary")
        summary_table.add_column("Metric", style="highlight")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("Duration", f"{duration:.1f} seconds")
        summary_table.add_row("Commands Processed", str(self.commands_processed))
        summary_table.add_row("Successful Operations", str(self.successful_operations))
        summary_table.add_row("Tool Calls Executed", str(self.tools.tool_call_count))
        summary_table.add_row("Session ID", self.session_id)
        
        console.print(summary_table)
        
        # Log session end
        self.logger.log_event("AGENT_SESSION_END", {
            "session_id": self.session_id,
            "duration": duration,
            "commands_processed": self.commands_processed,
            "successful_operations": self.successful_operations,
            "tool_calls": self.tools.tool_call_count
        })

def run_agent_mode(enter_stop: bool = False, transcription_method: Optional[str] = None, text_only: bool = False):
    """Run the agent mode session."""
    session = AgentSession(enter_stop, transcription_method, text_only)
    session.run_session()

if __name__ == "__main__":
    # Test the agent CLI
    run_agent_mode()