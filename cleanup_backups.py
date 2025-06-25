#!/usr/bin/env python3
"""
Backup cleanup script for Glyph.
Removes old backup files based on retention policies.
"""

import argparse
import sys
from datetime import datetime
from backup_manager import get_backup_manager
from utils import verbose_print, set_verbose
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def format_size(size_bytes: int) -> str:
    """Format byte size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def show_backup_stats(backup_manager):
    """Display current backup statistics."""
    stats = backup_manager.get_backup_stats()
    
    stats_table = Table(title="📊 Backup Statistics", box=box.ROUNDED)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row("Total Files", str(stats["total_files"]))
    stats_table.add_row("Total Size", format_size(stats["total_size_bytes"]))
    stats_table.add_row("Backup Directory", str(stats["backup_root"]))
    
    if stats["oldest_backup"]:
        stats_table.add_row("Oldest Backup", stats["oldest_backup"].strftime('%Y-%m-%d %H:%M:%S'))
    if stats["newest_backup"]:
        stats_table.add_row("Newest Backup", stats["newest_backup"].strftime('%Y-%m-%d %H:%M:%S'))
    
    console.print(stats_table)

def confirm_cleanup(days_to_keep: int, dry_run: bool = False) -> bool:
    """Ask user to confirm cleanup operation."""
    action = "would delete" if dry_run else "will delete"
    
    confirm_panel = Panel(
        f"[yellow]⚠️ This {action} all backup files older than {days_to_keep} days.[/yellow]\n\n"
        f"[red]This action cannot be undone.[/red]\n\n"
        f"Are you sure you want to continue?",
        title="Confirm Cleanup",
        style="yellow",
        box=box.ROUNDED
    )
    console.print(confirm_panel)
    
    if dry_run:
        return True  # No confirmation needed for dry run
    
    response = console.input("[bold yellow]Continue? [y/N]: [/bold yellow]").strip().lower()
    return response in ['y', 'yes']

def cleanup_backups(days_to_keep: int = 30, dry_run: bool = False, force: bool = False):
    """
    Clean up old backup files.
    
    Args:
        days_to_keep: Number of days to retain backups
        dry_run: Show what would be deleted without actually deleting
        force: Skip confirmation prompt
    """
    backup_manager = get_backup_manager()
    
    # Show current statistics
    console.print("\n📋 [bold white]Current Backup Status[/bold white]")
    show_backup_stats(backup_manager)
    
    # Get confirmation unless forced or dry run
    if not force and not dry_run:
        if not confirm_cleanup(days_to_keep, dry_run):
            console.print("❌ [yellow]Cleanup cancelled[/yellow]")
            return
    
    # Perform cleanup
    console.print(f"\n🧹 [bold green]{'Simulating' if dry_run else 'Starting'} cleanup...[/bold green]")
    
    if dry_run:
        # Simulate cleanup by showing what would be deleted
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        would_delete_count = 0
        would_delete_size = 0
        
        try:
            for backup_file in backup_manager.backup_root.rglob("*"):
                if backup_file.is_file() and backup_file.name != ".gitkeep":
                    file_mtime = backup_file.stat().st_mtime
                    if file_mtime < cutoff_time:
                        would_delete_count += 1
                        would_delete_size += backup_file.stat().st_size
                        verbose_print(f"Would delete: {backup_file}")
        
        except Exception as e:
            console.print(f"[red]Error during dry run: {e}[/red]")
            return
        
        # Show dry run results
        results_table = Table(title="🔍 Dry Run Results", box=box.ROUNDED)
        results_table.add_column("Action", style="cyan")
        results_table.add_column("Count", style="white")
        results_table.add_column("Size", style="white")
        
        results_table.add_row("Would Delete", str(would_delete_count), format_size(would_delete_size))
        
        console.print(results_table)
        
        if would_delete_count > 0:
            console.print(f"\n💡 [dim]Run without --dry-run to actually delete {would_delete_count} files[/dim]")
        else:
            console.print("\n✅ [green]No files need cleanup[/green]")
    
    else:
        # Actual cleanup
        stats = backup_manager.cleanup_old_backups(days_to_keep)
        
        # Show cleanup results
        results_table = Table(title="✅ Cleanup Results", box=box.ROUNDED)
        results_table.add_column("Action", style="cyan")
        results_table.add_column("Count", style="white")
        results_table.add_column("Size", style="white")
        
        results_table.add_row("Deleted", str(stats["deleted_files"]), format_size(stats["deleted_size_bytes"]))
        results_table.add_row("Kept", str(stats["kept_files"]), "")
        
        if stats["errors"] > 0:
            results_table.add_row("Errors", str(stats["errors"]), "")
        
        console.print(results_table)
        
        if stats["deleted_files"] > 0:
            console.print(f"\n✅ [green]Successfully cleaned up {stats['deleted_files']} old backup files[/green]")
        else:
            console.print("\n✅ [green]No files needed cleanup[/green]")
        
        # Show updated statistics
        console.print("\n📊 [bold white]Updated Backup Status[/bold white]")
        show_backup_stats(backup_manager)

def list_old_backups(days_to_keep: int = 30):
    """List backup files that would be deleted."""
    backup_manager = get_backup_manager()
    cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
    
    old_files = []
    
    try:
        for backup_file in backup_manager.backup_root.rglob("*"):
            if backup_file.is_file() and backup_file.name != ".gitkeep":
                file_mtime = backup_file.stat().st_mtime
                if file_mtime < cutoff_time:
                    old_files.append({
                        "path": backup_file,
                        "size": backup_file.stat().st_size,
                        "age_days": int((datetime.now().timestamp() - file_mtime) / (24 * 60 * 60))
                    })
    
    except Exception as e:
        console.print(f"[red]Error listing files: {e}[/red]")
        return
    
    if not old_files:
        console.print(f"✅ [green]No backup files older than {days_to_keep} days found[/green]")
        return
    
    # Sort by age, oldest first
    old_files.sort(key=lambda x: x["age_days"], reverse=True)
    
    # Show table of old files
    old_files_table = Table(title=f"📁 Files Older Than {days_to_keep} Days", box=box.ROUNDED)
    old_files_table.add_column("File", style="cyan")
    old_files_table.add_column("Age (days)", style="yellow")
    old_files_table.add_column("Size", style="white")
    
    total_size = 0
    for file_info in old_files[:20]:  # Show first 20
        old_files_table.add_row(
            str(file_info["path"].name),
            str(file_info["age_days"]),
            format_size(file_info["size"])
        )
        total_size += file_info["size"]
    
    if len(old_files) > 20:
        old_files_table.add_row("...", f"({len(old_files) - 20} more)", "...")
    
    console.print(old_files_table)
    console.print(f"\n📊 Total: {len(old_files)} files, {format_size(total_size)}")

def main():
    """Main entry point for backup cleanup script."""
    parser = argparse.ArgumentParser(description="🧹 Backup Cleanup Tool")
    parser.add_argument("--days", "-d", type=int, default=30, 
                       help="Number of days to retain backups (default: 30)")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be deleted without actually deleting")
    parser.add_argument("--force", "-f", action="store_true", 
                       help="Skip confirmation prompt")
    parser.add_argument("--list", "-l", action="store_true", 
                       help="List old files without deleting")
    parser.add_argument("--stats", "-s", action="store_true", 
                       help="Show backup statistics only")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        set_verbose(True)
    
    # Header
    title_panel = Panel(
        "🧹 [bold white]Backup Cleanup Tool[/bold white]\n"
        "Manage retention of voice editor backup files",
        style="blue",
        box=box.DOUBLE
    )
    console.print(title_panel)
    
    # Validate days parameter
    if args.days < 1:
        console.print("[red]❌ Days must be at least 1[/red]")
        sys.exit(1)
    
    try:
        if args.stats:
            # Show stats only
            backup_manager = get_backup_manager()
            show_backup_stats(backup_manager)
        
        elif args.list:
            # List old files
            list_old_backups(args.days)
        
        else:
            # Perform cleanup
            cleanup_backups(args.days, args.dry_run, args.force)
    
    except KeyboardInterrupt:
        console.print("\n❌ [yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()