import json
import os
import re
import argparse
from gitignore_parser import parse_gitignore

# Regex for non-English characters (outside Basic Latin and Latin-1 Supplement)
ENGLISH_OR_TECHNICAL_PATTERN = r'^[A-Za-z0-9\s,.?!;:\'\"(){}[\]/\\@#$%^&*+=<>_`~|-]+$'

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
    '.md': {
        'single_line_comment': [],
        'multi_line_comment': [r'<!--.*?-->'],
        'single_line_string': [],
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
    '.py': {
        'single_line_comment': [r'#.*?(?=\n|$)'],
        'multi_line_comment': [],
        'single_line_string': [r'"[^"\n]*"', r"'[^'\n]*'"],
        'multi_line_string': [r'""".*?"""', r"'''.*?'''"]
    }
}


def is_english_or_technical(text):
    return re.match(ENGLISH_OR_TECHNICAL_PATTERN, text) is not None


PATTERN_CHECK_SEQUENCE = ['multi_line_comment', 'single_line_comment', 'multi_line_string', 'single_line_string']


def process_file(file_path, patterns):
    non_english_map = []

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    for pattern_type in PATTERN_CHECK_SEQUENCE:
        for pattern in patterns.get(pattern_type, []):
            while True:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    matched_text = match.group().strip()
                    if matched_text and not is_english_or_technical(matched_text):
                        non_english_map.append(
                            {
                                'start_pos': match.start(),
                                'end_pos': match.end(),
                                'type': pattern_type,
                                'text': matched_text
                            })

                    # Replace matched text with spaces, preserving newline characters
                    replacement_text = ''.join([' ' if c != '\n' else '\n' for c in match.group()])
                    content = content[:match.start()] + replacement_text + content[match.end():]

                else:
                    break

    return non_english_map


def process_directory(root_dir, output_file):
    project_map = []
    gitignore_path = os.path.join(root_dir, '.gitignore')
    gitignore_matches = parse_gitignore(gitignore_path)

    """Process files in the directory, ignoring those that match .gitignore patterns."""
    for root, dirs, files in os.walk(root_dir):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and not gitignore_matches(os.path.join(root, d))]

        for file in files:
            file_path = os.path.join(root, file)
            if not file.startswith('.') and not gitignore_matches(file_path):
                # Process file
                file_ext = os.path.splitext(file)[1]
                if file_ext in LANG_PATTERNS:
                    print(f"Processing file: {file_path}")
                    file_path = os.path.join(root, file)
                    patterns = LANG_PATTERNS[file_ext]
                    file_map = process_file(file_path, patterns)
                    if file_map:
                        project_map.append({'file': file_path, 'map': file_map})

    # Write the map to a file in JSON format
    with open(output_file, 'w', encoding='utf-8') as map_file:
        json.dump(project_map, map_file, indent=4, ensure_ascii=False)


def main(input_path, output_file):
    process_directory(input_path, output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process files for non-English text.')
    parser.add_argument('input_path', type=str, help='Input file path')
    parser.add_argument('output_file', type=str, help='Output file name')

    args = parser.parse_args()
    main(args.input_path, args.output_file)
