from pathlib import Path

from pydantic import BaseModel

from workflow import utils
from workflow.file_iterator import FileIteratorBuilder
from workflow.step import Step, InputModelType, OutputModelType


def extract_words(words_regex: str, search_directory: Path) -> set[str]:
    words = set()
    pattern = utils.word_pattern(words_regex)

    def extract_pattern(filepath: str):
        with open(filepath, 'r') as file:
            try:
                content = file.read()
                matches = pattern.findall(content)
                words.update(matches)
            except UnicodeDecodeError:
                # skip
                return

    (FileIteratorBuilder()
     .with_directory(search_directory)
     .with_fn(extract_pattern)
     .build()).iterate_files()

    return words


class InputModel(BaseModel):
    words_regex: str
    search_directory: Path


class ExtractWords(Step):

    @property
    def input_model(self) -> InputModelType:
        return InputModel

    @property
    def output_model(self) -> OutputModelType:
        return set[str]

    def fn(self, data: InputModel) -> set[str]:
        return extract_words(data.words_regex, data.search_directory)
