import json
import os
import re
import argparse

# SQL file extension
EXTENSIONS = ['.sql']

# Regex for non-English characters (outside Basic Latin and Latin-1 Supplement)
ENGLISH_OR_TECHNICAL_PATTERN = r'^[A-Za-z0-9\s,.?!;:\'\"(){}[\]/\\@#$%^&*+=<>_`~|-]+$'

# Supported file extensions and their comment/string patterns
LANG_PATTERNS = {
    '.sql': {
        'single_line_comment': [r'--.*?$'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r"'([^']*)'"],
        'multi_line_string': []
    },
    '.json': {
        'single_line_comment': [],
        'multi_line_comment': [],
        'single_line_string': [r'"([^"]*)"'],
        'multi_line_string': []
    },
    '.yml': {
        'single_line_comment': [r'#.*'],
        'multi_line_comment': [],
        'single_line_string': [r"'([^']*)'", r'"([^"]*)"'],
        'multi_line_string': []
    },
    '.ts': {
        'single_line_comment': [r'//.*?$'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r"'([^']*)'", r'"([^"]*)"', r'`([^`]*)`'],
        'multi_line_string': []
    },
    '.tsx': {
        'single_line_comment': [r'//.*?$'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r"'([^']*)'", r'"([^"]*)"', r'`([^`]*)`'],
        'multi_line_string': []
    },
    '.js': {
        'single_line_comment': [r'//.*?$'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r"'([^']*)'", r'"([^"]*)"', r'`([^`]*)`'],
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
        'single_line_comment': [r'//.*?$'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r'"([^"]*)"'],
        'multi_line_string': [r'`([^`]*)`']  # Raw string literals in Go
    },
    '.java': {
        'single_line_comment': [r'//.*?$'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r'"([^"]*)"'],
        'multi_line_string': []
    },
    '.rs': {
        'single_line_comment': [r'//.*?$'],
        'multi_line_comment': [r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'],  # Nested comments support
        'single_line_string': [r'"([^"]*)"'],
        'multi_line_string': [r'r#*"([^"]*)"#']  # Raw string literals in Rust
    },
    '.c': {
        'single_line_comment': [r'//.*?$'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r'"([^"]*)"'],
        'multi_line_string': []
    },
    '.cpp': {
        'single_line_comment': [r'//.*?$'],
        'multi_line_comment': [r'/\*.*?\*/'],
        'single_line_string': [r'"([^"]*)"'],
        'multi_line_string': []
    },
    '.py': {
        'single_line_comment': [r'#.*'],
        'multi_line_comment': [],  # Python uses multi-line strings as multi-line comments
        'single_line_string': [r'"([^"]*)"', r"'([^']*)'"],
        'multi_line_string': [r'"""(.*?)"""', r"'''(.*?)'''"]
    }
}


def is_english_or_technical(text):
    return re.match(ENGLISH_OR_TECHNICAL_PATTERN, text) is not None


PATTERN_CHECK_SEQUENCE = ['multi_line_comment', 'multi_line_string', 'single_line_comment', 'single_line_string']


def find_non_english_in_line(line, patterns):
    results = []

    for check_sequence in PATTERN_CHECK_SEQUENCE:
        for pattern in patterns.get(check_sequence, []):
            matches = re.findall(pattern, line, re.DOTALL)
            for match in matches:
                if match.strip() and not is_english_or_technical(match):
                    results.append({'type': check_sequence, 'text': match})
                    break

    # # Check for multi-line comments or strings
    # for pattern in patterns.get('multi_line_comment', []) + patterns.get('multi_line_string', []):
    #     matches = re.findall(pattern, line, re.DOTALL)
    #     for match in matches:
    #         if match.strip() and not is_english_or_technical(match):
    #             results.append({'type': 'multi-line', 'text': match})
    #
    # # Check for single-line comments or strings
    # for pattern in patterns.get('single_line_comment', []) + patterns.get('single_line_string', []):
    #     matches = re.findall(pattern, line)
    #     for match in matches:
    #         if match.strip() and not is_english_or_technical(match):
    #             results.append({'type': 'single-line', 'text': match})

    return results


def process_file(file_path, patterns):
    non_english_map = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, 1):
            non_english_items = find_non_english_in_line(line, patterns)
            if non_english_items:
                non_english_map.append({'line': line_number, 'items': non_english_items})
    return non_english_map


def main(input_path, output_file):
    project_map = []

    for root, dirs, files in os.walk(input_path):
        for file in files:
            file_ext = os.path.splitext(file)[1]
            if file_ext in LANG_PATTERNS:
                file_path = os.path.join(root, file)
                patterns = LANG_PATTERNS[file_ext]
                file_map = process_file(file_path, patterns)
                if file_map:
                    project_map.append({'file': file_path, 'map': file_map})

    # Write the map to a file in JSON format
    with open(output_file, 'w', encoding='utf-8') as map_file:
        json.dump(project_map, map_file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process files for non-English text.')
    parser.add_argument('input_path', type=str, help='Input file path')
    parser.add_argument('output_file', type=str, help='Output file name')

    args = parser.parse_args()
    main(args.input_path, args.output_file)
