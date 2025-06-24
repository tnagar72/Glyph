# Voice Markdown Editor - Development Tasks

.PHONY: help install install-dev test lint format clean build upload docs run

# Default target
help:
	@echo "Voice Markdown Editor - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install production dependencies"
	@echo "  install-dev Install development dependencies"
	@echo "  setup       Setup development environment"
	@echo ""
	@echo "Development:"
	@echo "  run         Run the application interactively"
	@echo "  test        Run test suite"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black and isort"
	@echo "  clean       Clean build artifacts"
	@echo ""
	@echo "Backup Management:"
	@echo "  backup-stats       Show backup statistics"
	@echo "  backup-list        List old backup files"
	@echo "  backup-cleanup     Clean up old backups (interactive)"
	@echo "  backup-cleanup-dry Dry run cleanup (show what would be deleted)"
	@echo "  backup-cleanup-force Force cleanup without confirmation"
	@echo ""
	@echo "Distribution:"
	@echo "  build       Build package for distribution"
	@echo "  upload      Upload to PyPI (requires credentials)"
	@echo "  upload-test Upload to TestPyPI"
	@echo ""
	@echo "Documentation:"
	@echo "  docs        Generate documentation"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

setup: install-dev
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file - please add your OpenAI API key"; \
	fi
	@echo "Development environment ready!"

# Development targets
run:
	python main.py --interactive

test:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	mypy . --ignore-missing-imports

format:
	black . --line-length 100
	isort . --profile black

# Clean targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Distribution targets
build: clean
	python -m build

upload: build
	python -m twine upload dist/*

upload-test: build
	python -m twine upload --repository testpypi dist/*

# Documentation targets
docs:
	@echo "Generating documentation..."
	@echo "README.md - Main documentation"
	@echo "FUNCTIONALITY.md - Feature details"
	@echo "DEVELOPER_TOOLS.md - Advanced usage"
	@echo "FAQ.md - Common questions"
	@echo "EXAMPLES.md - Usage examples"

# Backup management targets
backup-stats:
	python cleanup_backups.py --stats

backup-list:
	python cleanup_backups.py --list

backup-cleanup:
	python cleanup_backups.py

backup-cleanup-dry:
	python cleanup_backups.py --dry-run

backup-cleanup-force:
	python cleanup_backups.py --force

# Quick development commands
dev-setup: setup
	@echo "Development environment is ready!"
	@echo "Try: make run"

quick-test:
	python main.py --transcript-only --verbose

demo:
	@echo "Running demo with example file..."
	python main.py --file examples/sample_todo.md --dry-run

# Version management
version:
	@python -c "from main import __version__; print(f'Version: {__version__}')"

# Environment validation
check-env:
	@python -c "import os; print('✅ OpenAI API key configured' if os.getenv('OPENAI_API_KEY') else '❌ OpenAI API key missing - check .env file')"
	@python -c "import sounddevice as sd; print('✅ Audio system available')" 2>/dev/null || echo "❌ Audio system check failed"

# Full development workflow
dev-check: check-env lint test
	@echo "✅ All development checks passed!"

# Installation verification
verify-install:
	python main.py --version
	python main.py --help
	@echo "✅ Installation verified successfully"