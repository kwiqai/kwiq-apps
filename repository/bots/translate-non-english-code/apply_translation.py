import json
import argparse


def update_file(file_path, updates):
    """
    Update the file at the given path based on the provided updates.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for update in updates:
        line_num = update['line']
        for item in update['items']:
            original_text = item['original_text']
            translated_text = item['translated_text']
            lines[line_num - 1] = lines[line_num - 1].replace(original_text, translated_text)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)


def apply_translations(map_file_path):
    """
    Apply translations from the map to the respective files.
    """
    with open(map_file_path, 'r', encoding='utf-8') as file:
        translation_map = json.load(file)

    for file_entry in translation_map:
        file_path = file_entry['file']
        updates = file_entry['map']
        update_file(file_path, updates)


def main(map_file_path):
    apply_translations(map_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Applies translation to the target files as per the map')
    parser.add_argument('map_path', type=str, help='Map file path')

    args = parser.parse_args()
    main(args.map_path)
