import os
import re
from pathlib import Path
from typing import Any

import yaml

from kwiq.core.flow import Flow
from kwiq.task.gitignore_matcher import GitIgnoreMatcher
from translate_non_english_code.utils import replace_full_width_chars, is_english_or_technical, LANG_PATTERNS, \
    WHOLE_LINE_PATTERN, find_non_english_chunks

# 'multi_line_comment', 'multi_line_string',
PATTERN_CHECK_SEQUENCE = ['single_line_comment', 'single_line_string']
MARKDOWN_FILE_EXTENSIONS = [".md"]
TEXT_FILE_EXTENSIONS = [".text", ".txt"]


# Process files for non-English text.
class PrepareForTranslation(Flow):
    name: str = "prepare-translation"

    def fn(self, search_directory: Path, output_file: Path) -> Any:
        project_map = []
        gitignore_matcher = GitIgnoreMatcher(base_dir=search_directory)

        """Process files in the directory, ignoring those that match .gitignore patterns."""
        for root, dirs, files in os.walk(search_directory):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not d.startswith('.')
                       and not gitignore_matcher.execute(file_path=os.path.join(root, d))]

            for file in files:
                file_path = os.path.join(root, file)
                if not file.startswith('.') and not gitignore_matcher.execute(file_path=file_path):
                    # Process file
                    file_ext = os.path.splitext(file)[1]
                    file_path = os.path.join(root, file)
                    file_map = None
                    if file_ext in LANG_PATTERNS:
                        print(f"Processing file: {file_path}")
                        patterns = LANG_PATTERNS[file_ext]
                        file_map = PrepareForTranslation.process_file(file_path, patterns)
                    elif file_ext in MARKDOWN_FILE_EXTENSIONS:
                        print(f"Processing markdown file: {file_path}")
                        file_map = PrepareForTranslation.process_markdown_file(file_path)
                    elif file_ext in TEXT_FILE_EXTENSIONS:
                        print(f"Processing text file: {file_path}")
                        file_map = PrepareForTranslation.process_text_file(file_path)

                    if file_map:
                        project_map.append({'file': file_path, 'map': file_map})

        # Write the map to a file in JSON format
        with open(output_file, 'w', encoding='utf-8') as map_file:
            yaml.dump(project_map, map_file, allow_unicode=True, default_style='')

    @classmethod
    def aggregate_data(cls, data):
        aggregated_map = {}
        for entry in data:
            original_text = entry['original_text']
            position = entry.get('position')

            if original_text not in aggregated_map:
                aggregated_map[original_text] = {
                    'original_text': original_text,
                    'positions': []
                }

                # Conditionally add fields if they are not None
                if entry.get('translation_input') is not None:
                    aggregated_map[original_text]['translation_input'] = entry['translation_input']
                    aggregated_map[original_text]['chunks'] = entry['chunks']
                if entry.get('translated_text') is not None:
                    aggregated_map[original_text]['translated_text'] = entry['translated_text']

            if position is not None:
                aggregated_map[original_text]['positions'].append(position)

        return list(aggregated_map.values())

    @classmethod
    def process_regular_text(cls, line_number, text):
        non_english_map_entry = None
        original_text = text
        processed_text = replace_full_width_chars(text)

        if not is_english_or_technical(processed_text):
            non_english_map_entry = {
                'position': line_number,
                'original_text': original_text,
                'translation_input': processed_text,
                'chunks': find_non_english_chunks(processed_text),
            }
        elif text != processed_text:
            non_english_map_entry = {
                'position': line_number,
                'original_text': original_text,
                'translated_text': processed_text
            }

        return non_english_map_entry

    @classmethod
    def process_markdown_line(cls, line_number, text, non_english_map):
        while text:
            # Find the first URL portion
            url_match = re.search(r'\[([^]]+)]\(([^)]+)\)', text)

            if url_match:
                # Process text before URL
                before_url = text[:url_match.start()]
                if before_url.strip():
                    result = PrepareForTranslation.process_regular_text(line_number, before_url.strip())
                    if result:
                        non_english_map.append(result)

                # Process URL title
                url_title = url_match.group(1)
                result = PrepareForTranslation.process_regular_text(line_number, url_title)
                if result:
                    non_english_map.append(result)

                # Update the remaining_line to start after the URL
                text = text[url_match.end():]
            else:
                # Process the remaining non-URL portion
                if text.strip():
                    result = PrepareForTranslation.process_regular_text(line_number, text.strip())
                    if result:
                        non_english_map.append(result)
                break

    @classmethod
    def process_markdown_file(cls, file_path):
        non_english_map = []

        with open(file_path, 'r', encoding='utf-8') as file:
            line_number = 0
            for line in file:
                line_number += 1
                stripped_line = line.strip()

                if '|' in stripped_line:  # Check for table row
                    columns = [col.strip() for col in stripped_line.split('|')]
                    for col in columns:
                        PrepareForTranslation.process_markdown_line(line_number, col, non_english_map)
                else:
                    PrepareForTranslation.process_markdown_line(line_number, stripped_line, non_english_map)

        return PrepareForTranslation.aggregate_data(non_english_map)

    @classmethod
    def process_text_file(cls, file_path):
        non_english_map = []

        with open(file_path, 'r', encoding='utf-8') as file:
            line_number = 0
            for line in file:
                line_number += 1
                stripped_line = line.strip()

                result = PrepareForTranslation.process_regular_text(line_number, stripped_line)
                if result:
                    non_english_map.append(result)

        return PrepareForTranslation.aggregate_data(non_english_map)

    @classmethod
    def process_file(cls, file_path, patterns):
        non_english_map = []

        with open(file_path, 'r', encoding='utf-8') as file:
            line_number = 0
            for content in file:
                line_number += 1
                for pattern_type in PATTERN_CHECK_SEQUENCE:
                    for pattern in patterns.get(pattern_type, []):
                        while True:
                            content, match = cls.match_pattern_for_code_file(content,
                                                                             line_number,
                                                                             non_english_map,
                                                                             pattern)
                            if not match:
                                break

                # match the whole line as a fallback
                cls.match_pattern_for_code_file(content, line_number, non_english_map, WHOLE_LINE_PATTERN)

        return PrepareForTranslation.aggregate_data(non_english_map)

    @classmethod
    def match_pattern_for_code_file(cls, content, line_number, non_english_map, pattern):
        match = re.search(pattern, content, re.DOTALL)
        if match:
            matched_content = match.group(1)
            # print("Matched pattern: ", pattern, matched_content)
            stripped_line = matched_content.strip()
            lines_without_full_width_chars = replace_full_width_chars(stripped_line)
            if lines_without_full_width_chars and not is_english_or_technical(
                    lines_without_full_width_chars):
                non_english_map.append(
                    {
                        'position': line_number,
                        'original_text': stripped_line,
                        'translation_input': lines_without_full_width_chars,
                        'chunks': find_non_english_chunks(lines_without_full_width_chars),
                    })
            elif stripped_line != lines_without_full_width_chars:
                non_english_map.append({
                    'position': line_number,
                    'original_text': stripped_line,
                    'translated_text': lines_without_full_width_chars
                })

            # Replace matched text with spaces, preserving newline characters
            content = content[:match.start()] + '' + content[match.end():]

        return content, match
