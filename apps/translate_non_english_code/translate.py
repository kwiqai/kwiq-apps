from pathlib import Path
from typing import Any, Optional

import yaml

from kwiq.core.flow import Flow
from kwiq.task.google_translate import GoogleTranslate


class Translate(Flow):
    name: str = "translate"

    def fn(self, input_path: Path, output_path: Path, translation_cache_path: Optional[Path]) -> Any:
        google_translator = GoogleTranslate(translation_cache_path=translation_cache_path)

        # Load the original map
        with open(input_path, 'r', encoding='utf-8') as file:
            input_map = yaml.full_load(file)

        output_map = []
        # Load the translated map
        for i, file_entry in enumerate(input_map):
            output_map_entries = []
            for j, input_entry in enumerate(file_entry['map']):
                if 'translation_input' in input_entry and input_entry['translation_input']:
                    translation_input = input_entry['translation_input']
                    translated_text = google_translator.execute(text=translation_input)
                    if translated_text is not None:
                        input_entry['translated_text'] = translated_text

                    if 'chunks' in input_entry and input_entry['chunks']:
                        chunks = input_entry['chunks']
                        output_chunks = []
                        for chunk in chunks:
                            translated_chunk = google_translator.execute(text=chunk)
                            if translated_chunk is not None:
                                output_chunks.append({
                                    'original': chunk,
                                    'translated': translated_chunk
                                })

                        input_entry['chunks'] = output_chunks

                output_map_entries.append(input_entry)

            output_map.append({
                "file": file_entry["file"],
                "map": output_map_entries
            })

        with open(output_path, 'w+', encoding='utf-8') as output_file:
            yaml.dump(output_map, output_file, allow_unicode=True, default_style='', default_flow_style=False)

        google_translator.close()
        print(f"Successfully translated input and written output to: {output_path}")
