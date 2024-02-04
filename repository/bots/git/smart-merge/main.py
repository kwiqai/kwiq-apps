import os
from pathlib import Path
from typing import List

from pydantic import BaseModel

import apply_renames
import setup_3_way_merge
from apply_3_way_merge import ApplyThreeWayMerge
from apply_renames import ApplyRenames
from commons import RepoInfo
import extract_words
from extract_words import ExtractWords
from run_command import RunCommand
from setup_3_way_merge import SetupThreeWayMerge
from workflow import human_step
from workflow.csv_writer import write_data_to_csv
from workflow.human_step import HumanStep


class ConfigData(BaseModel):
    local_project_path: str


if __name__ == '__main__':
    projects = {
        'agent': ConfigData(local_project_path='agent'),
        'server': ConfigData(local_project_path='server'),
        'cli': ConfigData(local_project_path='cli'),
        'message': ConfigData(local_project_path='proto'),
    }

    current_dir = os.getcwd()

    # step 1: setup 3 way merge for all projects
    # for folder, data in projects.items():
    #     os.chdir(current_dir)
    #     # server
    #     repos = {
    #         'base': RepoInfo(repo_path='https://github.com/deepflowio/deepflow.git',
    #                          branch='ca3706a53ead5e8f0a5ca7574d8616f4e6c14e4b',
    #                          sub_path=folder),
    #         'local': RepoInfo(repo_path=f'https://github.com/nebulaiq/nebulaiq-telemetry-{data.local_project_path}.git',
    #                           branch='main',
    #                           sub_path=''),
    #         'remote': RepoInfo(repo_path='https://github.com/deepflowio/deepflow.git',
    #                            branch='main',
    #                            sub_path=folder)
    #     }
    #
    #     SetupThreeWayMerge().execute(setup_3_way_merge.InputDataModel(output_dir=f"__{folder}", repo_infos=repos))

    # for each project
    #   step 2: checkout remote
    #   step 3: extract words for rename
    # unique_words = set()
    # for folder, data in projects.items():
    #     os.chdir(current_dir)
    #     base_dir = Path(f"__{folder}")
    #     project_directory = (base_dir / "merge_dir").resolve()
    #     os.chdir(project_directory)
    #     RunCommand().execute("git checkout local")
    #     words = ExtractWords().execute(extract_words.InputModel(words_regex="deepflow",
    #                                                             search_directory=project_directory))
    #     unique_words = unique_words.union(words)
    #
    # os.chdir(current_dir)
    # mapping_file = Path("input_mapping.csv")
    #
    # mapping_list: List[apply_renames.MappingData] = [apply_renames.MappingData(original_word=word, renamed_word=word)
    #                                                  for word
    #                                                  in unique_words]
    #
    # write_data_to_csv(mapping_list, mapping_file)

    os.chdir(current_dir)
    mapping_file = Path("rename_mapping.csv")

    def validate_mapping_file() -> bool:
        if mapping_file.exists():
            print(f"The file '{mapping_file}' exists.")
            return True

        print(f"The file '{mapping_file}' does not exist.")
        return False


    # step 4: human in the loop... expect file
    status = HumanStep().execute(
        human_step.InputModel(instruction="Ensure mapping file between original and renamed words exist",
                              validation_fn=validate_mapping_file))
    if status:
        mapping_file = mapping_file.resolve()

        # for each project
        #   step 5: apply transformation
        #   step 6: commit code
        #   step 7: apply 3 way merge
        for folder, data in projects.items():
            os.chdir(current_dir)
            base_dir = Path(f"__{folder}")
            project_directory = (base_dir / "merge_dir").resolve()
            # os.chdir(project_directory)
            # RunCommand().execute("git checkout remote")
            #
            # ApplyRenames().execute(apply_renames.InputModel(mapping_csv_path=mapping_file,
            #                                                 search_directory=project_directory))

            RunCommand().execute('git add .')
            RunCommand().execute(f'git commit -m "post transformation version"')
            #
            # ApplyThreeWayMerge().execute(base_dir)

        #   step 8: merge conflicts manually
        #   step 9: check-in merges to respective projects
