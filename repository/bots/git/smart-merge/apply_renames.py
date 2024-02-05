import re
from pathlib import Path

from pydantic import BaseModel

from workflow.csv_iterator import CSVIteratorBuilder
from workflow.file_iterator import FileIteratorBuilder
from workflow.step import Step, InputModelType, OutputModelType


class MappingData(BaseModel):
    original_word: str
    renamed_word: str


def apply_renames(search_directory: Path, mapping_csv_path: Path):
    # Read the mapping from CSV file
    mappings = []
    csv_iterator = (CSVIteratorBuilder()
                    .with_data_model(MappingData)
                    .with_file_path(mapping_csv_path)
                    .build())

    for row in csv_iterator:
        mappings.append(row)

    def apply_mapping(filepath: str):
        try:
            changed = False
            with open(filepath, 'r') as file:
                content = file.read()

            for mapping in mappings:
                pattern = re.compile(r'\b' + re.escape(mapping.original_word) + r'\b')

                def replacement(match, renamed_word=mapping.renamed_word):
                    nonlocal changed
                    changed = True
                    return renamed_word

                content = pattern.sub(replacement, content)

            if changed:
                with open(filepath, 'w') as file:
                    print(f"Writing file: {filepath}")
                    file.write(content)
        except UnicodeDecodeError:
            # skip
            return

    (FileIteratorBuilder()
     .with_directory(search_directory)
     .with_fn(apply_mapping)
     .build()).iterate_files()


class InputModel(BaseModel):
    mapping_csv_path: Path
    search_directory: Path


class ApplyRenames(Step):
    name: str = "apply-renames"

    @property
    def input_model(self) -> InputModelType:
        return InputModel

    @property
    def output_model(self) -> OutputModelType:
        return None

    def fn(self, data: InputModel) -> None:
        apply_renames(data.search_directory, data.mapping_csv_path)
