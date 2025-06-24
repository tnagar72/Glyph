#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        return f.read()

# Read requirements
def read_requirements():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="voice-markdown-editor",  # Will be updated with final project name
    version="1.0.0",
    author="Voice Markdown Editor Contributors",
    author_email="your-email@example.com",  # Update with actual email
    description="Transform your voice into intelligent markdown edits using Whisper and GPT-4",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/voice-markdown-editor",  # Update with actual repo
    project_urls={
        "Bug Reports": "https://github.com/your-username/voice-markdown-editor/issues",
        "Source": "https://github.com/your-username/voice-markdown-editor",
        "Documentation": "https://github.com/your-username/voice-markdown-editor#readme",
    },
    packages=find_packages(),
    py_modules=[
        "main",
        "recording", 
        "transcription",
        "llm",
        "interactive_cli",
        "live_transcription",
        "diff",
        "session_logger",
        "undo_manager",
        "md_file",
        "prompts",
        "cleaning",
        "utils"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: Markup",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Text Editors",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    keywords="voice, markdown, editing, whisper, gpt4, transcription, cli, obsidian",
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0", 
            "isort>=5.0.0",
            "flake8>=4.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "voice-md=main:main",
            "voice-markdown=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "prompts/*.txt",
            "examples/*.md",
            "*.md",
            "*.txt",
        ],
    },
    zip_safe=False,
)