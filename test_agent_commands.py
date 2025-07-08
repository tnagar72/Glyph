#!/usr/bin/env python3

"""
Test script for agent text-only mode with various spelling and naming scenarios.
This script helps test the agent's file finding and similarity matching capabilities.
"""

import tempfile
from pathlib import Path
import subprocess
import sys

def create_test_vault():
    """Create a test vault with various note types."""
    vault_dir = Path(tempfile.mkdtemp())
    print(f"📁 Creating test vault: {vault_dir}")
    
    # Create folder structure
    folders = [
        "Daily Notes",
        "Projects", 
        "Work",
        "Personal",
        "Archive"
    ]
    
    for folder in folders:
        (vault_dir / folder).mkdir(exist_ok=True)
    
    # Create test notes with various naming patterns
    test_notes = {
        # Daily Notes
        "Daily Notes/2024-07-08.md": "# Daily Standup - July 8th\n\n## Action Items\n- Review PR #123\n- Update documentation\n\n## Notes\nDiscussed new feature roadmap.",
        "Daily Notes/2024-07-07.md": "# Weekend Planning\n\n## Goals\n- Work on side project\n- Clean up workspace",
        
        # Project Notes
        "Projects/Website Redesign.md": "# Website Redesign Project\n\n## Goals\n- Improve user experience\n- Mobile responsiveness\n\n## Tasks\n- [ ] Create wireframes\n- [ ] Choose color scheme",
        "Projects/Mobile App Development.md": "# Mobile App Development\n\n## Features\n- User authentication\n- Data synchronization\n\n## Progress\nCompleted login flow.",
        "Projects/API Integration.md": "# API Integration Project\n\n## Endpoints\n- User management\n- Data retrieval\n\n## Status\nIn progress.",
        
        # Work Notes
        "Work/Weekly Review.md": "# Weekly Review\n\n## Achievements\n- Completed 3 features\n- Fixed 5 bugs\n\n## Next Week\n- Start new project",
        "Work/Meeting Notes.md": "# Team Meeting Notes\n\n## Agenda\n1. Project updates\n2. Resource allocation\n\n## Action Items\n- Schedule follow-up",
        "Work/Sprint Planning.md": "# Sprint Planning Session\n\n## Stories\n- User story A\n- User story B\n\n## Estimates\nTotal: 21 points",
        
        # Personal Notes
        "Personal/Shopping List.md": "# Shopping List\n\n## Groceries\n- Milk\n- Bread\n- Eggs\n\n## Other\n- Batteries",
        "Personal/Book Notes.md": "# Book Reading Notes\n\n## Currently Reading\n- The Pragmatic Programmer\n\n## Key Insights\nDRY principle importance.",
        "Personal/Travel Plans.md": "# Travel Plans\n\n## Destinations\n- Japan (Spring)\n- Europe (Summer)\n\n## Budget\n$5000 total",
        
        # Root level notes
        "Action Items.md": "# Action Items\n\n## High Priority\n- Complete project proposal\n- Review code changes\n\n## Medium Priority\n- Update documentation",
        "Ideas.md": "# Ideas and Brainstorming\n\n## App Ideas\n- Note-taking app\n- Habit tracker\n\n## Business Ideas\n- Consulting service",
        "Quick Notes.md": "# Quick Notes\n\n## Random Thoughts\n- Need to organize workspace\n- Consider learning new framework\n\n## Links\n- Interesting article about AI",
    }
    
    # Write all test notes
    for note_path, content in test_notes.items():
        note_file = vault_dir / note_path
        note_file.parent.mkdir(parents=True, exist_ok=True)
        note_file.write_text(content, encoding='utf-8')
    
    print(f"✅ Created {len(test_notes)} test notes")
    return vault_dir

def print_test_commands():
    """Print comprehensive test commands with various spelling and naming scenarios."""
    
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE AGENT TEST COMMANDS")
    print("="*80)
    print("\nTo test the agent, run:")
    print("python main.py --agent-mode --text-only")
    print("\nThen try these commands (copy/paste them one at a time):\n")
    
    test_scenarios = [
        ("📝 EXACT MATCHES", [
            "Create a note about today's meeting",
            "Open the Action Items note",
            "List notes in the Projects folder",
            "Open Daily Notes/2024-07-08.md",
        ]),
        
        ("🔤 SPELLING MISTAKES", [
            "Open Acton Items",  # Missing 'i' in Action
            "Find Weeky Review",  # Missing 'l' in Weekly  
            "Open Shooping List",  # Extra 'o' in Shopping
            "Show me the Mobil App note",  # Missing 'e' in Mobile
            "Open API Intgeration",  # Missing 'e' in Integration
            "Find Travl Plans",  # Missing 'e' in Travel
        ]),
        
        ("🔀 WORD REARRANGEMENTS", [
            "Open Items Action",  # Reversed: Action Items
            "Find Review Weekly",  # Reversed: Weekly Review
            "Open List Shopping",  # Reversed: Shopping List
            "Show App Mobile Development",  # Rearranged: Mobile App Development
            "Find Notes Meeting",  # Reversed: Meeting Notes
            "Open Planning Sprint",  # Reversed: Sprint Planning
        ]),
        
        ("🔍 PARTIAL MATCHES", [
            "Open daily note",  # Should find Daily Notes
            "Find meeting",  # Should find Meeting Notes
            "Show project notes",  # Should list projects
            "Open website",  # Should find Website Redesign
            "Find shopping",  # Should find Shopping List
            "Show book",  # Should find Book Notes
        ]),
        
        ("📁 FOLDER REFERENCES", [
            "List notes in Projects",
            "Show me Work notes", 
            "Open something in Personal folder",
            "Find notes in Daily Notes",
            "List all Personal notes",
        ]),
        
        ("💬 CONVERSATIONAL REFERENCES", [
            "Create a note called Today's Standup",
            "Add action items section to it",  # Should reference the just-created note
            "Open that note in Obsidian",  # Should reference the current focus
            "Create another note about weekend plans",
            "Link it to the standup note",  # Should link the two notes
        ]),
        
        ("🎯 COMPLEX SCENARIOS", [
            "Find notes that mention API",
            "Open the note about app development", 
            "Create a note called Team Retrospective in Work folder",
            "Add sections for What Went Well and Action Items to it",
            "Open the most recent daily note",
        ]),
        
        ("❌ AMBIGUOUS CASES", [
            "Open note",  # Should ask for clarification
            "Find project",  # Should list multiple matches
            "Show planning",  # Multiple planning notes exist
            "Open development",  # Could match multiple notes
        ]),
        
        ("🔧 ERROR HANDLING", [
            "Open nonexistent note",  # Should handle gracefully
            "Find xyz123",  # Should find no matches
            "Create a note with / invalid / name",  # Should handle invalid characters
            "Delete all notes",  # Should ask for confirmation
        ])
    ]
    
    for category, commands in test_scenarios:
        print(f"\n{category}")
        print("-" * len(category))
        for i, command in enumerate(commands, 1):
            print(f"{i:2d}. {command}")
        print()
    
    print("="*80)
    print("💡 TESTING TIPS:")
    print("- Watch how the agent resolves ambiguous names")
    print("- Notice the confidence scores in similarity matching")
    print("- Test the conversational context ('it', 'that note')")
    print("- Verify that Obsidian actually opens the correct notes")
    print("- Check that file creation works in the specified folders")
    print("="*80)

def main():
    """Main test setup function."""
    print("🧪 Agent Test Setup")
    print("===================")
    
    # Create test vault
    vault_dir = create_test_vault()
    
    print(f"\n📋 Test vault created at: {vault_dir}")
    print(f"📁 Contains folders: Daily Notes, Projects, Work, Personal, Archive")
    print(f"📄 Contains 14 test notes with various naming patterns")
    
    print(f"\n⚙️ To configure the agent with this test vault:")
    print(f"1. Run: python main.py --setup-agent") 
    print(f"2. Enter vault path: {vault_dir}")
    print(f"3. Configure other settings as desired")
    
    # Print test commands
    print_test_commands()
    
    return vault_dir

if __name__ == "__main__":
    main()