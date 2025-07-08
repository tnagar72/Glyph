#!/usr/bin/env python3

"""
Agent Prompts Module for Glyph.
Contains prompts for converting voice commands to structured tool calls.
"""

from typing import Dict, List, Optional

def get_agent_system_prompt() -> str:
    """Get the system prompt for the agent mode."""
    return """You are Glyph Agent, a conversational voice-controlled assistant for Obsidian vault management. You maintain context across multiple interactions and can understand references to previous operations.

## Your Capabilities

You can perform these operations through structured tool calls:

### File & Note Management
- create_note(name, folder?, content?) - Create a new note
- delete_note(name) - Delete an existing note  
- rename_note(old_name, new_name) - Rename a note
- move_note(name, target_folder) - Move note to folder
- list_notes(query?, folder?) - List/search notes
- read_note(name) - Read the content of a note
- summarize_note(name, heading?) - Read a note and add an intelligent summary section
- open_note(name) - Open a single note in Obsidian
- open_notes(query?, folder?) - Find and open multiple notes in Obsidian

### Section Editing
- insert_section(note, heading, content, position?) - Add new section
- append_section(note, heading, content) - Add to existing section
- replace_section(note, heading, content) - Replace section content
- delete_section(note, heading) - Remove a section

### Linking
- add_wikilink(source_note, target_note, alias?, position?) - Add [[links]]

## Response Format

You MUST respond with valid JSON containing either:

1. **Single Tool Call:**
```json
{
  "tool_call": "create_note",
  "arguments": {
    "name": "Meeting Notes",
    "folder": "Work",
    "content": "# Meeting Notes\n\n- Topic 1\n- Topic 2"
  }
}
```

2. **Multiple Tool Calls:**
```json
{
  "tool_calls": [
    {
      "tool_call": "create_note", 
      "arguments": {"name": "Project Plan", "content": "# Project Plan"}
    },
    {
      "tool_call": "add_wikilink",
      "arguments": {"source_note": "Index", "target_note": "Project Plan"}
    }
  ]
}
```

3. **Clarification Request:**
```json
{
  "clarification": "I need more information. Which folder should I create the note in?",
  "suggested_completions": ["Work", "Personal", "Projects"]
}
```

## Guidelines

1. **Conversational Context**: 
   - Use conversation history and working context to understand references
   - Handle pronouns like "it", "that", "the note I just created"
   - Remember what was just done and maintain conversational flow
   - Reference previous operations when relevant

2. **Smart Context Inference**: 
   - Infer reasonable defaults from conversation context
   - Use the "Current Focus" note when user says "it" or "that note"
   - Reference recently created/modified notes appropriately
   - Build on previous operations naturally

3. **Reference Resolution**: 
   - "it", "that" → Current Focus or Last Created/Modified Note
   - "the note I just created" → Last Created Note
   - "add to it" → Current Focus Note
   - "open that" → Last mentioned or created note

4. **Multi-step Operations**:
   - Break complex requests into multiple tool calls
   - Use logical sequencing (create before linking, etc.)
   - Consider dependencies between operations

5. **Content-Aware Operations**:
   - Always read note content before summarizing, analyzing, or extracting information
   - Use read_note to get the full content before creating summaries
   - Never use placeholder text like "[Summary will be filled]" - always provide actual content
   - When asked to summarize, extract key points, or analyze content, read the note first

6. **Safety First**:
   - Never delete without explicit confirmation in the request
   - Be conservative with destructive operations
   - Prefer appending/creating over replacing/deleting

7. **Obsidian Conventions**:
   - Use proper markdown formatting
   - Respect wikilink syntax: [[Note Name]]
   - Understand common Obsidian patterns (Daily Notes, MOCs, etc.)

## Example Interactions

**User**: "Create a note about today's standup meeting"
**Response**: 
```json
{
  "tool_call": "create_note",
  "arguments": {
    "name": "Daily Standup",
    "content": "# Daily Standup\\n\\n## Date\\n[Date will be filled]\\n\\n## Agenda\\n- \\n\\n## Action Items\\n- \\n\\n## Notes\\n- "
  }
}
```

**User**: "Add a section called Ideas to my project notes"  
**Response**:
```json
{
  "tool_call": "insert_section",
  "arguments": {
    "note": "project notes",
    "heading": "Ideas",
    "content": "## Ideas\n\n- "
  }
}
```

**User**: "Open all notes that contain CMU"
**Response**:
```json
{
  "tool_call": "open_notes",
  "arguments": {
    "query": "CMU"
  }
}
```

**User**: "Add a summary to my research paper"
**Response**:
```json
{
  "tool_call": "summarize_note",
  "arguments": {
    "name": "research paper",
    "heading": "Summary"
  }
}
```

Remember: Always respond with valid JSON. Never include explanations outside the JSON structure."""

def get_agent_user_prompt(command: str, context: Optional[Dict] = None) -> str:
    """Get the user prompt for a specific voice command."""
    prompt_parts = []
    
    # Add voice command
    prompt_parts.append(f"Voice Command: \"{command}\"")
    
    # Add context if available
    if context:
        # Add multi-turn state if active
        if context.get("current_state"):
            state = context["current_state"]
            prompt_parts.append(f"\n## Multi-Turn Task State (Iteration {state.get('iteration', 0)}):")
            prompt_parts.append(f"Original Goal: {state.get('user_goal', 'Unknown')}")
            
            if state.get("completed_actions"):
                prompt_parts.append("Completed Actions:")
                for action in state["completed_actions"][-3:]:  # Last 3 actions
                    prompt_parts.append(f"- {action.get('message', 'Unknown action')}")
            
            if state.get("available_data"):
                prompt_parts.append("Available Data:")
                for key, value in list(state["available_data"].items())[:5]:  # Top 5 data items
                    if isinstance(value, list):
                        prompt_parts.append(f"- {key}: {len(value)} items")
                    else:
                        prompt_parts.append(f"- {key}: {str(value)[:50]}...")
            
            if state.get("next_steps"):
                prompt_parts.append("Planned Next Steps:")
                for step in state["next_steps"]:
                    prompt_parts.append(f"- {step}")
        
        # Add conversation history for context
        if context.get("conversation_history"):
            recent_history = context["conversation_history"][-3:]  # Last 3 exchanges
            if recent_history:
                prompt_parts.append("\n## Recent Conversation:")
                for turn in recent_history:
                    prompt_parts.append(f"User: {turn['user']}")
                    if turn.get('assistant'):
                        prompt_parts.append(f"Assistant: {turn['assistant']}")
                    if turn.get('tool_calls'):
                        tool_names = [call.get('tool_call', 'unknown') for call in turn['tool_calls']]
                        prompt_parts.append(f"Actions: {', '.join(tool_names)}")
                    prompt_parts.append("")
        
        # Add working context for reference resolution
        if context.get("current_focus") or context.get("last_created_note") or context.get("last_modified_note"):
            prompt_parts.append("## Current Working Context:")
            
            if context.get("current_focus"):
                prompt_parts.append(f"Current Focus: {context['current_focus']}")
            
            if context.get("last_created_note"):
                prompt_parts.append(f"Last Created Note: {context['last_created_note']}")
            
            if context.get("last_modified_note"):
                prompt_parts.append(f"Last Modified Note: {context['last_modified_note']}")
            
            if context.get("last_opened_notes"):
                prompt_parts.append(f"Last Opened Notes: {', '.join(context['last_opened_notes'][:3])}")
        
        # Add session entities
        if context.get("session_entities"):
            entities = context["session_entities"]
            if entities:
                prompt_parts.append("## Session Entities:")
                for entity, notes in list(entities.items())[:5]:
                    prompt_parts.append(f"- {entity}: {', '.join(notes[:2])}")
    
    prompt_parts.append("\n## Instructions:")
    
    # Multi-turn specific instructions
    if context and context.get("current_state"):
        prompt_parts.append("This is part of a multi-turn task. Based on the current state:")
        prompt_parts.append("1. If the task can be completed with this command, generate appropriate tool calls")
        prompt_parts.append("2. If this is a continuation/refinement, build on the available data")
        prompt_parts.append("3. If the task is complete, indicate completion in your response")
        prompt_parts.append("4. Use the conversation history and working context to resolve references")
    else:
        prompt_parts.append("Convert this voice command into the appropriate tool call(s).")
        prompt_parts.append("Use the conversation history and working context to resolve references like 'it', 'that', 'the note I just created', etc.")
    
    return "\n".join(prompt_parts)

def get_reflection_prompt(command: str, current_state: Dict, iteration: int) -> str:
    """Get prompt for reflection-based multi-turn processing."""
    prompt_parts = []
    
    prompt_parts.append(f"## Multi-Turn Task Reflection (Iteration {iteration})")
    prompt_parts.append(f"User Goal: \"{current_state.get('user_goal', command)}\"")
    prompt_parts.append(f"Current Command: \"{command}\"")
    
    if current_state.get("completed_actions"):
        prompt_parts.append("\n## Completed Actions:")
        for i, action in enumerate(current_state["completed_actions"][-5:], 1):
            success = "✅" if action.get("success") else "❌"
            prompt_parts.append(f"{i}. {success} {action.get('message', 'Unknown')}")
    
    if current_state.get("available_data"):
        prompt_parts.append("\n## Available Data:")
        for key, value in list(current_state["available_data"].items())[:7]:
            if isinstance(value, list):
                prompt_parts.append(f"- {key}: {len(value)} items")
            elif isinstance(value, dict):
                prompt_parts.append(f"- {key}: {len(value)} properties")
            else:
                value_str = str(value)[:80]
                prompt_parts.append(f"- {key}: {value_str}{'...' if len(str(value)) > 80 else ''}")
    
    prompt_parts.append("\n## Task Analysis:")
    prompt_parts.append("Based on the completed actions and available data, determine the next steps.")
    prompt_parts.append("Respond with one of:")
    
    prompt_parts.append("\n**CONTINUE** - Generate tool calls to progress toward the goal:")
    prompt_parts.append("```json")
    prompt_parts.append("{")
    prompt_parts.append('  "action": "continue",')
    prompt_parts.append('  "tool_calls": [')
    prompt_parts.append('    {"tool_call": "...", "arguments": {...}}')
    prompt_parts.append('  ],')
    prompt_parts.append('  "reasoning": "Why these actions will progress toward the goal"')
    prompt_parts.append("}")
    prompt_parts.append("```")
    
    prompt_parts.append("\n**COMPLETE** - Task is finished:")
    prompt_parts.append("```json")
    prompt_parts.append("{")
    prompt_parts.append('  "action": "complete",')
    prompt_parts.append('  "summary": "What was accomplished",')
    prompt_parts.append('  "result": "Final result or outcome"')
    prompt_parts.append("}")
    prompt_parts.append("```")
    
    prompt_parts.append("\n**CLARIFY** - Need user input to proceed:")
    prompt_parts.append("```json")
    prompt_parts.append("{")
    prompt_parts.append('  "action": "clarify",')
    prompt_parts.append('  "question": "What specific information do you need?",')
    prompt_parts.append('  "options": ["option1", "option2", "option3"]')
    prompt_parts.append("}")
    prompt_parts.append("```")
    
    return "\n".join(prompt_parts)

def get_multi_step_prompt(commands: List[str]) -> str:
    """Get prompt for handling multiple commands in sequence."""
    commands_text = "\n".join([f"{i+1}. {cmd}" for i, cmd in enumerate(commands)])
    
    return f"""Multiple Voice Commands:
{commands_text}

Convert these commands into a sequence of tool calls. Consider:
1. Dependencies between commands
2. Logical ordering
3. Context sharing between steps

Respond with a "tool_calls" array containing all necessary operations."""

def get_clarification_prompt(original_command: str, ambiguity: str) -> str:
    """Get prompt for handling ambiguous commands."""
    return f"""Original Command: "{original_command}"

Ambiguity Detected: {ambiguity}

Please provide a clarification request with:
1. A clear question for the user
2. Suggested completions/options
3. Context about why clarification is needed

Use the clarification response format."""

def get_context_analysis_prompt(vault_structure: Dict) -> str:
    """Get prompt for analyzing vault context."""
    return f"""Vault Structure Analysis:
{vault_structure}

This context will help you make better decisions about:
- Where to create new notes
- Which existing notes to reference
- Appropriate folder structures
- Common naming conventions in this vault

Use this information to provide smarter defaults and suggestions."""

# Common command patterns for better recognition
COMMAND_PATTERNS = {
    "create": [
        "create a note",
        "make a new note",
        "add a note",
        "start a new document"
    ],
    "edit": [
        "add to",
        "update",
        "modify",
        "change",
        "edit"
    ],
    "organize": [
        "move",
        "organize",
        "put in folder",
        "categorize"
    ],
    "link": [
        "link to",
        "connect",
        "reference",
        "add link"
    ],
    "search": [
        "find",
        "search for",
        "list",
        "show me",
        "what notes"
    ]
}

def get_command_examples() -> List[Dict[str, str]]:
    """Get example commands with expected tool calls."""
    return [
        {
            "command": "Create a note about today's meeting",
            "tool_call": "create_note",
            "description": "Creates a new meeting note with basic structure"
        },
        {
            "command": "Add a section called Action Items to my project plan",
            "tool_call": "insert_section", 
            "description": "Adds a new section to an existing note"
        },
        {
            "command": "Move my grocery list to the personal folder",
            "tool_call": "move_note",
            "description": "Moves a note to a specific folder"
        },
        {
            "command": "Link the project plan to my daily notes",
            "tool_call": "add_wikilink",
            "description": "Creates a wikilink between notes"
        },
        {
            "command": "Find all notes about meetings",
            "tool_call": "list_notes",
            "description": "Searches for notes matching criteria"
        },
        {
            "command": "Open all notes with CMU in the title",
            "tool_call": "open_notes",
            "description": "Finds and opens multiple notes in Obsidian"
        }
    ]