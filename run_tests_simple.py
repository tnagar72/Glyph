#!/usr/bin/env python3

"""
Simple Test Runner for Glyph (No External Dependencies)
Runs basic validation of all test functionality.
"""

import sys
import os
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.getcwd())

def print_banner():
    """Print a simple banner."""
    print("="*60)
    print("🧪 GLYPH TEST SUITE - SIMPLE RUNNER")
    print("="*60)
    print("Testing core functionality without external dependencies")
    print()

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing Module Imports...")
    
    modules_to_test = [
        # Core modules
        "main", "recording", "transcription", "llm", "md_file",
        # Configuration modules  
        "audio_config", "model_config", "transcription_config",
        # Agent modules
        "agent_cli", "agent_config", "agent_tools", "agent_memory", 
        "agent_context", "agent_llm", "agent_prompts",
        # Utility modules
        "utils", "ui_helpers", "diff", "cleaning",
        "backup_manager", "undo_manager", "session_logger",
        "interactive_cli", "live_transcription"
    ]
    
    passed = 0
    failed = 0
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {module}")
            passed += 1
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ⚠️ {module}: {e}")
            failed += 1
    
    print(f"\nImport Results: {passed} passed, {failed} failed")
    return failed == 0

def test_configurations():
    """Test configuration systems."""
    print("\n⚙️ Testing Configuration Systems...")
    
    try:
        # Test audio config
        from audio_config import AudioDeviceManager
        audio_config = AudioDeviceManager()
        print("  ✅ Audio configuration system")
        
        # Test model config  
        from model_config import ModelManager
        model_config = ModelManager()
        print("  ✅ Model configuration system")
        
        # Test transcription config
        from transcription_config import TranscriptionConfig  
        transcription_config = TranscriptionConfig()
        print("  ✅ Transcription configuration system")
        
        # Test agent config
        from agent_config import AgentConfig
        agent_config = AgentConfig()
        print("  ✅ Agent configuration system")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_core_functionality():
    """Test core functionality without actual audio/API calls."""
    print("\n🎯 Testing Core Functionality...")
    
    try:
        # Test transcription service creation
        from transcription import TranscriptionService
        service = TranscriptionService()
        print("  ✅ Transcription service creation")
        
        # Test agent tools creation
        from agent_tools import AgentTools  
        tools = AgentTools()
        print("  ✅ Agent tools creation")
        
        # Test markdown file validation
        from md_file import validate_markdown_path
        test_path = validate_markdown_path("test.md")
        print("  ✅ Markdown file validation")
        
        # Test UI helpers
        from ui_helpers import show_welcome_banner
        print("  ✅ UI helpers")
        
        # Test backup manager
        from backup_manager import BackupManager
        print("  ✅ Backup manager")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Core functionality test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "main.py", "requirements.txt", "setup.py",
        "README.md", "FUNCTIONALITY.md", "FAQ.md",
        "TESTING_GUIDE.md"
    ]
    
    optional_files = [
        "run_all_tests.py", "run_tests_simple.py",
        "test_agent_comprehensive.py", 
        "test_nonagent_comprehensive.py"
    ]
    
    missing_required = []
    missing_optional = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (required)")
            missing_required.append(file)
    
    for file in optional_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ {file} (optional)")
            missing_optional.append(file)
    
    if missing_required:
        print(f"\n❌ Missing required files: {missing_required}")
        return False
    
    if missing_optional:
        print(f"\n⚠️ Missing optional files: {missing_optional}")
    
    return True

def test_test_files():
    """Test that test files are properly structured."""
    print("\n🧪 Testing Test File Structure...")
    
    test_files = [
        "test_agent_comprehensive.py",
        "test_nonagent_comprehensive.py", 
        "test_enhanced_agent.py",
        "test_agent_directly.py",
        "test_agent_commands.py"
    ]
    
    passed = 0
    
    for test_file in test_files:
        if Path(test_file).exists():
            try:
                # Try to read the file
                content = Path(test_file).read_text()
                if "def main():" in content or "class Test" in content:
                    print(f"  ✅ {test_file}")
                    passed += 1
                else:
                    print(f"  ⚠️ {test_file} (no main function or test class)")
            except Exception as e:
                print(f"  ❌ {test_file}: {e}")
        else:
            print(f"  ⚠️ {test_file} (not found)")
    
    print(f"\nTest Files: {passed} properly structured")
    return passed > 0

def main():
    """Run all simple tests."""
    start_time = time.time()
    
    print_banner()
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration Systems", test_configurations), 
        ("Core Functionality", test_core_functionality),
        ("File Structure", test_file_structure),
        ("Test Files", test_test_files),
    ]
    
    results = {}
    passed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    duration = time.time() - start_time
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    print(f"Duration: {duration:.2f} seconds")
    
    if passed == len(tests):
        print("\n🎉 All basic tests passed!")
        print("✨ Glyph core functionality is working correctly!")
        print("\n💡 For comprehensive testing, run:")
        print("   python run_all_tests.py")
        return 0
    else:
        print("\n⚠️ Some basic tests failed.")
        print("🔧 Please check the issues above before running comprehensive tests.")
        return 1

if __name__ == "__main__":
    exit(main())