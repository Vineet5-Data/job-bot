import re

def escape_latex(text: str) -> str:
    """Escapes special characters for plain text fields, preventing double-escaping."""
    if not text:
        return ""
    
    # Unescape first to prevent double-escaping if LLM already did it
    text = text.replace(r'\&', '&').replace(r'\%', '%').replace(r'\$', '$').replace(r'\#', '#').replace(r'\_', '_')
    
    replacements = {
        # A stray backslash in LLM output or in master_profile.json is a live
        # LaTeX command, not text: "O(n \log n)" compiles as math-only \log and
        # kills the build. Neutralise it here rather than trusting the source.
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}'
    }

    # Reads the ORIGINAL text char by char, so replacement output is never
    # rescanned and the backslashes it introduces stay intact.
    sanitized = ""
    for char in text:
        sanitized += replacements.get(char, char)

    return sanitized
