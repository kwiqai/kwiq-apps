import os
from typing import List

from kwiq.core.flow import Flow
from kwiq.task import apply_renames
from kwiq.task.csv_writer import write_data_to_csv
from kwiq.task.extract_words import ExtractWords
from kwiq.task.run_command import RunCommand

from smart_code_merge.commons import AppConfig


class PrepareTransformation(Flow):
    name: str = "prepare-transformation"

    def fn(self, config: AppConfig) -> None:
        working_dir = config.working_dir

        # for each project
        #   step 2: checkout remote
        #   step 3: extract words for rename
        unique_words = set()
        for project in config.projects:
            project_directory = (working_dir / f"__{project.key}" / "merge_dir").resolve()
            os.chdir(project_directory)
            # RunCommand().execute(command="git checkout local")
            words = ExtractWords().execute(words_regex=config.rename_words_regex, search_directory=project_directory)
            unique_words = unique_words.union(words)

        mapping_file = (working_dir / "input_mapping.csv")

        mapping_list: List[apply_renames.MappingData] = [
            apply_renames.MappingData(original_word=word, renamed_word=word)
            for word
            in unique_words]

        write_data_to_csv(mapping_list, mapping_file)

        # HUMAN STEP
