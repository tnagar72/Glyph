#!/usr/bin/env python3

"""
Demonstration of the enhanced agent architecture capabilities.
Shows memory, learning, and multi-turn conversation features.
"""

import sys
import os
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, os.getcwd())

def demo_memory_learning():
    """Demonstrate memory and learning capabilities."""
    print("🧠 Enhanced Agent Memory & Learning Demo")
    print("=" * 60)
    
    from agent_memory import get_agent_memory
    from agent_context import get_conversation_context
    
    memory = get_agent_memory()
    context = get_conversation_context()
    
    print("📚 Scenario: User learns to use different ways to refer to the same note")
    print()
    
    # Simulate first interaction
    print("👤 User: 'Summarize my Stanford SOP'")
    print("🤖 Agent: Finding note... (uses intelligent discovery)")
    memory.register_note_reference("stanford sop", "Wisconsin/Stanford Symbolic Systems SOP.md", "first mention")
    print("💾 Agent learns: 'stanford sop' → Stanford Symbolic Systems SOP")
    print()
    
    # Simulate second interaction with different terminology
    print("👤 User: 'Add a conclusion to my symbolic systems application'")
    memory.register_note_reference("symbolic systems application", "Wisconsin/Stanford Symbolic Systems SOP.md", "second mention")
    print("💾 Agent learns: 'symbolic systems application' → same note")
    print()
    
    # Simulate third interaction with typo
    print("👤 User: 'Open my standford document'")  # Typo: standford
    resolved = memory.resolve_note_reference("standford document")
    print(f"🧠 Agent remembers: 'standford document' → {resolved}")
    print("✨ No need to search again - memory resolved the typo!")
    print()
    
    # Show memory stats
    stats = memory.get_memory_stats()
    print(f"📊 Memory Stats: {stats['user_aliases']} aliases for {stats['unique_notes']} notes")
    print()

def demo_conversation_context():
    """Demonstrate conversation context and reference resolution."""
    print("💬 Enhanced Conversation Context Demo")
    print("=" * 60)
    
    from agent_context import get_conversation_context
    
    context = get_conversation_context()
    
    print("📚 Scenario: Multi-turn conversation with pronoun resolution")
    print()
    
    # Turn 1
    print("👤 User: 'Create a note about today's research meeting'")
    context.add_conversation_turn(
        user_input="Create a note about today's research meeting",
        assistant_response="Created 'Research Meeting - July 8th'",
        tool_calls=[{"tool_call": "create_note", "arguments": {"name": "Research Meeting - July 8th"}}],
        resolved_notes=["Research Meeting - July 8th.md"]
    )
    context.update_focus("Research Meeting - July 8th.md", "create_note")
    print("🤖 Agent: Created 'Research Meeting - July 8th'")
    print("💾 Context: Remembers this as 'current focus' and 'last created'")
    print()
    
    # Turn 2 - using pronoun
    print("👤 User: 'Add action items section to it'")
    resolved = context.resolve_reference("it")
    print(f"🧠 Agent resolves 'it' → {resolved}")
    context.add_conversation_turn(
        user_input="Add action items section to it",
        assistant_response="Added action items section to Research Meeting - July 8th",
        tool_calls=[{"tool_call": "insert_section", "arguments": {"note": "Research Meeting - July 8th", "heading": "Action Items"}}],
        resolved_notes=["Research Meeting - July 8th.md"]
    )
    print("🤖 Agent: Added action items section (knew which note without asking!)")
    print()
    
    # Turn 3 - complex reference
    print("👤 User: 'Open the note I just created in Obsidian'")
    resolved = context.resolve_reference("the note I just created")
    print(f"🧠 Agent resolves 'the note I just created' → {resolved}")
    print("🤖 Agent: Opening Research Meeting - July 8th in Obsidian")
    print()
    
    print("✨ The agent maintains conversation context across turns!")
    print()

def demo_enhanced_search():
    """Demonstrate enhanced file search capabilities."""
    print("🔍 Enhanced Search & Discovery Demo")
    print("=" * 60)
    
    from agent_config import get_agent_config
    
    config = get_agent_config()
    if not config.is_vault_configured():
        print("❌ Agent not configured. Skipping search demo.")
        return
    
    from agent_tools import AgentTools
    
    tools = AgentTools()
    
    print("📚 Scenario: User tries various ways to find the Stanford SOP")
    print()
    
    # First, show what's actually in the vault
    print("📁 What's actually in the vault:")
    result = tools._tool_list_notes(query="stanford")
    if result.success:
        notes = result.data.get('notes', [])
        for note in notes[:3]:
            print(f"   • {note}")
    print()
    
    search_attempts = [
        ("stanford sop", "Exact match"),
        ("symbolic systems", "Partial content match"),
        ("stanfrd sop", "Typo in 'stanford'"),
        ("standford symbolic", "Typo + partial"),
        ("sop stanford", "Word order reversed"),
        ("my stanford application", "Natural language description")
    ]
    
    print("🎯 Search attempts:")
    for query, description in search_attempts:
        result = tools._tool_list_notes(query=query)
        if result.success:
            notes = result.data.get('notes', [])
            found = len(notes)
            print(f"   '{query}' ({description}) → {found} match{'es' if found != 1 else ''}")
        
        # Also test memory resolution
        memory_result = tools.memory.resolve_note_reference(query)
        if memory_result:
            print(f"      💾 Memory: → {Path(memory_result).name}")
    
    print()
    print("✨ The agent can find files even with typos and different word orders!")
    print()

def demo_architecture_summary():
    """Show summary of the enhanced architecture."""
    print("🏗️ Enhanced Agent Architecture Summary")
    print("=" * 60)
    
    print("""
🧠 **Memory System**
   • Persistent note reference learning
   • Typo-resistant fuzzy matching
   • Entity and relationship tracking
   • User pattern learning

💬 **Conversation Context**
   • Multi-turn conversation tracking
   • Pronoun and reference resolution
   • Session state management
   • Working context maintenance

🔍 **Enhanced Search**
   • Semantic file discovery
   • Priority-based scoring
   • Folder path inclusion
   • Misspelling tolerance

🔄 **Multi-Turn Processing**
   • Reflection-based task planning
   • State-aware tool execution
   • Dynamic workflow adaptation
   • Intelligent task completion

🎓 **Learning System**
   • Automatic reference extraction
   • Interaction pattern learning
   • Context-aware entity recognition
   • User terminology adaptation

🛠️ **Tool Integration**
   • Memory-enhanced note resolution
   • Context-aware tool selection
   • Learning from successful operations
   • Intelligent fallback handling
   """)
    
    print("✨ Result: A truly conversational AI that learns and remembers!")

def main():
    """Run the complete demonstration."""
    print("🚀 Glyph Enhanced Agent Architecture Demo")
    print("=" * 70)
    print()
    
    # Run all demonstrations
    demo_memory_learning()
    print()
    demo_conversation_context()
    print()
    demo_enhanced_search()
    print()
    demo_architecture_summary()
    
    print("\n" + "=" * 70)
    print("🎉 Demo Complete!")
    print("=" * 70)
    print("""
The enhanced agent now provides:

✅ **Memory**: Remembers how you refer to notes
✅ **Context**: Understands pronouns and references  
✅ **Learning**: Gets better with each interaction
✅ **Search**: Finds files even with typos
✅ **Multi-turn**: Handles complex workflows
✅ **Intelligence**: Works like a real assistant

Try it with: python main.py --agent-mode --text-only
""")

if __name__ == "__main__":
    main()