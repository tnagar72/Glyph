import os
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from utils import verbose_print

class UndoManager:
    """Manages undo functionality for markdown file edits."""
    
    @staticmethod
    def find_latest_backup(original_file: str) -> Optional[str]:
        """Find the most recent backup file for the given original file."""
        original_path = Path(original_file)
        
        if not original_path.exists():
            return None
        
        # Look for backup files in the same directory
        backup_pattern = f"{original_path.stem}_backup_*{original_path.suffix}"
        backup_files = list(original_path.parent.glob(backup_pattern))
        
        if not backup_files:
            verbose_print(f"No backup files found for {original_file}")
            return None
        
        # Sort by modification time, newest first
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest_backup = backup_files[0]
        
        verbose_print(f"Found latest backup: {latest_backup}")
        return str(latest_backup)
    
    @staticmethod
    def restore_from_backup(original_file: str, backup_file: Optional[str] = None) -> bool:
        """
        Restore a file from its backup.
        
        Args:
            original_file: Path to the original file to restore
            backup_file: Specific backup file to restore from (optional)
            
        Returns:
            True if restoration was successful, False otherwise
        """
        try:
            original_path = Path(original_file)
            
            # Find backup file if not specified
            if backup_file is None:
                backup_file = UndoManager.find_latest_backup(original_file)
                if backup_file is None:
                    verbose_print(f"No backup file found for {original_file}")
                    return False
            
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                verbose_print(f"Backup file does not exist: {backup_file}")
                return False
            
            # Create a backup of the current file before restoring
            if original_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                pre_undo_backup = original_path.parent / f"{original_path.stem}_pre_undo_{timestamp}{original_path.suffix}"
                shutil.copy2(original_path, pre_undo_backup)
                verbose_print(f"Created pre-undo backup: {pre_undo_backup}")
            
            # Restore from backup
            shutil.copy2(backup_path, original_path)
            verbose_print(f"Restored {original_file} from {backup_file}")
            
            return True
            
        except Exception as e:
            verbose_print(f"Error during undo operation: {e}")
            return False
    
    @staticmethod
    def list_backups(original_file: str) -> List[str]:
        """List all available backup files for the given original file."""
        original_path = Path(original_file)
        
        if not original_path.exists():
            return []
        
        backup_pattern = f"{original_path.stem}_backup_*{original_path.suffix}"
        backup_files = list(original_path.parent.glob(backup_pattern))
        
        # Sort by modification time, newest first
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return [str(backup) for backup in backup_files]
    
    @staticmethod
    def get_backup_info(backup_file: str) -> dict:
        """Get information about a backup file."""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            return {}
        
        stat = backup_path.stat()
        return {
            "file": str(backup_path),
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "timestamp": stat.st_mtime
        }