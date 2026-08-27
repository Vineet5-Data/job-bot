import re

def escape_latex(text: str) -> str:
    """Escapes special characters for plain text fields, preventing double-escaping."""
    if not text:
        return ""
    
    # Unescape first to prevent double-escaping if LLM already did it
    text = text.replace(r'\&', '&').replace(r'\%', '%').replace(r'\$', '$').replace(r'\#', '#').replace(r'\_', '_')
    
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}'
    }
    
    sanitized = ""
    for char in text:
        sanitized += replacements.get(char, char)
        
    return sanitized
