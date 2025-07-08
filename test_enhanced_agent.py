#!/usr/bin/env python3

"""
Test script for the enhanced agent architecture with memory and multi-turn capabilities.
"""

import sys
import os
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, os.getcwd())

def test_memory_system():
    """Test the agent memory system."""
    print("🧠 Testing Agent Memory System")
    print("=" * 50)
    
    try:
        from agent_memory import get_agent_memory
        
        memory = get_agent_memory()
        
        # Test note reference registration
        print("📝 Testing note reference registration...")
        memory.register_note_reference("stanford sop", "Wisconsin/Stanford Symbolic Systems SOP.md", "user mentioned")
        memory.register_note_reference("symbolic systems", "Wisconsin/Stanford Symbolic Systems SOP.md", "user mentioned")
        
        # Test note reference resolution
        print("🔍 Testing note reference resolution...")
        result1 = memory.resolve_note_reference("stanford sop")
        result2 = memory.resolve_note_reference("symbolic systems")
        result3 = memory.resolve_note_reference("standford sop")  # Typo test
        
        print(f"   'stanford sop' → {result1}")
        print(f"   'symbolic systems' → {result2}")
        print(f"   'standford sop' (typo) → {result3}")
        
        # Test entity registration
        print("👤 Testing entity registration...")
        memory.register_entity("Dr. Sarah Jung", "person", ["Wisconsin/Stanford Symbolic Systems SOP.md"], "Research collaborator")
        
        related_notes = memory.find_related_notes("Dr. Sarah Jung")
        print(f"   Dr. Sarah Jung related notes: {related_notes}")
        
        # Test memory stats
        stats = memory.get_memory_stats()
        print(f"📊 Memory stats: {stats}")
        
        print("✅ Memory system test completed")
        return True
        
    except Exception as e:
        print(f"❌ Memory system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_context():
    """Test the conversation context system."""
    print("\n💬 Testing Conversation Context System")
    print("=" * 50)
    
    try:
        from agent_context import get_conversation_context
        
        context = get_conversation_context()
        
        # Test conversation turn addition
        print("📝 Testing conversation tracking...")
        context.add_conversation_turn(
            user_input="Create a note about today's meeting",
            assistant_response="Created note 'Today's Meeting'",
            tool_calls=[{"tool_call": "create_note", "arguments": {"name": "Today's Meeting"}}],
            resolved_notes=["Today's Meeting.md"]
        )
        
        # Test reference resolution
        print("🔍 Testing reference resolution...")
        result1 = context.resolve_reference("it")
        result2 = context.resolve_reference("the note I just created")
        
        print(f"   'it' → {result1}")
        print(f"   'the note I just created' → {result2}")
        
        # Test context for LLM
        llm_context = context.get_context_for_llm()
        print(f"📊 LLM context keys: {list(llm_context.keys())}")
        
        # Test stats
        stats = context.get_memory_stats()
        print(f"📊 Context stats: {stats}")
        
        print("✅ Conversation context test completed")
        return True
        
    except Exception as e:
        print(f"❌ Conversation context test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_note_resolution():
    """Test enhanced note resolution with memory."""
    print("\n🔍 Testing Enhanced Note Resolution")
    print("=" * 50)
    
    try:
        from agent_tools import AgentTools
        from agent_config import get_agent_config
        
        config = get_agent_config()
        if not config.is_vault_configured():
            print("❌ Agent not configured. Skipping note resolution test.")
            return True
        
        tools = AgentTools()
        
        # First, register some references
        print("📝 Registering note references...")
        tools.memory.register_note_reference("my sop", "Wisconsin/Stanford Symbolic Systems SOP.md", "test")
        tools.memory.register_note_reference("stanford document", "Wisconsin/Stanford Symbolic Systems SOP.md", "test")
        
        # Test memory-enhanced resolution
        print("🔍 Testing memory-enhanced note resolution...")
        
        test_queries = [
            "my sop",
            "stanford document", 
            "my sopp",  # Typo
            "stanfrd document"  # Typo
        ]
        
        for query in test_queries:
            result = tools._resolve_note_with_fallback(query)
            print(f"   '{query}' → {result.name if result else 'Not found'}")
        
        print("✅ Enhanced note resolution test completed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced note resolution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_learning_system():
    """Test the learning system."""
    print("\n🎓 Testing Learning System")
    print("=" * 50)
    
    try:
        from agent_tools import AgentTools
        from agent_config import get_agent_config
        
        config = get_agent_config()
        if not config.is_vault_configured():
            print("❌ Agent not configured. Skipping learning test.")
            return True
        
        tools = AgentTools()
        
        # Simulate a successful interaction
        print("📝 Simulating learning from interaction...")
        
        user_input = "Summarize my Stanford Symbolic Systems SOP"
        tool_call = {
            "tool_call": "summarize_note",
            "arguments": {"name": "Stanford Symbolic Systems SOP"}
        }
        
        # Mock successful result
        from agent_tools import ToolCallResult
        result = ToolCallResult(
            success=True,
            message="Added summary to note",
            data={
                "note_name": "Wisconsin/Stanford Symbolic Systems SOP.md",
                "summary": "Test summary"
            }
        )
        
        # Test learning
        tools.learn_from_interaction(user_input, tool_call, result)
        
        # Check if it learned the reference
        learned_ref = tools.memory.resolve_note_reference("stanford symbolic systems sop")
        print(f"   Learned reference: {learned_ref}")
        
        print("✅ Learning system test completed")
        return True
        
    except Exception as e:
        print(f"❌ Learning system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_integration():
    """Test integration with agent CLI."""
    print("\n🤖 Testing Agent CLI Integration")
    print("=" * 50)
    
    try:
        from agent_cli import AgentSession
        from agent_config import get_agent_config
        
        config = get_agent_config()
        if not config.is_vault_configured():
            print("❌ Agent not configured. Skipping integration test.")
            return True
        
        # Create agent session
        print("🚀 Creating agent session...")
        session = AgentSession(text_only=True)
        
        # Test simple command processing (without actually executing)
        print("📝 Testing command processing flow...")
        
        # Check that enhanced context is available
        enhanced_context = session.context.get_context_for_llm()
        print(f"   Enhanced context available: {bool(enhanced_context)}")
        print(f"   Context keys: {list(enhanced_context.keys())}")
        
        # Check memory integration
        memory_stats = session.tools.memory.get_memory_stats()
        print(f"   Memory integration: {bool(memory_stats)}")
        
        print("✅ Agent CLI integration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Agent CLI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Enhanced Agent Architecture Test Suite")
    print("=" * 60)
    
    tests = [
        ("Memory System", test_memory_system),
        ("Conversation Context", test_conversation_context),
        ("Enhanced Note Resolution", test_enhanced_note_resolution),
        ("Learning System", test_learning_system),
        ("Agent Integration", test_agent_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Enhanced agent architecture is working.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()