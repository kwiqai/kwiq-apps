import os
import shutil
from pathlib import Path
from typing import Dict

from pydantic import BaseModel

from commons import RepoInfo, clean_directory
from run_command import RunCommand
from workflow.step import Step, OutputModelType, InputModelType


def setup_git_repo(merge_dir: Path, temp_dir: Path, repo_infos: Dict[str, RepoInfo]):
    os.makedirs(merge_dir, exist_ok=True)
    os.chdir(merge_dir)
    RunCommand().execute('git init')
    RunCommand().execute('git commit --allow-empty -m "Initial empty commit"')
    RunCommand().execute('git branch -M base')

    os.makedirs(temp_dir, exist_ok=True)

    for branch_name, repo_info in repo_infos.items():
        # Clone specific branch to a temp folder
        temp_clone_dir = os.path.join(temp_dir, f"temp_{branch_name}")
        RunCommand().execute(f'git clone {repo_info.repo_path} {temp_clone_dir}')
        os.chdir(temp_clone_dir)
        RunCommand().execute(f'git checkout {repo_info.branch}')
        os.chdir(merge_dir)

        # If not base branch, create a new branch
        if branch_name != 'base':
            RunCommand().execute('git checkout base')
            RunCommand().execute(f'git checkout -b {branch_name}')

        clean_directory(merge_dir)

        # Copy the specific folder to the main repo directory
        src_dir = os.path.join(temp_clone_dir, repo_info.sub_path)

        # TODO: extract as command...
        for item in os.listdir(src_dir):
            if item == '.git':
                continue

            s = os.path.join(src_dir, item)
            d = os.path.join(merge_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, False, None)
            else:
                shutil.copy2(s, d)

        # Git add and commit
        RunCommand().execute('git add .')
        RunCommand().execute(f'git commit -m "{branch_name} version"')

        # Clean up temporary clone
        shutil.rmtree(temp_clone_dir)


class InputDataModel(BaseModel):
    output_dir: str
    repo_infos: Dict[str, RepoInfo]


class SetupThreeWayMerge(Step):
    @property
    def input_model(self) -> InputModelType:
        return InputDataModel

    @property
    def output_model(self) -> OutputModelType:
        return None

    def fn(self, data: InputDataModel):
        # Inputs
        base_dir = Path(data.output_dir)
        merge_dir = (base_dir / "merge_dir").resolve()
        temp_dir = (base_dir / "temp_dir").resolve()

        # Set up the git repository and branches
        setup_git_repo(merge_dir, temp_dir, data.repo_infos)
