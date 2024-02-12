import shutil
import tempfile
from pathlib import Path
from typing import Any

import yaml

from kwiq.core.flow import Flow


# Applies translation to the target files as per the map
class ApplyTranslation(Flow):
    name: str = "apply-translation"

    def fn(self, map_file_path: Path) -> Any:
        """
        Apply translations from the map to the respective files.
        """
        with open(map_file_path, 'r', encoding='utf-8') as file:
            translation_map = yaml.full_load(file)

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
        with (open(file_path, 'r', encoding='utf-8') as file,
              tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file):
            print(f"----> Writing applied translation to: {temp_file.name}")

            line_number = 0
            for content in file:
                line_number += 1

                for update in updates:
                    positions = set(update['positions'])
                    if positions is None or len(positions) == 0:
                        continue

                    if line_number not in positions:
                        continue

                    original_text = update['original_text']
                    translated_text = update['translated_text']

                    # Replace all the occurrence of the original text
                    content = content.replace(original_text, translated_text)
                    if 'chunks' in update and update['chunks']:
                        for chunk in update['chunks']:
                            original_chunk = chunk['original']
                            translated_chunk = chunk['translated']
                            content = content.replace(original_chunk, translated_chunk)

                print(content, file=temp_file, end='')

        shutil.move(temp_file.name, file_path)
        print(f"----> Successfully moved {temp_file.name} to {file_path}")
