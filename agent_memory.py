#!/usr/bin/env python3

"""
Agent Memory Module for Glyph.
Handles persistent memory for note references, entity tracking, and conversation context.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Set, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict

import difflib
from rich.console import Console

console = Console()

@dataclass
class EntityReference:
    """Represents an entity (person, project, concept) mentioned in conversations."""
    name: str
    type: str  # "person", "project", "concept", "location"
    related_notes: List[str]
    first_mentioned: str  # ISO timestamp
    last_mentioned: str
    context: str  # How it was mentioned
    
@dataclass
class NoteReference:
    """Represents how a user refers to a specific note."""
    user_term: str
    resolved_path: str
    confidence: float
    first_used: str  # ISO timestamp
    last_used: str
    usage_count: int
    context: str  # Context where it was mentioned

class AgentMemory:
    """Persistent memory system for the agent."""
    
    def __init__(self, memory_dir: Optional[str] = None):
        if memory_dir is None:
            memory_dir = os.path.expanduser("~/.glyph/memory")
        
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory storage
        self.note_references: Dict[str, List[NoteReference]] = defaultdict(list)  # note_path -> references
        self.user_aliases: Dict[str, str] = {}  # user_term -> note_path
        self.entities: Dict[str, EntityReference] = {}
        self.conversation_patterns: Dict[str, Any] = {}
        self.user_preferences: Dict[str, Any] = {}
        
        # Load existing memory
        self._load_memory()
    
    def _get_memory_file(self, name: str) -> Path:
        """Get path to memory file."""
        return self.memory_dir / f"{name}.json"
    
    def _load_memory(self):
        """Load memory from disk."""
        try:
            # Load note references
            note_refs_file = self._get_memory_file("note_references")
            if note_refs_file.exists():
                with open(note_refs_file, 'r') as f:
                    data = json.load(f)
                    for note_path, refs in data.items():
                        self.note_references[note_path] = [
                            NoteReference(**ref) for ref in refs
                        ]
            
            # Load user aliases
            aliases_file = self._get_memory_file("user_aliases")
            if aliases_file.exists():
                with open(aliases_file, 'r') as f:
                    self.user_aliases = json.load(f)
            
            # Load entities
            entities_file = self._get_memory_file("entities")
            if entities_file.exists():
                with open(entities_file, 'r') as f:
                    data = json.load(f)
                    self.entities = {
                        name: EntityReference(**entity) for name, entity in data.items()
                    }
            
            # Load conversation patterns
            patterns_file = self._get_memory_file("conversation_patterns")
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    self.conversation_patterns = json.load(f)
            
            # Load user preferences
            prefs_file = self._get_memory_file("user_preferences")
            if prefs_file.exists():
                with open(prefs_file, 'r') as f:
                    self.user_preferences = json.load(f)
                    
        except Exception as e:
            console.print(f"[warning]Warning: Could not load memory: {e}[/warning]")
    
    def _save_memory(self):
        """Save memory to disk."""
        try:
            # Save note references
            note_refs_data = {}
            for note_path, refs in self.note_references.items():
                note_refs_data[note_path] = [asdict(ref) for ref in refs]
            
            with open(self._get_memory_file("note_references"), 'w') as f:
                json.dump(note_refs_data, f, indent=2)
            
            # Save user aliases
            with open(self._get_memory_file("user_aliases"), 'w') as f:
                json.dump(self.user_aliases, f, indent=2)
            
            # Save entities
            entities_data = {name: asdict(entity) for name, entity in self.entities.items()}
            with open(self._get_memory_file("entities"), 'w') as f:
                json.dump(entities_data, f, indent=2)
            
            # Save conversation patterns
            with open(self._get_memory_file("conversation_patterns"), 'w') as f:
                json.dump(self.conversation_patterns, f, indent=2)
            
            # Save user preferences
            with open(self._get_memory_file("user_preferences"), 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
                
        except Exception as e:
            console.print(f"[error]Error saving memory: {e}[/error]")
    
    def register_note_reference(self, user_term: str, resolved_path: str, context: str = ""):
        """Remember how user refers to a note."""
        user_term_clean = user_term.lower().strip()
        timestamp = datetime.now().isoformat()
        
        # Update user aliases for quick lookup
        self.user_aliases[user_term_clean] = resolved_path
        
        # Update or create note reference
        existing_ref = None
        for ref in self.note_references[resolved_path]:
            if ref.user_term.lower() == user_term_clean:
                existing_ref = ref
                break
        
        if existing_ref:
            existing_ref.last_used = timestamp
            existing_ref.usage_count += 1
            existing_ref.context = context  # Update with latest context
        else:
            new_ref = NoteReference(
                user_term=user_term_clean,
                resolved_path=resolved_path,
                confidence=1.0,
                first_used=timestamp,
                last_used=timestamp,
                usage_count=1,
                context=context
            )
            self.note_references[resolved_path].append(new_ref)
        
        self._save_memory()
        console.print(f"[dim]💾 Remembered: '{user_term}' → '{resolved_path}'[/dim]")
    
    def resolve_note_reference(self, user_term: str) -> Optional[str]:
        """Find note from user's previous references."""
        user_term_clean = user_term.lower().strip()
        
        # Direct alias lookup
        if user_term_clean in self.user_aliases:
            path = self.user_aliases[user_term_clean]
            console.print(f"[dim]🧠 Memory: '{user_term}' → '{path}'[/dim]")
            return path
        
        # Fuzzy matching on stored references
        return self._fuzzy_match_references(user_term_clean)
    
    def _fuzzy_match_references(self, user_term: str) -> Optional[str]:
        """Find similar references using fuzzy matching."""
        best_match = None
        best_score = 0.0
        threshold = 0.8
        
        for alias, path in self.user_aliases.items():
            # Use difflib for fuzzy matching
            score = difflib.SequenceMatcher(None, user_term, alias).ratio()
            
            # Also check if user_term is contained in alias or vice versa
            if user_term in alias or alias in user_term:
                score = max(score, 0.9)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = path
        
        if best_match:
            console.print(f"[dim]🔍 Fuzzy match: '{user_term}' → '{best_match}' (score: {best_score:.2f})[/dim]")
            return best_match
        
        return None
    
    def register_entity(self, name: str, entity_type: str, related_notes: List[str], context: str = ""):
        """Register an entity (person, project, concept) with related notes."""
        name_clean = name.strip()
        timestamp = datetime.now().isoformat()
        
        if name_clean in self.entities:
            # Update existing entity
            entity = self.entities[name_clean]
            entity.related_notes = list(set(entity.related_notes + related_notes))
            entity.last_mentioned = timestamp
            entity.context = context
        else:
            # Create new entity
            self.entities[name_clean] = EntityReference(
                name=name_clean,
                type=entity_type,
                related_notes=related_notes,
                first_mentioned=timestamp,
                last_mentioned=timestamp,
                context=context
            )
        
        self._save_memory()
    
    def find_related_notes(self, entity_name: str) -> List[str]:
        """Find notes related to an entity."""
        entity_name_clean = entity_name.strip()
        
        # Direct lookup
        if entity_name_clean in self.entities:
            return self.entities[entity_name_clean].related_notes
        
        # Fuzzy lookup
        for name, entity in self.entities.items():
            if entity_name_clean.lower() in name.lower() or name.lower() in entity_name_clean.lower():
                return entity.related_notes
        
        return []
    
    def extract_and_register_entities(self, text: str, note_path: str):
        """Extract entities from text and register them."""
        # Simple pattern-based entity extraction
        
        # Extract person names (Dr. Name, Prof. Name)
        person_patterns = [
            r'Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Prof\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Professor\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in person_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                self.register_entity(f"Dr. {match}", "person", [note_path], f"Mentioned in {note_path}")
        
        # Extract project/research terms
        research_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:project|research|study)',
            r'(?:project|research|study)\s+(?:on|about)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in research_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                self.register_entity(match, "project", [note_path], f"Research mentioned in {note_path}")
    
    def learn_user_pattern(self, user_input: str, resolved_note: str):
        """Learn user's naming and reference patterns."""
        # Extract patterns like "my X", "the X I created", etc.
        patterns = [
            r'my\s+([a-z]+(?:\s+[a-z]+)*)',
            r'the\s+([a-z]+(?:\s+[a-z]+)*)\s+(?:I\s+(?:created|wrote|made))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, user_input.lower())
            for match in matches:
                pattern_key = f"user_refers_to_{match.replace(' ', '_')}"
                if pattern_key not in self.conversation_patterns:
                    self.conversation_patterns[pattern_key] = []
                self.conversation_patterns[pattern_key].append(resolved_note)
        
        self._save_memory()
    
    def suggest_completions(self, partial_command: str) -> List[str]:
        """Suggest completions based on user history."""
        suggestions = []
        partial_lower = partial_command.lower()
        
        # Look for partial matches in user aliases
        for alias, path in self.user_aliases.items():
            if partial_lower in alias:
                # Extract the note name for suggestion
                note_name = Path(path).stem
                suggestions.append(note_name)
        
        # Look for entity matches
        for entity_name in self.entities.keys():
            if partial_lower in entity_name.lower():
                suggestions.append(entity_name)
        
        return list(set(suggestions))[:5]  # Return top 5 unique suggestions
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get statistics about stored memory."""
        return {
            "note_references": sum(len(refs) for refs in self.note_references.values()),
            "unique_notes": len(self.note_references),
            "user_aliases": len(self.user_aliases),
            "entities": len(self.entities),
            "conversation_patterns": len(self.conversation_patterns)
        }
    
    def clear_memory(self):
        """Clear all memory (use with caution)."""
        self.note_references.clear()
        self.user_aliases.clear()
        self.entities.clear()
        self.conversation_patterns.clear()
        self.user_preferences.clear()
        
        # Remove files
        for file_name in ["note_references", "user_aliases", "entities", "conversation_patterns", "user_preferences"]:
            file_path = self._get_memory_file(file_name)
            if file_path.exists():
                file_path.unlink()
        
        console.print("[warning]🧹 Memory cleared[/warning]")

# Global memory instance
_agent_memory = None

def get_agent_memory() -> AgentMemory:
    """Get the global agent memory instance."""
    global _agent_memory
    if _agent_memory is None:
        _agent_memory = AgentMemory()
    return _agent_memory