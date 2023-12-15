import json
import argparse


def merge_maps(original_map_path, translated_map_path, merged_map_path):
    # Load the original map
    with open(original_map_path, 'r', encoding='utf-8') as file:
        original_map = json.load(file)

    # Load the translated map
    with open(translated_map_path, 'r', encoding='utf-8') as file:
        translated_map = json.load(file)

    # Merge the maps
    for file_entry_original, file_entry_translated in zip(original_map, translated_map):
        for line_entry_original, line_entry_translated in zip(file_entry_original['map'], file_entry_translated['map']):
            for item_original, item_translated in zip(line_entry_original['items'], line_entry_translated['items']):
                item_translated['original_text'] = item_original['text']
                item_translated['translated_text'] = item_translated.pop('text')

    # Save the merged map
    with open(merged_map_path, 'w', encoding='utf-8') as file:
        json.dump(translated_map, file, indent=4, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Merge original and translated text maps.')
    parser.add_argument('original_map_path', type=str, help='Path to the original map file')
    parser.add_argument('translated_map_path', type=str, help='Path to the translated map file')
    parser.add_argument('merged_map_path', type=str, help='Path for the new merged map file')

    args = parser.parse_args()
    merge_maps(args.original_map_path, args.translated_map_path, args.merged_map_path)


if __name__ == '__main__':
    main()
