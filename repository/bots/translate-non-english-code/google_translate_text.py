import json
import argparse
import html
from google.cloud import translate
from os import environ
import sys

GOOGLE_PROJECT_ID = environ.get("GOOGLE_PROJECT_ID", "")
assert GOOGLE_PROJECT_ID
PARENT = f"projects/{GOOGLE_PROJECT_ID}"


def translate_text(text: str, target_language_code: str) -> translate.Translation:
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        parent=PARENT,
        contents=[text],
        target_language_code=target_language_code,
    )

    return response.translations[0]


def translate_maps(input_map_path, translated_map_path):
    # Load the original map
    with open(input_map_path, 'r', encoding='utf-8') as file:
        input_map = json.load(file)

    # Load the translated map
    for file_entry in input_map:
        for input_entry in file_entry['map']:
            original_text = input_entry['text']
            input_entry['original_text'] = original_text
            print(f"Translating: {original_text}")

            try:
                translation = translate_text(original_text, 'en')
                translated_text = html.unescape(translation.translated_text)

                print(f"→→→ Got translation: {translated_text}")
                input_entry['translated_text'] = translated_text
            except Exception as err:
                print(f"→→→ Got error in translation: {err}", file=sys.stderr)
                input_entry['translated_text'] = "<ERROR>"

    # Save the merged map
    with open(translated_map_path, 'w', encoding='utf-8') as file:
        json.dump(input_map, file, indent=4, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Translates.')
    parser.add_argument('input_map_path', type=str, help='Path to the input map file')
    parser.add_argument('translated_map_path', type=str, help='Path to the translated map file')

    args = parser.parse_args()
    translate_maps(args.input_map_path, args.translated_map_path)


if __name__ == '__main__':
    main()
