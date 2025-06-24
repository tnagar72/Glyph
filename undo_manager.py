import os
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from utils import verbose_print
from backup_manager import get_backup_manager

class UndoManager:
    """Manages undo functionality for markdown file edits using centralized backup system."""
    
    @staticmethod
    def find_latest_backup(original_file: str) -> Optional[str]:
        """Find the most recent backup file for the given original file."""
        backup_manager = get_backup_manager()
        latest_backup = backup_manager.get_latest_backup(original_file)
        
        if latest_backup:
            verbose_print(f"Found latest backup: {latest_backup}")
        else:
            verbose_print(f"No backup files found for {original_file}")
        
        return latest_backup
    
    @staticmethod
    def restore_from_backup(original_file: str, backup_file: Optional[str] = None) -> bool:
        """
        Restore a file from its backup using centralized backup system.
        
        Args:
            original_file: Path to the original file to restore
            backup_file: Specific backup file to restore from (optional)
            
        Returns:
            True if restoration was successful, False otherwise
        """
        backup_manager = get_backup_manager()
        return backup_manager.restore_from_backup(original_file, backup_file)
    
    @staticmethod
    def list_backups(original_file: str) -> List[str]:
        """List all available backup files for the given original file."""
        backup_manager = get_backup_manager()
        backup_info_list = backup_manager.list_backups(original_file)
        return [info["path"] for info in backup_info_list]
    
    @staticmethod
    def get_backup_info(backup_file: str) -> dict:
        """Get information about a backup file."""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            return {}
        
        stat = backup_path.stat()
        
        # Extract backup type from filename if possible
        filename_parts = backup_path.stem.split('_')
        backup_type = filename_parts[-2] if len(filename_parts) >= 3 else "unknown"
        
        return {
            "file": str(backup_path),
            "type": backup_type,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "timestamp": stat.st_mtime
        }