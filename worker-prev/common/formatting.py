import re

def remove_think_tags(text):
    """
    Remove all occurrences of text within <think>...</think> (including the tags) from the provided text.
    
    Args:
        text (str): The input string that may contain <think> tags.
    
    Returns:
        str: The text with all <think>...</think> sections removed.
    """
    # Use re.sub with DOTALL flag to capture newlines within the <think> blocks.
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned_text
def remove_json_markdown(text):
    """
    Remove markdown code fences (like ```json ... ```) from the input text.
    
    Args:
        text (str): The text that may include markdown code fences.
        
    Returns:
        str: The text with markdown code fences removed.
    """
    # Use regex to remove any markdown code fence that might wrap the JSON.
    # This pattern removes the leading "```json" or "```", and the trailing "```".
    pattern = r"^```(?:json)?\s*(.*?)\s*```$"
    match = re.search(pattern, text.strip(), flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    
    return text.strip()