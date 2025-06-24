import os
import shutil
from pathlib import Path
from datetime import datetime
from utils import verbose_print

def read_markdown_file(file_path: str) -> str:
    """
    Read a markdown file and return its content.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a markdown file
    """
    
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if path.suffix.lower() not in ['.md', '.markdown']:
        raise ValueError(f"File must be a markdown file (.md or .markdown): {file_path}")
    
    try:
        verbose_print(f"Reading markdown file: {file_path}")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        verbose_print(f"Read {len(content)} characters from {file_path}")
        return content
        
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")

def write_markdown_file(file_path: str, content: str, create_backup: bool = True) -> str:
    """
    Write content to a markdown file, optionally creating a backup.
    
    Args:
        file_path: Path to the markdown file
        content: Content to write
        create_backup: Whether to create a backup of the original file
        
    Returns:
        Path to backup file if created, None otherwise
    """
    
    path = Path(file_path)
    backup_path = None
    
    # Create backup if file exists and backup is requested
    if path.exists() and create_backup:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = path.parent / f"{path.stem}_backup_{timestamp}{path.suffix}"
        shutil.copy2(path, backup_path)
        verbose_print(f"Backup created: {backup_path}")
    
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Normalize content before writing
        normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        verbose_print(f"Writing {len(normalized_content)} characters to {file_path}")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(normalized_content)
        
        verbose_print(f"Successfully wrote file: {file_path}")
        return str(backup_path) if backup_path else None
        
    except Exception as e:
        raise Exception(f"Error writing file {file_path}: {e}")

def validate_markdown_path(file_path: str) -> Path:
    """
    Validate and normalize a markdown file path.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Normalized Path object
        
    Raises:
        ValueError: If path is invalid
    """
    
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    path = Path(file_path).expanduser().resolve()
    
    if path.suffix.lower() not in ['.md', '.markdown']:
        # Auto-add .md extension if missing
        path = path.with_suffix('.md')
    
    return path