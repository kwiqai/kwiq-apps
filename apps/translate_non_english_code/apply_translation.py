import json
from pathlib import Path
from typing import Any

from kwiq.core.flow import Flow


# Applies translation to the target files as per the map
class ApplyTranslation(Flow):

    name: str = "apply-translation"

    def fn(self, map_file_path: Path) -> Any:
        """
        Apply translations from the map to the respective files.
        """
        with open(map_file_path, 'r', encoding='utf-8') as file:
            translation_map = json.load(file)

        for file_entry in translation_map:
            file_path = file_entry['file']
            print(f"Applying translation for: {file_path}")
            updates = file_entry['map']
            ApplyTranslation.update_file(file_path, updates)

    @classmethod
    def update_file(cls, file_path, updates):
        """
        Update the file at the given path based on the provided updates.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Sort updates in reverse order of start_pos to avoid offset issues
        # updates.sort(key=lambda x: x['start_pos'], reverse=True)

        for update in updates:
            original_text = update['original_text']
            translated_text = update['translated_text']

            # Replace only the first occurrence of the original text
            content = content.replace(original_text, translated_text, 1)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
