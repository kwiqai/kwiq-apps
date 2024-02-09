import os

from kwiq.core.flow import Flow
from kwiq.core.utils import current_date
from kwiq.task.clean_directory import CleanDirectory
from kwiq.task.copy_directory import CopyDirectory
from kwiq.task.run_command import RunCommand
from smart_code_merge.commons import AppConfig


class Commit(Flow):
    name: str = "commit"

    #   step 9: check-in merges to respective projects
    def fn(self, config: AppConfig, target_branch_name: str = f"upstream_merge_{current_date()}") -> None:
        working_dir = config.working_dir
        for project in config.projects:
            target_directory = project.local_project_path

            # git checkout - b target_branch_name
            os.chdir(target_directory)
            RunCommand().execute(command=f'git checkout -b {target_branch_name}')

            # clean dir
            CleanDirectory().execute(directory=target_directory, filter=lambda i: i == ".git")

            project_directory = (working_dir / f"__{project.key}" / "merge_dir").resolve()

            # copy dir
            CopyDirectory().execute(src_directory=project_directory,
                                    dest_directory=target_directory,
                                    filter=lambda i: i == ".git")

            RunCommand().execute(command='git add .')
            RunCommand().execute(command=f'git commit -m "{target_branch_name} version"')
            RunCommand().execute(command=f'git push origin {target_branch_name}')
