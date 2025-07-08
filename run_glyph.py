#!/usr/bin/env python3

"""
Wrapper script for Glyph that ensures proper module loading.
This script ensures that all modules including ui_helpers are available.
"""

import sys
import os

# Add the current directory to Python path to ensure ui_helpers is available
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    """Entry point for the glyph command."""
    # Import and run main
    from main import main as main_func
    main_func()

if __name__ == "__main__":
    main()