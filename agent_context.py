#!/usr/bin/env python3

"""
Agent Context Module for Glyph.
Handles conversation context tracking and state management for multi-turn interactions.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import deque

from rich.console import Console
from agent_memory import get_agent_memory

console = Console()

@dataclass
class AgentState:
    """Represents the current state of an agent task."""
    user_goal: str
    completed_actions: List[Dict[str, Any]]
    available_data: Dict[str, Any]
    next_steps: List[str]
    iteration: int
    task_complete: bool = False
    needs_clarification: bool = False
    clarification_question: str = ""

@dataclass
class ToolResult:
    """Enhanced tool result with state information."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    extracted_entities: List[str] = None
    note_references: List[str] = None
    state_updates: Dict[str, Any] = None

class ConversationContext:
    """Enhanced conversation context with learning and multi-turn capabilities."""
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.memory = get_agent_memory()
        
        # Conversation tracking
        self.conversation_history: deque = deque(maxlen=max_history)
        self.current_session_entities: Dict[str, List[str]] = {}
        self.session_notes: List[str] = []
        
        # Multi-turn state
        self.current_state: Optional[AgentState] = None
        self.state_history: List[AgentState] = []
        
        # Context tracking
        self.entities: Dict[str, List[str]] = {}  # entity -> related notes
        self.topics: Dict[str, List[str]] = {}   # topic -> related notes
        self.user_patterns: Dict[str, int] = {}  # pattern -> frequency
        self.recent_operations: deque = deque(maxlen=10)
        
        # Reference resolution
        self.current_focus: Optional[str] = None
        self.last_created_note: Optional[str] = None
        self.last_modified_note: Optional[str] = None
        self.last_opened_notes: List[str] = []
    
    def start_multi_turn_task(self, user_goal: str) -> AgentState:
        """Start a new multi-turn task."""
        self.current_state = AgentState(
            user_goal=user_goal,
            completed_actions=[],
            available_data={},
            next_steps=[],
            iteration=0
        )
        return self.current_state
    
    def update_state(self, tool_results: List[ToolResult], next_steps: List[str] = None) -> AgentState:
        """Update the current multi-turn state."""
        if not self.current_state:
            raise ValueError("No active multi-turn task")
        
        # Update state with tool results
        for result in tool_results:
            self.current_state.completed_actions.append({
                "success": result.success,
                "message": result.message,
                "data": result.data,
                "timestamp": datetime.now().isoformat()
            })
            
            # Merge available data
            if result.data:
                self.current_state.available_data.update(result.data)
            
            # Extract and register entities
            if result.extracted_entities:
                for entity in result.extracted_entities:
                    self.register_entity(entity, result.note_references or [])
            
            # Update note references
            if result.note_references:
                self.session_notes.extend(result.note_references)
        
        # Update next steps
        if next_steps:
            self.current_state.next_steps = next_steps
        
        self.current_state.iteration += 1
        
        # Save state to history
        self.state_history.append(self.current_state)
        
        return self.current_state
    
    def complete_task(self, summary: str = ""):
        """Mark the current task as complete."""
        if self.current_state:
            self.current_state.task_complete = True
            self.current_state.next_steps = []
            
            # Learn from the completed task
            self._learn_from_completed_task(summary)
        
        self.current_state = None
    
    def add_conversation_turn(self, user_input: str, assistant_response: str, 
                           tool_calls: Optional[List[Dict]] = None, 
                           resolved_notes: Optional[List[str]] = None):
        """Add a conversation turn to history."""
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response,
            "tool_calls": tool_calls or [],
            "resolved_notes": resolved_notes or []
        }
        
        self.conversation_history.append(turn)
        
        # Extract and learn from this turn
        self._extract_entities_from_turn(user_input, resolved_notes or [])
        self._learn_user_patterns(user_input)
        
        # Update note references in memory
        if resolved_notes:
            for note in resolved_notes:
                # Extract how user referred to this note
                note_references = self._extract_note_references(user_input)
                for ref in note_references:
                    self.memory.register_note_reference(ref, note, user_input)
    
    def resolve_reference(self, reference: str) -> Optional[str]:
        """Resolve pronouns and references to specific notes."""
        reference_lower = reference.lower().strip()
        
        # Handle pronouns and contextual references
        if reference_lower in ["it", "that", "this", "the note"]:
            return self.current_focus or self.last_modified_note or self.last_created_note
        
        if "just created" in reference_lower or "i created" in reference_lower:
            return self.last_created_note
        
        if "last opened" in reference_lower or "opened" in reference_lower:
            return self.last_opened_notes[0] if self.last_opened_notes else None
        
        if "current" in reference_lower or "this note" in reference_lower:
            return self.current_focus
        
        # Check memory for user's previous references
        memory_result = self.memory.resolve_note_reference(reference)
        if memory_result:
            return memory_result
        
        # Check session entities
        for entity, notes in self.current_session_entities.items():
            if reference_lower in entity.lower():
                return notes[0] if notes else None
        
        return None
    
    def register_entity(self, entity_name: str, related_notes: List[str]):
        """Register an entity in current session."""
        entity_clean = entity_name.strip()
        
        if entity_clean not in self.current_session_entities:
            self.current_session_entities[entity_clean] = []
        
        self.current_session_entities[entity_clean].extend(related_notes)
        self.current_session_entities[entity_clean] = list(set(self.current_session_entities[entity_clean]))
        
        # Also register in persistent memory
        self.memory.register_entity(entity_clean, "auto-detected", related_notes, "Session context")
    
    def update_focus(self, note_name: str, operation_type: str):
        """Update the current focus based on operations."""
        if operation_type in ["create_note", "open_note", "edit_note"]:
            self.current_focus = note_name
        
        if operation_type == "create_note":
            self.last_created_note = note_name
        
        if operation_type in ["edit_note", "insert_section", "append_section"]:
            self.last_modified_note = note_name
        
        if operation_type in ["open_note", "open_notes"]:
            if note_name not in self.last_opened_notes:
                self.last_opened_notes.insert(0, note_name)
            self.last_opened_notes = self.last_opened_notes[:5]  # Keep last 5
        
        # Record operation
        self.recent_operations.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation_type,
            "note": note_name
        })
    
    def get_context_for_llm(self) -> Dict[str, Any]:
        """Get context information for LLM processing."""
        return {
            "conversation_history": list(self.conversation_history)[-5:],  # Last 5 turns
            "current_focus": self.current_focus,
            "last_created_note": self.last_created_note,
            "last_modified_note": self.last_modified_note,
            "last_opened_notes": self.last_opened_notes[:3],
            "session_entities": dict(list(self.current_session_entities.items())[:10]),
            "recent_operations": list(self.recent_operations)[-5:],
            "current_state": self.current_state,
            "available_data": self.current_state.available_data if self.current_state else {}
        }
    
    def suggest_next_actions(self) -> List[str]:
        """Suggest possible next actions based on context."""
        suggestions = []
        
        # Based on recent operations
        if self.last_created_note:
            suggestions.append(f"Open {self.last_created_note} in Obsidian")
            suggestions.append(f"Add sections to {self.last_created_note}")
        
        if self.current_focus:
            suggestions.append(f"Link {self.current_focus} to other notes")
            suggestions.append(f"Summarize {self.current_focus}")
        
        # Based on session entities
        for entity, notes in self.current_session_entities.items():
            if len(notes) > 1:
                suggestions.append(f"Create overview of {entity} across notes")
        
        return suggestions[:5]
    
    def _extract_entities_from_turn(self, user_input: str, resolved_notes: List[str]):
        """Extract entities from user input and link to notes."""
        # Use the memory system's entity extraction
        for note in resolved_notes:
            self.memory.extract_and_register_entities(user_input, note)
    
    def _extract_note_references(self, text: str) -> List[str]:
        """Extract how user refers to notes in their input."""
        references = []
        
        # Pattern: "my X", "the X", "X note"
        patterns = [
            r'(?:my|the)\s+([a-zA-Z][\w\s]{2,30?})(?:\s+note)?',
            r'([a-zA-Z][\w\s]{2,30?})\s+(?:note|document|file)',
            r'"([^"]+)"',  # Quoted references
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'  # Title case phrases
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if len(match.strip()) > 2:  # Ignore very short matches
                    references.append(match.strip())
        
        return references
    
    def _learn_user_patterns(self, user_input: str):
        """Learn user's command patterns and preferences."""
        # Track common phrases
        patterns = [
            r'can you (.*)',
            r'please (.*)',
            r'i need to (.*)',
            r'help me (.*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, user_input.lower())
            for match in matches:
                self.user_patterns[match] = self.user_patterns.get(match, 0) + 1
    
    def _learn_from_completed_task(self, summary: str):
        """Learn from a completed multi-turn task."""
        if not self.current_state:
            return
        
        # Store successful task patterns
        task_pattern = {
            "goal": self.current_state.user_goal,
            "actions": len(self.current_state.completed_actions),
            "iterations": self.current_state.iteration,
            "success": True,
            "summary": summary
        }
        
        # This could be stored in memory for future task planning
        console.print(f"[dim]📚 Learned from task: {self.current_state.user_goal}[/dim]")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the conversation context."""
        return {
            "conversation_turns": len(self.conversation_history),
            "session_entities": len(self.current_session_entities),
            "session_notes": len(set(self.session_notes)),
            "user_patterns": len(self.user_patterns),
            "recent_operations": len(self.recent_operations),
            "current_task_active": self.current_state is not None,
            "memory_stats": self.memory.get_memory_stats()
        }

# Global context instance
_conversation_context = None

def get_conversation_context() -> ConversationContext:
    """Get the global conversation context instance."""
    global _conversation_context
    if _conversation_context is None:
        _conversation_context = ConversationContext()
    return _conversation_context