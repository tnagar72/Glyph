import os
import re
from pathlib import Path
from datetime import datetime
from utils import verbose_print

def load_prompt_template(template_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    template_path = Path(__file__).parent / "prompts" / f"{template_name}.txt"
    
    if not template_path.exists():
        verbose_print(f"Warning: Template {template_name}.txt not found, using fallback")
        return get_fallback_prompt(template_name)
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        verbose_print(f"Error loading template {template_name}: {e}")
        return get_fallback_prompt(template_name)

def get_fallback_prompt(template_name: str) -> str:
    """Fallback prompts if template files are missing."""
    if template_name == "system_prompt":
        return """You are a markdown editor assistant. Modify the markdown according to the user's instruction while preserving structure and Obsidian compatibility. Return only the modified content."""
    elif template_name == "user_prompt":
        return """Current Markdown File:\n{markdown_content}\n\nUser Instruction:\n{instruction}\n\nPlease return the modified markdown file:"""
    return ""

def analyze_markdown_content(content: str, filename: str = "unknown") -> dict:
    """Analyze markdown content to extract metadata for dynamic prompting."""
    
    lines = content.split('\n')
    
    # Count various elements
    sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
    tasks = re.findall(r'^\s*-\s+\[(.)\]', content, re.MULTILINE)
    links = re.findall(r'\[\[([^\]]+)\]\]|\[([^\]]+)\]\([^\)]+\)', content)
    tags = re.findall(r'#\w+', content)
    
    completed_tasks = sum(1 for task in tasks if task.lower() in ['x', 'v'])
    pending_tasks = len(tasks) - completed_tasks
    
    return {
        'filename': filename,
        'file_type': 'Obsidian Markdown' if '[[' in content or '#' in content else 'Standard Markdown',
        'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'line_count': len(lines),
        'sections': ', '.join(sections[:5]) + ('...' if len(sections) > 5 else ''),
        'task_count': len(tasks),
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'link_count': len(links),
        'tag_count': len(tags)
    }

def create_dynamic_prompts(markdown_content: str, instruction: str, filename: str = "unknown") -> tuple[str, str]:
    """Create dynamic system and user prompts with context analysis."""
    
    # Analyze the markdown content
    context = analyze_markdown_content(markdown_content, filename)
    verbose_print(f"Analyzed markdown: {context['task_count']} tasks, {context['line_count']} lines, {len(context['sections'])} sections")
    
    # Load and format system prompt
    system_template = load_prompt_template("system_prompt")
    system_prompt = system_template.format(**context)
    
    # Load and format user prompt
    user_template = load_prompt_template("user_prompt")
    user_prompt = user_template.format(
        markdown_content=markdown_content,
        instruction=instruction,
        **context
    )
    
    return system_prompt, user_prompt

# Legacy support - these are now generated dynamically
SYSTEM_PROMPT = load_prompt_template("system_prompt")
USER_PROMPT_TEMPLATE = load_prompt_template("user_prompt")