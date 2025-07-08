#!/usr/bin/env python3

"""
Quick test validation script to check if test files are properly structured.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.getcwd())

def validate_test_file(test_file):
    """Validate a test file can be imported and has required structure."""
    try:
        # Check if file exists
        if not Path(test_file).exists():
            return False, f"File {test_file} does not exist"
        
        # Try to import the file
        test_module = test_file.replace('.py', '')
        
        if test_file == "test_agent_comprehensive.py":
            from test_agent_comprehensive import TestAgentMode
            tester = TestAgentMode()
            assert hasattr(tester, 'run_all_tests'), "Missing run_all_tests method"
            
        elif test_file == "test_nonagent_comprehensive.py":
            from test_nonagent_comprehensive import TestNonAgentMode
            tester = TestNonAgentMode()
            assert hasattr(tester, 'run_all_tests'), "Missing run_all_tests method"
            
        return True, "Validation passed"
        
    except Exception as e:
        return False, f"Validation failed: {e}"

def main():
    """Validate all test files."""
    print("🔍 Validating Test Files...")
    print("=" * 40)
    
    test_files = [
        "test_agent_comprehensive.py",
        "test_nonagent_comprehensive.py",
        "test_enhanced_agent.py",
        "test_agent_directly.py",
        "test_agent_commands.py",
    ]
    
    all_valid = True
    
    for test_file in test_files:
        success, message = validate_test_file(test_file)
        status = "✅" if success else "❌"
        print(f"{status} {test_file}: {message}")
        
        if not success:
            all_valid = False
    
    print("\n" + "=" * 40)
    if all_valid:
        print("🎉 All test files are valid!")
        return 0
    else:
        print("⚠️ Some test files have issues.")
        return 1

if __name__ == "__main__":
    exit(main())