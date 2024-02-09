import json
from pathlib import Path
from typing import Any

from kwiq.core.flow import Flow
from kwiq.task.google_translate import GoogleTranslate
from kwiq.task.json_formatter import JsonFormatter


class Translate(Flow):
    name: str = "translate"

    def fn(self, input_map_path: Path, translated_map_path: Path) -> Any:
        google_translator = GoogleTranslate()

        # Load the original map
        with open(input_map_path, 'r', encoding='utf-8') as file:
            input_map = json.load(file)

        # Open the error log file
        with open(translated_map_path, 'w+', encoding='utf-8') as output_file:
            output_file.truncate()
            output_file.write('[')  # Start of JSON array

            # Load the translated map
            for i, file_entry in enumerate(input_map):
                if i > 0:
                    output_file.write(',')  # Separate JSON objects in the array

                # Dump the file entry
                json.dump({"file": file_entry["file"], "map": []}, output_file, indent=None, ensure_ascii=False)
                output_file.flush()  # Flush to write to file immediately

                for j, input_entry in enumerate(file_entry['map']):
                    if 'translated_text' in input_entry and input_entry['translated_text']:
                        translated_text = input_entry['translated_text']
                    elif 'translation_input' in input_entry and input_entry['translation_input']:
                        translation_input = input_entry['translation_input']
                        translated_text = google_translator.execute(text=translation_input)

                    input_entry['translated_text'] = translated_text
                    output_file.seek(0, 2)  # Go to the end of the file
                    end_position = output_file.tell()  # Get the position at the end
                    position_second_to_last = end_position - 2  # Calculate the position two characters before the end
                    output_file.seek(position_second_to_last, 0)  # Seek to that position
                    output_file.truncate()  # Remove the last character (']')
                    if j > 0:
                        output_file.write(',')  # Separate JSON objects in the array
                    json.dump(input_entry, output_file, indent=None, ensure_ascii=False)  # Dump the updated file entry
                    output_file.write(']}')  # End of JSON array
                    output_file.flush()  # Flush to write to file immediately

            output_file.write(']')  # Close the JSON array

        JsonFormatter().execute(input_file_path=translated_map_path)
