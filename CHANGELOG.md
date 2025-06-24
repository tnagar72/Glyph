# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enter-to-stop recording method to prevent terminal interference
- Comprehensive README with installation and usage examples
- Contributing guidelines and development setup
- Example markdown files for testing
- MIT License for open source distribution

### Changed
- Enhanced .gitignore to protect sensitive data
- Improved error handling and user feedback
- Updated documentation structure

### Fixed
- Terminal bell and lockup issues in iTerm with spacebar recording
- Audio validation and error recovery

## [1.0.0] - 2025-06-24

### Added
- Initial release of voice-controlled markdown editor
- OpenAI Whisper integration for local speech recognition
- GPT-4 powered intelligent markdown editing
- Rich terminal UI with colored diffs and progress indicators
- Interactive CLI mode with file browsing and model selection
- Live transcription mode for real-time voice streaming
- Automatic backup system with undo functionality
- Session logging and comprehensive error handling
- Obsidian-compatible formatting preservation
- Multiple Whisper model support (tiny to large)
- Press-to-talk and enter-to-stop recording methods
- Comprehensive documentation and examples

### Security
- Protected API keys and sensitive data with .gitignore
- Automatic backup creation before file modifications
- User approval required for all changes