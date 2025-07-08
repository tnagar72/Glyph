#!/usr/bin/env python3

"""
Direct test script for agent functionality.
Tests the agent logic without needing interactive input.
"""

import sys
import os
from pathlib import Path

# Add the current directory to path so we can import modules
sys.path.insert(0, os.getcwd())

from agent_cli import AgentSession
from agent_config import get_agent_config

def test_agent_commands():
    """Test agent commands directly without interactive input."""
    
    print("🧪 Testing Agent Commands Directly")
    print("=" * 50)
    
    # Check if agent is configured
    config = get_agent_config()
    if not config.is_vault_configured():
        print("❌ Agent not configured. Please run 'python main.py --setup-agent' first.")
        return
    
    print(f"✅ Agent configured with vault: {config.get_vault_path()}")
    print(f"📊 Vault contains notes from: {Path(config.get_vault_path()).name}")
    
    # Create agent session (text-only mode)
    session = AgentSession(enter_stop=True, transcription_method=None, text_only=True)
    
    # Test commands to try
    test_commands = [
        # Exact matches
        "List all notes",
        "Open Action Items",
        
        # Spelling mistakes
        "Open Acton Items",  # Missing 'i' in Action
        "Find weeky review",  # Missing 'l' in Weekly
        
        # Word rearrangements  
        "Open items action",  # Reversed: Action Items
        "Find review weekly",  # Reversed: Weekly Review
        
        # Partial matches
        "Open daily note",
        "Find meeting",
        "Show project notes",
        
        # Folder references
        "List notes in Projects",
        "Show Work notes",
        
        # Conversational
        "Create a note about today's standup",
        "Add action items section to it",
    ]
    
    print(f"\n🎯 Testing {len(test_commands)} commands:")
    print("-" * 30)
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n[{i:2d}/{len(test_commands)}] Testing: '{command}'")
        print("-" * 60)
        
        try:
            # Process the command directly
            success = session.process_command(command)
            
            if success:
                print(f"✅ Command processed successfully")
            else:
                print(f"❌ Command failed")
                
        except Exception as e:
            print(f"💥 Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 60)
        
        # Add a small delay to see results
        import time
        time.sleep(1)
    
    print(f"\n🏁 Testing completed!")
    print(f"📊 Session stats:")
    print(f"   Commands processed: {session.commands_processed}")
    print(f"   Successful operations: {session.successful_operations}")
    print(f"   Tool calls made: {session.tools.tool_call_count}")

def test_file_finding():
    """Test just the file finding capabilities."""
    
    print("\n🔍 Testing File Finding Capabilities")
    print("=" * 50)
    
    # Check if agent is configured
    config = get_agent_config()
    if not config.is_vault_configured():
        print("❌ Agent not configured.")
        return
    
    from agent_tools import AgentTools
    
    try:
        tools = AgentTools()
        
        # Test list_notes
        print("\n1. Testing list_notes:")
        result = tools._tool_list_notes()
        if result.success:
            notes = result.data.get('notes', [])
            print(f"   ✅ Found {len(notes)} notes")
            for note in notes[:5]:  # Show first 5
                print(f"      - {note}")
            if len(notes) > 5:
                print(f"      ... and {len(notes) - 5} more")
        else:
            print(f"   ❌ Failed: {result.message}")
        
        # Test search queries
        search_tests = [
            ("action", "Should find Action Items"),
            ("daily", "Should find daily notes"),
            ("project", "Should find project notes"),
            ("meeting", "Should find meeting notes"),
        ]
        
        print("\n2. Testing search queries:")
        for query, expected in search_tests:
            result = tools._tool_list_notes(query=query)
            if result.success:
                notes = result.data.get('notes', [])
                print(f"   Query '{query}': Found {len(notes)} notes - {expected}")
                for note in notes:
                    print(f"      - {note}")
            else:
                print(f"   Query '{query}': Failed - {result.message}")
        
        # Test similarity matching
        print("\n3. Testing similarity matching:")
        similarity_tests = [
            "acton",  # Missing 'i' in action
            "weeky",  # Missing 'l' in weekly  
            "meetng", # Missing 'i' in meeting
            "projet", # Missing 'c' in project
        ]
        
        for test_name in similarity_tests:
            suggestions = tools._find_similar_notes(test_name, max_suggestions=3)
            print(f"   '{test_name}': Found {len(suggestions)} suggestions")
            for suggestion in suggestions:
                print(f"      - {suggestion['note']} (confidence: {suggestion['confidence']:.2f}, {suggestion['reason']})")
                
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    
    print("🚀 Glyph Agent Direct Testing")
    print("=" * 50)
    
    # Test file finding first
    test_file_finding()
    
    # Ask if user wants to test full commands
    print("\n" + "=" * 50)
    response = input("🤔 Test full agent commands? This will actually execute operations. (y/N): ")
    
    if response.lower().startswith('y'):
        test_agent_commands()
    else:
        print("📋 Skipping full command testing. File finding tests completed.")