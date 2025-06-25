#!/usr/bin/env python3
"""
Centralized backup management for Glyph.
Handles creating, organizing, and cleaning up backup files.
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from utils import verbose_print

class BackupManager:
    """Manages centralized backup system for markdown files."""
    
    def __init__(self, backup_root: Optional[str] = None):
        """Initialize backup manager with configurable backup directory."""
        if backup_root is None:
            # Default to backups/ directory in the project root
            self.backup_root = Path(__file__).parent / "backups"
        else:
            self.backup_root = Path(backup_root)
        
        # Ensure backup directory exists
        self.backup_root.mkdir(parents=True, exist_ok=True)
        verbose_print(f"Backup manager initialized with root: {self.backup_root}")
    
    def _get_backup_subdir(self, original_file: str) -> Path:
        """Get the backup subdirectory for a given file."""
        original_path = Path(original_file).resolve()
        
        # Create a subdirectory structure based on the original file's path
        # This prevents naming conflicts and organizes backups
        relative_path = original_path.parent.name  # Just the immediate parent directory
        file_stem = original_path.stem
        
        # Create subdirectory: backups/parent_dir/filename/
        backup_subdir = self.backup_root / relative_path / file_stem
        backup_subdir.mkdir(parents=True, exist_ok=True)
        
        return backup_subdir
    
    def create_backup(self, original_file: str, backup_type: str = "auto") -> Optional[str]:
        """
        Create a backup of the given file.
        
        Args:
            original_file: Path to the file to backup
            backup_type: Type of backup (auto, manual, pre_undo, etc.)
        
        Returns:
            Path to the created backup file, or None if backup failed
        """
        try:
            original_path = Path(original_file)
            
            if not original_path.exists():
                verbose_print(f"Cannot backup non-existent file: {original_file}")
                return None
            
            # Get backup subdirectory
            backup_subdir = self._get_backup_subdir(original_file)
            
            # Create backup filename with timestamp and type
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{original_path.stem}_{backup_type}_{timestamp}{original_path.suffix}"
            backup_path = backup_subdir / backup_filename
            
            # Copy file to backup location
            shutil.copy2(original_path, backup_path)
            verbose_print(f"Created backup: {backup_path}")
            
            return str(backup_path)
            
        except Exception as e:
            verbose_print(f"Error creating backup for {original_file}: {e}")
            return None
    
    def list_backups(self, original_file: str) -> List[Dict[str, any]]:
        """
        List all backup files for a given original file.
        
        Args:
            original_file: Path to the original file
            
        Returns:
            List of backup info dictionaries sorted by creation time (newest first)
        """
        try:
            original_path = Path(original_file)
            backup_subdir = self._get_backup_subdir(original_file)
            
            if not backup_subdir.exists():
                return []
            
            # Find all backup files for this file
            backup_pattern = f"{original_path.stem}_*{original_path.suffix}"
            backup_files = list(backup_subdir.glob(backup_pattern))
            
            # Create info list with metadata
            backup_info = []
            for backup_file in backup_files:
                stat = backup_file.stat()
                
                # Extract backup type from filename
                filename_parts = backup_file.stem.split('_')
                backup_type = filename_parts[-2] if len(filename_parts) >= 3 else "unknown"
                
                backup_info.append({
                    "path": str(backup_file),
                    "filename": backup_file.name,
                    "type": backup_type,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime),
                    "created_str": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    "timestamp": stat.st_mtime
                })
            
            # Sort by creation time, newest first
            backup_info.sort(key=lambda x: x["timestamp"], reverse=True)
            
            verbose_print(f"Found {len(backup_info)} backups for {original_file}")
            return backup_info
            
        except Exception as e:
            verbose_print(f"Error listing backups for {original_file}: {e}")
            return []
    
    def get_latest_backup(self, original_file: str) -> Optional[str]:
        """Get the path to the most recent backup for a file."""
        backups = self.list_backups(original_file)
        if backups:
            return backups[0]["path"]
        return None
    
    def restore_from_backup(self, original_file: str, backup_path: Optional[str] = None) -> bool:
        """
        Restore a file from its backup.
        
        Args:
            original_file: Path to the file to restore
            backup_path: Specific backup to restore from (uses latest if None)
            
        Returns:
            True if restoration was successful
        """
        try:
            original_path = Path(original_file)
            
            # Find backup file if not specified
            if backup_path is None:
                backup_path = self.get_latest_backup(original_file)
                if backup_path is None:
                    verbose_print(f"No backup found for {original_file}")
                    return False
            
            backup_file = Path(backup_path)
            if not backup_file.exists():
                verbose_print(f"Backup file does not exist: {backup_path}")
                return False
            
            # Create a pre-restore backup of current state
            if original_path.exists():
                pre_restore_backup = self.create_backup(original_file, "pre_restore")
                if pre_restore_backup:
                    verbose_print(f"Created pre-restore backup: {pre_restore_backup}")
            
            # Restore from backup
            shutil.copy2(backup_file, original_path)
            verbose_print(f"Restored {original_file} from {backup_path}")
            
            return True
            
        except Exception as e:
            verbose_print(f"Error restoring {original_file}: {e}")
            return False
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> Dict[str, int]:
        """
        Clean up backup files older than specified days.
        
        Args:
            days_to_keep: Number of days to retain backups
            
        Returns:
            Dictionary with cleanup statistics
        """
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        deleted_count = 0
        deleted_size = 0
        kept_count = 0
        error_count = 0
        
        verbose_print(f"Cleaning up backups older than {days_to_keep} days...")
        
        try:
            # Walk through all backup files
            for backup_file in self.backup_root.rglob("*"):
                if backup_file.is_file() and backup_file.name != ".gitkeep":
                    try:
                        file_mtime = backup_file.stat().st_mtime
                        
                        if file_mtime < cutoff_time:
                            # File is old, delete it
                            file_size = backup_file.stat().st_size
                            backup_file.unlink()
                            deleted_count += 1
                            deleted_size += file_size
                            verbose_print(f"Deleted old backup: {backup_file}")
                        else:
                            kept_count += 1
                            
                    except Exception as e:
                        verbose_print(f"Error processing {backup_file}: {e}")
                        error_count += 1
            
            # Clean up empty directories
            self._cleanup_empty_dirs()
            
        except Exception as e:
            verbose_print(f"Error during cleanup: {e}")
            error_count += 1
        
        stats = {
            "deleted_files": deleted_count,
            "deleted_size_bytes": deleted_size,
            "kept_files": kept_count,
            "errors": error_count
        }
        
        verbose_print(f"Cleanup complete: {deleted_count} files deleted, {kept_count} files kept")
        return stats
    
    def _cleanup_empty_dirs(self):
        """Remove empty backup directories."""
        try:
            for dirpath in self.backup_root.rglob("*"):
                if dirpath.is_dir() and dirpath != self.backup_root:
                    try:
                        # Only remove if empty (except for .gitkeep files)
                        contents = list(dirpath.iterdir())
                        if not contents or (len(contents) == 1 and contents[0].name == ".gitkeep"):
                            if contents:  # Remove .gitkeep if it's the only file
                                contents[0].unlink()
                            dirpath.rmdir()
                            verbose_print(f"Removed empty backup directory: {dirpath}")
                    except OSError:
                        # Directory not empty, skip
                        pass
        except Exception as e:
            verbose_print(f"Error cleaning up empty directories: {e}")
    
    def get_backup_stats(self) -> Dict[str, any]:
        """Get statistics about the backup system."""
        total_files = 0
        total_size = 0
        oldest_backup = None
        newest_backup = None
        
        try:
            for backup_file in self.backup_root.rglob("*"):
                if backup_file.is_file() and backup_file.name != ".gitkeep":
                    total_files += 1
                    total_size += backup_file.stat().st_size
                    
                    file_mtime = backup_file.stat().st_mtime
                    if oldest_backup is None or file_mtime < oldest_backup:
                        oldest_backup = file_mtime
                    if newest_backup is None or file_mtime > newest_backup:
                        newest_backup = file_mtime
        
        except Exception as e:
            verbose_print(f"Error gathering backup stats: {e}")
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_backup": datetime.fromtimestamp(oldest_backup) if oldest_backup else None,
            "newest_backup": datetime.fromtimestamp(newest_backup) if newest_backup else None,
            "backup_root": str(self.backup_root)
        }


# Global backup manager instance
_backup_manager = None

def get_backup_manager() -> BackupManager:
    """Get the global backup manager instance."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager