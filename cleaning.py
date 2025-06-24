import re

def clean_markdown(gpt_output: str) -> str:
    """
    Clean GPT-4 output to ensure proper markdown formatting.
    
    Args:
        gpt_output: Raw output from GPT-4
        
    Returns:
        Cleaned markdown content
    """
    
    if not gpt_output:
        return ""
    
    content = gpt_output.strip()
    
    # Remove markdown code fences if GPT added them
    if content.startswith('```') and content.endswith('```'):
        # Remove opening fence
        lines = content.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        
        # Remove closing fence
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        
        content = '\n'.join(lines)
    
    # Remove any leading/trailing markdown indicators
    content = re.sub(r'^```\w*\n?', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n?```$', '', content, flags=re.MULTILINE)
    
    # Clean up extra whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 consecutive newlines
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)  # Remove trailing spaces
    
    # Ensure file ends with single newline
    content = content.rstrip() + '\n'
    
    return content

def validate_markdown_structure(content: str) -> bool:
    """
    Basic validation to ensure the content looks like valid markdown.
    
    Args:
        content: Markdown content to validate
        
    Returns:
        True if content appears to be valid markdown
    """
    
    if not content.strip():
        return False
    
    # Check for obvious non-markdown artifacts
    invalid_patterns = [
        r'```markdown',  # Code fence with markdown indicator
        r'Here is the modified',  # GPT explanation text
        r'I have modified',  # GPT explanation text
        r'The updated file',  # GPT explanation text
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False
    
    return True

def extract_markdown_from_response(response: str) -> str:
    """
    Extract markdown content from GPT response, handling various response formats.
    
    Args:
        response: Full GPT response
        
    Returns:
        Extracted markdown content
    """
    
    # First, try basic cleaning
    cleaned = clean_markdown(response)
    
    # If validation passes, return cleaned content
    if validate_markdown_structure(cleaned):
        return cleaned
    
    # Try to extract markdown from code blocks
    code_block_pattern = r'```(?:markdown)?\n(.*?)\n```'
    matches = re.findall(code_block_pattern, response, re.DOTALL | re.IGNORECASE)
    
    if matches:
        # Use the first code block found
        return clean_markdown(matches[0])
    
    # If all else fails, return the original cleaned response
    return cleaned