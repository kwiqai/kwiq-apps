import json
import os
import re
import argparse

# SQL file extension
EXTENSIONS = ['.sql']

# Regex for non-English characters (outside Basic Latin and Latin-1 Supplement)
# NON_ENGLISH_PATTERN = r'[^\u0000-\u007F]+'
ENGLISH_OR_TECHNICAL_PATTERN = r'^[A-Za-z0-9\s,.?!;:\'\"(){}[\]/\\@#$%^&*+=<>_`~|-]+$'

# Regex patterns for SQL comments and string literals
COMMENT_PATTERN = r'--.*?$|/\*.*?\*/'
STRING_LITERAL_PATTERN = r"'([^']*)'"


def is_english_or_technical(text):
    return re.match(ENGLISH_OR_TECHNICAL_PATTERN, text) is not None


def find_non_english_in_line(line):
    results = []

    # Check for comments
    comments = re.findall(COMMENT_PATTERN, line, re.DOTALL)
    for comment in comments:
        if comment.strip() and not is_english_or_technical(comment):
            results.append({'type': 'comment', 'text': comment})

    # Check for string literals
    string_literals = re.findall(STRING_LITERAL_PATTERN, line)
    for string_literal in string_literals:
        if string_literal.strip() and not is_english_or_technical(string_literal):
            results.append({'type': 'literal', 'text': string_literal})

    return results


def process_file(file_path):
    non_english_map = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, 1):
            non_english_items = find_non_english_in_line(line)
            if non_english_items:
                non_english_map.append({'line': line_number, 'items': non_english_items})
    return non_english_map


def main(input_path, output_file):
    project_map = []

    for root, dirs, files in os.walk(input_path):
        for file in files:
            if any(file.endswith(ext) for ext in EXTENSIONS):
                file_path = os.path.join(root, file)
                file_map = process_file(file_path)
                if file_map:
                    project_map.append({'file': file_path, 'map': file_map})

    # Write the map to a file in JSON format
    with open(output_file, 'w', encoding='utf-8') as map_file:
        json.dump(project_map, map_file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process SQL files for non-English text.')
    parser.add_argument('input_path', type=str, help='Input file path')
    parser.add_argument('output_file', type=str, help='Output file name')

    args = parser.parse_args()
    main(args.input_path, args.output_file)
