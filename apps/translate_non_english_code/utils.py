import re

# Regex for non-English characters (outside Basic Latin and Latin-1 Supplement)
ENGLISH_OR_TECHNICAL_PATTERN = r'^[A-Za-z0-9\s,.?!;:\'\"(){}[\]/\\@#$%^&*+=<>_`~|\u00B5①②③😊®©❤️│└├─-]+$'

# Supported file extensions and their comment/string patterns
LANG_PATTERNS = {
    '.sql': {
        'single_line_comment': [r'--.*?(?=\n|$)'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r"'[^'\n]*'"],
        'multi_line_string': []
    },
    '.json': {
        'single_line_comment': [],
        'multi_line_comment': [],
        'single_line_string': [r'"[^"\n]*"'],
        'multi_line_string': []
    },
    '.yaml': {
        'single_line_comment': [r'#.*?(?=\n|$)'],
        'multi_line_comment': [],
        'single_line_string': [r"'[^'\n]*'", r'"[^"\n]*"'],
        'multi_line_string': []
    },
    '.yml': {
        'single_line_comment': [r'#.*?(?=\n|$)'],
        'multi_line_comment': [],
        'single_line_string': [r"'[^'\n]*'", r'"[^"\n]*"'],
        'multi_line_string': []
    },
    '.ts': {
        'single_line_comment': [r'//.*?(?=\n|$)'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r"'[^'\n]*'", r'"[^"\n]*"', r'`[^`\n]*`'],
        'multi_line_string': []
    },
    '.tsx': {
        'single_line_comment': [r'//.*?(?=\n|$)'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r"'[^'\n]*'", r'"[^"\n]*"', r'`[^`\n]*`'],
        'multi_line_string': []
    },
    '.js': {
        'single_line_comment': [r'//.*?(?=\n|$)'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r"'[^'\n]*'", r'"[^"\n]*"', r'`[^`\n]*`'],
        'multi_line_string': []
    },
    '.css': {
        'single_line_comment': [],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [],
        'multi_line_string': []
    },
    '.go': {
        'single_line_comment': [r'//.*?(?=\n|$)'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r'"[^"\n]*"'],
        'multi_line_string': [r'`[^`\n]*`']
    },
    '.java': {
        'single_line_comment': [r'//.*?(?=\n|$)'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r'"[^"\n]*"'],
        'multi_line_string': []
    },
    '.rs': {
        'single_line_comment': [r'//.*?(?=\n|$)'],
        'multi_line_comment': [r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'],
        'single_line_string': [r'"[^"\n]*"'],
        'multi_line_string': [r'r#*"[^"]*"#']
    },
    '.c': {
        'single_line_comment': [r'//.*?(?=\n|$)'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r'"[^"\n]*"'],
        'multi_line_string': []
    },
    '.cpp': {
        'single_line_comment': [r'//.*?(?=\n|$)'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r'"[^"\n]*"'],
        'multi_line_string': []
    },
    '.proto': {
        'single_line_comment': [r'//.*?(?=\n|$)'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r'"[^"\n]*"'],  # Optional: Capture text within double quotes
        'multi_line_string': []
    },
    '.py': {
        'single_line_comment': [r'#.*?(?=\n|$)'],
        'multi_line_comment': [],
        'single_line_string': [r'"[^"\n]*"', r"'[^'\n]*'"],
        'multi_line_string': [r'""".*?"""', r"'''.*?'''"]
    }
}


def is_english_or_technical(text):
    return not text or text == "" or re.match(ENGLISH_OR_TECHNICAL_PATTERN, text) is not None


def replace_full_width_chars(text):
    # Mapping of full-width characters to their half-width equivalents
    replacements = {
        '，': ',',  # Full-width comma
        '：': ':',  # Full-width colon
        '；': ';',  # Full-width semicolon
        '。': '.',  # Full-width period
        '！': '!',  # Full-width exclamation mark
        '？': '?',  # Full-width question mark
        '（': '(',  # Full-width left parenthesis
        '）': ')',  # Full-width right parenthesis
        '【': '[',  # Full-width left square bracket
        '】': ']',  # Full-width right square bracket
        '《': '<',  # Full-width less than sign
        '》': '>',  # Full-width greater than sign
        '“': '"',  # Full-width double quote (left)
        '”': '"',  # Full-width double quote (right)
        '‘': "'",  # Full-width single quote (left)
        '’': "'",  # Full-width single quote (right)
        '－': '-',  # Full-width hyphen-minus
        '—': '-',  # Full-width em dash
        '–': '-',  # Full-width en dash
        '、': ',',  # asian comma
        '\u200B': '',  # non-breaking space
        '\u03BC': '\u00B5',  # mu symbol
        '\u00A0': ' ',  # Non-breaking space
        # '①': '(1)',
        # '②': '(2)',
        # '③': '(3)',

    }

    for full_width, half_width in replacements.items():
        text = text.replace(full_width, half_width)

    return text
