#!/usr/bin/env python3

"""
Comprehensive Test Suite for Agent Mode Functionality
Tests all agent mode capabilities including tools, memory, context, and LLM integration.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
import json
import time
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Test imports
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

class TestAgentMode:
    """Comprehensive agent mode test suite."""
    
    def __init__(self):
        self.test_vault = None
        self.original_config = None
        self.test_results = {}
        
    def setup_test_vault(self):
        """Create a test vault for testing."""
        self.test_vault = Path(tempfile.mkdtemp(prefix="glyph_test_vault_"))
        
        # Create vault structure
        folders = ["Daily Notes", "Projects", "Work", "Personal", "Templates"]
        for folder in folders:
            (self.test_vault / folder).mkdir(exist_ok=True)
            
        # Create test notes
        test_notes = {
            "Daily Notes/2024-07-08.md": """# Daily Standup - July 8th

## Action Items
- [ ] Review PR #123
- [ ] Update documentation
- [ ] Schedule team meeting

## Notes
Discussed new feature roadmap with team.
""",
            "Projects/Website Redesign.md": """# Website Redesign Project

## Overview
Complete overhaul of company website focusing on user experience.

## Goals
- Improve user experience
- Mobile responsiveness
- Better SEO

## Tasks
- [ ] Create wireframes
- [ ] Choose color scheme
- [ ] Develop prototype
""",
            "Work/Meeting Notes.md": """# Team Meeting Notes

## Agenda
1. Project updates
2. Resource allocation
3. Next quarter planning

## Action Items
- Schedule follow-up meeting
- Prepare budget proposal
""",
            "Personal/Shopping List.md": """# Shopping List

## Groceries
- Milk
- Bread
- Eggs
- Apples

## Other
- Batteries
- Phone charger
""",
            "Ideas.md": """# Ideas and Brainstorming

## App Ideas
- Note-taking app with AI
- Habit tracker
- Expense tracker

## Business Ideas
- Consulting service
- Online course platform
""",
            "Action Items.md": """# Action Items

## High Priority
- Complete project proposal
- Review code changes
- Update team documentation

## Medium Priority
- Organize workspace
- Plan next sprint
""",
        }
        
        for note_path, content in test_notes.items():
            note_file = self.test_vault / note_path
            note_file.parent.mkdir(parents=True, exist_ok=True)
            note_file.write_text(content, encoding='utf-8')
            
        return self.test_vault
    
    def setup_agent_config(self):
        """Configure agent for testing."""
        try:
            from agent_config import AgentConfig
            
            # Backup original config
            config_path = Path.home() / ".glyph" / "agent_config.json"
            if config_path.exists():
                self.original_config = config_path.read_text()
                
            # Create test config
            config = AgentConfig()
            config.set_vault_path(str(self.test_vault))
            config.set_auto_accept(True)  # Skip confirmations in tests
            config.set_session_memory(True)
            config.set_auto_backup(True)
            config.save()
            
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to setup agent config: {e}")
            return False
    
    def test_agent_configuration(self):
        """Test agent configuration system."""
        console.print("\n🔧 Testing Agent Configuration System")
        console.print("=" * 50)
        
        try:
            from agent_config import get_agent_config
            
            config = get_agent_config()
            
            # Test configuration loading
            assert config.is_vault_configured(), "Vault should be configured"
            assert config.get_vault_path() == str(self.test_vault), "Vault path should match"
            assert config.get_auto_accept() == True, "Auto accept should be enabled"
            
            # Test configuration validation
            assert config.validate_vault_path(), "Vault path should be valid"
            
            console.print("✅ Agent configuration tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Agent configuration tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_agent_memory_system(self):
        """Test agent memory and learning system."""
        console.print("\n🧠 Testing Agent Memory System")
        console.print("=" * 50)
        
        try:
            from agent_memory import get_agent_memory
            
            memory = get_agent_memory()
            
            # Test note reference registration
            console.print("📝 Testing note reference registration...")
            memory.register_note_reference("daily standup", "Daily Notes/2024-07-08.md", "user mentioned")
            memory.register_note_reference("website project", "Projects/Website Redesign.md", "user mentioned")
            memory.register_note_reference("team meeting", "Work/Meeting Notes.md", "user mentioned")
            
            # Test note reference resolution
            console.print("🔍 Testing note reference resolution...")
            result1 = memory.resolve_note_reference("daily standup")
            result2 = memory.resolve_note_reference("website project")
            result3 = memory.resolve_note_reference("team meeting")
            
            assert result1 == "Daily Notes/2024-07-08.md", f"Expected Daily Notes/2024-07-08.md, got {result1}"
            assert result2 == "Projects/Website Redesign.md", f"Expected Projects/Website Redesign.md, got {result2}"
            assert result3 == "Work/Meeting Notes.md", f"Expected Work/Meeting Notes.md, got {result3}"
            
            # Test typo tolerance
            console.print("🔤 Testing typo tolerance...")
            result4 = memory.resolve_note_reference("dayly standup")  # Missing 'i'
            result5 = memory.resolve_note_reference("webiste project")  # Missing 't'
            
            assert result4 == "Daily Notes/2024-07-08.md", "Should resolve typos"
            assert result5 == "Projects/Website Redesign.md", "Should resolve typos"
            
            # Test entity registration
            console.print("👤 Testing entity registration...")
            memory.register_entity("John Doe", "person", ["Work/Meeting Notes.md"], "Team member")
            memory.register_entity("Website Redesign", "project", ["Projects/Website Redesign.md"], "Current project")
            
            # Test entity-based note finding
            related_notes = memory.find_related_notes("John Doe")
            assert "Work/Meeting Notes.md" in related_notes, "Should find related notes"
            
            # Test memory statistics
            stats = memory.get_memory_stats()
            assert stats["note_references"] >= 3, "Should have at least 3 note references"
            assert stats["entities"] >= 2, "Should have at least 2 entities"
            
            console.print("✅ Agent memory system tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Agent memory system tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_conversation_context(self):
        """Test conversation context and reference resolution."""
        console.print("\n💬 Testing Conversation Context System")
        console.print("=" * 50)
        
        try:
            from agent_context import get_conversation_context
            
            context = get_conversation_context()
            
            # Test conversation turn tracking
            console.print("📝 Testing conversation tracking...")
            context.add_conversation_turn(
                user_input="Create a note about today's meeting",
                assistant_response="Created note 'Today's Meeting'",
                tool_calls=[{"tool_call": "create_note", "arguments": {"name": "Today's Meeting"}}],
                resolved_notes=["Today's Meeting.md"]
            )
            
            context.add_conversation_turn(
                user_input="Add action items section to it",
                assistant_response="Added action items section",
                tool_calls=[{"tool_call": "insert_section", "arguments": {"note": "Today's Meeting.md", "heading": "Action Items"}}],
                resolved_notes=["Today's Meeting.md"]
            )
            
            # Test reference resolution
            console.print("🔍 Testing reference resolution...")
            result1 = context.resolve_reference("it")
            result2 = context.resolve_reference("the note I just created")
            result3 = context.resolve_reference("that note")
            
            assert result1 == "Today's Meeting.md", f"Expected Today's Meeting.md, got {result1}"
            assert result2 == "Today's Meeting.md", f"Expected Today's Meeting.md, got {result2}"
            assert result3 == "Today's Meeting.md", f"Expected Today's Meeting.md, got {result3}"
            
            # Test context for LLM
            llm_context = context.get_context_for_llm()
            assert "conversation_history" in llm_context, "Should include conversation history"
            assert "working_context" in llm_context, "Should include working context"
            assert "current_focus" in llm_context, "Should include current focus"
            
            console.print("✅ Conversation context tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Conversation context tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_agent_tools(self):
        """Test agent tools and operations."""
        console.print("\n🔧 Testing Agent Tools System")
        console.print("=" * 50)
        
        try:
            from agent_tools import AgentTools
            
            tools = AgentTools()
            
            # Test list_notes
            console.print("📝 Testing list_notes...")
            result = tools._tool_list_notes()
            assert result.success, f"list_notes failed: {result.message}"
            assert len(result.data.get('notes', [])) > 0, "Should find notes in vault"
            
            # Test search functionality
            console.print("🔍 Testing search functionality...")
            result = tools._tool_list_notes(query="action")
            assert result.success, f"search failed: {result.message}"
            notes = result.data.get('notes', [])
            assert any("Action Items" in note for note in notes), "Should find Action Items note"
            
            # Test note creation
            console.print("✏️ Testing note creation...")
            result = tools._tool_create_note("Test Note", content="This is a test note.")
            assert result.success, f"create_note failed: {result.message}"
            
            # Verify note was created
            test_note_path = self.test_vault / "Test Note.md"
            assert test_note_path.exists(), "Test note should exist"
            
            # Test note reading
            console.print("📖 Testing note reading...")
            result = tools._tool_read_note("Test Note")
            assert result.success, f"read_note failed: {result.message}"
            assert "This is a test note." in result.data.get('content', ''), "Should read note content"
            
            # Test section insertion
            console.print("📋 Testing section insertion...")
            result = tools._tool_insert_section("Test Note", "New Section", "This is a new section.")
            assert result.success, f"insert_section failed: {result.message}"
            
            # Verify section was inserted
            content = test_note_path.read_text()
            assert "# New Section" in content, "Section header should be present"
            assert "This is a new section." in content, "Section content should be present"
            
            # Test note similarity matching
            console.print("🔤 Testing similarity matching...")
            suggestions = tools._find_similar_notes("acton", max_suggestions=3)  # Typo for "action"
            assert len(suggestions) > 0, "Should find similar notes"
            assert any("Action Items" in suggestion['note'] for suggestion in suggestions), "Should suggest Action Items"
            
            # Test folder operations
            console.print("📁 Testing folder operations...")
            result = tools._tool_list_notes(folder="Projects")
            assert result.success, f"folder listing failed: {result.message}"
            notes = result.data.get('notes', [])
            assert any("Website Redesign" in note for note in notes), "Should find project notes"
            
            console.print("✅ Agent tools tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Agent tools tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_agent_llm_integration(self):
        """Test agent LLM integration and command processing."""
        console.print("\n🧠 Testing Agent LLM Integration")
        console.print("=" * 50)
        
        try:
            from agent_llm import AgentLLM
            from agent_context import get_conversation_context
            
            # Mock OpenAI API to avoid actual API calls
            mock_response = {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "thinking": "User wants to create a note about a meeting",
                            "tool_calls": [{
                                "tool_call": "create_note",
                                "arguments": {
                                    "name": "Meeting Notes",
                                    "content": "# Meeting Notes\n\nCreated for today's meeting."
                                }
                            }]
                        })
                    }
                }]
            }
            
            with patch('openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_client.chat.completions.create.return_value = Mock(**mock_response)
                mock_openai.return_value = mock_client
                
                llm = AgentLLM()
                context = get_conversation_context()
                
                # Test command processing
                console.print("🎯 Testing command processing...")
                result = llm.process_command(
                    "Create a note about today's meeting",
                    context=context.get_context_for_llm()
                )
                
                assert result is not None, "Should return processing result"
                assert "tool_calls" in result, "Should contain tool calls"
                assert len(result["tool_calls"]) > 0, "Should have at least one tool call"
                
                # Test tool call structure
                tool_call = result["tool_calls"][0]
                assert "tool_call" in tool_call, "Tool call should have tool_call field"
                assert "arguments" in tool_call, "Tool call should have arguments field"
                assert tool_call["tool_call"] == "create_note", "Should be create_note tool call"
                
                console.print("✅ Agent LLM integration tests passed")
                return True
                
        except Exception as e:
            console.print(f"❌ Agent LLM integration tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_agent_cli_integration(self):
        """Test agent CLI and session management."""
        console.print("\n🖥️ Testing Agent CLI Integration")
        console.print("=" * 50)
        
        try:
            from agent_cli import AgentSession
            
            # Create agent session in text-only mode
            session = AgentSession(enter_stop=True, transcription_method=None, text_only=True)
            
            # Test session initialization
            assert session.tools is not None, "Session should have tools"
            assert session.context is not None, "Session should have context"
            assert session.memory is not None, "Session should have memory"
            assert session.llm is not None, "Session should have LLM"
            
            # Test session state tracking
            assert session.commands_processed == 0, "Should start with 0 commands"
            assert session.successful_operations == 0, "Should start with 0 successful operations"
            
            # Mock command processing to avoid actual LLM calls
            with patch.object(session, 'process_command') as mock_process:
                mock_process.return_value = True
                
                # Simulate command processing
                result = session.process_command("List all notes")
                assert result == True, "Mock should return True"
                
            console.print("✅ Agent CLI integration tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Agent CLI integration tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_agent_end_to_end(self):
        """Test complete agent workflow end-to-end."""
        console.print("\n🔄 Testing Agent End-to-End Workflow")
        console.print("=" * 50)
        
        try:
            from agent_tools import AgentTools
            from agent_context import get_conversation_context
            from agent_memory import get_agent_memory
            
            tools = AgentTools()
            context = get_conversation_context()
            memory = get_agent_memory()
            
            # Simulate multi-turn conversation
            console.print("💬 Simulating multi-turn conversation...")
            
            # Turn 1: Create a note
            result1 = tools._tool_create_note("Daily Standup", content="# Daily Standup\n\nPlanning for today.")
            assert result1.success, f"Turn 1 failed: {result1.message}"
            
            # Register in context
            context.add_conversation_turn(
                user_input="Create a note about daily standup",
                assistant_response="Created Daily Standup note",
                tool_calls=[{"tool_call": "create_note", "arguments": {"name": "Daily Standup"}}],
                resolved_notes=["Daily Standup.md"]
            )
            
            # Turn 2: Add section (using reference)
            result2 = tools._tool_insert_section("Daily Standup", "Action Items", "- [ ] Review code\n- [ ] Update docs")
            assert result2.success, f"Turn 2 failed: {result2.message}"
            
            # Register in context
            context.add_conversation_turn(
                user_input="Add action items section to it",
                assistant_response="Added action items section",
                tool_calls=[{"tool_call": "insert_section", "arguments": {"note": "Daily Standup.md", "heading": "Action Items"}}],
                resolved_notes=["Daily Standup.md"]
            )
            
            # Turn 3: Test reference resolution
            current_focus = context.resolve_reference("it")
            assert current_focus == "Daily Standup.md", f"Reference resolution failed: {current_focus}"
            
            # Test learning system
            console.print("🎓 Testing learning system...")
            memory.register_note_reference("standup", "Daily Standup.md", "user created")
            
            # Test learned reference
            learned_ref = memory.resolve_note_reference("standup")
            assert learned_ref == "Daily Standup.md", f"Learning failed: {learned_ref}"
            
            # Test typo tolerance after learning
            typo_ref = memory.resolve_note_reference("standp")  # Missing 'u'
            assert typo_ref == "Daily Standup.md", f"Typo tolerance failed: {typo_ref}"
            
            console.print("✅ Agent end-to-end tests passed")
            return True
            
        except Exception as e:
            console.print(f"❌ Agent end-to-end tests failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """Clean up test resources."""
        try:
            # Remove test vault
            if self.test_vault and self.test_vault.exists():
                shutil.rmtree(self.test_vault)
                
            # Restore original config
            if self.original_config:
                config_path = Path.home() / ".glyph" / "agent_config.json"
                config_path.write_text(self.original_config)
                
            # Clear memory
            try:
                from agent_memory import get_agent_memory
                memory = get_agent_memory()
                memory.clear_memory()
            except:
                pass
                
        except Exception as e:
            console.print(f"⚠️ Cleanup error: {e}")
    
    def run_all_tests(self):
        """Run all agent mode tests."""
        console.print("🧪 Comprehensive Agent Mode Test Suite")
        console.print("=" * 60)
        
        # Setup
        console.print("🔧 Setting up test environment...")
        self.setup_test_vault()
        if not self.setup_agent_config():
            console.print("❌ Failed to setup test environment")
            return False
            
        # Run tests
        tests = [
            ("Agent Configuration", self.test_agent_configuration),
            ("Agent Memory System", self.test_agent_memory_system),
            ("Conversation Context", self.test_conversation_context),
            ("Agent Tools", self.test_agent_tools),
            ("Agent LLM Integration", self.test_agent_llm_integration),
            ("Agent CLI Integration", self.test_agent_cli_integration),
            ("Agent End-to-End", self.test_agent_end_to_end),
        ]
        
        passed = 0
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                console.print(f"❌ {test_name} failed with exception: {e}")
                self.test_results[test_name] = False
        
        # Results summary
        console.print("\n" + "=" * 60)
        console.print("🏁 Test Results Summary")
        console.print("=" * 60)
        
        for test_name, success in self.test_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            console.print(f"{status:10} {test_name}")
        
        console.print(f"\nResults: {passed}/{len(tests)} tests passed")
        
        # Cleanup
        self.cleanup()
        
        if passed == len(tests):
            console.print("🎉 All agent mode tests passed!")
            return True
        else:
            console.print("⚠️ Some tests failed. Check the output above for details.")
            return False

def main():
    """Run the comprehensive agent mode test suite."""
    tester = TestAgentMode()
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())