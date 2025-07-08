#!/usr/bin/env python3

"""
Test specific agent commands to verify file finding and reference resolution.
"""

import sys
import os
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, os.getcwd())

from agent_cli import AgentSession
from agent_config import get_agent_config

def test_specific_commands():
    """Test specific commands that demonstrate file finding capabilities."""
    
    print("🎯 Testing Specific Agent Commands")
    print("=" * 60)
    
    # Check if agent is configured
    config = get_agent_config()
    if not config.is_vault_configured():
        print("❌ Agent not configured. Please run 'python main.py --setup-agent' first.")
        return
    
    print(f"✅ Agent configured with vault: {config.get_vault_path()}")
    
    # Create agent session (text-only mode)
    session = AgentSession(enter_stop=True, transcription_method=None, text_only=True)
    
    # Specific test commands to verify file finding
    test_scenarios = [
        {
            "category": "🔍 File Finding Tests",
            "commands": [
                "List notes with 'meeting' in the name",
                "Open Weekly Meeting note",  # Should find "Weekly Meeting.md"
                "Find notes about projects",
                "Open API Integration",  # From your vault
            ]
        },
        {
            "category": "🔤 Spelling Mistake Tests", 
            "commands": [
                "Open Metting Notes",  # Missing 'e' in Meeting
                "Find projet notes",   # Missing 'c' in project  
                "Open Weeky Meeting",  # Missing 'l' in Weekly
                "Show researh notes",  # Missing 'c' in research
            ]
        },
        {
            "category": "🔀 Word Rearrangement Tests",
            "commands": [
                "Open Notes Meeting",    # Reversed: Meeting Notes
                "Find Meeting Weekly",   # Reversed: Weekly Meeting
                "Show Integration API",  # Reversed: API Integration
                "Open Planning Sprint",  # If exists: Sprint Planning
            ]
        },
        {
            "category": "📁 Folder Search Tests",
            "commands": [
                "List notes in Wisconsin folder",
                "Show Research notes", 
                "Find notes in Neurotech",
                "List all CMU notes",
            ]
        },
        {
            "category": "💬 Conversational Tests",
            "commands": [
                "Create a note called Test Agent Note",
                "Add a section called Testing to it",      # Should reference the just-created note
                "Open that note in Obsidian",             # Should reference current focus
                "List the most recent notes",
            ]
        }
    ]
    
    total_commands = sum(len(scenario["commands"]) for scenario in test_scenarios)
    command_count = 0
    
    for scenario in test_scenarios:
        print(f"\n{scenario['category']}")
        print("=" * len(scenario['category']))
        
        for command in scenario["commands"]:
            command_count += 1
            print(f"\n[{command_count:2d}/{total_commands}] Testing: '{command}'")
            print("-" * 70)
            
            try:
                # Process the command directly
                success = session.process_command(command)
                
                if success:
                    print(f"✅ SUCCESS: Command processed successfully")
                else:
                    print(f"❌ FAILED: Command processing failed")
                    
            except Exception as e:
                print(f"💥 ERROR: {e}")
                # Don't print full traceback to keep output clean
            
            print("-" * 70)
    
    print(f"\n🏁 Testing Summary")
    print("=" * 30)
    print(f"📊 Session Statistics:")
    print(f"   • Commands processed: {session.commands_processed}")
    print(f"   • Successful operations: {session.successful_operations}")
    print(f"   • Tool calls made: {session.tools.tool_call_count}")
    print(f"   • Success rate: {(session.successful_operations/max(session.commands_processed,1)*100):.1f}%")

def quick_file_test():
    """Quick test of just the file search without full agent processing."""
    
    print("🔍 Quick File Search Test")
    print("=" * 40)
    
    config = get_agent_config()
    if not config.is_vault_configured():
        print("❌ Agent not configured.")
        return
    
    from agent_tools import AgentTools
    
    try:
        tools = AgentTools()
        
        # Test specific searches based on what we saw in the vault
        searches = [
            ("meeting", "Looking for meeting notes"),
            ("research", "Looking for research notes"), 
            ("project", "Looking for project notes"),
            ("wisconsin", "Looking for Wisconsin notes"),
            ("neurotech", "Looking for Neurotech notes"),
        ]
        
        for query, description in searches:
            print(f"\n📋 {description} (query: '{query}'):")
            result = tools._tool_list_notes(query=query)
            
            if result.success:
                notes = result.data.get('notes', [])
                print(f"   Found {len(notes)} matches:")
                
                # Show first few matches
                for note in notes[:3]:
                    print(f"      • {note}")
                if len(notes) > 3:
                    print(f"      ... and {len(notes) - 3} more")
            else:
                print(f"   ❌ Search failed: {result.message}")
        
        # Test similarity matching on misspelled terms
        print(f"\n🔤 Similarity Matching Test:")
        misspellings = ["meetng", "researh", "proyect", "wisconsn"]
        
        for misspelling in misspellings:
            suggestions = tools._find_similar_notes(misspelling, max_suggestions=2)
            print(f"   '{misspelling}' → {len(suggestions)} suggestions:")
            for suggestion in suggestions:
                print(f"      • {suggestion['note']} ({suggestion['confidence']:.2f})")
                
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    print("🚀 Glyph Agent Command Testing")
    print("=" * 50)
    
    # First run quick file test
    quick_file_test()
    
    print("\n" + "=" * 50)
    print("🎯 Now testing full agent command processing...")
    print("⚠️  This will actually execute operations in your vault!")
    print("=" * 50)
    
    # Run full command tests
    test_specific_commands()