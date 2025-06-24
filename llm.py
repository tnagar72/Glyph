import os
from openai import OpenAI
from prompts import create_dynamic_prompts
from utils import verbose_print

def call_gpt_api(markdown_content: str, instruction: str, filename: str = "unknown") -> str:
    """
    Calls GPT-4 to modify markdown content based on user instruction.
    
    Args:
        markdown_content: Current markdown file content
        instruction: User's voice-transcribed instruction
        filename: Name of the file being edited
        
    Returns:
        Modified markdown content from GPT-4
    """
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    if not client.api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Create dynamic prompts with context analysis
    system_prompt, user_prompt = create_dynamic_prompts(markdown_content, instruction, filename)
    
    try:
        verbose_print(f"Sending request to GPT-4 (model: gpt-4, temperature: 0.1)")
        verbose_print(f"Input content length: {len(markdown_content)} characters")
        verbose_print(f"Instruction: {instruction}")
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent editing
            max_tokens=4000   # Adjust based on your typical file sizes
        )
        
        modified_content = response.choices[0].message.content.strip()
        verbose_print(f"GPT-4 response length: {len(modified_content)} characters")
        verbose_print("GPT-4 processing completed successfully")
        
        return modified_content
        
    except Exception as e:
        verbose_print(f"GPT-4 API error: {e}")
        # Let the calling function handle the error display with Rich
        raise Exception(f"GPT-4 API error: {e}")