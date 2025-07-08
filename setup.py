#!/usr/bin/env python3

"""
Glyph - Voice-controlled markdown editing and Obsidian vault management.

Setup script for professional package distribution.
"""

from setuptools import setup, find_packages
import os
import sys

# Ensure Python version compatibility
if sys.version_info < (3, 8):
    print("ERROR: Glyph requires Python 3.8 or higher.")
    print(f"You are using Python {sys.version}")
    sys.exit(1)

# Read long description from README
def read_long_description():
    """Read the long description from README.md."""
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Glyph - Voice-controlled markdown editing and Obsidian vault management"

# Read requirements from requirements.txt
def read_requirements():
    """Parse requirements from requirements.txt."""
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
            lines = f.readlines()
            # Filter out comments, empty lines, and development dependencies
            requirements = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-e"):
                    requirements.append(line)
            return requirements
    except FileNotFoundError:
        # Fallback minimal requirements
        return [
            "openai>=1.0.0,<2.0.0",
            "openai-whisper>=20240930", 
            "numpy>=1.21.0,<2.0.0",
            "rich>=13.0.0,<15.0.0",
            "sounddevice>=0.4.0,<1.0.0",
        ]

# Read version from main.py or use default
def get_version():
    """Get version from main.py or use default."""
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(here, "main.py"), encoding="utf-8") as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('__version__'):
                    return line.split('"')[1]
    except (FileNotFoundError, IndexError):
        pass
    return "2.0.0"

setup(
    # Package metadata
    name="glyph-voice",
    version=get_version(),
    author="Tanay Nagar",
    author_email="tnagar@andrew.cmu.edu",
    maintainer="Tanay Nagar",
    maintainer_email="tnagar@andrew.cmu.edu",
    
    # Package description
    description="Voice-controlled markdown editing and Obsidian vault management with conversational AI",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    
    # URLs
    url="https://github.com/tnagar72/Glyph",
    project_urls={
        "Bug Reports": "https://github.com/tnagar72/Glyph/issues",
        "Source Code": "https://github.com/tnagar72/Glyph",
        "Documentation": "https://github.com/tnagar72/Glyph/blob/main/README.md",
        "Changelog": "https://github.com/tnagar72/Glyph/blob/main/CHANGELOG.md",
        "Architecture": "https://github.com/tnagar72/Glyph/blob/main/ARCHITECTURE.md",
        "Testing Guide": "https://github.com/tnagar72/Glyph/blob/main/TESTING_GUIDE.md",
    },
    
    # Package discovery
    packages=find_packages(exclude=["tests", "tests.*", "*.tests", "*.tests.*"]),
    py_modules=[
        # Core modules
        "main",
        "recording", 
        "transcription",
        "transcription_config",
        "llm",
        "md_file",
        "cleaning",
        "diff",
        "utils",
        
        # Configuration modules
        "audio_config",
        "model_config",
        
        # UI modules
        "interactive_cli",
        "live_transcription",
        "ui_helpers",
        
        # Agent system
        "agent_cli",
        "agent_llm",
        "agent_tools",
        "agent_config",
        "agent_prompts", 
        "agent_memory",
        "agent_context",
        
        # Backup and session management
        "backup_manager",
        "undo_manager",
        "session_logger",
        "cleanup_backups",
        
        # Enhanced transcription
        "transcription_enhanced",
        
        # Demo and examples
        "demo_enhanced_agent",
        "run_glyph",
    ],
    
    # Package classification
    classifiers=[
        # Development status
        "Development Status :: 5 - Production/Stable",
        
        # Intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        
        # Topics
        "Topic :: Text Processing :: Markup",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Text Editors",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Documentation",
        "Topic :: Utilities",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Programming language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        
        # Operating system
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        
        # Environment
        "Environment :: Console",
        "Environment :: MacOS X",
        
        # Natural language
        "Natural Language :: English",
    ],
    
    # Keywords for discoverability
    keywords=[
        "voice", "speech", "markdown", "editing", "whisper", "gpt4", "openai",
        "transcription", "cli", "obsidian", "notes", "documentation", "ai",
        "assistant", "conversation", "productivity", "terminal", "voice-control",
        "knowledge-management", "note-taking", "automation", "workflow"
    ],
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-mock>=3.10.0,<4.0.0",
            "black>=23.0.0,<24.0.0",
            "isort>=5.12.0,<6.0.0",
            "flake8>=6.0.0,<7.0.0",
            "mypy>=1.0.0,<2.0.0",
            "pre-commit>=3.0.0,<4.0.0",
            "twine>=4.0.0,<5.0.0",  # For package publishing
        ],
        "test": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-mock>=3.10.0,<4.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0,<6.0.0",
            "sphinx-rtd-theme>=1.2.0,<2.0.0",
            "myst-parser>=0.18.0,<1.0.0",
        ],
        "performance": [
            "memory-profiler>=0.60.0,<1.0.0",
            "psutil>=5.9.0,<6.0.0",
        ],
    },
    
    # Console scripts
    entry_points={
        "console_scripts": [
            "glyph=main:main",
            "glyph-cleanup=cleanup_backups:main",
            "glyph-test=run_all_tests:main",
        ],
    },
    
    # Package data
    include_package_data=True,
    package_data={
        "": [
            "prompts/*.txt",
            "examples/*.md",
            "assets/*",
            "*.md",
            "*.txt",
            "*.json",
            "*.yml",
            "*.yaml",
        ],
    },
    
    # Data files
    data_files=[
        ("share/glyph/prompts", ["prompts/system_prompt.txt"] if os.path.exists("prompts/system_prompt.txt") else []),
        ("share/glyph/examples", ["examples/sample.md"] if os.path.exists("examples/sample.md") else []),
        ("share/glyph/docs", [
            "README.md",
            "FUNCTIONALITY.md", 
            "ARCHITECTURE.md",
            "TESTING_GUIDE.md",
        ]),
    ],
    
    # Installation options
    zip_safe=False,
    platforms=["any"],
    
    # License
    license="MIT",
    license_files=["LICENSE"],
    
    # Project maturity
    obsoletes=["obsidian-voice-updater"],  # If this replaces an older package
)