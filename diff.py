import difflib
from typing import List, Tuple
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from ui_helpers import (
    GLYPH_PRIMARY, GLYPH_SECONDARY, GLYPH_ACCENT, GLYPH_HIGHLIGHT,
    GLYPH_SUCCESS, GLYPH_ERROR, GLYPH_WARNING, GLYPH_MUTED
)

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
        console.print(f"\n✅ [{GLYPH_SUCCESS}]No changes detected[/{GLYPH_SUCCESS}]")
        return []
    
    # Create rich diff visualization with Glyph styling
    _render_rich_diff(diff, filename)
    
    return diff

def _render_rich_diff(diff_lines: List[str], filename: str):
    """
    Render a beautiful diff using Glyph styling.
    
    Args:
        diff_lines: List of diff lines from difflib
        filename: Name of the file being diffed
    """
    
    console.print()  # Add spacing
    
    # Header panel with Glyph branding
    title = Text()
    title.append("◈ ", style=f"bold {GLYPH_ACCENT}")
    title.append("Changes Preview: ", style="bold white")
    title.append(filename, style=f"bold {GLYPH_HIGHLIGHT}")
    title.append(" ◈", style=f"bold {GLYPH_ACCENT}")
    
    # Create table with Glyph styling
    table = Table(
        show_header=True,
        box=box.HEAVY,
        title=title,
        title_style=f"bold {GLYPH_PRIMARY}",
        border_style=GLYPH_SECONDARY
    )
    
    table.add_column("", style=GLYPH_MUTED, width=4, justify="right")  # Line numbers
    table.add_column("Diff", style="", min_width=60)
    
    line_num = 0
    in_hunk = False
    
    for line in diff_lines:
        if line.startswith('---') or line.startswith('+++'):
            # File headers - style them nicely
            if line.startswith('---'):
                styled_line = Text()
                styled_line.append("--- ", style=f"bold {GLYPH_ERROR}")
                styled_line.append(line[4:].strip(), style=GLYPH_ERROR)
            else:
                styled_line = Text()
                styled_line.append("+++ ", style=f"bold {GLYPH_SUCCESS}")
                styled_line.append(line[4:].strip(), style=GLYPH_SUCCESS)
            
            table.add_row("", styled_line)
            
        elif line.startswith('@@'):
            # Hunk header
            in_hunk = True
            styled_line = Text(line.strip(), style=f"bold {GLYPH_PRIMARY} on grey23")
            table.add_row("", styled_line)
            
        elif in_hunk and line:
            line_num += 1
            
            if line.startswith('+'):
                # Addition with Glyph success color
                styled_line = Text()
                styled_line.append("+ ", style=f"bold {GLYPH_SUCCESS}")
                
                # Syntax highlight the markdown content
                content = line[1:].rstrip('\n')
                if content.strip():
                    try:
                        syntax = Syntax(content, "markdown", theme="github-dark", line_numbers=False, word_wrap=True)
                        styled_line.append(content, style=GLYPH_SUCCESS)
                    except:
                        styled_line.append(content, style=GLYPH_SUCCESS)
                
                table.add_row(str(line_num), styled_line)
                
            elif line.startswith('-'):
                # Deletion with Glyph error color
                styled_line = Text()
                styled_line.append("- ", style=f"bold {GLYPH_ERROR}")
                
                content = line[1:].rstrip('\n')
                if content.strip():
                    styled_line.append(content, style=GLYPH_ERROR)
                
                table.add_row(str(line_num), styled_line)
                
            elif line.startswith(' '):
                # Context line with muted color
                styled_line = Text()
                styled_line.append("  ", style=GLYPH_MUTED)
                
                content = line[1:].rstrip('\n')
                if content.strip():
                    styled_line.append(content, style=GLYPH_MUTED)
                
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
            # Rich prompt with Glyph styling
            console.print(f"✅ [bold {GLYPH_SUCCESS}]Accept changes?[/bold {GLYPH_SUCCESS}] [{GLYPH_MUTED}]\\[y/N][/{GLYPH_MUTED}]: ", end="")
            response = input().strip().lower()
            
            if response in ['y', 'yes']:
                console.print(f"🎉 [bold {GLYPH_SUCCESS}]Changes accepted![/bold {GLYPH_SUCCESS}]")
                return True
            elif response in ['n', 'no', '']:  # Default to 'no' if empty
                console.print(f"❌ [{GLYPH_WARNING}]Changes rejected[/{GLYPH_WARNING}]")
                return False
            else:
                console.print(f"[{GLYPH_ERROR}]Please enter 'y' for yes or 'n' for no[/{GLYPH_ERROR}]")
                
        except KeyboardInterrupt:
            console.print(f"\n❌ [{GLYPH_ERROR}]Operation cancelled by user[/{GLYPH_ERROR}]")
            return False
        except EOFError:
            console.print(f"\n❌ [{GLYPH_ERROR}]Input error[/{GLYPH_ERROR}]")
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
    
    # Create a summary table with Glyph styling
    summary_table = Table(
        show_header=False,
        box=box.HEAVY,
        padding=(0, 1),
        border_style=GLYPH_SECONDARY
    )
    
    summary_table.add_column("Icon", style="bold", width=3)
    summary_table.add_column("Type", style="bold", width=12)
    summary_table.add_column("Count", style="bold", width=8)
    
    summary_table.add_row("📊", "Summary", "")
    summary_table.add_row("✅", f"[{GLYPH_SUCCESS}]Additions[/{GLYPH_SUCCESS}]", f"[{GLYPH_SUCCESS}]+{additions}[/{GLYPH_SUCCESS}]")
    summary_table.add_row("❌", f"[{GLYPH_ERROR}]Deletions[/{GLYPH_ERROR}]", f"[{GLYPH_ERROR}]-{deletions}[/{GLYPH_ERROR}]")
    
    console.print(summary_table)