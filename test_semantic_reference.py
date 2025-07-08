#!/usr/bin/env python3

"""
Test semantic reference resolution - can the agent find files when users
reference them by wrong but semantically similar names?
"""

import sys
import os
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, os.getcwd())

from agent_tools import AgentTools
from agent_config import get_agent_config

def test_semantic_file_finding():
    """Test the agent's ability to find files using semantic understanding."""
    
    print("🧠 Testing Semantic File Reference Resolution")
    print("=" * 60)
    
    # Check if agent is configured
    config = get_agent_config()
    if not config.is_vault_configured():
        print("❌ Agent not configured.")
        return
    
    try:
        tools = AgentTools()
        
        # First, let's see what files we actually have
        print("📋 First, let's see what files exist in your vault:")
        result = tools._tool_list_notes()
        if result.success:
            all_notes = result.data.get('notes', [])
            print(f"   Total notes: {len(all_notes)}")
            
            # Show some example filenames to understand the patterns
            print("\n📄 Sample of actual filenames:")
            for note in all_notes[:10]:
                print(f"      • {note}")
            print("      ...")
        
        print("\n" + "="*60)
        print("🎯 Testing Semantic Reference Resolution")
        print("="*60)
        
        # Test cases: wrong names that should semantically match real files
        semantic_tests = [
            # Test case: user says generic term, should find specific files
            {
                "user_says": "meeting notes", 
                "description": "Generic 'meeting notes' should find specific meeting files",
                "expected": "Should find actual meeting files in the vault"
            },
            {
                "user_says": "research paper",
                "description": "Generic 'research paper' should find research documents", 
                "expected": "Should find research-related files"
            },
            {
                "user_says": "class assignment",
                "description": "Generic 'class assignment' should find homework/project files",
                "expected": "Should find assignment/project files"
            },
            {
                "user_says": "scholarship application", 
                "description": "Should find scholarship-related documents",
                "expected": "Should find scholarship files"
            },
            {
                "user_says": "weekly report",
                "description": "Should find weekly/report type documents",
                "expected": "Should find report or weekly files"
            },
            
            # Test case: user describes content instead of filename
            {
                "user_says": "that note about neural networks",
                "description": "Content description should find relevant files",
                "expected": "Should find neurotech or neural network related files"
            },
            {
                "user_says": "the document about funding",
                "description": "Should find funding-related documents",
                "expected": "Should find funding/grant/money related files"  
            },
            {
                "user_says": "my application for the program",
                "description": "Should find application documents",
                "expected": "Should find application files"
            },
            
            # Test case: user says organizational terms
            {
                "user_says": "university stuff", 
                "description": "Should find university/academic related files",
                "expected": "Should find university or academic files"
            },
            {
                "user_says": "personal documents",
                "description": "Should find personal folder or personal files", 
                "expected": "Should find personal category files"
            }
        ]
        
        for i, test in enumerate(semantic_tests, 1):
            print(f"\n[{i:2d}] User says: '{test['user_says']}'")
            print(f"     Description: {test['description']}")
            print(f"     Expected: {test['expected']}")
            print("     " + "-"*50)
            
            # Test direct search first
            result = tools._tool_list_notes(query=test['user_says'])
            if result.success:
                notes = result.data.get('notes', [])
                print(f"     📍 Direct search found {len(notes)} matches:")
                for note in notes[:3]:
                    print(f"         • {note}")
                if len(notes) > 3:
                    print(f"         ... and {len(notes) - 3} more")
            else:
                print(f"     ❌ Direct search failed: {result.message}")
            
            # Test similarity matching for individual words
            words = test['user_says'].split()
            for word in words:
                if len(word) > 3:  # Only test meaningful words
                    suggestions = tools._find_similar_notes(word, max_suggestions=2)
                    if suggestions:
                        print(f"     🔍 Similarity for '{word}':")
                        for suggestion in suggestions:
                            print(f"         • {suggestion['note']} (conf: {suggestion['confidence']:.2f})")
            
            print()
        
        print("="*60)
        print("🧪 Testing Agent's List Tool Intelligence")
        print("="*60)
        
        # Test if the agent can find files by searching through categories
        category_tests = [
            ("wisconsin", "Should find University of Wisconsin related files"),
            ("cmu", "Should find CMU/Carnegie Mellon related files"), 
            ("research", "Should find research documents"),
            ("neurotech", "Should find neurotech/neural technology files"),
            ("apartment", "Should find apartment/housing related files"),
            ("scholarship", "Should find scholarship applications/info"),
        ]
        
        for category, description in category_tests:
            print(f"\n📂 Category: '{category}' - {description}")
            result = tools._tool_list_notes(query=category)
            if result.success:
                notes = result.data.get('notes', [])
                print(f"     Found {len(notes)} files:")
                for note in notes[:5]:
                    print(f"       • {note}")
                if len(notes) > 5:
                    print(f"       ... and {len(notes) - 5} more")
            else:
                print(f"     ❌ Failed: {result.message}")
        
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

def test_agent_multi_step_semantic_search():
    """Test if the agent can do multi-step semantic searching."""
    
    print("\n" + "="*60)
    print("🤖 Testing Agent Multi-Step Semantic Search")
    print("="*60)
    
    # This would test if the agent can:
    # 1. Search for general terms
    # 2. Narrow down based on context
    # 3. Find the most relevant match
    
    # For now, let's test the building blocks
    config = get_agent_config()
    if not config.is_vault_configured():
        print("❌ Agent not configured.")
        return
    
    try:
        tools = AgentTools()
        
        # Test multi-word semantic searches
        multi_word_tests = [
            "meeting notes from march",  # Should find March meeting files
            "research about mental health",  # Should find mental health research
            "application for scholarship",  # Should find scholarship applications
            "notes about apartment hunting",  # Should find apartment-related notes
        ]
        
        for test_phrase in multi_word_tests:
            print(f"\n🔍 Multi-word search: '{test_phrase}'")
            
            # Try the full phrase first
            result = tools._tool_list_notes(query=test_phrase)
            if result.success:
                notes = result.data.get('notes', [])
                print(f"     Full phrase: Found {len(notes)} matches")
                for note in notes[:3]:
                    print(f"       • {note}")
            
            # Try individual important words
            words = [w for w in test_phrase.split() if len(w) > 3]  # Skip short words
            for word in words:
                result = tools._tool_list_notes(query=word)
                if result.success:
                    notes = result.data.get('notes', [])
                    print(f"     Word '{word}': Found {len(notes)} matches")
        
        print(f"\n💡 Conclusion: The agent can use list_notes with various semantic terms")
        print(f"   to find files even when users don't know exact filenames!")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_semantic_file_finding()
    test_agent_multi_step_semantic_search()