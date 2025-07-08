#!/usr/bin/env python3

"""
Master Test Runner for Glyph Voice-Controlled Markdown Editor
Runs all comprehensive test suites for both agent and non-agent functionality.
"""

import sys
import os
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

# Add current directory to path
sys.path.insert(0, os.getcwd())

console = Console()

def check_dependencies():
    """Check if all required dependencies are available."""
    console.print("🔍 Checking Dependencies...")
    
    required_modules = [
        'numpy', 'scipy', 'sounddevice', 'whisper', 'openai', 
        'rich', 'pathlib', 'tempfile', 'unittest.mock'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        console.print(f"❌ Missing dependencies: {', '.join(missing)}")
        console.print("💡 Install with: pip install numpy scipy sounddevice openai-whisper openai rich")
        return False
    
    console.print("✅ All dependencies available")
    return True

def run_test_suite(test_file, description):
    """Run a specific test suite."""
    console.print(f"\n🧪 Running {description}")
    console.print("=" * 60)
    
    try:
        # Import and run the test
        if test_file == "test_agent_comprehensive.py":
            from test_agent_comprehensive import TestAgentMode
            tester = TestAgentMode()
            result = tester.run_all_tests()
        elif test_file == "test_nonagent_comprehensive.py":
            from test_nonagent_comprehensive import TestNonAgentMode
            tester = TestNonAgentMode()
            result = tester.run_all_tests()
        else:
            console.print(f"❌ Unknown test file: {test_file}")
            return False
        
        return result
        
    except Exception as e:
        console.print(f"❌ Failed to run {description}: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_existing_tests():
    """Run existing test files."""
    console.print("\n🔄 Running Existing Test Files")
    console.print("=" * 60)
    
    existing_tests = [
        ("test_enhanced_agent.py", "Enhanced Agent Architecture Tests"),
        ("test_agent_directly.py", "Direct Agent Tests"),
        ("test_agent_commands.py", "Agent Commands Tests"),
    ]
    
    results = {}
    
    for test_file, description in existing_tests:
        test_path = Path(test_file)
        if test_path.exists():
            console.print(f"\n🎯 Running {description}...")
            
            try:
                # Run the test file as a subprocess to avoid import conflicts
                import subprocess
                result = subprocess.run([
                    sys.executable, test_file
                ], capture_output=True, text=True, cwd=os.getcwd())
                
                if result.returncode == 0:
                    console.print(f"✅ {description} passed")
                    results[description] = True
                else:
                    console.print(f"❌ {description} failed")
                    if result.stdout:
                        console.print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                    if result.stderr:
                        console.print("STDERR:", result.stderr[-500:])  # Last 500 chars
                    results[description] = False
                    
            except Exception as e:
                console.print(f"❌ Failed to run {description}: {e}")
                results[description] = False
        else:
            console.print(f"⚠️ {test_file} not found, skipping {description}")
            results[description] = None
    
    return results

def generate_test_report(results):
    """Generate a comprehensive test report."""
    console.print("\n" + "=" * 80)
    console.print("📊 COMPREHENSIVE TEST REPORT")
    console.print("=" * 80)
    
    # Create results table
    table = Table(show_header=True, box=box.HEAVY)
    table.add_column("Test Suite", style="bold white", width=40)
    table.add_column("Status", style="bold", width=15)
    table.add_column("Description", width=30)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results.items():
        if result is True:
            status = "[green]✅ PASS[/green]"
            passed += 1
        elif result is False:
            status = "[red]❌ FAIL[/red]"
            failed += 1
        else:
            status = "[yellow]⚠️ SKIP[/yellow]"
            skipped += 1
        
        table.add_row(test_name, status, "")
    
    console.print(table)
    
    # Summary statistics
    total = passed + failed + skipped
    console.print(f"\n📈 Summary Statistics:")
    console.print(f"   Total Tests: {total}")
    console.print(f"   Passed: {passed} ({passed/total*100:.1f}%)" if total > 0 else "   Passed: 0")
    console.print(f"   Failed: {failed} ({failed/total*100:.1f}%)" if total > 0 else "   Failed: 0")
    console.print(f"   Skipped: {skipped} ({skipped/total*100:.1f}%)" if total > 0 else "   Skipped: 0")
    
    # Overall result
    if failed == 0 and passed > 0:
        console.print("\n🎉 [bold green]ALL TESTS PASSED![/bold green]")
        console.print("✨ Glyph is ready for production use!")
    elif failed > 0:
        console.print(f"\n⚠️ [bold yellow]{failed} TEST(S) FAILED[/bold yellow]")
        console.print("🔧 Please review the failed tests and fix any issues.")
    else:
        console.print("\n❓ [bold blue]NO TESTS RUN[/bold blue]")
        console.print("🚀 Please ensure test files are available and dependencies are installed.")
    
    return passed, failed, skipped

def main():
    """Main test runner function."""
    start_time = time.time()
    
    # Show banner
    banner = Panel(
        "[bold cyan]🧪 GLYPH COMPREHENSIVE TEST SUITE 🧪[/bold cyan]\n\n"
        "[white]Testing all functionality of the Glyph Voice-Controlled Markdown Editor[/white]\n"
        "[dim]Including agent mode, non-agent mode, and all subsystems[/dim]",
        style="cyan",
        box=box.DOUBLE
    )
    console.print(banner)
    
    # Check dependencies
    if not check_dependencies():
        console.print("❌ Cannot run tests without required dependencies")
        return 1
    
    # Test results collection
    all_results = {}
    
    # Run comprehensive test suites
    comprehensive_tests = [
        ("test_agent_comprehensive.py", "Agent Mode Comprehensive Tests"),
        ("test_nonagent_comprehensive.py", "Non-Agent Mode Comprehensive Tests"),
    ]
    
    console.print(f"\n🚀 Running {len(comprehensive_tests)} comprehensive test suites...")
    
    for test_file, description in comprehensive_tests:
        test_path = Path(test_file)
        if test_path.exists():
            result = run_test_suite(test_file, description)
            all_results[description] = result
        else:
            console.print(f"⚠️ {test_file} not found, skipping {description}")
            all_results[description] = None
    
    # Run existing test files
    existing_results = run_existing_tests()
    all_results.update(existing_results)
    
    # Generate report
    passed, failed, skipped = generate_test_report(all_results)
    
    # Execution time
    duration = time.time() - start_time
    console.print(f"\n⏱️ Total execution time: {duration:.2f} seconds")
    
    # Return appropriate exit code
    return 0 if failed == 0 and passed > 0 else 1

if __name__ == "__main__":
    exit(main())