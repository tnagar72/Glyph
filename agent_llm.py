#!/usr/bin/env python3

"""
Agent LLM Module for Glyph.
Handles conversion of voice commands to structured tool calls using GPT-4.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

from openai import OpenAI
from rich.console import Console

from agent_prompts import get_agent_system_prompt, get_agent_user_prompt
from agent_config import get_agent_config
from utils import verbose_print

console = Console()

@dataclass
class AgentResponse:
    """Response from the agent LLM."""
    success: bool
    tool_calls: Optional[List[Dict[str, Any]]] = None
    clarification: Optional[str] = None
    suggested_completions: Optional[List[str]] = None
    error_message: Optional[str] = None
    raw_response: Optional[str] = None

class AgentLLM:
    """Handles LLM interactions for agent mode."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.config = get_agent_config()
        self.session_id = session_id
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        if not self.client.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Import context after initialization to avoid circular imports
        from agent_context import get_conversation_context
        self.context = get_conversation_context()
        
        # Session context for memory (legacy - gradually migrating to context)
        self.session_context = {
            "recent_notes": [],
            "open_notes": [],
            "session_history": [],
            "current_folder": None,
            "conversation_history": [],  # Full conversation context
            "working_context": {         # Current working state
                "last_created_note": None,
                "last_modified_note": None,
                "last_opened_notes": [],
                "current_focus": None,
                "recent_operations": []
            }
        }
    
    def update_context(self, context_updates: Dict[str, Any]):
        """Update session context with new information."""
        self.session_context.update(context_updates)
        
        # Limit context size to prevent token overflow
        if len(self.session_context["session_history"]) > 10:
            self.session_context["session_history"] = self.session_context["session_history"][-10:]
        
        # Limit conversation history to last 20 exchanges
        if len(self.session_context["conversation_history"]) > 20:
            self.session_context["conversation_history"] = self.session_context["conversation_history"][-20:]
        
        # Limit recent operations to last 10
        if len(self.session_context["working_context"]["recent_operations"]) > 10:
            self.session_context["working_context"]["recent_operations"] = self.session_context["working_context"]["recent_operations"][-10:]
    
    def update_working_context(self, operation_type: str, result: Dict[str, Any]):
        """Update working context based on operation results."""
        working_ctx = self.session_context["working_context"]
        
        # Update based on operation type
        if operation_type == "create_note":
            working_ctx["last_created_note"] = result.get("note_name")
            working_ctx["current_focus"] = result.get("note_name")
        elif operation_type == "edit_note" or operation_type.startswith("insert_") or operation_type.startswith("append_"):
            working_ctx["last_modified_note"] = result.get("note_name")
            working_ctx["current_focus"] = result.get("note_name")
        elif operation_type == "open_note" or operation_type == "open_notes":
            # Handle both single note and multiple notes
            if operation_type == "open_note":
                # Single note opened
                note_name = result.get("note_name")
                if note_name:
                    working_ctx["last_opened_notes"] = [note_name]
                    working_ctx["current_focus"] = note_name
            else:
                # Multiple notes opened  
                opened_notes = result.get("opened_notes", [])
                if opened_notes:
                    working_ctx["last_opened_notes"] = opened_notes
                    working_ctx["current_focus"] = opened_notes[0] if len(opened_notes) == 1 else None
        elif operation_type == "list_notes":
            # Don't change focus for list operations, but track the query
            pass
        
        # Add to recent operations
        working_ctx["recent_operations"].append({
            "type": operation_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_conversation_turn(self, user_input: str, assistant_response: str, tool_calls: Optional[List[Dict]] = None):
        """Add a conversation turn to history."""
        turn = {
            "user": user_input,
            "assistant": assistant_response,
            "tool_calls": tool_calls or [],
            "timestamp": datetime.now().isoformat()
        }
        self.session_context["conversation_history"].append(turn)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from GPT response."""
        # Remove markdown code blocks if present
        response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'^```\s*$', '', response, flags=re.MULTILINE)
        
        # Remove any leading/trailing whitespace
        response = response.strip()
        
        # Try to find JSON content within the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return response
    
    def _validate_tool_call(self, tool_call: Dict[str, Any]) -> bool:
        """Validate a single tool call structure."""
        if not isinstance(tool_call, dict):
            return False
        
        # Must have tool_call field
        if "tool_call" not in tool_call:
            return False
        
        # Must have arguments field (can be empty dict)
        if "arguments" not in tool_call:
            tool_call["arguments"] = {}
        
        return True
    
    def _parse_agent_response(self, response_text: str) -> AgentResponse:
        """Parse GPT response into structured AgentResponse."""
        try:
            # Clean the response
            clean_response = self._clean_json_response(response_text)
            verbose_print(f"Cleaned response: {clean_response}")
            
            # Parse JSON
            response_data = json.loads(clean_response)
            
            # Handle clarification request
            if "clarification" in response_data:
                return AgentResponse(
                    success=True,
                    clarification=response_data["clarification"],
                    suggested_completions=response_data.get("suggested_completions", []),
                    raw_response=response_text
                )
            
            # Handle single tool call
            if "tool_call" in response_data:
                if self._validate_tool_call(response_data):
                    return AgentResponse(
                        success=True,
                        tool_calls=[response_data],
                        raw_response=response_text
                    )
                else:
                    return AgentResponse(
                        success=False,
                        error_message="Invalid tool call structure",
                        raw_response=response_text
                    )
            
            # Handle multiple tool calls
            if "tool_calls" in response_data:
                tool_calls = response_data["tool_calls"]
                if not isinstance(tool_calls, list):
                    return AgentResponse(
                        success=False,
                        error_message="tool_calls must be a list",
                        raw_response=response_text
                    )
                
                # Validate all tool calls
                valid_calls = []
                for call in tool_calls:
                    if self._validate_tool_call(call):
                        valid_calls.append(call)
                    else:
                        verbose_print(f"Invalid tool call: {call}")
                
                if valid_calls:
                    return AgentResponse(
                        success=True,
                        tool_calls=valid_calls,
                        raw_response=response_text
                    )
                else:
                    return AgentResponse(
                        success=False,
                        error_message="No valid tool calls found",
                        raw_response=response_text
                    )
            
            # No recognized response format
            return AgentResponse(
                success=False,
                error_message="Response does not contain tool_call, tool_calls, or clarification",
                raw_response=response_text
            )
            
        except json.JSONDecodeError as e:
            verbose_print(f"JSON decode error: {e}")
            return AgentResponse(
                success=False,
                error_message=f"Invalid JSON response: {e}",
                raw_response=response_text
            )
        except Exception as e:
            verbose_print(f"Parse error: {e}")
            return AgentResponse(
                success=False,
                error_message=f"Failed to parse response: {e}",
                raw_response=response_text
            )
    
    def process_voice_command(self, command: str, context: Optional[Dict] = None) -> AgentResponse:
        """Process a voice command and return structured tool calls."""
        try:
            verbose_print(f"Processing voice command: {command}")
            
            # Merge provided context with session context
            full_context = self.session_context.copy()
            if context:
                full_context.update(context)
            
            # Create prompts
            system_prompt = get_agent_system_prompt()
            user_prompt = get_agent_user_prompt(command, full_context)
            
            verbose_print(f"System prompt length: {len(system_prompt)}")
            verbose_print(f"User prompt: {user_prompt}")
            
            # Call GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent parsing
                max_tokens=2000  # Allow for complex multi-step operations
            )
            
            response_text = response.choices[0].message.content.strip()
            verbose_print(f"Raw GPT response: {response_text}")
            
            # Parse the response
            agent_response = self._parse_agent_response(response_text)
            
            # Update session history if successful
            if agent_response.success and agent_response.tool_calls:
                self.session_context["session_history"].append({
                    "command": command,
                    "tool_calls": len(agent_response.tool_calls),
                    "timestamp": "now"  # Could be proper timestamp
                })
            
            return agent_response
            
        except Exception as e:
            verbose_print(f"Agent LLM error: {e}")
            return AgentResponse(
                success=False,
                error_message=f"LLM processing failed: {e}"
            )
    
    def process_clarification_response(self, original_command: str, clarification_response: str) -> AgentResponse:
        """Process user's response to a clarification request."""
        # Combine the original command with the clarification
        combined_command = f"{original_command} (clarification: {clarification_response})"
        return self.process_voice_command(combined_command)
    
    def get_vault_context(self, vault_path: str) -> Dict[str, Any]:
        """Analyze vault structure to provide context."""
        try:
            from pathlib import Path
            vault = Path(vault_path)
            
            if not vault.exists():
                return {}
            
            # Get recent notes (by modification time)
            md_files = list(vault.rglob("*.md"))
            md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            recent_notes = [f.stem for f in md_files[:20]]  # Top 20 recent notes
            
            # Get folder structure
            folders = [str(p.relative_to(vault)) for p in vault.rglob("*") if p.is_dir() and not p.name.startswith('.')]
            
            # Common note patterns
            daily_notes = [f.stem for f in md_files if re.match(r'\d{4}-\d{2}-\d{2}', f.stem)]
            
            context = {
                "recent_notes": recent_notes,
                "folders": folders[:10],  # Limit to prevent token overflow
                "daily_notes": daily_notes[:5],
                "total_notes": len(md_files)
            }
            
            self.update_context(context)
            return context
            
        except Exception as e:
            verbose_print(f"Error getting vault context: {e}")
            return {}
    
    def suggest_note_name(self, command: str) -> str:
        """Suggest a note name based on the command."""
        # Simple heuristics for note naming
        command_lower = command.lower()
        
        # Extract key terms
        words = re.findall(r'\b\w+\b', command_lower)
        
        # Remove common words
        stop_words = {'a', 'an', 'the', 'for', 'about', 'on', 'in', 'with', 'note', 'create', 'make', 'new'}
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        if meaningful_words:
            # Capitalize and join
            return ' '.join(word.capitalize() for word in meaningful_words[:4])
        else:
            return "New Note"
    
    def analyze_command_intent(self, command: str) -> Dict[str, Any]:
        """Analyze command to determine intent and extract key information."""
        command_lower = command.lower()
        
        intent_analysis = {
            "intent": "unknown",
            "confidence": 0.0,
            "entities": {},
            "modifiers": []
        }
        
        # Intent detection patterns
        if any(word in command_lower for word in ['create', 'make', 'new', 'add']):
            intent_analysis["intent"] = "create"
            intent_analysis["confidence"] = 0.8
        elif any(word in command_lower for word in ['edit', 'update', 'modify', 'change']):
            intent_analysis["intent"] = "edit"
            intent_analysis["confidence"] = 0.7
        elif any(word in command_lower for word in ['delete', 'remove', 'trash']):
            intent_analysis["intent"] = "delete"
            intent_analysis["confidence"] = 0.9
        elif any(word in command_lower for word in ['move', 'organize', 'put']):
            intent_analysis["intent"] = "organize"
            intent_analysis["confidence"] = 0.7
        elif any(word in command_lower for word in ['find', 'search', 'list', 'show']):
            intent_analysis["intent"] = "search"
            intent_analysis["confidence"] = 0.8
        
        # Extract note names (simple heuristic)
        note_pattern = r'(?:note|file|document)\s+(?:called|named|about)\s+([^,\.]+)'
        note_match = re.search(note_pattern, command_lower)
        if note_match:
            intent_analysis["entities"]["note_name"] = note_match.group(1).strip()
        
        return intent_analysis
    
    def get_completion(self, prompt: str, model: str = "gpt-4") -> str:
        """Get a simple completion from the LLM for summarization tasks."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            verbose_print(f"Completion error: {e}")
            raise e
    
    def process_multi_turn_command(self, command: str, max_iterations: int = 5) -> List[AgentResponse]:
        """Process a command with multi-turn reflection capabilities."""
        from agent_prompts import get_reflection_prompt
        
        # Start multi-turn task
        state = self.context.start_multi_turn_task(command)
        responses = []
        
        for iteration in range(max_iterations):
            console.print(f"[dim]🔄 Multi-turn iteration {iteration + 1}/{max_iterations}[/dim]")
            
            # Get reflection prompt
            prompt = get_reflection_prompt(command, state.__dict__, iteration)
            
            try:
                # Get LLM response
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a multi-turn task planning agent. Analyze the current state and determine the next action."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1500
                )
                
                response_text = response.choices[0].message.content.strip()
                parsed_response = self._parse_reflection_response(response_text)
                
                if parsed_response.action == "complete":
                    console.print(f"[success]✅ Task completed: {parsed_response.summary}[/success]")
                    self.context.complete_task(parsed_response.summary)
                    break
                
                elif parsed_response.action == "clarify":
                    console.print(f"[warning]❓ Clarification needed: {parsed_response.question}[/warning]")
                    # Return clarification to user
                    agent_response = AgentResponse(
                        success=True,
                        clarification=parsed_response.question,
                        suggested_completions=parsed_response.options
                    )
                    responses.append(agent_response)
                    break
                
                elif parsed_response.action == "continue":
                    # Execute tool calls
                    agent_response = AgentResponse(
                        success=True,
                        tool_calls=parsed_response.tool_calls,
                        raw_response=response_text
                    )
                    responses.append(agent_response)
                    
                    # Update state (this would be done in the CLI after tool execution)
                    # For now, just increment iteration
                    state.iteration += 1
                
            except Exception as e:
                console.print(f"[error]Multi-turn processing error: {e}[/error]")
                break
        
        return responses
    
    def _parse_reflection_response(self, response_text: str) -> 'ReflectionResponse':
        """Parse reflection response from LLM."""
        try:
            # Extract JSON from response
            import json
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                return ReflectionResponse(
                    action=data.get("action", "continue"),
                    tool_calls=data.get("tool_calls", []),
                    summary=data.get("summary", ""),
                    question=data.get("question", ""),
                    options=data.get("options", []),
                    reasoning=data.get("reasoning", "")
                )
            else:
                # Fallback parsing
                return ReflectionResponse(
                    action="continue",
                    tool_calls=[],
                    summary="Failed to parse response",
                    question="",
                    options=[],
                    reasoning=""
                )
        except Exception as e:
            verbose_print(f"Error parsing reflection response: {e}")
            return ReflectionResponse(
                action="continue",
                tool_calls=[],
                summary="Parse error",
                question="",
                options=[],
                reasoning=""
            )

@dataclass
class ReflectionResponse:
    """Response from reflection-based processing."""
    action: str  # "continue", "complete", "clarify"
    tool_calls: List[Dict[str, Any]]
    summary: str
    question: str
    options: List[str]
    reasoning: str

def create_agent_llm(session_id: Optional[str] = None) -> AgentLLM:
    """Create an AgentLLM instance."""
    return AgentLLM(session_id)

if __name__ == "__main__":
    # Test the agent LLM
    try:
        agent = create_agent_llm()
        
        # Test commands
        test_commands = [
            "Create a note about today's meeting",
            "Add a section called Action Items to my project plan",
            "Find all notes about meetings"
        ]
        
        for cmd in test_commands:
            console.print(f"\n[bold]Testing:[/bold] {cmd}")
            response = agent.process_voice_command(cmd)
            console.print(f"Success: {response.success}")
            if response.tool_calls:
                console.print(f"Tool calls: {len(response.tool_calls)}")
            if response.clarification:
                console.print(f"Clarification: {response.clarification}")
            if response.error_message:
                console.print(f"Error: {response.error_message}")
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")