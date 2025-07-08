#!/usr/bin/env python3

"""
Agent Tools Module for Glyph.
Handles structured tool calls for Obsidian vault operations.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from agent_config import get_agent_config
from backup_manager import get_backup_manager
from ui_helpers import (
    GLYPH_PRIMARY, GLYPH_SUCCESS, GLYPH_ERROR, GLYPH_WARNING, 
    GLYPH_HIGHLIGHT, GLYPH_MUTED, show_success_message, show_error_message, console
)

@dataclass
class ToolCallResult:
    """Result of a tool call execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    backup_created: Optional[str] = None

class AgentToolError(Exception):
    """Exception raised by agent tool operations."""
    pass

class AgentTools:
    """Handles all agent tool calls for Obsidian vault operations."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.config = get_agent_config()
        self.backup_manager = get_backup_manager()
        self.session_id = session_id or datetime.now().strftime('%Y%m%d_%H%M%S')
        self.tool_call_count = 0
        
        # Import memory and context after initialization to avoid circular imports
        from agent_memory import get_agent_memory
        from agent_context import get_conversation_context
        self.memory = get_agent_memory()
        self.context = get_conversation_context()
        
        # Validate vault configuration
        if not self.config.is_vault_configured():
            raise AgentToolError("Agent vault not configured. Run 'glyph --setup-agent' first.")
        
        self.vault_path = Path(self.config.get_vault_path())
    
    def _validate_vault_access(self):
        """Validate vault access and permissions."""
        if not self.vault_path.exists():
            raise AgentToolError(f"Vault path does not exist: {self.vault_path}")
        
        if not self.vault_path.is_dir():
            raise AgentToolError(f"Vault path is not a directory: {self.vault_path}")
    
    def _validate_note_name(self, name: str) -> str:
        """Validate and normalize note name."""
        if not name:
            raise AgentToolError("Note name cannot be empty")
        
        # Remove or replace invalid characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        
        # Add .md extension if not present
        if not safe_name.endswith('.md'):
            safe_name += '.md'
        
        return safe_name
    
    def _get_note_path(self, name: str, folder: Optional[str] = None) -> Path:
        """Get full path to a note within the vault."""
        safe_name = self._validate_note_name(name)
        
        if folder:
            # Validate folder path
            folder_path = self.vault_path / folder
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
            return folder_path / safe_name
        else:
            return self.vault_path / safe_name
    
    def _resolve_note_with_fallback(self, name: str) -> Optional[Path]:
        """Resolve note name to path with smart fallback for similar notes."""
        try:
            # 1. Check memory first - highest priority
            memory_result = self.memory.resolve_note_reference(name)
            if memory_result:
                note_path = self.vault_path / memory_result
                if note_path.exists():
                    console.print(f"[dim]🧠 Memory resolved: '{name}' → '{memory_result}'[/dim]")
                    return note_path
                else:
                    console.print(f"[warning]Memory reference invalid: {memory_result}[/warning]")
            
            # 2. Check conversation context
            context_result = self.context.resolve_reference(name)
            if context_result:
                note_path = self.vault_path / context_result
                if note_path.exists():
                    console.print(f"[dim]🔄 Context resolved: '{name}' → '{context_result}'[/dim]")
                    # Remember this resolution for future use
                    self.memory.register_note_reference(name, context_result, "context resolution")
                    return note_path
            
            # 3. Traditional contextual reference resolution
            resolved_name = self._resolve_contextual_reference(name)
            if resolved_name and resolved_name != name:
                console.print(f"[dim]→ Resolving '{name}' to '{resolved_name}' from context[/dim]")
                name = resolved_name
            
            # Handle relative paths
            if '/' in name:
                note_path = self.vault_path / name
                if not name.endswith('.md'):
                    note_path = self.vault_path / (name + '.md')
            else:
                note_path = self._get_note_path(name)
            
            # First try exact match
            if note_path.exists():
                return note_path
            
            # If exact match fails, try smart note finding
            console.print(f"[warning]note '{name}' not found - searching for similar notes...[/warning]")
            
            suggestions = self._find_similar_notes(name, max_suggestions=5)
            
            if not suggestions:
                console.print(f"[error]no similar notes found for '{name}'[/error]")
                return None
            
            # Ask user to confirm which note they meant
            selected_note = self._ask_user_for_note_confirmation(name, suggestions)
            
            if not selected_note:
                console.print(f"[warning]note selection cancelled for '{name}'[/warning]")
                return None
            
            # Return the selected note path
            return self.vault_path / selected_note
            
        except Exception as e:
            console.print(f"[error]❌ Error resolving note '{name}': {e}[/error]")
            return None
    
    def _resolve_contextual_reference(self, name: str) -> Optional[str]:
        """Resolve contextual references like 'current', 'last', 'recent' to actual note names."""
        # This method should access working context from the agent LLM
        # Since we don't have direct access, we'll implement a simple version here
        
        # For references that can be resolved from recent operations
        name_lower = name.lower().strip()
        
        # These are handled by the LLM prompt context, but we can add some basic resolution here
        if name_lower in ['current', 'focus', 'current note', 'focused note']:
            # Could be resolved if we had access to working context
            # For now, return None to let normal resolution handle it
            return None
        elif name_lower in ['last', 'last note', 'recent', 'recent note']:
            # Could be resolved if we had access to working context  
            # For now, return None to let normal resolution handle it
            return None
        
        return None
    
    def _backup_before_edit(self, file_path: Path) -> Optional[str]:
        """Create backup before editing if enabled."""
        if not self.config.get_backup_before_edits():
            return None
        
        if file_path.exists():
            backup_path = self.backup_manager.create_backup(
                str(file_path), 
                backup_type="agent_edit"
            )
            return backup_path
        return None
    
    def _increment_tool_calls(self):
        """Increment and validate tool call count."""
        self.tool_call_count += 1
        max_calls = self.config.get_max_tool_calls()
        
        if self.tool_call_count > max_calls:
            raise AgentToolError(f"Maximum tool calls per session exceeded ({max_calls})")
    
    def _open_in_obsidian_after_edit(self, note_path: Path) -> bool:
        """Open a note in Obsidian after editing it."""
        try:
            from utils import open_obsidian_with_file
            return open_obsidian_with_file(str(note_path))
        except Exception as e:
            # Don't fail the operation if Obsidian opening fails
            return False
    
    def execute_tool_call(self, tool_call: Dict[str, Any]) -> ToolCallResult:
        """Execute a tool call with validation and error handling."""
        try:
            self._validate_vault_access()
            self._increment_tool_calls()
            
            tool_name = tool_call.get("tool_call")
            arguments = tool_call.get("arguments", {})
            
            if not tool_name:
                return ToolCallResult(False, "No tool_call specified")
            
            # Route to appropriate tool method
            method_name = f"_tool_{tool_name}"
            if not hasattr(self, method_name):
                return ToolCallResult(False, f"Unknown tool call: {tool_name}")
            
            method = getattr(self, method_name)
            return method(**arguments)
            
        except AgentToolError as e:
            return ToolCallResult(False, str(e))
        except Exception as e:
            return ToolCallResult(False, f"Unexpected error: {str(e)}")
    
    def learn_from_interaction(self, user_input: str, tool_call: Dict[str, Any], result: ToolCallResult):
        """Learn from user interactions for future reference resolution."""
        try:
            tool_name = tool_call.get("tool_call", "")
            arguments = tool_call.get("arguments", {})
            
            # Learn note references
            if result.success and "note" in str(result.data):
                resolved_note = None
                
                # Extract resolved note name from result
                if result.data and isinstance(result.data, dict):
                    resolved_note = (result.data.get("note_name") or 
                                   result.data.get("note_path") or 
                                   result.data.get("note"))
                
                if resolved_note:
                    # Extract how user referred to the note
                    note_references = self._extract_user_note_references(user_input)
                    for ref in note_references:
                        self.memory.register_note_reference(ref, resolved_note, user_input)
                    
                    # Extract entities from the content if applicable
                    if "content" in str(result.data):
                        content = result.data.get("content", "")
                        if content:
                            self.memory.extract_and_register_entities(content, resolved_note)
                    
                    # Update conversation context
                    self.context.update_focus(resolved_note, tool_name)
                    
                    # Learn user patterns
                    self.memory.learn_user_pattern(user_input, resolved_note)
        
        except Exception as e:
            console.print(f"[dim]Warning: Learning failed: {e}[/dim]")
    
    def _extract_user_note_references(self, user_input: str) -> List[str]:
        """Extract how user refers to notes in their input."""
        import re
        references = []
        
        # Common patterns for note references
        patterns = [
            r'(?:my|the)\s+([a-zA-Z][\w\s]{2,30})(?:\s+(?:note|file|document))?',
            r'([a-zA-Z][\w\s]{2,30})\s+(?:note|document|file|sop)',
            r'"([^"]+)"',  # Quoted references
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z][a-z]+)*)'  # Title case phrases
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                match = match.strip()
                if len(match) > 2 and match.lower() not in ['the', 'my', 'note', 'file', 'document']:
                    references.append(match)
        
        return list(set(references))  # Remove duplicates
    
    # File & Note Management Tools
    
    def _tool_create_note(self, name: str, folder: Optional[str] = None, content: str = "") -> ToolCallResult:
        """Create a new note in the vault."""
        try:
            note_path = self._get_note_path(name, folder)
            
            if note_path.exists():
                return ToolCallResult(False, f"Note already exists: {note_path.name}")
            
            # Create the note
            note_path.write_text(content, encoding='utf-8')
            
            # Open the note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(note_path)
            
            message = f"Created note: {note_path.relative_to(self.vault_path)}"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True, 
                message,
                {"note_name": name, "note_path": str(note_path.relative_to(self.vault_path)), "opened_in_obsidian": obsidian_opened}
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to create note: {e}")
    
    def _tool_delete_note(self, name: str) -> ToolCallResult:
        """Delete a note from the vault."""
        try:
            note_path = self._get_note_path(name)
            
            if not note_path.exists():
                return ToolCallResult(False, f"Note does not exist: {name}")
            
            # Create backup before deletion
            backup_path = self._backup_before_edit(note_path)
            
            # Delete the note
            note_path.unlink()
            
            return ToolCallResult(
                True, 
                f"Deleted note: {name}",
                {"note_name": name, "note_path": str(note_path.relative_to(self.vault_path))},
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to delete note: {e}")
    
    def _tool_rename_note(self, old_name: str, new_name: str) -> ToolCallResult:
        """Rename a note in the vault."""
        try:
            old_path = self._get_note_path(old_name)
            new_path = self._get_note_path(new_name)
            
            if not old_path.exists():
                return ToolCallResult(False, f"Note does not exist: {old_name}")
            
            if new_path.exists():
                return ToolCallResult(False, f"Target name already exists: {new_name}")
            
            # Create backup before rename
            backup_path = self._backup_before_edit(old_path)
            
            # Rename the note
            old_path.rename(new_path)
            
            # Open the renamed note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(new_path)
            
            message = f"Renamed note: {old_name} → {new_name}"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True, 
                message,
                {
                    "note_name": new_name,
                    "old_path": str(old_path.relative_to(self.vault_path)),
                    "new_path": str(new_path.relative_to(self.vault_path)),
                    "opened_in_obsidian": obsidian_opened
                },
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to rename note: {e}")
    
    def _tool_move_note(self, name: str, target_folder: str) -> ToolCallResult:
        """Move a note to a different folder."""
        try:
            current_path = self._get_note_path(name)
            target_path = self._get_note_path(name, target_folder)
            
            if not current_path.exists():
                return ToolCallResult(False, f"Note does not exist: {name}")
            
            if target_path.exists():
                return ToolCallResult(False, f"Note already exists in target folder: {target_folder}/{name}")
            
            # Create backup before move
            backup_path = self._backup_before_edit(current_path)
            
            # Ensure target folder exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the note
            current_path.rename(target_path)
            
            # Open the moved note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(target_path)
            
            message = f"Moved note: {name} → {target_folder}/"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True, 
                message,
                {
                    "old_path": str(current_path.relative_to(self.vault_path)),
                    "new_path": str(target_path.relative_to(self.vault_path)),
                    "opened_in_obsidian": obsidian_opened
                },
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to move note: {e}")
    
    def _tool_list_notes(self, query: Optional[str] = None, folder: Optional[str] = None) -> ToolCallResult:
        """List notes in the vault with optional filtering and semantic search."""
        try:
            search_path = self.vault_path
            if folder:
                search_path = self.vault_path / folder
                if not search_path.exists():
                    return ToolCallResult(False, f"Folder does not exist: {folder}")
            
            # Find all markdown files
            md_files = list(search_path.rglob("*.md"))
            
            # Filter by query if provided
            if query:
                query_lower = query.lower()
                filtered_files = []
                
                # Multi-word semantic search
                query_words = query_lower.split()
                
                for f in md_files:
                    file_path_lower = str(f.relative_to(self.vault_path)).lower()
                    
                    # Method 1: Exact phrase match (highest priority)
                    if query_lower in file_path_lower:
                        filtered_files.append((f, 100))  # Priority score
                    
                    # Method 2: All words present (high priority)
                    elif all(word in file_path_lower for word in query_words):
                        filtered_files.append((f, 90))
                    
                    # Method 3: Most words present (medium priority)
                    elif len(query_words) > 1:
                        word_matches = sum(1 for word in query_words if word in file_path_lower)
                        if word_matches >= len(query_words) * 0.5:  # At least half the words
                            priority = 50 + (word_matches / len(query_words)) * 30
                            filtered_files.append((f, priority))
                    
                    # Method 4: Single word match (lower priority)
                    else:
                        # Check both filename and full path (including folder names)
                        filename_match = query_lower in f.stem.lower()
                        path_match = query_lower in file_path_lower
                        if filename_match or path_match:
                            filtered_files.append((f, 30))
                
                # Sort by priority (highest first) and extract files
                filtered_files.sort(key=lambda x: x[1], reverse=True)
                md_files = [f[0] for f in filtered_files]
            
            # Convert to relative paths
            note_list = [str(f.relative_to(self.vault_path)) for f in md_files]
            
            return ToolCallResult(
                True, 
                f"Found {len(note_list)} notes" + (f" matching '{query}'" if query else ""),
                {"notes": note_list, "count": len(note_list), "query": query}
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to list notes: {e}")
    
    def _find_similar_notes(self, target_name: str, max_suggestions: int = 5) -> List[Dict[str, Any]]:
        """Find notes similar to the target name using improved matching algorithms."""
        try:
            # Get all notes in the vault
            all_notes_result = self._tool_list_notes()
            if not all_notes_result.success:
                return []
            
            all_notes = all_notes_result.data.get('notes', [])
            if not all_notes:
                return []
            
            # Use our improved matching algorithm directly
            return self._fallback_simple_matching(target_name, all_notes, max_suggestions)
                
        except Exception as e:
            # Return empty list on any error
            console.print(f"[error]Error finding similar notes: {e}[/error]")
            return []
    
    def _fallback_simple_matching(self, target_name: str, all_notes: List[str], max_suggestions: int) -> List[Dict[str, Any]]:
        """Advanced fallback matching using multiple algorithms."""
        import difflib
        import re
        
        # Clean target name for matching
        target_clean = target_name.lower().replace('.md', '').strip()
        target_words = re.findall(r'\w+', target_clean)
        
        suggestions = []
        for note in all_notes:
            note_clean = note.lower().replace('.md', '').strip()
            note_words = re.findall(r'\w+', note_clean)
            
            # 1. Exact substring match (highest priority)
            if target_clean in note_clean:
                suggestions.append({
                    "note": note,
                    "reason": f"Contains '{target_clean}'",
                    "confidence": 0.95
                })
                continue
            
            # 2. Reverse substring match
            if note_clean in target_clean:
                suggestions.append({
                    "note": note,
                    "reason": f"Note name contained in search",
                    "confidence": 0.90
                })
                continue
            
            # 3. Word-by-word matching
            word_matches = 0
            partial_matches = 0
            for target_word in target_words:
                for note_word in note_words:
                    if target_word == note_word:
                        word_matches += 1
                    elif target_word in note_word or note_word in target_word:
                        partial_matches += 0.5
            
            # 4. Fuzzy string matching
            similarity = difflib.SequenceMatcher(None, target_clean, note_clean).ratio()
            
            # 5. Check for common patterns
            pattern_bonus = 0
            # Check if it's a folder path search
            if '/' in target_name:
                folder_part = target_name.split('/')[-1].lower()
                if folder_part in note_clean:
                    pattern_bonus = 0.3
            
            # Calculate final score
            word_score = (word_matches + partial_matches) / len(target_words) if target_words else 0
            final_score = max(similarity, word_score) + pattern_bonus
            
            # Only include notes with decent relevance
            if final_score > 0.25 or word_matches > 0:
                reason_parts = []
                if word_matches > 0:
                    reason_parts.append(f"{word_matches} exact word matches")
                if partial_matches > 0:
                    reason_parts.append(f"{partial_matches:.1f} partial matches")
                if similarity > 0.3:
                    reason_parts.append(f"{similarity:.1%} similarity")
                
                reason = ", ".join(reason_parts) if reason_parts else f"Low similarity ({similarity:.1%})"
                
                suggestions.append({
                    "note": note,
                    "reason": reason,
                    "confidence": final_score
                })
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:max_suggestions]
    
    def _ask_user_for_note_confirmation(self, target_name: str, suggestions: List[Dict[str, Any]]) -> Optional[str]:
        """Clean note selection interface like modern CLI tools."""
        
        console.print(f"[muted]note '{target_name}' not found. similar notes:[/muted]")
        console.print()
        
        # Show options cleanly
        for i, suggestion in enumerate(suggestions, 1):
            note_name = suggestion['note']
            confidence = suggestion.get('confidence', 0)
            reason = suggestion.get('reason', '')
            
            # Clean confidence indicator
            if confidence >= 0.8:
                conf_icon = "●●●"
            elif confidence >= 0.6:
                conf_icon = "●●○"
            else:
                conf_icon = "●○○"
            
            console.print(f"  [muted]{i}.[/muted] {note_name}")
            console.print(f"     [muted]{conf_icon} {reason}[/muted]")
            console.print()
        
        # Add manual entry option
        console.print(f"  [muted]{len(suggestions) + 1}.[/muted] [italic]type exact note name manually[/italic]")
        console.print()
        
        # Simple prompt
        console.print(f"[muted]select note (1-{len(suggestions) + 1}) or 'n' to cancel:[/muted] ", end="")
        choice = input().strip()
        
        if choice.lower() in ['n', 'no', 'cancel']:
            return None
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(suggestions):
                selected_note = suggestions[index]['note']
                console.print(f"[success]selected:[/success] {selected_note}")
                return selected_note
            elif index == len(suggestions):
                # Manual entry
                console.print("[muted]enter exact note name (with or without .md):[/muted] ", end="")
                manual_name = input().strip()
                if manual_name:
                    if not manual_name.endswith('.md'):
                        manual_name += '.md'
                    console.print(f"[success]using:[/success] {manual_name}")
                    return manual_name
                else:
                    console.print("[error]no name entered[/error]")
                    return None
            else:
                console.print("[error]invalid selection[/error]")
                return None
        except ValueError:
            console.print("[error]invalid input[/error]")
            return None
    
    # Section Editing Tools
    
    def _tool_insert_section(self, note: str, heading: str, content: str, position: str = "end") -> ToolCallResult:
        """Insert a new section in a note with smart note finding."""
        try:
            note_path = self._resolve_note_with_fallback(note)
            
            if not note_path:
                return ToolCallResult(False, f"Could not find or resolve note: {note}")
            
            # Create backup before edit
            backup_path = self._backup_before_edit(note_path)
            
            # Read current content
            current_content = note_path.read_text(encoding='utf-8')
            
            # Format section
            section_content = f"\n## {heading}\n\n{content}\n"
            
            if position == "end":
                new_content = current_content + section_content
            elif position == "start":
                new_content = section_content + current_content
            else:
                # Insert after specific heading (future enhancement)
                new_content = current_content + section_content
            
            # Write updated content
            note_path.write_text(new_content, encoding='utf-8')
            
            # Open the note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(note_path)
            
            message = f"Inserted section '{heading}' in {note}"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True, 
                message,
                {"note": note, "heading": heading, "position": position, "opened_in_obsidian": obsidian_opened},
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to insert section: {e}")
    
    def _tool_append_section(self, note: str, heading: str, content: str) -> ToolCallResult:
        """Append content to an existing section with smart note finding."""
        try:
            note_path = self._resolve_note_with_fallback(note)
            
            if not note_path:
                return ToolCallResult(False, f"Could not find or resolve note: {note}")
            
            # Create backup before edit
            backup_path = self._backup_before_edit(note_path)
            
            # Read current content
            current_content = note_path.read_text(encoding='utf-8')
            
            # Find the section and append content
            lines = current_content.split('\n')
            new_lines = []
            found_section = False
            in_section = False
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # Check if this is the target heading
                if line.strip().startswith('#') and heading.lower() in line.lower():
                    found_section = True
                    in_section = True
                    continue
                
                # Check if we've reached the next section
                if in_section and line.strip().startswith('#'):
                    # Insert content before this new section
                    new_lines.insert(-1, content)
                    in_section = False
            
            # If we found the section but never hit another heading, append at the end
            if found_section and in_section:
                new_lines.append(content)
            
            if not found_section:
                return ToolCallResult(False, f"Section '{heading}' not found in {note}")
            
            # Write updated content
            note_path.write_text('\n'.join(new_lines), encoding='utf-8')
            
            # Open the note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(note_path)
            
            message = f"Appended content to section '{heading}' in {note}"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True, 
                message,
                {"note": note, "heading": heading, "opened_in_obsidian": obsidian_opened},
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to append to section: {e}")
    
    def _tool_replace_section(self, note: str, heading: str, content: str) -> ToolCallResult:
        """
        Replace the ENTIRE content of an existing section.
        WARNING: This completely replaces all content in the section.
        For minor edits, use edit_section_content or fix_spelling_in_section instead.
        """
        try:
            note_path = self._resolve_note_with_fallback(note)
            
            if not note_path:
                return ToolCallResult(False, f"Could not find or resolve note: {note}")
            
            # Create backup before edit
            backup_path = self._backup_before_edit(note_path)
            
            # Read current content
            current_content = note_path.read_text(encoding='utf-8')
            
            # Find and replace the section content
            lines = current_content.split('\n')
            new_lines = []
            found_section = False
            in_section = False
            
            for line in lines:
                # Check if this is the target heading
                if line.strip().startswith('#') and heading.lower() in line.lower():
                    new_lines.append(line)
                    new_lines.append('')  # Empty line after heading
                    new_lines.append(content)
                    found_section = True
                    in_section = True
                    continue
                
                # Skip content in target section
                if in_section:
                    if line.strip().startswith('#'):
                        # Reached next section
                        new_lines.append('')  # Empty line before next section
                        new_lines.append(line)
                        in_section = False
                    # Skip lines within the target section
                    continue
                
                new_lines.append(line)
            
            if not found_section:
                return ToolCallResult(False, f"Section '{heading}' not found in {note}")
            
            # Write updated content
            note_path.write_text('\n'.join(new_lines), encoding='utf-8')
            
            # Open the note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(note_path)
            
            message = f"Replaced section '{heading}' in {note}"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True, 
                message,
                {"note": note, "heading": heading, "opened_in_obsidian": obsidian_opened},
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to replace section: {e}")
    
    def _tool_edit_section_content(self, note: str, heading: str, old_text: str, new_text: str) -> ToolCallResult:
        """Edit specific content within a section without replacing the entire section."""
        try:
            note_path = self._resolve_note_with_fallback(note)
            
            if not note_path:
                return ToolCallResult(False, f"Could not find or resolve note: {note}")
            
            # Create backup before edit
            backup_path = self._backup_before_edit(note_path)
            
            # Read current content
            current_content = note_path.read_text(encoding='utf-8')
            
            # Find the section and make targeted edit
            lines = current_content.split('\n')
            new_lines = []
            found_section = False
            in_section = False
            section_content_lines = []
            
            for line in lines:
                # Check if this is the target heading
                if line.strip().startswith('#') and heading.lower() in line.lower():
                    new_lines.append(line)
                    found_section = True
                    in_section = True
                    continue
                
                # Check if we've reached the next section
                if in_section and line.strip().startswith('#'):
                    # Process the collected section content
                    section_content = '\n'.join(section_content_lines)
                    if old_text in section_content:
                        edited_content = section_content.replace(old_text, new_text)
                        new_lines.extend(edited_content.split('\n'))
                    else:
                        new_lines.extend(section_content_lines)
                    
                    # Add the new section header
                    new_lines.append(line)
                    in_section = False
                    section_content_lines = []
                    continue
                
                # Collect section content or add to output
                if in_section:
                    section_content_lines.append(line)
                else:
                    new_lines.append(line)
            
            # Handle case where target section is at the end of file
            if found_section and in_section and section_content_lines:
                section_content = '\n'.join(section_content_lines)
                if old_text in section_content:
                    edited_content = section_content.replace(old_text, new_text)
                    new_lines.extend(edited_content.split('\n'))
                else:
                    new_lines.extend(section_content_lines)
            
            if not found_section:
                return ToolCallResult(False, f"Section '{heading}' not found in {note}")
            
            # Check if any changes were made
            final_content = '\n'.join(new_lines)
            if final_content == current_content:
                return ToolCallResult(False, f"Text '{old_text}' not found in section '{heading}'")
            
            # Write updated content
            note_path.write_text(final_content, encoding='utf-8')
            
            # Open the note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(note_path)
            
            message = f"Edited content in section '{heading}' of {note}"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True, 
                message,
                {"note": note, "heading": heading, "old_text": old_text, "new_text": new_text, "opened_in_obsidian": obsidian_opened},
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to edit section content: {e}")
    
    def _tool_fix_spelling_in_section(self, note: str, heading: str, corrections: dict) -> ToolCallResult:
        """Fix multiple spelling errors in a section using a dictionary of corrections."""
        try:
            note_path = self._resolve_note_with_fallback(note)
            
            if not note_path:
                return ToolCallResult(False, f"Could not find or resolve note: {note}")
            
            # Create backup before edit
            backup_path = self._backup_before_edit(note_path)
            
            # Read current content
            current_content = note_path.read_text(encoding='utf-8')
            
            # Find the section and make spelling corrections
            lines = current_content.split('\n')
            new_lines = []
            found_section = False
            in_section = False
            section_content_lines = []
            corrections_made = 0
            
            for line in lines:
                # Check if this is the target heading
                if line.strip().startswith('#') and heading.lower() in line.lower():
                    new_lines.append(line)
                    found_section = True
                    in_section = True
                    continue
                
                # Check if we've reached the next section
                if in_section and line.strip().startswith('#'):
                    # Process the collected section content with corrections
                    section_content = '\n'.join(section_content_lines)
                    corrected_content = section_content
                    
                    for wrong_word, correct_word in corrections.items():
                        if wrong_word in corrected_content:
                            corrected_content = corrected_content.replace(wrong_word, correct_word)
                            corrections_made += 1
                    
                    new_lines.extend(corrected_content.split('\n'))
                    
                    # Add the new section header
                    new_lines.append(line)
                    in_section = False
                    section_content_lines = []
                    continue
                
                # Collect section content or add to output
                if in_section:
                    section_content_lines.append(line)
                else:
                    new_lines.append(line)
            
            # Handle case where target section is at the end of file
            if found_section and in_section and section_content_lines:
                section_content = '\n'.join(section_content_lines)
                corrected_content = section_content
                
                for wrong_word, correct_word in corrections.items():
                    if wrong_word in corrected_content:
                        corrected_content = corrected_content.replace(wrong_word, correct_word)
                        corrections_made += 1
                
                new_lines.extend(corrected_content.split('\n'))
            
            if not found_section:
                return ToolCallResult(False, f"Section '{heading}' not found in {note}")
            
            if corrections_made == 0:
                return ToolCallResult(False, f"No spelling errors found to correct in section '{heading}'")
            
            # Write updated content
            note_path.write_text('\n'.join(new_lines), encoding='utf-8')
            
            # Open the note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(note_path)
            
            message = f"Fixed {corrections_made} spelling error(s) in section '{heading}' of {note}"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True, 
                message,
                {"note": note, "heading": heading, "corrections": corrections, "corrections_made": corrections_made, "opened_in_obsidian": obsidian_opened},
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to fix spelling in section: {e}")
    
    def _tool_delete_section(self, note: str, heading: str) -> ToolCallResult:
        """Delete a section from a note."""
        try:
            note_path = self._get_note_path(note)
            
            if not note_path.exists():
                return ToolCallResult(False, f"Note does not exist: {note}")
            
            # Create backup before edit
            backup_path = self._backup_before_edit(note_path)
            
            # Read current content
            current_content = note_path.read_text(encoding='utf-8')
            
            # Find and remove the section
            lines = current_content.split('\n')
            new_lines = []
            found_section = False
            in_section = False
            
            for line in lines:
                # Check if this is the target heading
                if line.strip().startswith('#') and heading.lower() in line.lower():
                    found_section = True
                    in_section = True
                    continue
                
                # Skip content in target section
                if in_section:
                    if line.strip().startswith('#'):
                        # Reached next section
                        new_lines.append(line)
                        in_section = False
                    # Skip lines within the target section
                    continue
                
                new_lines.append(line)
            
            if not found_section:
                return ToolCallResult(False, f"Section '{heading}' not found in {note}")
            
            # Write updated content
            note_path.write_text('\n'.join(new_lines), encoding='utf-8')
            
            # Open the note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(note_path)
            
            message = f"Deleted section '{heading}' from {note}"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True, 
                message,
                {"note": note, "heading": heading, "opened_in_obsidian": obsidian_opened},
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to delete section: {e}")
    
    # Note Opening Tools
    
    def _tool_open_note(self, name: str) -> ToolCallResult:
        """Open a note in Obsidian with smart fallback to similar notes."""
        from rich.text import Text
        from rich.panel import Panel
        from rich.align import Align
        from rich import box
        
        try:
            # Handle relative paths by constructing the full path directly
            # This allows opening notes with folder structures like "folder/note.md"
            if '/' in name:
                # If name contains path separators, treat it as a relative path
                note_path = self.vault_path / name
                if not name.endswith('.md'):
                    note_path = self.vault_path / (name + '.md')
            else:
                # Simple note name, use the normal path resolution
                note_path = self._get_note_path(name)
            
            # First try exact match
            if note_path.exists():
                return self._open_note_file(note_path, name)
            
            # If exact match fails, try smart note finding with luxurious messaging
            search_text = Text()
            search_text.append("◇ ", style="bold accent")
            search_text.append("Exact match not found", style="warning")
            search_text.append(" — ", style="muted")
            search_text.append("Initiating intelligent discovery", style="italic primary")
            search_text.append(" ◇", style="bold accent")
            
            console.print(Panel(
                Align.center(search_text),
                style="warning",
                box=box.ROUNDED,
                padding=(0, 2)
            ))
            
            suggestions = self._find_similar_notes(name, max_suggestions=5)
            
            if not suggestions:
                return ToolCallResult(False, f"No similar notes found for '{name}'. Try listing notes first or check the spelling.")
            
            # Ask user to confirm which note they meant
            selected_note = self._ask_user_for_note_confirmation(name, suggestions)
            
            if not selected_note:
                return ToolCallResult(False, f"Note selection cancelled for '{name}'")
            
            # Open the selected note
            selected_path = self.vault_path / selected_note
            return self._open_note_file(selected_path, selected_note)
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to open note: {e}")
    
    def _open_note_file(self, note_path: Path, display_name: str) -> ToolCallResult:
        """Helper method to open a note file in Obsidian."""
        from utils import open_obsidian_with_file
        
        try:
            success = open_obsidian_with_file(str(note_path))
            if success:
                return ToolCallResult(
                    True, 
                    f"Opened note in Obsidian: {display_name}",
                    {"note_name": display_name, "note_path": str(note_path.relative_to(self.vault_path))}
                )
            else:
                return ToolCallResult(False, f"Failed to open {display_name} in Obsidian")
        except Exception as e:
            return ToolCallResult(False, f"Error opening note in Obsidian: {e}")
    
    def _tool_open_notes(self, query: Optional[str] = None, folder: Optional[str] = None) -> ToolCallResult:
        """Find and open multiple notes in Obsidian."""
        try:
            # First list the notes
            list_result = self._tool_list_notes(query, folder)
            if not list_result.success:
                return list_result
            
            notes = list_result.data.get('notes', [])
            if not notes:
                return ToolCallResult(False, f"No notes found matching criteria")
            
            # Open each note in Obsidian
            from utils import open_obsidian_with_file
            opened_count = 0
            failed_notes = []
            
            for note in notes:
                note_path = self.vault_path / note
                try:
                    success = open_obsidian_with_file(str(note_path))
                    if success:
                        opened_count += 1
                    else:
                        failed_notes.append(note)
                except Exception as e:
                    failed_notes.append(note)
            
            message = f"Opened {opened_count}/{len(notes)} notes in Obsidian"
            if failed_notes:
                message += f" (failed: {', '.join(failed_notes[:3])}{'...' if len(failed_notes) > 3 else ''})"
            
            return ToolCallResult(
                True, 
                message,
                {
                    "total_notes": len(notes),
                    "opened": opened_count,
                    "failed": len(failed_notes),
                    "opened_notes": [n for n in notes if n not in failed_notes],  # For working context tracking
                    "notes_opened": [n for n in notes if n not in failed_notes]  # Keep for backward compatibility
                }
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to open notes: {e}")
    
    # Note Content Tools
    
    def _tool_read_note(self, name: str) -> ToolCallResult:
        """Read the content of a note."""
        try:
            note_path = self._resolve_note_with_fallback(name)
            
            if not note_path:
                return ToolCallResult(False, f"Could not find or resolve note: {name}")
            
            # Read the file content
            content = note_path.read_text(encoding='utf-8')
            
            return ToolCallResult(
                True,
                f"Read note: {name}",
                {
                    "note_name": name,
                    "note_path": str(note_path.relative_to(self.vault_path)),
                    "content": content,
                    "word_count": len(content.split()),
                    "char_count": len(content)
                }
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to read note: {e}")
    
    def _tool_summarize_note(self, name: str, heading: str = "Summary") -> ToolCallResult:
        """Read a note and add a summary section with key points."""
        try:
            note_path = self._resolve_note_with_fallback(name)
            
            if not note_path:
                return ToolCallResult(False, f"Could not find or resolve note: {name}")
            
            # Read the file content
            content = note_path.read_text(encoding='utf-8')
            
            # Create a simple summary by extracting key points
            summary = self._generate_summary(content)
            
            # Create backup before edit
            backup_path = self._backup_before_edit(note_path)
            
            # Add the summary section
            section_content = f"\n## {heading}\n\n{summary}\n"
            new_content = content + section_content
            
            # Write updated content
            note_path.write_text(new_content, encoding='utf-8')
            
            # Open the note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(note_path)
            
            message = f"Added summary to {name}"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True,
                message,
                {
                    "note_name": name,
                    "heading": heading,
                    "summary": summary,
                    "opened_in_obsidian": obsidian_opened
                },
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to summarize note: {e}")
    
    def _generate_summary(self, content: str) -> str:
        """Generate a comprehensive summary using GPT."""
        try:
            from agent_llm import AgentLLM
            
            # Clean the content to remove existing summary sections
            import re
            lines = content.split('\n')
            cleaned_lines = []
            skip_summary = False
            
            for line in lines:
                # Skip existing summary sections
                if re.match(r'^#+\s*(summary|executive summary|enhanced summary)', line.strip(), re.IGNORECASE):
                    skip_summary = True
                    continue
                elif line.strip().startswith('#') and skip_summary:
                    skip_summary = False
                    cleaned_lines.append(line)
                elif not skip_summary:
                    cleaned_lines.append(line)
            
            cleaned_content = '\n'.join(cleaned_lines).strip()
            
            # If content is too long, take first portion for summary
            if len(cleaned_content) > 4000:
                cleaned_content = cleaned_content[:4000] + "..."
            
            # Create summary prompt
            summary_prompt = f"""Please create a concise summary of the following document. Keep it brief but comprehensive - aim for 3-4 short sections with bullet points.

Document content:
{cleaned_content}

Please provide a well-structured summary that captures:
1. Main purpose/theme (1-2 sentences)
2. Key research projects (3-4 bullet points max)
3. Notable achievements/findings (2-3 bullet points max)
4. Future goals (1-2 bullet points max)

Keep each bullet point to 1-2 lines maximum. Use **bold headings** and be concise."""

            # Use the LLM to generate summary
            llm = AgentLLM()
            
            # Use the LLM to generate a comprehensive summary
            try:
                summary = llm.get_completion(summary_prompt)
                return summary.strip()
            except Exception as e:
                console.print(f"[error]LLM summary generation failed: {e}[/error]")
                return self._fallback_summary(cleaned_content)
                
        except Exception as e:
            console.print(f"[error]Summary generation error: {e}[/error]")
            return self._fallback_summary(content)
    
    def _fallback_summary(self, content: str) -> str:
        """Fallback summary method if GPT fails."""
        word_count = len(content.split())
        
        # Extract first paragraph as overview
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 50]
        
        summary_parts = []
        
        if paragraphs:
            summary_parts.append("**Overview:**")
            first_para = paragraphs[0]
            if len(first_para) > 200:
                first_para = first_para[:197] + "..."
            summary_parts.append(first_para)
            summary_parts.append("")
        
        summary_parts.append(f"**Document Statistics:** {word_count} words")
        summary_parts.append("")
        summary_parts.append("*Note: This is a basic summary. For a comprehensive analysis, the document would benefit from manual review.*")
        
        return "\n".join(summary_parts)
    
    # Linking Tools
    
    def _tool_add_wikilink(self, source_note: str, target_note: str, alias: Optional[str] = None, position: str = "end") -> ToolCallResult:
        """Add a wikilink to a note."""
        try:
            source_path = self._get_note_path(source_note)
            
            if not source_path.exists():
                return ToolCallResult(False, f"Source note does not exist: {source_note}")
            
            # Create backup before edit
            backup_path = self._backup_before_edit(source_path)
            
            # Format the wikilink
            target_clean = target_note.replace('.md', '')
            if alias:
                wikilink = f"[[{target_clean}|{alias}]]"
            else:
                wikilink = f"[[{target_clean}]]"
            
            # Read current content and add link
            current_content = source_path.read_text(encoding='utf-8')
            
            if position == "end":
                new_content = f"{current_content}\n\n{wikilink}"
            else:
                new_content = f"{wikilink}\n\n{current_content}"
            
            # Write updated content
            source_path.write_text(new_content, encoding='utf-8')
            
            # Open the note in Obsidian
            obsidian_opened = self._open_in_obsidian_after_edit(source_path)
            
            message = f"Added wikilink to {target_note} in {source_note}"
            if obsidian_opened:
                message += " (opened in Obsidian)"
            
            return ToolCallResult(
                True, 
                message,
                {"source": source_note, "target": target_note, "alias": alias, "opened_in_obsidian": obsidian_opened},
                backup_path
            )
            
        except Exception as e:
            return ToolCallResult(False, f"Failed to add wikilink: {e}")
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool calls."""
        tools = []
        for method_name in dir(self):
            if method_name.startswith('_tool_'):
                tool_name = method_name[6:]  # Remove '_tool_' prefix
                tools.append(tool_name)
        return sorted(tools)
    
    def show_tool_call_preview(self, tool_call: Dict[str, Any]) -> Panel:
        """Create a preview panel for a tool call."""
        tool_name = tool_call.get("tool_call", "unknown")
        arguments = tool_call.get("arguments", {})
        
        # Create preview content
        preview_text = Text()
        preview_text.append(f"Tool: ", style="bold white")
        preview_text.append(f"{tool_name}\n", style=f"bold {GLYPH_HIGHLIGHT}")
        
        if arguments:
            preview_text.append("Arguments:\n", style="bold white")
            for key, value in arguments.items():
                preview_text.append(f"  {key}: ", style=GLYPH_MUTED)
                preview_text.append(f"{value}\n", style="white")
        
        return Panel(
            preview_text,
            title="🛠️ Tool Call Preview",
            border_style=GLYPH_PRIMARY,
            box=box.ROUNDED
        )

def create_agent_tools(session_id: Optional[str] = None) -> AgentTools:
    """Create an AgentTools instance."""
    return AgentTools(session_id)

if __name__ == "__main__":
    # Test the tool system
    try:
        tools = create_agent_tools()
        console.print(f"Available tools: {', '.join(tools.get_available_tools())}")
    except AgentToolError as e:
        console.print(f"[red]Error: {e}[/red]")