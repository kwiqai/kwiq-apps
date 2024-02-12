import configparser
import re

# Regex for non-English characters (outside Basic Latin and Latin-1 Supplement)
ENGLISH_OR_TECHNICAL_PATTERN = r'^[A-Za-z0-9\s,.?!;:\'\"(){}[\]/\\@#$%^&*+=<>_`~|\u00B5①②③😊®©❤️␍␊│└├─-]+$'

NON_ENGLISH_CHUNK = r'\b([\w]*?[^A-Za-z0-9\s,.?!;:\'\"(){}[\]/\\@#$%^&*+=<>_`~|\u00B5①②③😊®©❤️␍␊│└├─-]+[\w]*?)\b'

WHOLE_LINE_PATTERN = r'^(.*)$'

__SQL_COMMENT_PATTERN = r'--(.*?)$'
__SINGLE_LINE_COMMENT_PATTERN = r'/[/]+(.*?)$'
__PYTHON_COMMENT_PATTERN = r'[#]+(.*?)$'
__SINGLE_QUOTED_STRING_PATTERN = r"'(.*?)'"
__DOUBLE_QUOTED_STRING_PATTERN = r'"(.*?)"'
__TICK_QUOTED_STRING_PATTERN = r'`(.*?)`'

# THESE WOULD NEED A DIFFERENT STYLE OF PROCESSING... FOR NOW LET IT LINE BY LINE PROCESSING
__MULTILINE_COMMENT_PATTERN_1 = r'/\*(.*?)\*/'
__MULTILINE_COMMENT_PATTERN_2 = r'^[\s]*[*](.*?)$'
__SINGLE_QUOTE_DOCSTRING_PATTERN = r"'''(.*?)'''"
__DOUBLE_QUOTE_DOCSTRING_PATTERN = r'"""(.*?)"""'

# Supported file extensions and their comment/string patterns
LANG_PATTERNS = {
    '.sql': {
        'single_line_comment': [__SQL_COMMENT_PATTERN,
                                __MULTILINE_COMMENT_PATTERN_1,
                                __MULTILINE_COMMENT_PATTERN_2],
        'single_line_string': [__SINGLE_QUOTED_STRING_PATTERN],
    },
    '.json': {
        'single_line_comment': [],
        'single_line_string': [__DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.yaml': {
        'single_line_comment': [__PYTHON_COMMENT_PATTERN],
        'single_line_string': [__SINGLE_QUOTED_STRING_PATTERN,
                               __DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.yml': {
        'single_line_comment': [__PYTHON_COMMENT_PATTERN],
        'single_line_string': [__SINGLE_QUOTED_STRING_PATTERN,
                               __DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.ts': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN],
        'single_line_string': [__SINGLE_QUOTED_STRING_PATTERN,
                               __DOUBLE_QUOTED_STRING_PATTERN,
                               __TICK_QUOTED_STRING_PATTERN],
    },
    '.tsx': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN],
        'single_line_string': [__SINGLE_QUOTED_STRING_PATTERN,
                               __DOUBLE_QUOTED_STRING_PATTERN,
                               __TICK_QUOTED_STRING_PATTERN],
    },
    '.js': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN],
        'single_line_string': [__SINGLE_QUOTED_STRING_PATTERN,
                               __DOUBLE_QUOTED_STRING_PATTERN,
                               __TICK_QUOTED_STRING_PATTERN],
    },
    '.css': {
        'single_line_comment': [],
        'single_line_string': [],
    },
    '.go': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN],
        'single_line_string': [__DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.java': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN],
        'single_line_string': [__DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.rs': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN,
                                __MULTILINE_COMMENT_PATTERN_1,
                                __MULTILINE_COMMENT_PATTERN_2],
        'single_line_string': [__DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.h': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN,
                                __MULTILINE_COMMENT_PATTERN_1,
                                __MULTILINE_COMMENT_PATTERN_2],
        'single_line_string': [__DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.hpp': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN,
                                __MULTILINE_COMMENT_PATTERN_1,
                                __MULTILINE_COMMENT_PATTERN_2],
        'single_line_string': [__DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.c': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN,
                                __MULTILINE_COMMENT_PATTERN_1,
                                __MULTILINE_COMMENT_PATTERN_2],
        'single_line_string': [__DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.cpp': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN,
                                __MULTILINE_COMMENT_PATTERN_1,
                                __MULTILINE_COMMENT_PATTERN_2],
        'single_line_string': [__DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.proto': {
        'single_line_comment': [__SINGLE_LINE_COMMENT_PATTERN],
        'single_line_string': [__DOUBLE_QUOTED_STRING_PATTERN],
    },
    '.py': {
        'single_line_comment': [__PYTHON_COMMENT_PATTERN,
                                __SINGLE_QUOTE_DOCSTRING_PATTERN,
                                __DOUBLE_QUOTE_DOCSTRING_PATTERN],
        'single_line_string': [__SINGLE_QUOTED_STRING_PATTERN,
                               __DOUBLE_QUOTED_STRING_PATTERN],
    }
}


def is_english_or_technical(text):
    return not text or text == "" or re.match(ENGLISH_OR_TECHNICAL_PATTERN, text) is not None


def find_non_english_chunks(text):
    chunks = set()
    for match in re.finditer(NON_ENGLISH_CHUNK, text, re.DOTALL):
        chunks.add(match.group(1))

    return list(chunks)


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
    }

    for full_width, half_width in replacements.items():
        text = text.replace(full_width, half_width)

    return text
