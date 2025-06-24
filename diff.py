import difflib
from typing import List, Tuple
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

console = Console()

def show_diff(original: str, modified: str, filename: str = "markdown file") -> List[str]:
    """
    Generate and display a rich, colorful diff between original and modified content.
    
    Args:
        original: Original content
        modified: Modified content  
        filename: Name of file being modified (for display)
        
    Returns:
        List of diff lines for programmatic use
    """
    
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)
    
    diff = list(difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        lineterm=''
    ))
    
    if not diff:
        console.print("\n✅ [green]No changes detected[/green]")
        return []
    
    # Create rich diff visualization
    _render_rich_diff(diff, filename)
    
    return diff

def _render_rich_diff(diff_lines: List[str], filename: str):
    """
    Render a beautiful GitHub-style diff using Rich.
    
    Args:
        diff_lines: List of diff lines from difflib
        filename: Name of the file being diffed
    """
    
    console.print()  # Add spacing
    
    # Header panel
    title = Text()
    title.append("📋 Changes Preview: ", style="bold white")
    title.append(filename, style="bold cyan")
    
    # Create table for side-by-side view
    table = Table(
        show_header=True,
        box=box.ROUNDED,
        title=title,
        title_style="bold white"
    )
    
    table.add_column("", style="dim", width=4, justify="right")  # Line numbers
    table.add_column("Diff", style="", min_width=60)
    
    line_num = 0
    in_hunk = False
    
    for line in diff_lines:
        if line.startswith('---') or line.startswith('+++'):
            # File headers - style them nicely
            if line.startswith('---'):
                styled_line = Text()
                styled_line.append("--- ", style="bold red")
                styled_line.append(line[4:].strip(), style="red")
            else:
                styled_line = Text()
                styled_line.append("+++ ", style="bold green")
                styled_line.append(line[4:].strip(), style="green")
            
            table.add_row("", styled_line)
            
        elif line.startswith('@@'):
            # Hunk header
            in_hunk = True
            styled_line = Text(line.strip(), style="bold magenta on grey23")
            table.add_row("", styled_line)
            
        elif in_hunk and line:
            line_num += 1
            
            if line.startswith('+'):
                # Addition
                styled_line = Text()
                styled_line.append("+ ", style="bold green")
                
                # Syntax highlight the markdown content
                content = line[1:].rstrip('\n')
                if content.strip():
                    try:
                        syntax = Syntax(content, "markdown", theme="github-dark", line_numbers=False, word_wrap=True)
                        styled_line.append(content, style="green")
                    except:
                        styled_line.append(content, style="green")
                
                table.add_row(str(line_num), styled_line)
                
            elif line.startswith('-'):
                # Deletion
                styled_line = Text()
                styled_line.append("- ", style="bold red")
                
                content = line[1:].rstrip('\n')
                if content.strip():
                    styled_line.append(content, style="red")
                
                table.add_row(str(line_num), styled_line)
                
            elif line.startswith(' '):
                # Context line
                styled_line = Text()
                styled_line.append("  ", style="dim")
                
                content = line[1:].rstrip('\n')
                if content.strip():
                    styled_line.append(content, style="dim white")
                
                table.add_row(str(line_num), styled_line)
    
    console.print(table)

def _render_inline_diff(original: str, modified: str, filename: str):
    """
    Alternative: render inline diff with syntax highlighting.
    """
    
    # Header
    header = Panel(
        f"[bold white]📋 Changes Preview: [cyan]{filename}[/cyan]",
        style="blue",
        box=box.DOUBLE
    )
    console.print(header)
    
    # Show original
    console.print("\n[bold red]--- Original[/bold red]")
    if original.strip():
        original_syntax = Syntax(original, "markdown", theme="github-dark", line_numbers=True)
        console.print(Panel(original_syntax, title="Before", border_style="red"))
    
    # Show modified  
    console.print("\n[bold green]+++ Modified[/bold green]")
    if modified.strip():
        modified_syntax = Syntax(modified, "markdown", theme="github-dark", line_numbers=True)
        console.print(Panel(modified_syntax, title="After", border_style="green"))

def get_user_approval(changes_detected: bool = True) -> bool:
    """
    Ask user for approval to apply changes with rich styling.
    
    Args:
        changes_detected: Whether changes were actually detected
        
    Returns:
        True if user approves, False otherwise
    """
    
    if not changes_detected:
        return False
    
    console.print()  # Add spacing
    
    while True:
        try:
            # Rich prompt
            console.print("✅ [bold green]Accept changes?[/bold green] [dim]\\[y/N][/dim]: ", end="")
            response = input().strip().lower()
            
            if response in ['y', 'yes']:
                console.print("🎉 [bold green]Changes accepted![/bold green]")
                return True
            elif response in ['n', 'no', '']:  # Default to 'no' if empty
                console.print("❌ [yellow]Changes rejected[/yellow]")
                return False
            else:
                console.print("[red]Please enter 'y' for yes or 'n' for no[/red]")
                
        except KeyboardInterrupt:
            console.print("\n❌ [red]Operation cancelled by user[/red]")
            return False
        except EOFError:
            console.print("\n❌ [red]Input error[/red]")
            return False

def count_changes(diff_lines: List[str]) -> Tuple[int, int]:
    """
    Count additions and deletions in diff.
    
    Args:
        diff_lines: List of diff lines
        
    Returns:
        Tuple of (additions, deletions)
    """
    
    additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
    
    return additions, deletions

def show_change_summary(diff_lines: List[str]) -> None:
    """
    Show a beautiful summary of changes using Rich.
    
    Args:
        diff_lines: List of diff lines
    """
    
    if not diff_lines:
        return
    
    additions, deletions = count_changes(diff_lines)
    
    # Create a summary table
    summary_table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 1)
    )
    
    summary_table.add_column("Icon", style="bold", width=3)
    summary_table.add_column("Type", style="bold", width=12)
    summary_table.add_column("Count", style="bold", width=8)
    
    summary_table.add_row("📊", "Summary", "")
    summary_table.add_row("✅", "[green]Additions[/green]", f"[green]+{additions}[/green]")
    summary_table.add_row("❌", "[red]Deletions[/red]", f"[red]-{deletions}[/red]")
    
    console.print(summary_table)